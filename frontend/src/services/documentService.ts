import axios from "axios";

const API_URL = "http://localhost:8000";

export const uploadDocuments = async (
  files: FileList
) => {

  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  const token =
    localStorage.getItem("token");

  const response = await axios.post(
    `${API_URL}/documents/upload`,
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data"
      }
    }
  );

  return response.data;
};

export const getDocumentStatus = async (
  documentId: string
) => {

  const token =
    localStorage.getItem("token");

  const response = await axios.get(
    `${API_URL}/documents/${documentId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );

  return response.data;
};

export const getDocumentReview = async (
  documentId: string
) => {

  const token =
    localStorage.getItem("token");

  const response = await axios.get(
    `${API_URL}/documents/${documentId}/review`,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );

  return response.data;
};

export const validateDocument = async (
  documentId: string,
  transcripcion: string
) => {

  const token =
    localStorage.getItem("token");

  const response = await axios.put(
    `${API_URL}/documents/${documentId}/validate`,
    {
      transcripcion
    },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );

  return response.data;
};

export const getDocuments = async (
  nombre?: string,
  tipo?: string,
  estado?: string
) => {

  const token =
    localStorage.getItem("token");

  const response =
    await axios.get(
      `${API_URL}/documents`,
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        },
        params: {
          nombre,
          tipo,
          estado
        }
      }
    );

  return response.data;
};