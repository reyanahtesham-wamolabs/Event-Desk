import React, { useState } from "react";
import { api, type EventCategory, type TicketTier } from "../lib/api";

interface Props { onClose: () => void; onCreated: () => void; }

const CATEGORIES: EventCategory[] = ["music", "sports", "conference", "theater", "other"];

export default function CreateEventModal({ onClose, onCreated }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    description: "",
    event_time: "",
    category: "music" as EventCategory,
    gold_ticket_count: 0,
    gold_ticket_price: 0,
    silver_ticket_count: 0,
    silver_ticket_price: 0,
    bronze_ticket_count: 0,
    bronze_ticket_price: 0,
  });

  const set = (k: string, v: string | number) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const payload = {
        ...form,
        event_time: new Date(form.event_time).toISOString(),
        gold_ticket_count: Number(form.gold_ticket_count),
        gold_ticket_price: Number(form.gold_ticket_price),
        silver_ticket_count: Number(form.silver_ticket_count),
        silver_ticket_price: Number(form.silver_ticket_price),
        bronze_ticket_count: Number(form.bronze_ticket_count),
        bronze_ticket_price: Number(form.bronze_ticket_price),
      };
      await api.post("/events", payload);
      onCreated();
    } catch (err: unknown) {
      setError((err as Error).message);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <form onSubmit={handleSubmit}
        className="relative w-full max-w-xl max-h-[90vh] overflow-y-auto glass-strong rounded-2xl shadow-2xl animate-fade-in p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Create New Event</h2>
          <button type="button" onClick={onClose} className="p-2 text-slate-500 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <Field label="Title" required>
            <input value={form.title} onChange={e => set("title", e.target.value)} required
              placeholder="Amazing Concert Night"
              className="input-field" />
          </Field>

          <Field label="Description">
            <textarea value={form.description} onChange={e => set("description", e.target.value)} rows={3}
              placeholder="Tell attendees what to expect…"
              className="input-field resize-none" />
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Date & Time" required>
              <input type="datetime-local" value={form.event_time} onChange={e => set("event_time", e.target.value)} required
                className="input-field" />
            </Field>
            <Field label="Category" required>
              <select value={form.category} onChange={e => set("category", e.target.value as EventCategory)}
                className="input-field">
                {CATEGORIES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </Field>
          </div>

          {/* Ticket tiers */}
          <div>
            <p className="text-sm font-medium text-white mb-3">Ticket Tiers</p>
            <div className="space-y-3">
              {([["gold","🥇 Gold","badge-gold"],["silver","🥈 Silver","badge-silver"],["bronze","🥉 Bronze","badge-bronze"]] as const).map(([tier, label, cls]) => (
                <div key={tier} className="glass rounded-xl p-3">
                  <p className={`badge ${cls} mb-2`}>{label}</p>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Count" compact>
                      <input type="number" min="0" value={form[`${tier}_ticket_count` as keyof typeof form]}
                        onChange={e => set(`${tier}_ticket_count`, e.target.value)}
                        className="input-field" />
                    </Field>
                    <Field label="Price ($)" compact>
                      <input type="number" min="0" value={form[`${tier}_ticket_price` as keyof typeof form]}
                        onChange={e => set(`${tier}_ticket_price`, e.target.value)}
                        className="input-field" />
                    </Field>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button type="submit" disabled={loading}
            className="flex-1 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-colors disabled:opacity-50">
            {loading ? "Creating…" : "Create Event (as Draft)"}
          </button>
          <button type="button" onClick={onClose}
            className="px-6 py-3 glass hover:bg-white/10 text-slate-300 font-medium rounded-xl transition-colors">
            Cancel
          </button>
        </div>
      </form>

      <style>{`
        .input-field {
          width: 100%;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 10px;
          padding: 10px 14px;
          color: white;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s;
        }
        .input-field:focus { border-color: rgb(59,94,242); }
        .input-field option { background: #1a1a2e; }
      `}</style>
    </div>
  );
}

function Field({ label, children, required, compact }: {
  label: string; children: React.ReactNode; required?: boolean; compact?: boolean;
}) {
  return (
    <div>
      <label className={`block text-slate-400 mb-1.5 ${compact ? "text-xs" : "text-sm"} font-medium`}>
        {label}{required && <span className="text-red-400 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  );
}
