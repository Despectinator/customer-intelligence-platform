import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";

import AuthLayout from "../components/auth/AuthLayout";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { supabase } = useAuth();

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    setLoading(true);
    setError("");

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }

    navigate("/dashboard");
  }

  return (
    <AuthLayout>
      <div className="space-y-8">

        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-teal-400">
            Customer Intelligence Platform
          </p>

          <h1 className="mt-3 text-5xl font-bold text-white">
            Welcome Back
          </h1>

          <p className="mt-3 text-slate-400">
            Sign in to continue.
          </p>
        </div>

        <form
          className="space-y-6"
          onSubmit={handleLogin}
        >

          <div>

            <label className="mb-2 block text-sm text-slate-300">
              Email
            </label>

            <div className="flex items-center rounded-xl border border-slate-700 bg-slate-900 px-4">

              <Mail className="h-5 w-5 text-slate-500" />

              <input
                type="email"
                className="w-full bg-transparent px-3 py-4 text-white outline-none"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

            </div>

          </div>

          <div>

            <label className="mb-2 block text-sm text-slate-300">
              Password
            </label>

            <div className="flex items-center rounded-xl border border-slate-700 bg-slate-900 px-4">

              <Lock className="h-5 w-5 text-slate-500" />

              <input
                type={showPassword ? "text" : "password"}
                className="w-full bg-transparent px-3 py-4 text-white outline-none"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <button
                type="button"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-slate-500" />
                ) : (
                  <Eye className="h-5 w-5 text-slate-500" />
                )}
              </button>

            </div>

          </div>

          {error && (
            <p className="text-red-400">
              {error}
            </p>
          )}

          <button
            disabled={loading}
            className="w-full rounded-xl bg-teal-500 py-4 font-semibold text-white hover:bg-teal-400"
          >
            {loading ? "Signing In..." : "Sign In"}
          </button>

        </form>

        <div className="text-center text-slate-400">

          Don't have an account?{" "}

          <Link
            to="/signup"
            className="text-teal-400"
          >
            Create one
          </Link>

        </div>

      </div>
    </AuthLayout>
  );
}
