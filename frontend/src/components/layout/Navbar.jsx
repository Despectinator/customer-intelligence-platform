import { Menu } from "lucide-react";

export default function Navbar({ user, onOpen }) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center border-b border-gray-200 bg-white px-6 lg:px-10">
      <button type="button" aria-label="Open navigation" className="mr-4 text-slate-400 lg:hidden" onClick={onOpen}>
        <Menu className="h-6 w-6" />
      </button>
      <div className="flex-1">
        <h2 className="text-xl font-semibold text-slate-900">Dashboard</h2>
      </div>
      <p className="hidden max-w-xs truncate text-sm text-slate-500 sm:block">{user?.email}</p>
    </header>
  );
}
