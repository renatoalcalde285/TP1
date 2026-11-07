import {
  useEffect,
  useState
} from "react";

import {
  useParams
} from "react-router-dom";

import {
  getDocumentStatus
} from "../services/documentService";

import "../styles/processing.css";

type EstadoDocumento =
  | "PENDIENTE"
  | "PROCESANDO"
  | "PROCESADO"
  | "ERROR";

import {
  useNavigate
} from "react-router-dom";

export default function ProcessingPage() {

  const { documentId } = useParams();
  const navigate = useNavigate();

  const [estado, setEstado] =
    useState<EstadoDocumento>(
      "PENDIENTE"
    );

  useEffect(() => {

    if (!documentId) return;

    const fetchStatus = async () => {

      try {

        const data =
          await getDocumentStatus(
            documentId
          );

        setEstado(
          data.estado
        );

        if (
              data.estado === "PROCESADO"
            ) {

              navigate(
                `/review/${documentId}`
              );

            }

      } catch (error) {

        console.error(error);

        setEstado("ERROR");
      }
    };

    fetchStatus();

    const interval = setInterval(
      fetchStatus,
      3000
    );

    return () =>
      clearInterval(interval);

  }, [documentId]);

  const getProgress = () => {

    switch (estado) {

      case "PENDIENTE":
        return 25;

      case "PROCESANDO":
        return 75;

      case "PROCESADO":
        return 100;

      case "ERROR":
        return 0;

      default:
        return 0;
    }
  };

  const getMessage = () => {

    switch (estado) {

      case "PENDIENTE":
        return "Documento en cola...";

      case "PROCESANDO":
        return "Procesando documento...";

      case "PROCESADO":
        return "Proceso completado";

      case "ERROR":
        return "Error durante el procesamiento";

      default:
        return "";
    }
  };

  return (

    <div className="processing-page">

      <div className="processing-card">

        <h2>
          Procesamiento del documento
        </h2>

        <p>
          El documento está siendo procesado por el sistema
        </p>

        <div className="file-box">
          Documento #{documentId}
        </div>

        <div
            style={{
                marginTop: "20px",
                marginBottom: "20px",
                fontWeight: "600"
            }}
            >
            Estado actual: {estado}
        </div>

        <button
          disabled
          className="processing-button"
        >
          Transcribir documento
        </button>

        <div className="progress-container">

          <div className="progress-info">

            <span>
              {getMessage()}
            </span>

            <span>
              {getProgress()}%
            </span>

          </div>

          <div className="progress-bar">

            <div
              className="progress-fill"
              style={{
                width: `${getProgress()}%`
              }}
            />

          </div>

        </div>

      </div>

    </div>
  );
}
