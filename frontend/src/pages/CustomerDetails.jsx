import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useProject } from "../hooks/useProject";
import customerService from "../services/customerService";

export default function CustomerDetails() {
  const { customerId } = useParams();
  const { currentProject } = useProject();
  const [customer, setCustomer] = useState(null);
  const [segment, setSegment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadCustomer() {
      if (!currentProject?.id || !customerId) return;
      setLoading(true);
      setError("");

      try {
        const [customerData, segmentData] = await Promise.all([
          customerService.getCustomer(currentProject.id, customerId),
          customerService.getCustomerSegment(customerId),
        ]);

        if (!cancelled) {
          setCustomer(customerData);
          setSegment(segmentData);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError.message || "Could not load customer details.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadCustomer();
    return () => {
      cancelled = true;
    };
  }, [currentProject, customerId]);

  function getSegmentStyle(segmentName) {
    const styles = {
      "Loyal High-Value": "bg-green-100 text-green-700",
      "At Risk": "bg-red-100 text-red-700",
      New: "bg-blue-100 text-blue-700",
      Lost: "bg-slate-200 text-slate-700",
    };
    return styles[segmentName] || "bg-cyan-100 text-cyan-700";
  }

  if (!currentProject) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
        <p className="font-semibold text-slate-900">No project selected</p>
      </div>
    );
  }

  return (
    <div>
      <Link
        to="/customers"
        className="text-sm font-medium text-cyan-600 hover:text-cyan-700"
      >
        ← Back to Customers
      </Link>

      <div className="mt-6">
        <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">Customer</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">Customer Details</h1>
        <p className="mt-2 text-slate-500">
          Customer information, segmentation, and recommendations.
        </p>
      </div>

      {error && (
        <p className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {loading ? (
        <p className="py-20 text-center text-slate-600">Loading customer details...</p>
      ) : !customer ? (
        <div className="mt-8 rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
          <p className="font-semibold text-slate-900">Customer not found</p>
        </div>
      ) : (
        <>
          <section className="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-slate-500">Customer</p>
                <h2 className="mt-1 text-2xl font-bold text-slate-900">
                  {customer.first_name} {customer.last_name}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {customer.company || "No company provided"}
                </p>
              </div>
              <Link
                to={`/customers/${customer.id}/transactions`}
                className="rounded-xl bg-cyan-600 px-5 py-3 text-center text-sm font-semibold text-white transition hover:bg-cyan-700"
              >
                View Transactions
              </Link>
            </div>
          </section>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900">Customer Information</h2>
              <div className="mt-5 space-y-4">
                {[
                  ["Full Name", `${customer.first_name} ${customer.last_name}`],
                  ["Email", customer.email || "—"],
                  ["Phone", customer.phone || "—"],
                  ["Company", customer.company || "—"],
                  ["Customer ID", customer.id],
                ].map(([label, value]) => (
                  <div key={label}>
                    <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
                    <p className="mt-1 break-all font-medium text-slate-800">{value}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900">Customer Segment</h2>
              {!segment ? (
                <div className="mt-6 rounded-xl border border-dashed border-gray-300 px-4 py-10 text-center">
                  <p className="text-sm text-slate-500">
                    This customer has not been segmented yet.
                  </p>
                </div>
              ) : (
                <div className="mt-5">
                  <span className={`inline-flex rounded-full px-4 py-2 text-sm font-semibold ${getSegmentStyle(segment.segment_name)}`}>
                    {segment.segment_name || "Unassigned"}
                  </span>
                  <div className="mt-6">
                    <p className="text-xs uppercase tracking-wide text-slate-400">Cluster</p>
                    <p className="mt-1 text-xl font-bold text-slate-900">#{segment.cluster_number}</p>
                  </div>
                  <div className="mt-6">
                    <p className="text-xs uppercase tracking-wide text-slate-400">Recommendation</p>
                    <p className="mt-2 leading-6 text-slate-600">
                      {segment.recommendation || "No recommendation available."}
                    </p>
                  </div>
                  <div className="mt-6">
                    <p className="text-xs uppercase tracking-wide text-slate-400">Generated</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {segment.generated_at
                        ? new Date(segment.generated_at).toLocaleString()
                        : "—"}
                    </p>
                  </div>
                </div>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}
