import { api } from "../lib/api";

function projectPath(projectId, resource) {
  return `/projects/${projectId}/dashboard/${resource}`;
}

export function getDashboard(projectId) {
  return api.get(projectPath(projectId, "overview"));
}

export function getRevenue(projectId) {
  return api.get(`/projects/${projectId}/segments/summary`);
}

export function getInsights(projectId) {
  return api.get(projectPath(projectId, "migrations"));
}

export function getRecommendations(projectId) {
  return api.get(`/projects/${projectId}/segments`);
}

export default {
  getDashboard,
  getRevenue,
  getInsights,
  getRecommendations,
};
