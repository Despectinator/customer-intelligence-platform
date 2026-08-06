import { useEffect } from "react";

export default function Modal({ title, onClose, children }) {
  useEffect(() => { const handleKey = (event) => { if (event.key === "Escape") onClose(); }; window.addEventListener("keydown", handleKey); return () => window.removeEventListener("keydown", handleKey); }, [onClose]);
  return <div className="fixed inset-0 z-50 flex items-center justify-center p-4"><button type="button" aria-label="Close dialog" className="absolute inset-0 cursor-default bg-black/60" onClick={onClose} /><div role="dialog" aria-modal="true" aria-label={title} className="relative w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl"><div className="mb-5 flex items-center justify-between"><h2 className="text-lg font-semibold text-white">{title}</h2><button type="button" onClick={onClose} aria-label="Close" className="text-xl leading-none text-slate-400 hover:text-white">&times;</button></div>{children}</div></div>;
}
