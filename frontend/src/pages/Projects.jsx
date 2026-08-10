import { useEffect, useState } from "react";

import { useProject } from "../hooks/useProject";
import projectService from "../services/projectService";

export default function Projects() {
  const { currentProject, setCurrentProject } = useProject();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError("");

      try {
        const data = await projectService.getProjects();
        if (!cancelled) setProjects(data || []);
      } catch (loadError) {
        if (!cancelled) {
          console.error(loadError);
          setError(loadError.message || "Could not load projects.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  async function handleCreate(event) {
    event.preventDefault();

    if (!form.name.trim()) {
      setError("Project name is required.");
      return;
    }

    setSaving(true);
    setError("");

    try {
      const createdProject = await projectService.createProject({
        name: form.name.trim(),
        description: form.description.trim() || null,
      });

      setProjects((previous) => [createdProject, ...previous]);
      setCurrentProject(createdProject);
      setForm({ name: "", description: "" });
      setShowForm(false);
    } catch (createError) {
      console.error(createError);
      setError(createError.message || "Could not create project.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(project) {
    const confirmed = window.confirm(
      `Delete project "${project.name}"? This action cannot be undone.`
    );
    if (!confirmed) return;

    setError("");

    try {
      await projectService.deleteProject(project.id);
      setProjects((previous) =>
        previous.filter((item) => item.id !== project.id)
      );
      if (currentProject?.id === project.id) setCurrentProject(null);
    } catch (deleteError) {
      console.error(deleteError);
      setError(deleteError.message || "Could not delete project.");
    }
  }

  return (
    <div>
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">
            Projects
          </p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Projects</h1>
          <p className="mt-2 text-slate-500">
            Create and manage your customer intelligence projects.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            setShowForm((previous) => !previous);
            setError("");
          }}
          className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700"
        >
          {showForm ? "Cancel" : "+ New Project"}
        </button>
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {showForm && (
        <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Create Project</h2>
          <form onSubmit={handleCreate} className="mt-5 space-y-5">
            <div>
              <label htmlFor="project-name" className="mb-2 block text-sm font-medium text-slate-700">
                Project Name
              </label>
              <input
                id="project-name"
                name="name"
                type="text"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g. Demo Store"
                className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
              />
            </div>
            <div>
              <label htmlFor="project-description" className="mb-2 block text-sm font-medium text-slate-700">
                Description
              </label>
              <textarea
                id="project-description"
                name="description"
                value={form.description}
                onChange={handleChange}
                rows={3}
                placeholder="Optional project description"
                className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
              />
            </div>
            <button
              type="submit"
              disabled={saving}
              className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving ? "Creating..." : "Create Project"}
            </button>
          </form>
        </section>
      )}

      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Your Projects</h2>
          <span className="text-sm text-slate-500">
            {projects.length} project{projects.length === 1 ? "" : "s"}
          </span>
        </div>

        {loading ? (
          <div className="rounded-2xl border border-gray-200 bg-white px-6 py-16 text-center shadow-sm">
            <p className="text-slate-600">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-16 text-center shadow-sm">
            <p className="font-semibold text-slate-900">No projects yet</p>
            <p className="mt-2 text-sm text-slate-500">
              Create your first project to start managing customers.
            </p>
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => {
              const isCurrent = currentProject?.id === project.id;

              return (
                <article
                  key={project.id}
                  className={`rounded-2xl border bg-white p-6 shadow-sm transition ${
                    isCurrent
                      ? "border-cyan-500 ring-2 ring-cyan-100"
                      : "border-gray-200 hover:border-cyan-300"
                  }`}
                >
                  <h3 className="text-lg font-semibold text-slate-900">
                    {project.name}
                  </h3>
                  {isCurrent && (
                    <span className="mt-2 inline-block rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">
                      Current Project
                    </span>
                  )}
                  <p className="mt-4 min-h-[48px] text-sm text-slate-500">
                    {project.description || "No description provided."}
                  </p>
                  <p className="mt-4 text-xs text-slate-400">
                    Created {project.created_at ? new Date(project.created_at).toLocaleDateString() : "—"}
                  </p>
                  <div className="mt-6 flex items-center gap-3">
                    {!isCurrent ? (
                      <button
                        type="button"
                        onClick={() => setCurrentProject(project)}
                        className="rounded-lg bg-cyan-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-700"
                      >
                        Select
                      </button>
                    ) : (
                      <span className="rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600">
                        Selected
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => handleDelete(project)}
                      className="rounded-lg px-4 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
