PROMPT_EXTRACT = """
Analiza el texto proporcionado.

Devuelve únicamente un JSON válido.

Estructura:

{
  "tipo_documento": "",

  "paciente": {
    "nombre": "",
    "documento_identidad": "",
    "sexo": "",
    "edad": "",
    "fecha_nacimiento": ""
  },

  "atencion": {
    "fecha_atencion": "",
    "hora_atencion": "",
    "ipress": "",
    "medico": ""
  },

  "consulta": {
    "motivo_consulta": "",
    "anamnesis": ""
  },

  "diagnostico": {
    "cie10": "",
    "descripcion": ""
  },

  "tratamiento": "",

  "observaciones": ""
}

Si un dato no existe,
devuelve una cadena vacía.

No devuelvas texto adicional.
No expliques nada.
Solo devuelve JSON válido.
"""