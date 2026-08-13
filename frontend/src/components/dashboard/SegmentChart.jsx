export default function SegmentChart({ data = [], loading = false, title = "Customer Segments" }) {
  if (loading) {
    return <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"><h2 className="text-lg font-semibold text-slate-900">{title}</h2><div className="mt-5 flex min-h-64 items-center justify-center text-sm text-slate-500">Loading segment data...</div></section>;
  }

  if (data.length === 0) {
    return <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"><h2 className="text-lg font-semibold text-slate-900">{title}</h2><div className="mt-5 flex min-h-64 items-center justify-center text-sm text-slate-500">No segment data available.</div></section>;
  }

  const totalCustomers = data.reduce((total, item) => total + Number(item.customer_count || 0), 0);
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const colors = ["text-cyan-500", "text-emerald-500", "text-amber-500", "text-rose-500", "text-violet-500", "text-blue-500"];

  function percentageFor(segment) {
    return Number(segment.revenue_percentage || (Number(segment.customer_count || 0) / Math.max(totalCustomers, 1)) * 100);
  }

  const metrics = data.map((segment, index) => {
    const percentage = percentageFor(segment);
    const previousPercentage = data.slice(0, index).reduce((total, item) => total + percentageFor(item), 0);
    return { segment, percentage, dashLength: (percentage / 100) * circumference, dashOffset: -(previousPercentage / 100) * circumference };
  });

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div><h2 className="text-lg font-semibold text-slate-900">{title}</h2><p className="mt-1 text-xs text-slate-500">Customer distribution by segment</p></div>
        <div className="rounded-lg bg-slate-50 px-3 py-2 text-right"><p className="text-xs text-slate-500">Customers</p><p className="text-lg font-bold text-slate-900">{totalCustomers.toLocaleString()}</p></div>
      </div>

      <div className="mt-6 flex flex-col items-center gap-6 sm:flex-row">
        <div className="relative flex h-64 w-64 shrink-0 items-center justify-center">
          <svg viewBox="0 0 220 220" className="h-56 w-56 -rotate-90" role="img" aria-label="Customer segment distribution chart">
            <circle cx="110" cy="110" r={radius} fill="none" stroke="currentColor" strokeWidth="28" className="text-slate-100" />
            {metrics.map(({ segment, percentage, dashLength, dashOffset }, index) => (
              <circle key={segment.segment_name} cx="110" cy="110" r={radius} fill="none" stroke="currentColor" strokeWidth="28" strokeLinecap="round" strokeDasharray={`${dashLength} ${circumference - dashLength}`} strokeDashoffset={dashOffset} className={`${colors[index % colors.length]} transition-all duration-500`}>
                <title>{`${segment.segment_name}: ${percentage.toFixed(1)}%`}</title>
              </circle>
            ))}
          </svg>
          <div className="absolute text-center"><p className="text-3xl font-bold text-slate-900">{totalCustomers}</p><p className="text-xs text-slate-500">Total customers</p></div>
        </div>

        <div className="w-full space-y-3">
          {data.map((segment, index) => {
            const percentage = percentageFor(segment);
            return <div key={segment.segment_name} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2.5"><div className="flex min-w-0 items-center gap-3"><span className={`h-3 w-3 shrink-0 rounded-full bg-current ${colors[index % colors.length]}`} /><span className="truncate text-sm font-medium text-slate-700">{segment.segment_name}</span></div><div className="ml-3 flex items-center gap-3"><span className="text-sm font-semibold text-slate-900">{segment.customer_count}</span><span className="w-14 text-right text-xs text-slate-500">{percentage.toFixed(1)}%</span></div></div>;
          })}
        </div>
      </div>
    </section>
  );
}
