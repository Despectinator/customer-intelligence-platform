import { LogOut, X } from "lucide-react";
import { NavLink } from "react-router-dom";

import { navigation } from "../../constants/navigation";
import { useProject } from "../../hooks/useProject";

export default function Sidebar({ user, signOut, mobileOpen, onClose }) {
  const { currentProject } = useProject();

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-800 bg-slate-950 p-6 transition-transform lg:translate-x-0 ${
        mobileOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="mb-10 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-teal-400">
            Customer Intelligence
          </p>
          <p className="mt-2 text-xs text-slate-500">Analytics platform</p>
        </div>
        <button type="button" aria-label="Close navigation" className="text-slate-400 lg:hidden" onClick={onClose}>
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="space-y-2" aria-label="Main navigation">
        {navigation.map(({ label, path, icon: Icon }) => {
          const projectId = currentProject?.id;
          const projectPath =
            label === "Customers"
              ? projectId
                ? `/projects/${projectId}/customers`
                : path
              : label === "Analytics"
                ? projectId
                  ? `/projects/${projectId}/analytics`
                  : path
                : label === "Upload CSV"
                  ? projectId
                    ? `/projects/${projectId}/upload`
                    : path
                  : path;

          return (
          <NavLink
            key={path}
            to={projectPath}
            end
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive ? "bg-teal-500/15 text-teal-300" : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
          );
        })}
      </nav>

      <div className="mt-auto border-t border-slate-800 pt-5">
        <p className="truncate text-xs text-slate-500">{user?.email}</p>
        <button type="button" onClick={signOut} className="mt-4 flex items-center gap-3 text-sm text-slate-400 transition hover:text-red-400">
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
