import { api } from "../lib/api";

export function getProjects() {
  return api.get("/projects");
}

export function createProject(project) {
  return api.post("/projects", project);
}

export function getProject(projectId) {
  return api.get(`/projects/${projectId}`);
}

export function updateProject(projectId, project) {
  return api.put(`/projects/${projectId}`, project);
}

export function deleteProject(projectId) {
  return api.del(`/projects/${projectId}`);
}

export default {
  getProjects,
  createProject,
  getProject,
  updateProject,
  deleteProject,
};
