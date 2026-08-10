import { api } from "../lib/api";

export function getCustomers(projectId) {
  return api.get(`/projects/${projectId}/customers`);
}

export function getCustomer(projectId, customerId) {
  return api.get(`/projects/${projectId}/customers/${customerId}`);
}

export function createCustomer(projectId, customer) {
  return api.post(`/projects/${projectId}/customers`, customer);
}

export function updateCustomer(projectId, customerId, customer) {
  return api.put(
    `/projects/${projectId}/customers/${customerId}`,
    customer
  );
}

export function deleteCustomer(projectId, customerId) {
  return api.del(`/projects/${projectId}/customers/${customerId}`);
}

export function getCustomerSegment(customerId) {
  return api.get(`/customers/${customerId}/segment`);
}

export default {
  getCustomers,
  getCustomer,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  getCustomerSegment,
};
