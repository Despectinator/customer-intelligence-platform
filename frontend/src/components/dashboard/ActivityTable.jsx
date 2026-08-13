export default function ActivityTable({
  activities = [],
  loading = false,
  emptyMessage = "No recent activity available.",
}) {
  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">
        Recent Activity
      </h2>

      {loading ? (
        <p className="mt-5 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">
          Loading recent activity...
        </p>
      ) : activities.length === 0 ? (
        <p className="mt-5 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">
          {emptyMessage}
        </p>
      ) : (
        <div className="mt-5 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-slate-400">
                <th className="pb-3 font-medium">Activity</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-200 text-slate-600">
              {activities.map((activity) => (
                <tr key={activity.id}>
                  <td className="py-3">{activity.label}</td>
                  <td className="py-3">{activity.date}</td>
                  <td className="py-3">
                    <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-600">
                      {activity.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
