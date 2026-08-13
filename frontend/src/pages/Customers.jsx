import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import customerService from "../services/customerService";

export default function Customers() {
  const { projectId } = useParams();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!projectId) {
      return;
    }

    async function loadCustomers() {
      setLoading(true);
      setError("");

      try {
        const data = await customerService.getCustomers(projectId);
        setCustomers(data || []);
      } catch (loadError) {
        setError(loadError.message || "Could not load customers.");
      } finally {
        setLoading(false);
      }
    }

    loadCustomers();
  }, [projectId]);

  return (
    <div>
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">
          Customers
        </p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">
          Customers
        </h1>
        <p className="mt-1 text-slate-500">
          Select a customer to view their transactions.
        </p>
      </div>

      {error && (
        <p className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {!projectId ? (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
          <p className="font-semibold text-slate-900">No project selected</p>
        </div>
      ) : loading ? (
        <p className="py-20 text-center text-slate-600">Loading customers...</p>
      ) : customers.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
          <p className="font-semibold text-slate-900">No customers yet</p>
        </div>
      ) : (
        <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-200 bg-slate-50">
                <tr>
                  <th className="px-5 py-4 font-semibold text-slate-700">
                    Customer
                  </th>
                  <th className="px-5 py-4 font-semibold text-slate-700">
                    Email
                  </th>
                  <th className="px-5 py-4 text-right font-semibold text-slate-700">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4">
                      <Link
                        to={`/projects/${projectId}/customers/${customer.id}`}
                        className="font-semibold text-slate-900 hover:text-cyan-600"
                      >
                        {customer.first_name} {customer.last_name}
                      </Link>
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {customer.email}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="flex items-center justify-end gap-5">
                        <Link
                          to={`/projects/${projectId}/customers/${customer.id}`}
                          className="font-medium text-cyan-600 hover:text-cyan-700"
                        >
                          View Customer
                        </Link>
                        <Link
                          to={`/projects/${projectId}/customers/${customer.id}/transactions`}
                          className="font-medium text-cyan-600 hover:text-cyan-700"
                        >
                          View Transactions
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
