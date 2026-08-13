import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import analyticsService from "../services/analyticsService";
import customerService from "../services/customerService";
import MigrationHistory from "../components/dashboard/MigrationHistory";
import RecommendationPanel from "../components/dashboard/RecommendationPanel";

export default function Analytics() {
  const { projectId } = useParams();
  const [summary, setSummary] = useState([]);
  const [segments, setSegments] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [migrations, setMigrations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [migrationLoading, setMigrationLoading] = useState(false);
  const [recomputing, setRecomputing] = useState(false);
  const [error, setError] = useState("");

  async function loadAnalytics() {
    if (!projectId) return;
    setLoading(true);
    setMigrationLoading(true);
    setError("");

    try {
      const [summaryData, segmentData, customerData, migrationData] = await Promise.all([
        analyticsService.getSegmentSummary(projectId),
        analyticsService.getSegments(projectId),
        customerService.getCustomers(projectId),
        analyticsService.getMigrations(projectId),
      ]);
      setSummary(summaryData || []);
      setSegments(segmentData || []);
      setCustomers(customerData || []);
      setMigrations(migrationData || []);
    } catch (loadError) {
      setError(loadError.message || "Could not load analytics.");
    } finally {
      setLoading(false);
      setMigrationLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!projectId) return;
      setLoading(true);
      setMigrationLoading(true);
      setError("");

      try {
        const [summaryData, segmentData, customerData, migrationData] = await Promise.all([
          analyticsService.getSegmentSummary(projectId),
          analyticsService.getSegments(projectId),
          customerService.getCustomers(projectId),
          analyticsService.getMigrations(projectId),
        ]);

        if (!cancelled) {
          setSummary(summaryData || []);
          setSegments(segmentData || []);
          setCustomers(customerData || []);
          setMigrations(migrationData || []);
        }
      } catch (loadError) {
        if (!cancelled) setError(loadError.message || "Could not load analytics.");
      } finally {
        if (!cancelled) {
          setLoading(false);
          setMigrationLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  async function handleRecompute() {
    if (!projectId) return;
    setRecomputing(true);
    setError("");
    try {
      await analyticsService.recomputeSegments(projectId);
      await loadAnalytics();
    } catch (recomputeError) {
      setError(recomputeError.message || "Could not recompute segments.");
    } finally {
      setRecomputing(false);
    }
  }

  function getCustomerName(customerId) {
    const customer = customers.find((item) => item.id === customerId);
    return customer ? `${customer.first_name} ${customer.last_name}` : customerId;
  }

  function getSegmentStyle(segmentName) {
    const styles = {
      "Loyal High-Value": "bg-green-100 text-green-700",
      "At Risk": "bg-red-100 text-red-700",
      New: "bg-blue-100 text-blue-700",
      Lost: "bg-slate-200 text-slate-700",
    };
    return styles[segmentName] || "bg-cyan-100 text-cyan-700";
  }

  const recommendations = segments
    .filter((segment) => segment.segment_name && segment.recommendation)
    .map((segment) => ({
      id: segment.customer_id,
      segment: segment.segment_name,
      text: segment.recommendation,
    }));
  const totalCustomers = summary.reduce(
    (total, segment) => total + Number(segment.customer_count || 0),
    0
  );
  const totalRevenue = summary.reduce(
    (total, segment) => total + Number(segment.revenue_total || 0),
    0
  );

  return (
    <div>
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">Analytics</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Customer Analytics</h1>
          <p className="mt-2 text-slate-500">Segment distribution and customer intelligence for the current project.</p>
        </div>
        <button type="button" onClick={handleRecompute} disabled={!projectId || recomputing} className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-60">
          {recomputing ? "Recomputing..." : "Recompute Segments"}
        </button>
      </div>

      {error && <p className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      {!projectId ? (
        <div className="mt-8 rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm"><p className="font-semibold text-slate-900">No project selected</p></div>
      ) : loading ? (
        <p className="py-20 text-center text-slate-600">Loading analytics...</p>
      ) : (
        <>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              ["Total Customers", totalCustomers],
              ["Segmented Customers", segments.length],
              ["Total Revenue", `₨${totalRevenue.toLocaleString()}`],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
                <p className="text-sm text-slate-500">{label}</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 grid gap-6 xl:grid-cols-2">
            <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900">Segmented Customers</h2>
              {segments.length === 0 ? (
                <p className="mt-6 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center text-sm text-slate-500">No customers have been segmented yet.</p>
              ) : (
                <div className="mt-5 space-y-3">
                  {segments.map((segment) => (
                    <div key={segment.customer_id} className="rounded-xl bg-slate-50 px-4 py-3">
                      <div className="flex items-center justify-between gap-4">
                        <div className="min-w-0">
                          <p className="truncate font-semibold text-slate-900">
                            {getCustomerName(segment.customer_id)}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            Cluster #{segment.cluster_number}
                          </p>
                        </div>

                        <span className={`shrink-0 whitespace-nowrap rounded-full px-3 py-1 text-xs font-semibold ${getSegmentStyle(segment.segment_name)}`}>
                          {segment.segment_name || "Unassigned"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <RecommendationPanel recommendations={recommendations} emptyMessage="No recommendations available yet." />
          </div>

          <div className="mt-6"><MigrationHistory migrations={migrations} loading={migrationLoading} /></div>
        </>
      )}
    </div>
  );
}
