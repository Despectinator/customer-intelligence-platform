import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import customerService from "../services/customerService";

export default function CustomerDetails() {
  const { projectId, customerId } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState(null);
  const [segment, setSegment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    company: "",
  });

  useEffect(() => {
    let cancelled = false;

    async function loadCustomer() {
      if (!projectId || !customerId) return;
      setLoading(true);
      setError("");

      try {
        const [customerData, segmentData] = await Promise.all([
          customerService.getCustomer(projectId, customerId),
          customerService.getCustomerSegment(customerId),
        ]);

        if (!cancelled) {
          setCustomer(customerData);
          setSegment(segmentData);
          setFormData({
            first_name: customerData.first_name || "",
            last_name: customerData.last_name || "",
            email: customerData.email || "",
            phone: customerData.phone || "",
            company: customerData.company || "",
          });
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
  }, [projectId, customerId]);

  function getSegmentStyle(segmentName) {
    const styles = {
      "Loyal High-Value": "bg-green-100 text-green-700",
      "At Risk": "bg-red-100 text-red-700",
      New: "bg-blue-100 text-blue-700",
      Lost: "bg-slate-200 text-slate-700",
    };
    return styles[segmentName] || "bg-cyan-100 text-cyan-700";
  }

  function handleInputChange(event) {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
  }

  function resetForm() {
    setError("");
    setFormData({
      first_name: customer.first_name || "",
      last_name: customer.last_name || "",
      email: customer.email || "",
      phone: customer.phone || "",
      company: customer.company || "",
    });
  }

  async function handleSave(event) {
    event.preventDefault();
    if (!projectId || !customerId) return;
    setSaving(true);
    setError("");

    try {
      const updatedCustomer = await customerService.updateCustomer(
        projectId,
        customerId,
        {
          first_name: formData.first_name.trim(),
          last_name: formData.last_name.trim(),
          email: formData.email.trim(),
          phone: formData.phone.trim() || null,
          company: formData.company.trim() || null,
        }
      );
      setCustomer(updatedCustomer);
      setEditing(false);
    } catch (saveError) {
      setError(saveError.message || "Could not update customer.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!projectId || !customerId) return;
    const confirmed = window.confirm(
      `Are you sure you want to delete ${customer.first_name} ${customer.last_name}?\n\nThis action cannot be undone.`
    );
    if (!confirmed) return;

    setDeleting(true);
    setError("");

    try {
      await customerService.deleteCustomer(projectId, customerId);
      navigate(`/projects/${projectId}/customers`);
    } catch (deleteError) {
      setError(deleteError.message || "Could not delete customer.");
      setDeleting(false);
    }
  }

  if (!projectId) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
        <p className="font-semibold text-slate-900">No project selected</p>
      </div>
    );
  }

  return (
    <div>
      <Link to={`/projects/${projectId}/customers`} className="text-sm font-medium text-cyan-600 hover:text-cyan-700">
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
            <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-slate-500">Customer</p>
                <h2 className="mt-1 text-2xl font-bold text-slate-900">
                  {customer.first_name} {customer.last_name}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {customer.company || "No company provided"}
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Link to={`/projects/${projectId}/customers/${customer.id}/transactions`} className="rounded-xl bg-cyan-600 px-5 py-3 text-center text-sm font-semibold text-white transition hover:bg-cyan-700">
                  View Transactions
                </Link>
                <button type="button" onClick={() => { resetForm(); setEditing(true); }} disabled={editing || deleting} className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50">
                  Edit Customer
                </button>
                <button type="button" onClick={handleDelete} disabled={deleting || saving} className="rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50">
                  {deleting ? "Deleting..." : "Delete Customer"}
                </button>
              </div>
            </div>
          </section>

          {editing && (
            <section className="mt-6 rounded-2xl border border-cyan-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900">Edit Customer</h2>
              <p className="mt-1 text-sm text-slate-500">Update the customer's information below.</p>
              <form onSubmit={handleSave} className="mt-5">
                <div className="grid gap-5 md:grid-cols-2">
                  {[
                    ["first_name", "First Name", "text", 100],
                    ["last_name", "Last Name", "text", 100],
                    ["email", "Email", "email", undefined],
                    ["phone", "Phone", "text", 30],
                    ["company", "Company", "text", 255],
                  ].map(([name, label, type, maxLength]) => (
                    <div key={name} className={name === "company" ? "md:col-span-2" : ""}>
                      <label htmlFor={name} className="block text-sm font-medium text-slate-700">{label}</label>
                      <input id={name} name={name} type={type} value={formData[name]} onChange={handleInputChange} required={name === "first_name" || name === "last_name" || name === "email"} maxLength={maxLength} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100" />
                    </div>
                  ))}
                </div>
                <div className="mt-6 flex flex-wrap justify-end gap-3">
                  <button type="button" onClick={() => { resetForm(); setEditing(false); }} disabled={saving} className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50">Cancel</button>
                  <button type="submit" disabled={saving} className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:opacity-50">{saving ? "Saving..." : "Save Changes"}</button>
                </div>
              </form>
            </section>
          )}

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
                  <p className="text-sm text-slate-500">This customer has not been segmented yet.</p>
                </div>
              ) : (
                <div className="mt-5">
                  <span className={`inline-flex rounded-full px-4 py-2 text-sm font-semibold ${getSegmentStyle(segment.segment_name)}`}>
                    {segment.segment_name || "Unassigned"}
                  </span>
                  <div className="mt-6"><p className="text-xs uppercase tracking-wide text-slate-400">Cluster</p><p className="mt-1 text-xl font-bold text-slate-900">#{segment.cluster_number}</p></div>
                  <div className="mt-6"><p className="text-xs uppercase tracking-wide text-slate-400">Recommendation</p><p className="mt-2 leading-6 text-slate-600">{segment.recommendation || "No recommendation available."}</p></div>
                  <div className="mt-6"><p className="text-xs uppercase tracking-wide text-slate-400">Generated</p><p className="mt-1 text-sm text-slate-500">{segment.generated_at ? new Date(segment.generated_at).toLocaleString() : "—"}</p></div>
                </div>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
}
