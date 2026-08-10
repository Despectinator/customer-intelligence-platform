import { api } from "../lib/api";

export function getSegments(projectId) {
  return api.get(`/projects/${projectId}/segments`);
}

export function getSegmentSummary(projectId) {
  return api.get(`/projects/${projectId}/segments/summary`);
}

export function recomputeSegments(projectId) {
  return api.post(`/projects/${projectId}/segments/recompute`);
}

export function getCustomerSegment(customerId) {
  return api.get(`/customers/${customerId}/segment`);
}

export function getDashboardOverview(projectId) {
  return api.get(`/projects/${projectId}/dashboard/overview`);
}

export function getRevenue(projectId) {
  return api.get(`/projects/${projectId}/dashboard/revenue`);
}

export function getActivity(projectId) {
  return api.get(`/projects/${projectId}/dashboard/activity`);
}

export function getMigrations(projectId) {
  return api.get(`/projects/${projectId}/dashboard/migrations`);
}

export default {
  getSegments,
  getSegmentSummary,
  recomputeSegments,
  getCustomerSegment,
  getDashboardOverview,
  getRevenue,
  getActivity,
  getMigrations,
};
