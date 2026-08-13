import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Settings() {
  const { user, signOut, supabase } = useAuth();
  const [email, setEmail] = useState(user?.email || "");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [emailLoading, setEmailLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [emailMessage, setEmailMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  async function handleEmailUpdate(event) {
    event.preventDefault();
    setEmailLoading(true);
    setEmailMessage("");
    setEmailError("");

    try {
      const { error } = await supabase.auth.updateUser({ email: email.trim() });
      if (error) throw error;
      setEmailMessage("Email update requested. Check your inbox to confirm it.");
    } catch (updateError) {
      setEmailError(updateError.message || "Could not update your email.");
    } finally {
      setEmailLoading(false);
    }
  }

  async function handlePasswordUpdate(event) {
    event.preventDefault();
    setPasswordMessage("");
    setPasswordError("");

    if (newPassword.length < 6) {
      setPasswordError("Password must be at least 6 characters.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("Passwords do not match.");
      return;
    }

    setPasswordLoading(true);

    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });
      if (error) throw error;
      setNewPassword("");
      setConfirmPassword("");
      setPasswordMessage("Password updated successfully.");
    } catch (updateError) {
      setPasswordError(updateError.message || "Could not update your password.");
    } finally {
      setPasswordLoading(false);
    }
  }

  return (
    <div>
      <p className="text-sm uppercase tracking-[0.2em] text-cyan-600">Settings</p>
      <h1 className="mt-2 text-3xl font-bold text-slate-900">Account Settings</h1>
      <p className="mt-2 text-slate-500">Manage your account details and security.</p>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Email Address</h2>
          <p className="mt-1 text-sm text-slate-500">Current account: {user?.email || "—"}</p>
          <form onSubmit={handleEmailUpdate} className="mt-5 space-y-4">
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
            />
            {emailError && <p className="text-sm text-red-600">{emailError}</p>}
            {emailMessage && <p className="text-sm text-emerald-600">{emailMessage}</p>}
            <button
              type="submit"
              disabled={emailLoading}
              className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white hover:bg-cyan-700 disabled:opacity-60"
            >
              {emailLoading ? "Updating..." : "Update Email"}
            </button>
          </form>
        </section>

        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Change Password</h2>
          <form onSubmit={handlePasswordUpdate} className="mt-5 space-y-4">
            <input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
            />
            <input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
            />
            {passwordError && <p className="text-sm text-red-600">{passwordError}</p>}
            {passwordMessage && <p className="text-sm text-emerald-600">{passwordMessage}</p>}
            <button
              type="submit"
              disabled={passwordLoading}
              className="rounded-xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white hover:bg-cyan-700 disabled:opacity-60"
            >
              {passwordLoading ? "Updating..." : "Update Password"}
            </button>
          </form>
        </section>
      </div>

      <section className="mt-6 rounded-2xl border border-red-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Sign Out</h2>
        <p className="mt-1 text-sm text-slate-500">End your current session on this device.</p>
        <button
          type="button"
          onClick={signOut}
          className="mt-5 rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white hover:bg-red-700"
        >
          Sign Out
        </button>
      </section>
    </div>
  );
}
