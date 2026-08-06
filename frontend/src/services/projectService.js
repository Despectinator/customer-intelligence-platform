import { api } from "../lib/api";

export const getProjects = () => api.get("/projects");

export default {
  getProjects,
};
