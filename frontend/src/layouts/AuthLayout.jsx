import ClusterAnimation from "../components/ClusterAnimation";

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950">
      <div className="grid min-h-screen lg:grid-cols-2">

        <div className="hidden lg:block p-10">
          <ClusterAnimation />
        </div>

        <div className="flex items-center justify-center p-10">
          <div className="w-full max-w-md">
            {children}
          </div>
        </div>

      </div>
    </div>
  );
}