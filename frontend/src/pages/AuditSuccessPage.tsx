import { useNavigate, useParams } from "react-router-dom";

export default function AuditSuccessPage() {

  const navigate = useNavigate();

  const { documentId } = useParams();

  return (

    <div
      style={{
        minHeight: "100vh",
        background: "#9aa0ac",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}
    >

      <div
        style={{
          width: "420px",
          background: "#fff",
          borderRadius: "12px",
          padding: "32px",
          textAlign: "center",
          boxShadow: "0 8px 20px rgba(0,0,0,.15)"
        }}
      >

        <div
          style={{
            width: "72px",
            height: "72px",
            borderRadius: "50%",
            background: "#dcfce7",
            margin: "0 auto 20px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: "36px",
            color: "#16a34a"
          }}
        >
          ✓
        </div>

        <h2>
          Documento Auditado Exitosamente
        </h2>

        <p
          style={{
            color: "#64748b",
            lineHeight: 1.6
          }}
        >
          La Historia Clínica DOC-{documentId}
          ha sido verificada, corregida y aprobada
          correctamente.
        </p>

        <button
          onClick={() => navigate("/audit")}
          style={{
            width: "100%",
            padding: "12px",
            background: "#1e40af",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            marginTop: "20px",
            cursor: "pointer"
          }}
        >
          Auditar siguiente documento
        </button>

        <button
          onClick={() => navigate("/audit")}
          style={{
            width: "100%",
            padding: "12px",
            background: "#fff",
            color: "#475569",
            border: "1px solid #cbd5e1",
            borderRadius: "8px",
            marginTop: "10px",
            cursor: "pointer"
          }}
        >
          Volver al listado general
        </button>

      </div>

    </div>

  );

}