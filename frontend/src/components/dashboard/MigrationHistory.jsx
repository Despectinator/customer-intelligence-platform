function timeAgo(value) {
  const changedAt = new Date(value);
  const seconds = Math.max(0, Math.floor((Date.now() - changedAt.getTime()) / 1000));

  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

function segmentStyle(segment) {
  const styles = {
    "Loyal High-Value": "border-green-100 bg-green-100 text-green-700",
    "At Risk": "border-red-100 bg-red-100 text-red-700",
    New: "border-blue-100 bg-blue-100 text-blue-700",
    Lost: "border-slate-200 bg-slate-200 text-slate-700",
  };
  return styles[segment] || "border-slate-200 bg-slate-50 text-slate-600";
}

export default function MigrationHistory({ migrations = [], loading = false }) {
  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Segment History</h2>
          <p className="mt-1 text-sm text-slate-500">Recent customer segment changes</p>
        </div>
        <div className="rounded-xl bg-cyan-50 px-3 py-2 text-xs font-semibold text-cyan-700">
          {migrations.length} change{migrations.length === 1 ? "" : "s"}
        </div>
      </div>

      {loading ? (
        <div className="mt-6 space-y-4">
          {[1, 2, 3].map((item) => <div key={item} className="h-24 animate-pulse rounded-xl bg-slate-50" />)}
        </div>
      ) : migrations.length === 0 ? (
        <p className="mt-6 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">
          No segment changes recorded yet.
        </p>
      ) : (
        <ol className="relative mt-6 space-y-4 before:absolute before:bottom-5 before:left-[13px] before:top-5 before:w-px before:bg-slate-200">
          {migrations.map((migration) => (
            <li key={migration.id} className="relative pl-9">
              <span className="absolute left-1 top-5 z-10 h-[18px] w-[18px] rounded-full border-4 border-white bg-cyan-500 shadow-sm" />
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 transition hover:border-cyan-200 hover:bg-cyan-50/30">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="font-semibold text-slate-900">{migration.customer_name}</p>
                  <time className="text-xs text-slate-400" dateTime={migration.changed_at}>
                    {timeAgo(migration.changed_at)}
                  </time>
                </div>
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs font-semibold">
                  <span className={`rounded-full border px-3 py-1 ${segmentStyle(migration.old_segment)}`}>
                    {migration.old_segment || "Unassigned"}
                  </span>
                  <span className="text-lg leading-none text-cyan-500" aria-hidden="true">→</span>
                  <span className={`rounded-full border px-3 py-1 ${segmentStyle(migration.new_segment)}`}>
                    {migration.new_segment}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
