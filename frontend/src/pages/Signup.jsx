import { useState } from "react";
import { Link } from "react-router-dom";
import { Mail, Lock, User, Eye, EyeOff } from "lucide-react";

import AuthLayout from "../components/auth/AuthLayout";
import { useAuth } from "../hooks/useAuth";

export default function Signup() {
  const { supabase } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSignup(e) {
    e.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });

    setLoading(false);

    if (error) {
      setError(error.message);
      return;
    }

    setMessage(
      "Account created! Please check your email to verify your account."
    );
  }

  return (
    <AuthLayout>
      <div className="space-y-8">

        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-teal-400">
            Customer Intelligence Platform
          </p>

          <h1 className="mt-3 text-5xl font-bold text-white">
            Create Account
          </h1>

          <p className="mt-3 text-slate-400">
            Start analyzing customer intelligence today.
          </p>
        </div>

        <form
          onSubmit={handleSignup}
          className="space-y-6"
        >

          <div>
            <label className="mb-2 block text-sm text-slate-300">
              Full Name
            </label>

            <div className="flex items-center rounded-xl border border-slate-700 bg-slate-900 px-4">

              <User className="h-5 w-5 text-slate-500" />

              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-transparent px-3 py-4 text-white outline-none"
              />

            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm text-slate-300">
              Email
            </label>

            <div className="flex items-center rounded-xl border border-slate-700 bg-slate-900 px-4">

              <Mail className="h-5 w-5 text-slate-500" />

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-transparent px-3 py-4 text-white outline-none"
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
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-transparent px-3 py-4 text-white outline-none"
              />

              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
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

          {message && (
            <p className="text-green-400">
              {message}
            </p>
          )}

          <button
            disabled={loading}
            className="w-full rounded-xl bg-teal-500 py-4 font-semibold text-white hover:bg-teal-400"
          >
            {loading ? "Creating Account..." : "Create Account"}
          </button>

        </form>

        <div className="text-center text-slate-400">

          Already have an account?

          <Link
            to="/"
            className="ml-2 text-teal-400"
          >
            Sign In
          </Link>

        </div>

      </div>
    </AuthLayout>
  );
}
