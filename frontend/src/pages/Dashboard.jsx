import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getDashboard,
  getRevenue,
  getActivity,
  getRecommendations,
  getMigrations,
} from "../services/dashboardService";
import projectService from "../services/projectService";
import { useProject } from "../hooks/useProject";
import KPICard from "../components/dashboard/KPICard";
import RevenueChart from "../components/dashboard/RevenueChart";
import SegmentChart from "../components/dashboard/SegmentChart";
import RecentActivityTable from "../components/dashboard/ActivityTable";
import RecommendationPanel from "../components/dashboard/RecommendationPanel";
import MigrationHistory from "../components/dashboard/MigrationHistory";
import ProjectFormModal from "../components/modal/ProjectFormModal";

export default function Dashboard() {
  const { currentProject, setCurrentProject } = useProject();
  const [projects, setProjects] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [segmentData, setSegmentData] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [activityData, setActivityData] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [migrations, setMigrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [segmentLoading, setSegmentLoading] = useState(false);
  const [activityLoading, setActivityLoading] = useState(false);
  const [migrationLoading, setMigrationLoading] = useState(false);
  const [error, setError] = useState("");
  const [dashboardError, setDashboardError] = useState("");
  const [modalMode, setModalMode] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProjects() {
      setLoading(true);
      setError("");

      try {
        const response = await projectService.getProjects();

        if (!cancelled) {
          setProjects(response || []);
        }
      } catch (loadError) {
        console.error(loadError);
        setError(loadError.message || "Could not load projects.");
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadProjects();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!currentProject) {
      return;
    }

    async function loadDashboard() {
      setDashboardLoading(true);
      setSegmentLoading(true);
      setActivityLoading(true);
      setMigrationLoading(true);
      setDashboardError("");

      try {
        const [dashboardResponse, revenueResponse, activityResponse, recommendationsResponse, migrationResponse] = await Promise.all([
          getDashboard(currentProject.id),
          getRevenue(currentProject.id),
          getActivity(currentProject.id),
          getRecommendations(currentProject.id),
          getMigrations(currentProject.id),
        ]);

        console.log("Dashboard response:", dashboardResponse);
        console.log("Revenue response:", revenueResponse);
        console.log("Activity response:", activityResponse);
        console.log("Recommendations response:", recommendationsResponse);

        setDashboard(dashboardResponse);
        setSegmentData(dashboardResponse.segment_breakdown || []);
        setRevenueData(revenueResponse || []);
        setActivityData(activityResponse || []);
        setMigrations(migrationResponse || []);

        const uniqueRecommendations = [];
        const seenSegments = new Set();

        for (const segment of recommendationsResponse || []) {
          if (
            segment.segment_name &&
            segment.recommendation &&
            !seenSegments.has(segment.segment_name)
          ) {
            seenSegments.add(segment.segment_name);

            uniqueRecommendations.push({
              id: segment.segment_name,
              segment: segment.segment_name,
              text: segment.recommendation,
            });
          }
        }

        setRecommendations(uniqueRecommendations);
      } catch (loadError) {
        console.error("Dashboard loading failed:", loadError);
        setDashboardError(loadError.message || "Could not load dashboard data.");
      } finally {
        setDashboardLoading(false);
        setSegmentLoading(false);
        setActivityLoading(false);
        setMigrationLoading(false);
      }
    }

    loadDashboard();
  }, [currentProject]);

  async function handleCreate(values) {
    const created = await projectService.createProject(values);
    setProjects((current) => [created, ...current]);
    setCurrentProject(created);
  }

  async function handleUpdate(projectId, values) {
    const updated = await projectService.updateProject(projectId, values);
    setProjects((current) =>
      current.map((project) => (project.id === projectId ? updated : project))
    );
  }

  async function handleDelete(project) {
    if (!window.confirm(`Delete "${project.name}"? This cannot be undone.`)) return;

    try {
      await projectService.deleteProject(project.id);
      setProjects((current) => {
        const remaining = current.filter(({ id }) => id !== project.id);
        if (currentProject?.id === project.id) {
          setDashboard(null);
          setCurrentProject(remaining[0] ?? null);
        }
        return remaining;
      });
    } catch (deleteError) {
      setError(deleteError.message || "Could not delete this project.");
    }
  }

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-600">
        Loading dashboard...
      </div>
    );
  }

  const status = dashboard?.segmentation_status;
  const emptyMessage =
    status === "no_data"
      ? "No customer data yet."
      : status === "no_transactions"
        ? "No transactions yet."
        : status === "insufficient_data"
          ? "Insufficient segmentation data."
          : status === "not_generated"
            ? "Segmentation has not been generated yet."
            : "No data available for this project.";

  return (
    <div>
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">Dashboard</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="mt-1 text-slate-500">
            Customer Intelligence Overview
          </p>
          <p className="mt-2 text-sm text-slate-500">
            Current Project: {currentProject?.name ?? "No project selected"}
          </p>
        </div>
        {projects.length > 0 && (
          <label className="flex items-center gap-3 text-sm text-slate-600">
            Project
            <select value={currentProject?.id ?? ""} onChange={(event) => setCurrentProject(projects.find(({ id }) => id === event.target.value) ?? null)} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-700 shadow-sm outline-none focus:border-cyan-500">
              {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
            </select>
          </label>
        )}
        <button
          type="button"
          onClick={() => setModalMode("create")}
          className="rounded-xl bg-teal-500 px-4 py-3 text-sm font-semibold text-white hover:bg-teal-400"
        >
          New project
        </button>
      </div>

      <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Key performance indicators">
        <KPICard title="Revenue" value={dashboard ? `₨${dashboard.total_revenue.toLocaleString()}` : "—"} subtitle="Current dataset" icon="₨" color="emerald" loading={dashboardLoading} />
        <KPICard title="Customers" value={dashboard ? dashboard.total_customers : "—"} subtitle="Registered" icon="👥" color="cyan" loading={dashboardLoading} />
        <KPICard title="Projects" value={projects.length} subtitle="Active" icon="📁" color="amber" loading={loading} />
        <KPICard title="Segments" value={status === "ready" ? segmentData.length : "—"} subtitle={status === "ready" ? "Generated" : "Not available"} icon="🧠" color="rose" loading={segmentLoading} />
      </section>

      <section className="mb-6 grid grid-cols-1 gap-6 xl:grid-cols-2" aria-label="Analytics overview">
        <RevenueChart data={revenueData} loading={dashboardLoading} emptyMessage={emptyMessage} />
        <SegmentChart
          data={segmentData}
          loading={segmentLoading}
          status={dashboard?.segmentation_status}
          message={dashboard?.segmentation_message}
        />
      </section>

      <section className="mb-10 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <RecentActivityTable activities={activityData} loading={activityLoading} emptyMessage={emptyMessage} />
        <RecommendationPanel recommendations={recommendations} emptyMessage={status === "ready" ? "No recommendations available yet." : emptyMessage} />
      </section>

      <section className="mb-10">
        <MigrationHistory migrations={migrations} loading={migrationLoading} />
      </section>

      {error && (
        <div className="rounded-xl border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {dashboardError && (
        <div className="mb-6 rounded-xl border border-amber-400/30 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {dashboardError}
        </div>
      )}

      {!loading && !error && projects.length === 0 && (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
          <p className="text-lg font-semibold text-slate-900">No projects yet</p>
          <p className="mt-2 text-sm text-slate-500">
            Create a project to start tracking customers and transactions.
          </p>
        </div>
      )}

      {!loading && !error && projects.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {projects.map((project) => (
            <article key={project.id} className="flex flex-col justify-between rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
              <div>
                <Link to={`/projects/${project.id}/customers`} className="text-lg font-semibold text-slate-900 hover:text-cyan-600">
                  {project.name}
                </Link>
                {project.description && <p className="mt-2 line-clamp-2 text-sm text-slate-600">{project.description}</p>}
                {project.created_at && <p className="mt-4 text-xs text-slate-500">Created {new Date(project.created_at).toLocaleDateString()}</p>}
              </div>
              <div className="mt-5 flex gap-4 border-t border-gray-200 pt-4 text-sm">
                <button type="button" onClick={() => setModalMode({ edit: project })} className="text-slate-500 hover:text-slate-900">Edit</button>
                <button type="button" onClick={() => handleDelete(project)} className="text-slate-400 hover:text-red-400">Delete</button>
              </div>
            </article>
          ))}
        </div>
      )}

      {modalMode === "create" && (
        <ProjectFormModal title="New project" submitLabel="Create" onSubmit={handleCreate} onClose={() => setModalMode(null)} />
      )}

      {modalMode?.edit && (
        <ProjectFormModal title="Edit project" submitLabel="Save" initialValues={modalMode.edit} onSubmit={(values) => handleUpdate(modalMode.edit.id, values)} onClose={() => setModalMode(null)} />
      )}
    </div>
  );
}
