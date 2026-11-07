import {
  useEffect,
  useState
} from "react";

import {
  useNavigate
} from "react-router-dom";

import {
  getDocuments
} from "../services/documentService";

export default function AuditDashboardPage() {

  const navigate =
    useNavigate();

  const [documents, setDocuments] =
    useState<any[]>([]);

  const [nombre, setNombre] =
    useState("");

  const [tipo, setTipo] =
    useState("");

  const [estado, setEstado] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [selectedDocument, setSelectedDocument] =
    useState<any>(null);

  const loadDocuments =
    async () => {

      try {

        const response =
          await getDocuments(
            nombre,
            tipo,
            estado
          );

        setDocuments(
          response
        );

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);

      }
    };

  useEffect(() => {

    loadDocuments();

  }, []);

  useEffect(() => {

    loadDocuments();

  }, [estado]);

  if (loading) {

    return (
      <h2>
        Cargando documentos...
      </h2>
    );
  }

  return (

    <div
      style={{
        minHeight: "100vh",
        background: "#eef2f6",
        padding: "16px"
      }}
    >

      <div
        style={{
          background: "#ffffff",
          padding: "20px 28px",
          borderRadius: "12px",
          border: "1px solid #cfd8e3",
          boxShadow: "0 4px 12px rgba(15,23,42,0.08)",
          marginBottom: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >

        <div>

          <h1
            style={{
              margin: 0,
              color: "#1e3a8a"
            }}
          >
            Sistema de Digitalización - Módulo de Auditoría
          </h1>

          <p
            style={{
              margin: "4px 0 0 0",
              color: "#64748b"
            }}
          >
            Instituto Nacional de Enfermedades Neoplásicas (INEN)
          </p>

        </div>

        <div
          style={{
            color: "#64748b"
          }}
        >
          Auditor
        </div>

      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "360px 1fr",
          gap: "16px"
        }}
      >

        <div
          style={{
            background: "#fff",
            borderRadius: "12px",
            border: "1px solid #dbe3ea",
            overflow: "hidden"
          }}
        >

          <div
            style={{
              padding: "18px"
            }}
          >

            <h3
              style={{
                marginTop: 0,
                color: "#334155"
              }}
            >
              REGISTRO DE DOCUMENTOS
            </h3>

            <input
              type="text"
              placeholder="Buscar por paciente..."
              value={nombre}
              onChange={(e) =>
                setNombre(
                  e.target.value
                )
              }
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                marginBottom: "12px",
                boxSizing: "border-box"
              }}
            />

            <input
              type="text"
              placeholder="Tipo documento..."
              value={tipo}
              onChange={(e) =>
                setTipo(
                  e.target.value
                )
              }
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                marginBottom: "12px",
                boxSizing: "border-box"
              }}
            />

            <button
              onClick={loadDocuments}
              style={{
                width: "100%",
                padding: "10px",
                border: "none",
                borderRadius: "8px",
                background: "#1e40af",
                color: "white",
                cursor: "pointer",
                marginBottom: "12px"
              }}
            >
              Buscar
            </button>

            <div
              style={{
                display: "flex",
                gap: "8px",
                flexWrap: "wrap"
              }}
            >

              <button
                onClick={() =>
                  setEstado("")
                }
                style={{
                  border: "none",
                  borderRadius: "20px",
                  padding: "6px 14px",
                  cursor: "pointer",
                  background:
                    estado === ""
                      ? "#1e40af"
                      : "#e2e8f0",
                  color:
                    estado === ""
                      ? "#fff"
                      : "#334155"
                }}
              >
                Todos
              </button>

              <button
                onClick={() =>
                  setEstado("PENDIENTE")
                }
                style={{
                  border: "none",
                  borderRadius: "20px",
                  padding: "6px 14px",
                  cursor: "pointer",
                  background:
                    estado === "PENDIENTE"
                      ? "#facc15"
                      : "#e2e8f0"
                }}
              >
                Pendientes
              </button>

              <button
                onClick={() =>
                  setEstado("VALIDADO")
                }
                style={{
                  border: "none",
                  borderRadius: "20px",
                  padding: "6px 14px",
                  cursor: "pointer",
                  background:
                    estado === "VALIDADO"
                      ? "#22c55e"
                      : "#e2e8f0"
                }}
              >
                Auditados
              </button>

            </div>

          </div>

          <div>

            {
              documents.map(
                (doc) => (

                  <div
                    key={
                      doc.id_documento
                    }
                    onClick={() =>
                      setSelectedDocument(doc)
                    }

                    style={{
                      padding: "16px",
                      borderTop:
                        "1px solid #e2e8f0",
                      cursor: "pointer"
                    }}
                  >

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between"
                      }}
                    >

                      <strong
                        style={{
                          color: "#1e40af"
                        }}
                      >
                        DOC-
                        {doc.id_documento}
                      </strong>

                      <span
                        style={{
                          fontSize: "12px",
                          padding: "4px 10px",
                          borderRadius: "16px",
                          background:
                            doc.estado_validacion ===
                            "VALIDADO"
                              ? "#dcfce7"
                              : "#fef3c7"
                        }}
                      >
                        {
                          doc.estado_validacion
                        }
                      </span>

                    </div>

                    <div
                      style={{
                        marginTop: "6px",
                        color: "#64748b",
                        fontSize: "14px"
                      }}
                    >
                      {
                        doc.tipo_documento ||
                        "Sin tipo"
                      }
                    </div>

                    <div
                      style={{
                        marginTop: "4px",
                        color: "#64748b",
                        fontSize: "13px"
                      }}
                    >
                      {
                        doc.nombre ||
                        "Sin nombre"
                      }
                    </div>

                  </div>

                )
              )
            }

          </div>

        </div>

        <div
  style={{
    background: "#fff",
    borderRadius: "12px",
    border: "1px solid #dbe3ea",
    minHeight: "700px",
    padding: "20px"
  }}
>
  {
    !selectedDocument ? (

      <div
        style={{
          height: "100%",
          minHeight: "650px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "#94a3b8",
          fontSize: "18px"
        }}
      >
        Seleccione un documento del listado para comenzar la auditoría
      </div>

    ) : (

      <>

        <h2
          style={{
            marginTop: 0
          }}
        >
          Vista Previa del Documento
        </h2>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: "20px"
          }}
        >

          <img
            src={`http://localhost:8000/documents/${selectedDocument.id_documento}/image`}
            alt={`DOC-${selectedDocument.id_documento}`}
            style={{
              width: "100%",
              maxHeight: "550px",
              objectFit: "contain",
              border: "1px solid #ddd",
              borderRadius: "8px"
            }}
          />

        </div>

        <div
          style={{
            marginBottom: "20px"
          }}
        >

          <p>
            <strong>
              Documento:
            </strong>
            {" "}
            DOC-{selectedDocument.id_documento}
          </p>

          <p>
            <strong>
              Nombre:
            </strong>
            {" "}
            {
              selectedDocument.nombre ||
              "Sin nombre"
            }
          </p>

          <p>
            <strong>
              Tipo:
            </strong>
            {" "}
            {
              selectedDocument.tipo_documento ||
              "Sin tipo"
            }
          </p>

          <p>
            <strong>
              Estado:
            </strong>
            {" "}
            {
              selectedDocument.estado_validacion
            }
          </p>

        </div>

        <button
          onClick={() =>
            navigate(
              `/review/${selectedDocument.id_documento}`
            )
          }
          style={{
            padding: "12px 20px",
            background: "#1e40af",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer"
          }}
        >
          Auditar Documento
        </button>

      </>

    )
  }
</div>
      </div>

    </div>
  );
}