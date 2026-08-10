import { api } from "../lib/api";

export function getTransactions(customerId) {
  return api.get(`/customers/${customerId}/transactions`);
}

export function createTransaction(customerId, transaction) {
  return api.post(
    `/customers/${customerId}/transactions`,
    transaction
  );
}

export function updateTransaction(
  customerId,
  transactionId,
  transaction
) {
  return api.put(
    `/customers/${customerId}/transactions/${transactionId}`,
    transaction
  );
}

export function deleteTransaction(customerId, transactionId) {
  return api.del(
    `/customers/${customerId}/transactions/${transactionId}`
  );
}

export default {
  getTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
};
