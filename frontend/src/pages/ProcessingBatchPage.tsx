import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getDocumentStatus
} from "../services/documentService";

type EstadoDocumento =
  | "PENDIENTE"
  | "PROCESANDO"
  | "PROCESADO"
  | "ERROR";

interface DocumentoLote {
  id: number;
  estado: EstadoDocumento;
}

export default function ProcessingBatchPage() {

  const navigate = useNavigate();

  const [documentos, setDocumentos] =
    useState<DocumentoLote[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    const stored =
      sessionStorage.getItem(
        "batchDocuments"
      );

    if (!stored) {

      navigate("/upload");

      return;
    }

    const ids =
      JSON.parse(stored);

    setDocumentos(
      ids.map(
        (id: number) => ({
          id,
          estado: "PENDIENTE"
        })
      )
    );

    setLoading(false);

  }, [navigate]);

  useEffect(() => {

    if (documentos.length === 0)
      return;

    const interval =
      setInterval(async () => {

        try {

          const updated =
            await Promise.all(

              documentos.map(
                async (doc) => {

                  const response =
                    await getDocumentStatus(
                      String(doc.id)
                    );

                  return {
                    ...doc,
                    estado:
                      response.estado
                  };

                }
              )

            );

          setDocumentos(updated);

          const allDone =
            updated.every(
              doc =>
                doc.estado ===
                "PROCESADO"
            );

          if (allDone) {

            clearInterval(interval);

            sessionStorage.removeItem(
              "batchDocuments"
            );

            setTimeout(() => {

              navigate("/upload");

            }, 2000);

          }

        } catch (error) {

          console.error(error);

        }

      }, 3000);

    return () =>
      clearInterval(interval);

  }, [documentos, navigate]);

  if (loading) {

    return (
      <h2>
        Cargando...
      </h2>
    );

  }

  const processed =
    documentos.filter(
      d =>
        d.estado ===
        "PROCESADO"
    ).length;

  const progress =
    documentos.length === 0
      ? 0
      : Math.round(
          (processed /
            documentos.length) *
            100
        );

  return (

    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#eef2f6"
      }}
    >

      <div
        style={{
          width: "700px",
          background: "#fff",
          borderRadius: "12px",
          padding: "30px",
          border:
            "1px solid #dbe3ea",
          boxShadow:
            "0 4px 12px rgba(15,23,42,0.08)"
        }}
      >

        <h2>
          Procesamiento por Lotes
        </h2>

        <p>
          Documentos enviados:
          {" "}
          {documentos.length}
        </p>

        <div
          style={{
            height: "20px",
            background: "#e2e8f0",
            borderRadius: "20px",
            overflow: "hidden",
            marginBottom: "20px"
          }}
        >

          <div
            style={{
              width:
                `${progress}%`,
              height: "100%",
              background:
                "#2563eb",
              transition:
                "width .3s"
            }}
          />

        </div>

        <p>
          Avance:
          {" "}
          {progress}%
        </p>

        <div>

          {
            documentos.map(
              doc => (

                <div
                  key={doc.id}
                  style={{
                    display:
                      "flex",
                    justifyContent:
                      "space-between",
                    padding:
                      "10px 0",
                    borderBottom:
                      "1px solid #e5e7eb"
                  }}
                >

                  <span>
                    Documento {
                      doc.id
                    }
                  </span>

                  <span>
                    {
                      doc.estado
                    }
                  </span>

                </div>

              )
            )
          }

        </div>

        {
          progress ===
            100 && (

            <div
              style={{
                marginTop:
                  "20px",
                color:
                  "#16a34a",
                fontWeight:
                  600
              }}
            >
              Todos los documentos
              fueron procesados.
              Redirigiendo...
            </div>

          )
        }

      </div>

    </div>

  );

}