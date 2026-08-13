import { useRef, useState } from "react";
import { Upload as UploadIcon, FileText, X } from "lucide-react";
import { useParams } from "react-router-dom";

import uploadService from "../services/uploadService";

export default function Upload() {
  const { projectId } = useParams();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0];
    setError("");
    setResult(null);

    if (!selectedFile) {
      setFile(null);
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      setFile(null);
      setError("Please select a CSV file.");
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setFile(null);
      setError("The CSV file must be smaller than 5 MB.");
      return;
    }

    setFile(selectedFile);
  }

  function removeFile() {
    setFile(null);
    setError("");
    setResult(null);

    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function handleUpload() {
    if (!projectId) {
      setError("Please select a project first.");
      return;
    }

    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await uploadService.uploadTransactionsCsv(
        projectId,
        file
      );
      setResult(data);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (uploadError) {
      setError(uploadError.message || "The CSV upload could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">
        Upload CSV
      </p>
      <h1 className="mt-2 text-3xl font-bold text-slate-900">
        Import Transactions
      </h1>
      <p className="mt-2 text-slate-500">
        Upload customer transaction data into the current project.
      </p>

      {!projectId ? (
        <div className="mt-8 rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
          <p className="font-semibold text-slate-900">No project selected</p>
          <p className="mt-2 text-sm text-slate-500">
            Select a project before uploading transaction data.
          </p>
        </div>
      ) : (
        <>
          <section className="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">
              Current Project
            </h2>
            <p className="mt-1 text-sm text-slate-500">Project {projectId}</p>

            <div className="mt-6 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-10 text-center">
              <UploadIcon className="mx-auto h-10 w-10 text-cyan-600" />
              <h3 className="mt-4 font-semibold text-slate-900">
                Upload a CSV file
              </h3>
              <p className="mt-2 text-sm text-slate-500">Maximum file size: 5 MB</p>
              <label className="mt-5 inline-flex cursor-pointer items-center rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700">
                Choose CSV file
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,text/csv"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>

            {file && (
              <div className="mt-5 flex items-center justify-between rounded-xl border border-cyan-100 bg-cyan-50 px-4 py-3">
                <div className="flex min-w-0 items-center gap-3">
                  <FileText className="h-5 w-5 shrink-0 text-cyan-600" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-900">{file.name}</p>
                    <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button type="button" onClick={removeFile} className="ml-4 text-slate-400 hover:text-red-500" aria-label="Remove selected file">
                  <X className="h-5 w-5" />
                </button>
              </div>
            )}

            {error && (
              <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || loading}
              className="mt-6 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Uploading..." : "Upload CSV"}
            </button>
          </section>

          {result && (
            <section className="mt-6 rounded-2xl border border-green-200 bg-green-50 p-6">
              <h2 className="text-lg font-semibold text-green-900">Upload completed</h2>
              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl bg-white p-4">
                  <p className="text-sm text-slate-500">Customers created</p>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{result.customers_created}</p>
                </div>
                <div className="rounded-xl bg-white p-4">
                  <p className="text-sm text-slate-500">Transactions inserted</p>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{result.transactions_inserted}</p>
                </div>
                <div className="rounded-xl bg-white p-4">
                  <p className="text-sm text-slate-500">Rows skipped</p>
                  <p className="mt-1 text-2xl font-bold text-slate-900">{result.rows_skipped}</p>
                </div>
              </div>

              {result.errors?.length > 0 && (
                <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4">
                  <p className="font-semibold text-amber-900">Validation errors</p>
                  <ul className="mt-3 space-y-2 text-sm text-amber-800">
                    {result.errors.map((item, index) => (
                      <li key={`${item.row}-${index}`}>
                        Row {item.row}: {item.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}
