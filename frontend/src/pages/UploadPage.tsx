import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { uploadDocuments } from "../services/documentService";

import "../styles/upload.css";

export default function UploadPage() {

  const navigate = useNavigate();

  const [files, setFiles] =
    useState<FileList | null>(null);

  const [loading, setLoading] =
    useState(false);

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {

    setFiles(e.target.files);
  };

  const handleUpload = async () => {

    if (!files) {

      alert(
        "Seleccione al menos un archivo"
      );

      return;
    }

    try {

      setLoading(true);

      const data =
        await uploadDocuments(files);

      const documentId =
        data[0].id_documento;

      navigate(
        `/processing/${documentId}`
      );

    } catch (error) {

      console.error(error);

      alert(
        "Error al cargar documentos"
      );
    }
    finally {

      setLoading(false);
    }
  };

  return (

    <div className="upload-page">

      <div className="upload-card">

        <h2>
          Selecciona una imagen de documento
        </h2>

        <p>
          PNG · JPG · TIFF — cualquier resolución
        </p>

        <div className="file-container">

          <input
            type="file"
            multiple
            accept=".png,.jpg,.jpeg,.tif,.tiff"
            onChange={handleFileChange}
          />

          <span>

            {
              files?.length
                ? `${files.length} archivo(s) seleccionado(s)`
                : "No se ha seleccionado ningún archivo"
            }

          </span>

        </div>

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={loading}
        >
          {
            loading
              ? "Subiendo..."
              : "Transcribir documento"
          }
        </button>

      </div>

    </div>
  );
}