export default function SegmentSummary({ data = [], loading = false }) {
  const maxCustomers = Math.max(...data.map((segment) => Number(segment.customer_count || 0)), 1);

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Segment Summary</h2>
      {loading ? (
        <p className="mt-6 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">Loading segment summary...</p>
      ) : data.length === 0 ? (
        <p className="mt-6 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">No segment summary available.</p>
      ) : (
        <div className="mt-6 space-y-5">
          {data.map((segment) => (
            <div key={segment.segment_name}>
              <div className="mb-2 flex items-center justify-between"><span className="font-medium text-slate-800">{segment.segment_name}</span><span className="text-sm font-semibold text-cyan-600">{segment.customer_count}</span></div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-cyan-500" style={{ width: `${(Number(segment.customer_count || 0) / maxCustomers) * 100}%` }} /></div>
              <p className="mt-1 text-xs text-slate-500">{Number(segment.revenue_percentage || 0).toFixed(2)}% of revenue · ₨{Number(segment.revenue_total || 0).toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
