export default function KPICard({
  title,
  value,
  subtitle,
  icon,
  color = "cyan",
  loading = false,
}) {
  const colors = {
    cyan: "bg-cyan-500",
    emerald: "bg-emerald-500",
    amber: "bg-amber-500",
    rose: "bg-rose-500",
  };

  return (
    <div className="flex items-start justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <p className="text-sm text-slate-500">{title}</p>
        {loading ? (
          <>
            <div className="mt-3 h-9 w-28 animate-pulse rounded-lg bg-slate-200" />
            {subtitle && <div className="mt-3 h-4 w-24 animate-pulse rounded bg-slate-100" />}
          </>
        ) : (
          <>
            <h2 className="mt-2 text-3xl font-bold text-slate-900">{value}</h2>
            {subtitle && <p className="mt-2 text-sm text-slate-400">{subtitle}</p>}
          </>
        )}
      </div>
      <div className={`flex h-12 w-12 items-center justify-center rounded-xl text-white ${colors[color]}`}>
        {icon}
      </div>
    </div>
  );
}
