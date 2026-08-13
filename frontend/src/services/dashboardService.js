import { api } from "../lib/api";

function projectPath(projectId, resource) {
  return `/projects/${projectId}/dashboard/${resource}`;
}

export function getDashboard(projectId) {
  return api.get(projectPath(projectId, "overview"));
}

export function getRevenue(projectId) {
  return api.get(`/projects/${projectId}/dashboard/revenue`);
}

export function getSegmentSummary(projectId) {
  return api.get(`/projects/${projectId}/segments/summary`);
}

export function getInsights(projectId) {
  return api.get(projectPath(projectId, "migrations"));
}

export function getRecommendations(projectId) {
  return api.get(`/projects/${projectId}/segments`);
}

export function getActivity(projectId) {
  return api.get(`/projects/${projectId}/dashboard/activity`);
}

export function getMigrations(projectId) {
  return api.get(projectPath(projectId, "migrations"));
}

export default {
  getDashboard,
  getRevenue,
  getSegmentSummary,
  getInsights,
  getRecommendations,
  getActivity,
  getMigrations,
};
