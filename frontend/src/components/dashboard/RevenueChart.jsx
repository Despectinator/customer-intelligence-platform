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

        <div className="mt-5 flex min-h-64 items-center justify-center text-sm text-slate-500">
          Loading revenue data...
        </div>
      </section>
    );
  }

  if (data.length === 0) {
    return (
      <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>

        <div className="mt-5 flex min-h-64 items-center justify-center text-sm text-slate-500">
          {emptyMessage}
        </div>
      </section>
    );
  }

  const maxRevenue = Math.max(...data.map((item) => item.revenue), 1);

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>

      <div className="mt-5">
        <div className="relative h-64 w-full">
          <div className="absolute inset-0 flex items-end justify-between gap-2">
            {data.map((item) => {
              const height = Math.max(
                (item.revenue / maxRevenue) * 100,
                3
              );

              return (
                <div
                  key={item.date}
                  className="flex h-full flex-1 items-end"
                >
                  <div
                    title={`${item.date}: ₨${item.revenue.toLocaleString()}`}
                    className="w-full rounded-t-lg bg-cyan-500 transition-all hover:bg-cyan-400"
                    style={{ height: `${height}%` }}
                  />
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-3 flex justify-between gap-2 text-xs text-slate-400">
          {data.map((item) => (
            <span
              key={item.date}
              className="min-w-0 flex-1 truncate text-center"
              title={item.date}
            >
              {new Date(item.date).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              })}
            </span>
          ))}
        </div>

        <div className="mt-5 border-t border-gray-100 pt-4">
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Total revenue</span>
            <span className="font-semibold text-slate-900">
              ₨
              {data
                .reduce((total, item) => total + Number(item.revenue), 0)
                .toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
