"""
Fine-tuning de Qwen2.5-VL-7B-Instruct con (Q)LoRA para HTR a nivel línea.

- Congela el encoder visual y entrena LoRA solo en el modelo de lenguaje.
- La loss se calcula SOLO sobre la respuesta (la transcripción), no sobre el prompt.

Uso (QLoRA, cabe en ~24 GB):
  python train_qwen_lora.py --train data/train.jsonl --val data/val.jsonl --out runs/rodrigo-lora --qlora

Kaggle (T4 16 GB, sin bf16):
  python train_qwen_lora.py ... --qlora --fp16 --bs 1 --grad_accum 16 --max_pixels 401408
"""
import argparse
import inspect
import json
import math

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from PIL import Image
from torch.utils.data import Dataset
from transformers import (
    AutoProcessor,
    BitsAndBytesConfig,
    Qwen2_5_VLForConditionalGeneration,
    Trainer,
    TrainingArguments,
)

PROMPT = "Transcribe exactamente el texto manuscrito de esta imagen. Devuelve solo la transcripción, sin comentarios."


class JsonlDataset(Dataset):
    def __init__(self, path, limit=None):
        with open(path, encoding="utf-8") as f:
            self.rows = [json.loads(l) for l in f if l.strip()]
        if limit:
            self.rows = self.rows[:limit]

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        return self.rows[i]


class Collator:
    def __init__(self, processor):
        self.p = processor
        tok = processor.tokenizer
        self.asst = tok.encode("<|im_start|>assistant\n", add_special_tokens=False)
        self.pad_id = tok.pad_token_id

    def _answer_start(self, ids):
        n = len(self.asst)
        for i in range(len(ids) - n, -1, -1):
            if ids[i : i + n] == self.asst:
                return i + n
        return None

    def __call__(self, batch):
        texts, images = [], []
        for r in batch:
            msgs = [
                {"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]},
                {"role": "assistant", "content": [{"type": "text", "text": r["text"]}]},
            ]
            texts.append(self.p.apply_chat_template(msgs, tokenize=False))
            images.append(Image.open(r["image"]).convert("RGB"))

        enc = self.p(text=texts, images=images, return_tensors="pt", padding=True)
        labels = enc["input_ids"].clone()
        for b in range(labels.size(0)):
            start = self._answer_start(enc["input_ids"][b].tolist())
            labels[b, : start if start is not None else labels.size(1)] = -100
        labels[labels == self.pad_id] = -100
        enc["labels"] = labels
        return enc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-VL-7B-Instruct")
    ap.add_argument("--train", required=True)
    ap.add_argument("--val", required=True)
    ap.add_argument("--out", default="runs/rodrigo-lora")
    ap.add_argument("--qlora", action="store_true", help="Carga en 4-bit (recomendado si tienes <40 GB de VRAM)")
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--bs", type=int, default=4)
    ap.add_argument("--grad_accum", type=int, default=4)
    ap.add_argument("--lora_r", type=int, default=16)
    ap.add_argument("--max_pixels", type=int, default=1024 * 28 * 28)
    ap.add_argument("--max_val", type=int, default=300, help="Limita la validación para que no tarde demasiado")
    ap.add_argument("--fp16", action="store_true", help="Usa fp16 en vez de bf16 (OBLIGATORIO en Kaggle T4/P100)")
    ap.add_argument("--limit_train", type=int, default=None, help="Usa solo N líneas de train (prueba rápida)")
    ap.add_argument("--resume", action="store_true", help="Continúa desde el último checkpoint en --out")
    args = ap.parse_args()
    dtype = torch.float16 if args.fp16 else torch.bfloat16

    processor = AutoProcessor.from_pretrained(args.model, min_pixels=64 * 28 * 28, max_pixels=args.max_pixels)
    processor.tokenizer.padding_side = "right"

    bnb = (
        BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,
        )
        if args.qlora
        else None
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=dtype,
        quantization_config=bnb,
        attn_implementation="sdpa",
        device_map={"": 0},  # una sola GPU: más estable que repartir el modelo entre 2 T4
    )

    if args.qlora:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    else:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()

    # LoRA solo en el LLM: la regex excluye cualquier módulo del encoder visual ("visual")
    lora = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_r * 2,
        lora_dropout=0.05,
        target_modules=r"^(?!.*visual).*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    train_ds = JsonlDataset(args.train, limit=args.limit_train)
    val_ds = JsonlDataset(args.val, limit=args.max_val)
    print(f"train={len(train_ds)}  val={len(val_ds)}")

    # warmup en pasos (transformers 5.x eliminó warmup_ratio)
    steps_per_epoch = math.ceil(len(train_ds) / (args.bs * args.grad_accum))
    warmup_steps = max(1, int(0.03 * steps_per_epoch * args.epochs))

    targ_kwargs = dict(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.bs,
        per_device_eval_batch_size=args.bs,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=warmup_steps,
        weight_decay=0.0,
        bf16=not args.fp16,
        fp16=args.fp16,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=200,
        save_strategy="steps",
        save_steps=200,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        remove_unused_columns=False,
        dataloader_num_workers=2,
        report_to="none",
    )
    # Compatibilidad entre versiones de transformers: descarta argumentos que la versión instalada no conoce
    valid = set(inspect.signature(TrainingArguments.__init__).parameters)
    if "eval_strategy" not in valid and "evaluation_strategy" in valid:  # transformers < 4.41
        targ_kwargs["evaluation_strategy"] = targ_kwargs.pop("eval_strategy")
    dropped = [k for k in targ_kwargs if k not in valid]
    if dropped:
        print("Aviso: esta versión de transformers no acepta", dropped, "-> se ignoran")
    targs = TrainingArguments(**{k: v for k, v in targ_kwargs.items() if k in valid})
    print(f"pasos/época={steps_per_epoch}  warmup_steps={warmup_steps}")

    trainer = Trainer(
        model=model,
        args=targs,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=Collator(processor),
    )
    trainer.train(resume_from_checkpoint=True if args.resume else None)
    trainer.save_model(args.out)
    processor.save_pretrained(args.out)
    print(f"Adaptador LoRA guardado en {args.out}")


if __name__ == "__main__":
    main()
