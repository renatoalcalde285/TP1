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

  const [campos, setCampos] =
    useState<any>({});

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

        setCampos(
          response.datos_estructurados || {}
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
        campos
      );

      alert(
        "Documento validado correctamente"
      );

      const response =
        await getDocumentReview(
          documentId!
        );

      setData(response);

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
          <div
  style={{
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "30px",
    marginTop: "20px"
  }}
>

  <div>

    <h2>
      Imagen Original
    </h2>

    <div
  style={{
    background: "#f8fafc",
    border: "1px solid #dbe3ea",
    borderRadius: "12px",
    padding: "15px"
  }}
></div>

    <img
      src={`http://localhost:8000/documents/${documentId}/image`}
      alt="Documento"
      style={{
        width: "100%",
        border: "1px solid #ccc",
        borderRadius: "8px"
      }}
    />

  </div>

  <div>

    <h2>
      Campos Extraídos
    </h2>

    <div
  style={{
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    background: "#f8fafc",
    border: "1px solid #dbe3ea",
    borderRadius: "12px",
    padding: "20px",
    maxHeight: "850px",
    overflowY: "auto",
    boxShadow: "0 2px 8px rgba(15,23,42,.06)"
  }}
>

      <div>

        <label>
          Tipo Documento
        </label>

        <input
          value={
            campos.tipo_documento || ""
          }
          onChange={(e) =>
            setCampos({
              ...campos,
              tipo_documento:
                e.target.value
            })
          }
          style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
        />

      </div>

<h3
  style={{
    color: "#1e40af",
    marginBottom: "5px"
  }}
>
  Información del Paciente
</h3>

      <div>

        <label>
          Nombre
        </label>

        <input
          value={
            campos.paciente?.nombre || ""
          }
          onChange={(e) =>
            setCampos({
              ...campos,
              paciente: {
                ...campos.paciente,
                nombre:
                  e.target.value
              }
            })
          }
          style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
        />

      </div>

      <div>

        <label>
          Documento
        </label>

        <input
          value={
            campos.paciente?.documento_identidad || ""
          }
          onChange={(e) =>
            setCampos({
              ...campos,
              paciente: {
                ...campos.paciente,
                documento_identidad:
                  e.target.value
              }
            })
          }
          style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
        />

      </div>

      <div>

        <label>
          Sexo
        </label>

        <input
          value={
            campos.paciente?.sexo || ""
          }
          onChange={(e) =>
            setCampos({
              ...campos,
              paciente: {
                ...campos.paciente,
                sexo:
                  e.target.value
              }
            })
          }
          style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
        />

      </div>

      <div>

        <label>
          Fecha Nacimiento
        </label>

        <input
          value={
            campos.paciente?.fecha_nacimiento || ""
          }
          onChange={(e) =>
            setCampos({
              ...campos,
              paciente: {
                ...campos.paciente,
                fecha_nacimiento:
                  e.target.value
              }
            })
          }
          style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
        />

      </div>

      <div>

  <label>
    Edad
  </label>

  <input
    value={
      campos.paciente?.edad || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        paciente: {
          ...campos.paciente,
          edad: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
  />

</div>

<hr />

<h3
  style={{
    color: "#1e40af",
    marginTop: "10px",
    marginBottom: "5px"
  }}
>
  Atención
</h3>

<div>

  <label>
    Fecha Atención
  </label>

  <input
    value={
      campos.atencion?.fecha_atencion || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        atencion: {
          ...campos.atencion,
          fecha_atencion: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
  />

</div>

<div>

  <label>
    Hora Atención
  </label>

  <input
    value={
      campos.atencion?.hora_atencion || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        atencion: {
          ...campos.atencion,
          hora_atencion: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
  />

</div>

<div>

  <label>
    IPRESS
  </label>

  <input
    value={
      campos.atencion?.ipress || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        atencion: {
          ...campos.atencion,
          ipress: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
  />

</div>

<div>

  <label>
    Médico
  </label>

  <input
    value={
      campos.atencion?.medico || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        atencion: {
          ...campos.atencion,
          medico: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
  />

</div>

<hr />

<h3
  style={{
    color: "#1e40af",
    marginTop: "10px",
    marginBottom: "5px"
  }}
>
  Consulta
</h3>

<div>

  <label>
    Motivo Consulta
  </label>

  <textarea
    value={
      campos.consulta?.motivo_consulta || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        consulta: {
          ...campos.consulta,
          motivo_consulta: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  minHeight: "80px",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  resize: "vertical",
  background: "#fff"
}}
  />

</div>

<div>

  <label>
    Anamnesis
  </label>

  <textarea
    value={
      campos.consulta?.anamnesis || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        consulta: {
          ...campos.consulta,
          anamnesis: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  minHeight: "80px",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  resize: "vertical",
  background: "#fff"
}}
  />

</div>

<hr />

<h3
  style={{
    color: "#1e40af",
    marginTop: "10px",
    marginBottom: "5px"
  }}
>
  Diagnóstico
</h3>

<div>

  <label>
    CIE10
  </label>

  <input
    value={
      campos.diagnostico?.cie10 || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        diagnostico: {
          ...campos.diagnostico,
          cie10: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  background: "#fff"
}}
  />

</div>

<div>

  <label>
    Descripción
  </label>

  <textarea
    value={
      campos.diagnostico?.descripcion || ""
    }
    onChange={(e) =>
      setCampos({
        ...campos,
        diagnostico: {
          ...campos.diagnostico,
          descripcion: e.target.value
        }
      })
    }
    style={{
  width: "100%",
  minHeight: "80px",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  resize: "vertical",
  background: "#fff"
}}
  />

</div>

<hr />

<h3
  style={{
    color: "#1e40af",
    marginTop: "10px",
    marginBottom: "5px"
  }}
>
  Tratamiento
</h3>

<textarea
  value={
    campos.tratamiento || ""
  }
  onChange={(e) =>
    setCampos({
      ...campos,
      tratamiento: e.target.value
    })
  }
  style={{
  width: "100%",
  minHeight: "100px",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  resize: "vertical",
  background: "#fff"
}}
/>

<hr />

<h3
  style={{
    color: "#1e40af",
    marginTop: "10px",
    marginBottom: "5px"
  }}
>
  Observaciones
</h3>

<textarea
  value={
    campos.observaciones || ""
  }
  onChange={(e) =>
    setCampos({
      ...campos,
      observaciones: e.target.value
    })
  }
  style={{
  width: "100%",
  minHeight: "100px",
  padding: "10px 12px",
  borderRadius: "8px",
  border: "1px solid #d4dce7",
  boxSizing: "border-box",
  resize: "vertical",
  background: "#fff"
}}
/>

<button
  onClick={handleValidate}
  style={{
    marginTop: "20px",
    padding: "14px 24px",
width: "100%",
fontWeight: 600,
fontSize: "15px",
    background: "#1e40af",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer"
  }}
>
  Guardar Corrección
</button>

    </div>

  </div>

</div>
        </>

      )}

    </div>
  );
}