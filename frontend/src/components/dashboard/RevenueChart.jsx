export default function RevenueChart({
  title = "Revenue by Segment",
  data = [],
  loading = false,
}) {
  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>

      <div className="mt-5 min-h-64">
        {loading ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-slate-500">
            Loading revenue data...
          </div>
        ) : data.length === 0 ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-slate-500">
            No revenue data available.
          </div>
        ) : (
          <div className="space-y-5">
            {data.map((segment) => (
              <div key={segment.segment_name}>
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-medium text-slate-800">
                    {segment.segment_name}
                  </span>

                  <span className="font-semibold text-slate-900">
                    Rs {segment.revenue_total.toLocaleString()}
                  </span>
                </div>

                <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-cyan-500"
                    style={{
                      width: `${Math.min(segment.revenue_percentage, 100)}%`,
                    }}
                  />
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  {segment.revenue_percentage}% of total revenue
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}