import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { uploadDocuments } from "../services/documentService";

import "../styles/upload.css";

export default function UploadPage() {

  const navigate = useNavigate();

  const handleLogout = () => {

  localStorage.removeItem("token");

  navigate("/");

};

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

      const documentIds = data.map(
        (item: any) => item.id_documento
      );

      sessionStorage.setItem(
        "batchDocuments",
        JSON.stringify(documentIds)
      );

      navigate(
        "/processing-batch"
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

    <div
      style={{
        position: "absolute",
        top: "20px",
        right: "20px"
      }}
    >
      <button
        onClick={handleLogout}
        style={{
          padding: "10px 16px",
          borderRadius: "8px",
          border: "1px solid #cbd5e1",
          background: "#475569",
          color: "#ffffff",
          cursor: "pointer",
          fontWeight: 500,
          boxShadow: "0 2px 6px rgba(0,0,0,.08)"
        }}
      >
        Cerrar sesión
      </button>
    </div>

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