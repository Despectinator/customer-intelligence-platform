import { useState } from "react";
import Modal from "./Modal";
import FormField from "../auth/FormField";

export default function ProjectFormModal({ initialValues, title, submitLabel, onSubmit, onClose }) {
  const [name, setName] = useState(initialValues?.name || "");
  const [description, setDescription] = useState(initialValues?.description || "");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  async function handleSubmit(event) { event.preventDefault(); setError(""); setSubmitting(true); try { await onSubmit({ name, description }); onClose(); } catch (submitError) { setError(submitError.message || "Something went wrong."); } finally { setSubmitting(false); } }
  return <Modal title={title} onClose={onClose}><form onSubmit={handleSubmit} className="space-y-4"><FormField label="Name" value={name} onChange={setName} /><label className="block"><span className="text-sm text-slate-300">Description</span><textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={3} className="mt-1.5 w-full resize-none rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400" /></label>{error && <p className="text-sm text-red-400" role="alert">{error}</p>}<div className="flex justify-end gap-3 pt-2"><button type="button" onClick={onClose} className="rounded-xl px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button><button type="submit" disabled={submitting} className="rounded-xl bg-teal-500 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-400 disabled:opacity-50">{submitting ? "Saving..." : submitLabel}</button></div></form></Modal>;
}
