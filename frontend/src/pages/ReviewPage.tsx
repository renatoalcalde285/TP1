import {
  useEffect,
  useState
} from "react";

import {
  useParams
} from "react-router-dom";

import {
  getDocumentReview,
  validateDocument
} from "../services/documentService";

export default function ReviewPage() {

  const { documentId } = useParams();

  const [data, setData] =
    useState<any>(null);

  const [texto, setTexto] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    const loadData = async () => {

      try {

        const response =
          await getDocumentReview(
            documentId!
          );

        setData(response);

        setTexto(
          response.transcripcion
        );

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
        texto
      );

      alert(
        "Documento validado correctamente"
      );

      const response =
        await getDocumentReview(
          documentId!
        );

      setData(response);

      setTexto(
        response.transcripcion
      );

    } catch (error) {

      console.error(error);

      alert(
        "Error al validar documento"
      );

    }
  };

  if (loading) {
    return <h2>Cargando...</h2>;
  }

  return (

    <div
      style={{
        padding: "30px",
        maxWidth: "1200px",
        margin: "0 auto"
      }}
    >

      <h1>
        Documento #{data.id_documento}
      </h1>

      <p>
        Estado: {data.estado}
      </p>

      <p>
        Estado validación:{" "}
        {data.estado_validacion}
      </p>

      <p>
        Tiempo:{" "}
        {
          (
            data.tiempo_procesamiento_ms /
            1000
          ).toFixed(2)
        }
        {" "}
        segundos
      </p>

      <hr />

      {data.datos_estructurados && (

        <>
          <h2>
            Datos Extraídos
          </h2>

          <div
            style={{
              border: "1px solid #ccc",
              padding: "15px",
              marginBottom: "25px",
              backgroundColor: "#f8f8f8"
            }}
          >

            <p>
              <strong>
                Tipo Documento:
              </strong>{" "}
              {
                data.datos_estructurados
                  .tipo_documento
              }
            </p>

            <p>
              <strong>
                Nombre:
              </strong>{" "}
              {
                data.datos_estructurados
                  .paciente?.nombre
              }
            </p>

            <p>
              <strong>
                Sexo:
              </strong>{" "}
              {
                data.datos_estructurados
                  .paciente?.sexo
              }
            </p>

            <p>
              <strong>
                Documento:
              </strong>{" "}
              {
                data.datos_estructurados
                  .paciente?.documento_identidad
              }
            </p>

            <p>
              <strong>
                Fecha Nacimiento:
              </strong>{" "}
              {
                data.datos_estructurados
                  .paciente?.fecha_nacimiento
              }
            </p>

            <p>
              <strong>
                Edad:
              </strong>{" "}
              {
                data.datos_estructurados
                  .paciente?.edad
              }
            </p>

            <details
              style={{
                marginTop: "20px"
              }}
            >
              <summary>
                Ver JSON completo
              </summary>

              <pre
                style={{
                  overflowX: "auto",
                  padding: "10px",
                  background: "#eee"
                }}
              >
                {JSON.stringify(
                  data.datos_estructurados,
                  null,
                  2
                )}
              </pre>

            </details>

          </div>
        </>

      )}

      <h2>
        Transcripción OCR
      </h2>

      <textarea
        value={texto}
        onChange={(e) =>
          setTexto(
            e.target.value
          )
        }
        style={{
          width: "100%",
          height: "500px"
        }}
      />

      <button
        onClick={handleValidate}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          cursor: "pointer"
        }}
      >
        Guardar Validación
      </button>

    </div>
  );
}