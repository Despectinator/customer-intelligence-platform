export default function FormField({ label, type = "text", value, onChange, autoComplete, required = true, minLength }) {
  return (
    <label className="block">
      <span className="text-sm text-slate-300">{label}</span>
      <input type={type} value={value} onChange={(event) => onChange(event.target.value)} autoComplete={autoComplete} required={required} minLength={minLength} className="mt-1.5 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition-colors focus:border-teal-400 focus:ring-1 focus:ring-teal-400" />
    </label>
  );
}
