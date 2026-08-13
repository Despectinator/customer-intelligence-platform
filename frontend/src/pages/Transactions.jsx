import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import transactionService from "../services/transactionService";

export default function Transactions() {
  const { projectId, customerId } = useParams();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({
    order_date: "",
    order_amount: "",
    payment_method: "",
  });

  async function loadTransactions() {
    if (!customerId) return;

    setLoading(true);
    setError("");

    try {
      const data = await transactionService.getTransactions(customerId);
      setTransactions(data || []);
    } catch (loadError) {
      setError(loadError.message || "Could not load transactions.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!customerId) return;

      setLoading(true);
      setError("");

      try {
        const data = await transactionService.getTransactions(customerId);
        if (!cancelled) {
          setTransactions(data || []);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError.message || "Could not load transactions.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [customerId]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  function resetForm() {
    setForm({ order_date: "", order_amount: "", payment_method: "" });
    setEditingId(null);
    setShowForm(false);
  }

  function startEdit(transaction) {
    setForm({
      order_date: transaction.order_date,
      order_amount: transaction.order_amount,
      payment_method: transaction.payment_method || "",
    });
    setEditingId(transaction.id);
    setShowForm(true);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const payload = {
      order_date: form.order_date,
      order_amount: Number(form.order_amount),
      payment_method: form.payment_method || null,
    };

    try {
      if (editingId) {
        await transactionService.updateTransaction(customerId, editingId, payload);
      } else {
        await transactionService.createTransaction(customerId, payload);
      }

      resetForm();
      await loadTransactions();
    } catch (saveError) {
      setError(saveError.message || "Could not save transaction.");
    }
  }

  async function handleDelete(transactionId) {
    if (!window.confirm("Are you sure you want to delete this transaction?")) {
      return;
    }

    setError("");

    try {
      await transactionService.deleteTransaction(customerId, transactionId);
      await loadTransactions();
    } catch (deleteError) {
      setError(deleteError.message || "Could not delete transaction.");
    }
  }

  function formatAmount(amount) {
    return `₨${Number(amount).toLocaleString("en-PK", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }

  return (
    <div>
      <Link
        to={`/projects/${projectId}/customers`}
        className="text-sm font-medium text-cyan-600 hover:text-cyan-700"
      >
        ← Back to Customers
      </Link>

      <div className="mt-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">
            Transactions
          </p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">
            Customer Transactions
          </h1>
          <p className="mt-2 text-slate-500">
            Transaction history for customer {customerId}.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            resetForm();
            setShowForm(true);
          }}
          className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700"
        >
          + Add Transaction
        </button>
      </div>

      {error && (
        <p className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {showForm && (
        <section className="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">
              {editingId ? "Edit Transaction" : "Add Transaction"}
            </h2>
            <button
              type="button"
              onClick={resetForm}
              className="text-sm text-slate-500 hover:text-slate-900"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleSubmit} className="mt-5 grid gap-4 md:grid-cols-3">
            <div>
              <label htmlFor="order_date" className="mb-2 block text-sm font-medium text-slate-700">
                Order Date
              </label>
              <input
                id="order_date"
                name="order_date"
                type="date"
                value={form.order_date}
                onChange={handleChange}
                required
                className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
              />
            </div>

            <div>
              <label htmlFor="order_amount" className="mb-2 block text-sm font-medium text-slate-700">
                Amount
              </label>
              <input
                id="order_amount"
                name="order_amount"
                type="number"
                min="0.01"
                step="0.01"
                value={form.order_amount}
                onChange={handleChange}
                required
                placeholder="2500.00"
                className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
              />
            </div>

            <div>
              <label htmlFor="payment_method" className="mb-2 block text-sm font-medium text-slate-700">
                Payment Method
              </label>
              <select
                id="payment_method"
                name="payment_method"
                value={form.payment_method}
                onChange={handleChange}
                className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
              >
                <option value="">Select method</option>
                <option value="Cash">Cash</option>
                <option value="Card">Card</option>
                <option value="Bank Transfer">Bank Transfer</option>
                <option value="Online">Online</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="md:col-span-3">
              <button
                type="submit"
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                {editingId ? "Update Transaction" : "Add Transaction"}
              </button>
            </div>
          </form>
        </section>
      )}

      {loading ? (
        <p className="py-20 text-center text-slate-600">Loading transactions...</p>
      ) : transactions.length === 0 ? (
        <div className="mt-8 rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
          <p className="font-semibold text-slate-900">No transactions yet</p>
          <p className="mt-2 text-sm text-slate-500">
            Add the first transaction for this customer.
          </p>
        </div>
      ) : (
        <section className="mt-8 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-200 bg-slate-50">
                <tr>
                  <th className="px-5 py-4 font-semibold text-slate-700">Order Date</th>
                  <th className="px-5 py-4 font-semibold text-slate-700">Amount</th>
                  <th className="px-5 py-4 font-semibold text-slate-700">Payment Method</th>
                  <th className="px-5 py-4 font-semibold text-slate-700">Created</th>
                  <th className="px-5 py-4 text-right font-semibold text-slate-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4 text-slate-700">{transaction.order_date}</td>
                    <td className="px-5 py-4 font-semibold text-slate-900">
                      {formatAmount(transaction.order_amount)}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {transaction.payment_method || "—"}
                    </td>
                    <td className="px-5 py-4 text-slate-500">
                      {new Date(transaction.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="flex justify-end gap-3">
                        <button
                          type="button"
                          onClick={() => startEdit(transaction)}
                          className="font-medium text-cyan-600 hover:text-cyan-700"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(transaction.id)}
                          className="font-medium text-red-600 hover:text-red-700"
                        >
                          Delete
                        </button>
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
