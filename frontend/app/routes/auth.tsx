import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";

export default function AuthPage() {
  const { user, login, signup, loading } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "attendee" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user) navigate("/");
  }, [user, navigate]);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true); setError("");
    try {
      if (mode === "login") {
        await login(form.email, form.password);
      } else {
        await signup(form.name, form.email, form.password, form.role);
      }
      navigate("/");
    } catch (err: unknown) {
      setError((err as Error).message);
    }
    setSubmitting(false);
  };

  if (loading) return null;

  return (
    <div className="min-h-[90vh] flex items-center justify-center p-4">
      {/* Background blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-600/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4 animate-pulse-glow">
            E
          </div>
          <h1 className="text-3xl font-black text-white">EventDesk</h1>
          <p className="text-slate-400 mt-1">Discover, book, and manage events</p>
        </div>

        {/* Card */}
        <div className="glass-strong rounded-2xl p-8 shadow-2xl">
          {/* Mode toggle */}
          <div className="flex gap-1 p-1 glass rounded-xl mb-6">
            {(["login", "signup"] as const).map(m => (
              <button key={m} onClick={() => { setMode(m); setError(""); }}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                  mode === m ? "bg-blue-600 text-white shadow" : "text-slate-400 hover:text-white"
                }`}>
                {m === "login" ? "Sign In" : "Create Account"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && (
              <div>
                <label className="block text-sm text-slate-400 mb-1.5 font-medium">Full Name</label>
                <input value={form.name} onChange={e => set("name", e.target.value)} required
                  placeholder="John Doe"
                  className="w-full glass border border-white/10 focus:border-blue-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors placeholder-slate-600" />
              </div>
            )}

            <div>
              <label className="block text-sm text-slate-400 mb-1.5 font-medium">Email</label>
              <input type="email" value={form.email} onChange={e => set("email", e.target.value)} required
                placeholder="you@example.com"
                className="w-full glass border border-white/10 focus:border-blue-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors placeholder-slate-600" />
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1.5 font-medium">Password</label>
              <input type="password" value={form.password} onChange={e => set("password", e.target.value)} required
                placeholder="••••••••"
                className="w-full glass border border-white/10 focus:border-blue-500 rounded-xl px-4 py-3 text-white text-sm outline-none transition-colors placeholder-slate-600" />
            </div>

            {mode === "signup" && (
              <div>
                <label className="block text-sm text-slate-400 mb-1.5 font-medium">Account Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: "attendee", icon: "🎟️", label: "Attendee" },
                    { value: "organizer", icon: "🎪", label: "Organizer" },
                    { value: "admin", icon: "⚡", label: "Admin" },
                  ].map(opt => (
                    <button key={opt.value} type="button"
                      onClick={() => set("role", opt.value)}
                      className={`flex flex-col items-center gap-1 p-3 rounded-xl border text-xs font-medium transition-all ${
                        form.role === opt.value
                          ? "border-blue-500 bg-blue-500/15 text-blue-400"
                          : "border-white/10 glass text-slate-400 hover:border-white/20"
                      }`}>
                      <span className="text-xl">{opt.icon}</span>
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <div className="px-4 py-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-sm animate-slide-down">
                {error}
              </div>
            )}

            <button type="submit" disabled={submitting}
              className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-all disabled:opacity-50 mt-2">
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {mode === "login" ? "Signing in…" : "Creating account…"}
                </span>
              ) : (
                mode === "login" ? "Sign In" : "Create Account"
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-slate-600 mt-6">
          Event Desk — Your premier event management platform
        </p>
      </div>
    </div>
  );
}
