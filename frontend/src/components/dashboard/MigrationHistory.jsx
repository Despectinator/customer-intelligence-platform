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

export default function MigrationHistory({ migrations = [], loading = false }) {
  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Segment History</h2>

      {loading ? (
        <p className="mt-5 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">
          Loading segment history...
        </p>
      ) : migrations.length === 0 ? (
        <p className="mt-5 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">
          No segment changes recorded yet.
        </p>
      ) : (
        <ul className="mt-5 space-y-3">
          {migrations.map((migration) => (
            <li key={migration.id} className="rounded-xl bg-slate-50 p-4">
              <p className="font-semibold text-slate-900">{migration.customer_name}</p>
              <p className="mt-1 text-sm text-slate-600">
                {migration.old_segment || "Unassigned"} → {migration.new_segment}
              </p>
              <p className="mt-1 text-xs text-slate-400">{timeAgo(migration.changed_at)}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
