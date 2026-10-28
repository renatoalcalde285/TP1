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