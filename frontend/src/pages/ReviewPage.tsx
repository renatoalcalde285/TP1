
import {
  useEffect,
  useState
} from "react";

import {
  useParams,
  useNavigate
} from "react-router-dom";

import {
  getDocumentReview,
  validateDocument
} from "../services/documentService";

export default function ReviewPage() {

  const { documentId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState<any>(null);
  const [campos, setCampos] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const loadData = async () => {

      try {

        const response = await getDocumentReview(
          documentId!
        );

        setData(response);
        setCampos(response.datos_estructurados || {});

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);

      }
    };

    loadData();

  }, [documentId]);

  const handleValidate = async () => {

    try {

      await validateDocument(
        documentId!,
        campos
      );

      navigate(
        `/audit-success/${documentId}`
      );

      const response = await getDocumentReview(
        documentId!
      );

      console.log("REVIEW RESPONSE");
      console.log(response);

      setData(response);
      setCampos(response.datos_estructurados || {});

    } catch (error) {

      console.error(error);

      alert("Error al validar documento");

    }
  };

  if (loading) {
    return <h2>Cargando...</h2>;
  }

  return (

    <div className="review-page">

      <style>{`

        /* CONFIGURACIÓN GENERAL */

        .review-page,
        .review-page * {
          box-sizing: border-box;
        }

        .review-page {
          height: 100vh;
          background: #eef3f8;
          padding: 10px;
          font-family: Arial, Helvetica, sans-serif;
          color: #334155;
          overflow: hidden;
        }

        /* CONTENEDOR PRINCIPAL */

        .review-container {
          width: 100%;
          max-width: 1250px;
          height: 100%;
          min-height: 0;
          margin: 0 auto;
          background: #ffffff;
          border: 1px solid #d5deea;
          border-radius: 8px;
          display: flex;
          flex-direction: column;
          box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
          overflow: hidden;
        }

        /* ENCABEZADO */

        .review-header {
          flex-shrink: 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 20px;
          background: #ffffff;
          border-bottom: 1px solid #dbe3ec;
          gap: 15px;
        }

        .review-header h1 {
          font-size: 20px;
          font-weight: 600;
          color: #173b87;
          margin: 0 0 5px 0;
        }

        .review-subtitle {
          font-size: 12px;
          color: #718096;
          margin: 0;
        }

        .review-status {
          background: #fff2c9;
          color: #a45a00;
          border: 1px solid #ffe29a;
          border-radius: 20px;
          padding: 6px 13px;
          font-size: 11px;
          font-weight: 500;
          white-space: nowrap;
        }

        /* CONTENIDO PRINCIPAL */

        .review-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          padding: 16px;
          flex: 1;
          min-height: 0;
          overflow: hidden;
          background: #f1f5f9;
        }

        /* PANELES */

        .review-panel {
          background: #ffffff;
          border: 1px solid #d5deea;
          border-radius: 9px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          min-width: 0;
          min-height: 0;
          height: 100%;
          box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
        }

        .panel-header {
          flex-shrink: 0;
          min-height: 48px;
          padding: 12px 17px;
          display: flex;
          align-items: center;
          background: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
        }

        .panel-header h2 {
          font-size: 13px;
          font-weight: 700;
          color: #475569;
          letter-spacing: 0.4px;
          margin: 0;
        }

        /* IMAGEN ORIGINAL */

        .image-container {
          flex: 1;
          min-height: 0;
          padding: 0;
          background: #e2e8f0;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
        }

        .image-container img {
          display: block;
          width: 100%;
          height: 100%;
          object-fit: contain;
          object-position: center;
        }

        /* FORMULARIO */

        .form-content {
          flex: 1;
          min-height: 0;
          overflow-y: auto;
          padding: 16px 20px;
          background: #ffffff;
          display: flex;
          flex-direction: column;
          gap: 14px;
        }

        .form-content::-webkit-scrollbar {
          width: 8px;
        }

        .form-content::-webkit-scrollbar-track {
          background: #f1f5f9;
        }

        .form-content::-webkit-scrollbar-thumb {
          background: #a8a8a8;
          border-radius: 10px;
        }

        /* SECCIONES */

        .form-section {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .section-title {
          color: #173b87;
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.3px;
          padding-bottom: 7px;
          border-bottom: 1px solid #dbeafe;
          margin: 0;
        }

        /* CAMPOS */

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .form-group label {
          color: #64748b;
          font-size: 11px;
          font-weight: 500;
        }

        .form-control {
          width: 100%;
          padding: 9px 11px;
          border: 1px solid #cbd8e8;
          border-radius: 6px;
          background: #ffffff;
          color: #334155;
          font-size: 12px;
          font-family: inherit;
          outline: none;
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-control:focus {
          border-color: #4f83ff;
          box-shadow: 0 0 0 3px rgba(79, 131, 255, 0.12);
        }

        textarea.form-control {
          resize: vertical;
          min-height: 90px;
          line-height: 1.5;
        }

        /* TRATAMIENTOS */

        .treatment-card {
          background: #f8fafc;
          border: 1px solid #dbe3ec;
          border-radius: 7px;
          padding: 11px;
          display: flex;
          flex-direction: column;
          gap: 9px;
        }

        /* BARRA INFERIOR */

        .review-footer {
          flex-shrink: 0;
          min-height: 58px;
          padding: 9px 16px;
          display: flex;
          justify-content: flex-end;
          align-items: center;
          gap: 10px;
          background: #ffffff;
          border-top: 1px solid #dbe3ec;
        }

        .btn-save {
          background: #24459c;
          color: #ffffff;
          border: 1px solid #24459c;
          border-radius: 6px;
          padding: 11px 22px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }

        .btn-save:hover {
          background: #19377f;
        }

        .btn-save:active {
          transform: scale(0.98);
        }

        /* RESPONSIVE */

        @media (max-width: 850px) {

          .review-page {
            height: auto;
            min-height: 100vh;
            overflow: auto;
          }

          .review-container {
            height: auto;
            min-height: calc(100vh - 20px);
          }

          .review-content {
            grid-template-columns: 1fr;
            overflow: visible;
          }

          .review-panel {
            min-height: 450px;
          }

          .image-container {
            min-height: 400px;
          }

          .form-content {
            overflow: visible;
          }

        }

        @media (max-width: 500px) {

          .review-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .review-footer {
            justify-content: stretch;
          }

          .btn-save {
            width: 100%;
          }

          .form-content {
            padding: 16px;
          }

        }

      `}</style>

      <div className="review-container">

        {/* ENCABEZADO */}

        <header className="review-header">

          <div>

            <button
              onClick={() => navigate("/audit")}
              style={{
                border: "none",
                background: "transparent",
                color: "#173b87",
                fontWeight: 600,
                cursor: "pointer",
                padding: 0,
                marginBottom: "6px"
              }}
            >
              ← Volver
            </button>

            <h1>
              Auditoría de Documento Médico
            </h1>

            <p className="review-subtitle">
              ID: DOC-{data.id_documento}
            </p>

          </div>

          <span className="review-status">
            {data.estado_validacion || "Pendiente de Revisión"}
          </span>

        </header>

        {/* CONTENIDO PRINCIPAL */}

        {data.datos_estructurados && (

          <main className="review-content">

            {/* PANEL IZQUIERDO: IMAGEN ORIGINAL */}

            <section className="review-panel">

              <div className="panel-header">

                <h2>
                  IMAGEN ORIGINAL
                </h2>

              </div>

              <div className="image-container">

                <img
                  src={`http://localhost:8000/documents/${documentId}/image`}
                  alt="Documento médico original"
                />

              </div>

            </section>

            {/* PANEL DERECHO: CAMPOS EXTRAÍDOS */}

            <section className="review-panel">

              <div className="panel-header">

                <h2>
                  DATOS EXTRAÍDOS POR IA (EDITABLE)
                </h2>

              </div>

              <div className="form-content">

                {/* INFORMACIÓN DEL PACIENTE */}

                <section className="form-section">

                  <h3 className="section-title">
                    Información del Paciente
                  </h3>

                  <div className="form-group">

                    <label>Nombre</label>

                    <input
                      className="form-control"
                      value={campos.paciente?.nombre || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          paciente: {
                            ...campos.paciente,
                            nombre: e.target.value
                          }
                        })
                      }
                    />

                  </div>

                  <div className="form-group">

                    <label>N° Historia Clínica</label>

                    <input
                      className="form-control"
                      value={campos.paciente?.numero_hc || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          paciente: {
                            ...campos.paciente,
                            numero_hc: e.target.value
                          }
                        })
                      }
                    />

                  </div>

                  <div className="form-group">

                    <label>Sexo</label>

                    <input
                      className="form-control"
                      value={campos.paciente?.sexo || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          paciente: {
                            ...campos.paciente,
                            sexo: e.target.value
                          }
                        })
                      }
                    />

                  </div>

                  <div className="form-group">

                    <label>Edad</label>

                    <input
                      className="form-control"
                      value={campos.paciente?.edad || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          paciente: {
                            ...campos.paciente,
                            edad: e.target.value
                          }
                        })
                      }
                    />

                  </div>

                </section>

                {/* FECHA */}

                <section className="form-section">

                  <h3 className="section-title">
                    Fecha
                  </h3>

                  <div className="form-group">

                    <label>Fecha</label>

                    <input
                      className="form-control"
                      value={campos.fecha_texto || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          fecha_texto: e.target.value
                        })
                      }
                    />

                  </div>

                </section>

                {/* DIAGNÓSTICO */}

                <section className="form-section">

                  <h3 className="section-title">
                    Diagnóstico
                  </h3>

                  <div className="form-group">

                    <textarea
                      className="form-control"
                      value={campos.diagnostico || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          diagnostico: e.target.value
                        })
                      }
                    />

                  </div>

                </section>

                {/* TRATAMIENTOS */}

                <section className="form-section">

                  <h3 className="section-title">
                    Tratamientos
                  </h3>

                  {campos.tratamiento?.map(
                    (item: any, index: number) => (

                      <div
                        key={index}
                        className="treatment-card"
                      >

                        <div className="form-group">

                          <label>Medicamento</label>

                          <input
                            className="form-control"
                            value={item.medicamento || ""}
                            onChange={(e) => {

                              const nuevosTratamientos = [
                                ...campos.tratamiento
                              ];

                              nuevosTratamientos[index] = {
                                ...nuevosTratamientos[index],
                                medicamento: e.target.value
                              };

                              setCampos({
                                ...campos,
                                tratamiento: nuevosTratamientos
                              });

                            }}
                          />

                        </div>

                        <div className="form-group">

                          <label>Dosis</label>

                          <input
                            className="form-control"
                            value={item.dosis || ""}
                            onChange={(e) => {

                              const nuevosTratamientos = [
                                ...campos.tratamiento
                              ];

                              nuevosTratamientos[index] = {
                                ...nuevosTratamientos[index],
                                dosis: e.target.value
                              };

                              setCampos({
                                ...campos,
                                tratamiento: nuevosTratamientos
                              });

                            }}
                          />

                        </div>

                        <div className="form-group">

                          <label>Vía</label>

                          <input
                            className="form-control"
                            value={item.via || ""}
                            onChange={(e) => {

                              const nuevosTratamientos = [
                                ...campos.tratamiento
                              ];

                              nuevosTratamientos[index] = {
                                ...nuevosTratamientos[index],
                                via: e.target.value
                              };

                              setCampos({
                                ...campos,
                                tratamiento: nuevosTratamientos
                              });

                            }}
                          />

                        </div>

                        <div className="form-group">

                          <label>Frecuencia</label>

                          <input
                            className="form-control"
                            value={item.frecuencia || ""}
                            onChange={(e) => {

                              const nuevosTratamientos = [
                                ...campos.tratamiento
                              ];

                              nuevosTratamientos[index] = {
                                ...nuevosTratamientos[index],
                                frecuencia: e.target.value
                              };

                              setCampos({
                                ...campos,
                                tratamiento: nuevosTratamientos
                              });

                            }}
                          />

                        </div>

                      </div>

                    )
                  )}

                </section>

                {/* EVOLUCIÓN */}

                <section className="form-section">

                  <h3 className="section-title">
                    Evolución
                  </h3>

                  <div className="form-group">

                    <textarea
                      className="form-control"
                      style={{ minHeight: "180px" }}
                      value={campos.evolucion || ""}
                      onChange={(e) =>
                        setCampos({
                          ...campos,
                          evolucion: e.target.value
                        })
                      }
                    />

                  </div>

                </section>

              </div>

            </section>

          </main>

        )}

        {/* BARRA INFERIOR */}

        <footer className="review-footer">

          <button
            onClick={handleValidate}
            className="btn-save"
          >
            Guardar Corrección
          </button>

        </footer>

      </div>

    </div>

  );

}
