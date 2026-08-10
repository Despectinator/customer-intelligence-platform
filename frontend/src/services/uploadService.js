import { api } from "../lib/api";

export function uploadTransactionsCsv(projectId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return api.post(
    `/projects/${projectId}/transactions/upload-csv`,
    formData
  );
}

export default {
  uploadTransactionsCsv,
};
