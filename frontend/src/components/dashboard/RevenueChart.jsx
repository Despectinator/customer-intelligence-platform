export default function RevenueChart({
  title = "Revenue Trend",
  data = [],
  loading = false,
  emptyMessage = "No revenue data available.",
}) {
  if (loading) {
    return (
      <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        <div className="mt-5 flex min-h-64 items-center justify-center text-sm text-slate-500">Loading revenue data...</div>
      </section>
    );
  }

  if (data.length === 0) {
    return (
      <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        <div className="mt-5 flex min-h-64 items-center justify-center text-sm text-slate-500">{emptyMessage}</div>
      </section>
    );
  }

  const width = 800;
  const height = 300;
  const padding = { top: 20, right: 25, bottom: 45, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const values = data.map((item) => Number(item.revenue) || 0);
  const maxRevenue = Math.max(...values, 1);

  const points = data.map((item, index) => {
    const x = data.length === 1 ? padding.left + chartWidth / 2 : padding.left + (index / (data.length - 1)) * chartWidth;
    const y = padding.top + chartHeight - (values[index] / maxRevenue) * chartHeight;
    return { x, y, date: item.date, revenue: values[index] };
  });

  const linePoints = points.map((point) => `${point.x},${point.y}`).join(" ");
  const areaPoints = [
    `${padding.left},${padding.top + chartHeight}`,
    ...points.map((point) => `${point.x},${point.y}`),
    `${padding.left + chartWidth},${padding.top + chartHeight}`,
  ].join(" ");
  const formatRevenue = (value) => `₨${Number(value).toLocaleString("en-PK", { maximumFractionDigits: 0 })}`;
  const totalRevenue = values.reduce((total, value) => total + value, 0);

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <p className="mt-1 text-xs text-slate-500">Revenue performance over time</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500">Total revenue</p>
          <p className="mt-1 text-lg font-bold text-slate-900">{formatRevenue(totalRevenue)}</p>
        </div>
      </div>

      <div className="mt-5 w-full overflow-hidden">
        <svg viewBox={`0 0 ${width} ${height}`} className="h-64 w-full" role="img" aria-label="Revenue trend chart">
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const y = padding.top + chartHeight * (1 - ratio);
            return <line key={ratio} x1={padding.left} x2={padding.left + chartWidth} y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />;
          })}

          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const y = padding.top + chartHeight * (1 - ratio);
            return <text key={ratio} x={padding.left - 10} y={y + 4} textAnchor="end" fontSize="11" fill="#94a3b8">{formatRevenue(maxRevenue * ratio)}</text>;
          })}

          <polygon points={areaPoints} fill="#cffafe" opacity="0.45" />
          <polyline points={linePoints} fill="none" stroke="#0891b2" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

          {points.map((point) => (
            <g key={point.date}>
              <circle cx={point.x} cy={point.y} r="5" fill="white" stroke="#0891b2" strokeWidth="3" />
              <title>{`${point.date}: ${formatRevenue(point.revenue)}`}</title>
            </g>
          ))}

          {points.map((point, index) => {
            const showLabel = data.length <= 8 || index === 0 || index === data.length - 1 || index % Math.ceil(data.length / 6) === 0;
            if (!showLabel) return null;
            return <text key={`label-${point.date}`} x={point.x} y={height - 15} textAnchor="middle" fontSize="11" fill="#94a3b8">{new Date(point.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</text>;
          })}
        </svg>
      </div>
    </section>
  );
}
