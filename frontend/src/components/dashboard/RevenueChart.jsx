export default function RevenueChart({ title = "Revenue Trend", children }) {
  return <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"><h2 className="text-lg font-semibold text-slate-900">{title}</h2><div className="mt-5 flex min-h-64 items-center justify-center rounded-xl border border-dashed border-gray-300 text-sm text-slate-500">{children || "Revenue chart will appear here."}</div></section>;
}
