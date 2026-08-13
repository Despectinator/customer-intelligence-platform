export default function SegmentChart({
  title = "Customer Segments",
  data = [],
  loading = false,
  status = "ready",
  message = "",
}) {
  const maxCustomers = Math.max(
    ...data.map((segment) => Number(segment.customer_count || 0)),
    1
  );

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">
        {title}
      </h2>

      <div className="mt-5 min-h-64">
        {loading ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-slate-500">
            Loading segment data...
          </div>
        ) : status !== "ready" ? (
          <div className="flex min-h-64 flex-col items-center justify-center text-center text-sm text-slate-500">
            <p className="font-semibold text-slate-700">
              {status === "no_data"
                ? "No customer data yet"
                : status === "no_transactions"
                  ? "No transactions yet"
                  : status === "insufficient_data"
                    ? "Insufficient segmentation data"
                    : "Segmentation not generated"}
            </p>
            <p className="mt-2 max-w-sm">{message}</p>
          </div>
        ) : data.length === 0 ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-slate-500">
            No segment data available.
          </div>
        ) : (
          <div className="space-y-5">
            {data.map((segment) => {
              const customerCount = Number(segment.customer_count || 0);
              const width = (customerCount / maxCustomers) * 100;

              return (
                <div key={segment.segment_name}>
                  <div className="mb-2 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-800">
                        {segment.segment_name}
                      </p>

                      <p className="text-xs text-slate-500">
                        {Number(
                          segment.revenue_percentage || 0
                        ).toFixed(2)}% of revenue
                      </p>
                    </div>

                    <span className="text-sm font-bold text-cyan-600">
                      {customerCount}
                    </span>
                  </div>

                  <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-cyan-500 transition-all duration-500"
                      style={{ width: `${width}%` }}
                    />
                  </div>

                  <div className="mt-1 text-xs text-slate-400">
                    Revenue: ₨
                    {Number(
                      segment.revenue_total || 0
                    ).toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
