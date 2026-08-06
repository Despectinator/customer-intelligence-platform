import { useState } from "react";
import { Outlet } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function AppShell({ children }) {
  const { user, signOut } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const content = children ?? <Outlet />;

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      {mobileOpen && (
        <button type="button" aria-label="Close navigation" className="fixed inset-0 z-30 bg-black/60 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}
      <Sidebar user={user} signOut={signOut} mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <div className="lg:pl-72">
        <Navbar user={user} onOpen={() => setMobileOpen(true)} />
        <main className="min-h-[calc(100vh-4rem)] px-6 py-8 lg:px-10">{content}</main>
      </div>
    </div>
  );
}
