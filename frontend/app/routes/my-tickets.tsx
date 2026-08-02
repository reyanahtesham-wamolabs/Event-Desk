import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { api, type Ticket } from "../lib/api";
import { useAuth } from "../context/AuthContext";

const TIER_CFG = {
  gold: { label: "🥇 Gold", cls: "badge-gold" },
  silver: { label: "🥈 Silver", cls: "badge-silver" },
  bronze: { label: "🥉 Bronze", cls: "badge-bronze" },
} as const;

const STATUS_CFG: Record<string, { cls: string; label: string }> = {
  available: { cls: "text-green-400 bg-green-400/10", label: "Available" },
  booked: { cls: "text-blue-400 bg-blue-400/10", label: "Booked" },
  cancelled: { cls: "text-red-400 bg-red-400/10", label: "Cancelled" },
};

export default function MyTicketsPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState<string | null>(null);
  const [msg, setMsg] = useState({ text: "", err: false });

  useEffect(() => {
    if (!authLoading && !user) navigate("/auth");
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (user) fetchTickets();
  }, [user]);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const data = await api.get<Ticket[]>("/tickets/my-tickets");
      setTickets(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const cancelTicket = async (id: string) => {
    setCancelling(id);
    try {
      await api.post(`/tickets/${id}/cancel`);
      setMsg({ text: "Ticket cancelled.", err: false });
      await fetchTickets();
    } catch (e: unknown) {
      setMsg({ text: (e as Error).message, err: true });
    }
    setCancelling(null);
    setTimeout(() => setMsg({ text: "", err: false }), 3000);
  };

  if (authLoading || loading) return <PageLoader />;
  if (!user) return null;

  const active = tickets.filter(t => t.status !== "cancelled");
  const cancelled = tickets.filter(t => t.status === "cancelled");

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-white">My Tickets</h1>
        <p className="text-slate-400 mt-1">{active.length} active booking{active.length !== 1 ? "s" : ""}</p>
      </div>

      {msg.text && (
        <div className={`mb-4 px-4 py-3 rounded-xl text-sm font-medium animate-slide-down ${
          msg.err ? "bg-red-500/15 border border-red-500/30 text-red-300" : "bg-green-500/15 border border-green-500/30 text-green-300"
        }`}>
          {msg.text}
        </div>
      )}

      {tickets.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-6xl mb-4">🎟️</p>
          <p className="text-xl font-semibold text-white mb-2">No tickets yet</p>
          <p className="text-slate-400 mb-6">Browse events and book your first ticket!</p>
          <button onClick={() => navigate("/")} className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors">
            Explore Events
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Active */}
          {active.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest mb-3">Active</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {active.map(ticket => <TicketCard key={ticket.id} ticket={ticket} onCancel={() => cancelTicket(ticket.id)} cancelling={cancelling === ticket.id} />)}
              </div>
            </section>
          )}

          {/* Cancelled */}
          {cancelled.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest mb-3">Cancelled</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {cancelled.map(ticket => <TicketCard key={ticket.id} ticket={ticket} onCancel={() => {}} cancelling={false} />)}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

function TicketCard({ ticket, onCancel, cancelling }: { ticket: Ticket; onCancel: () => void; cancelling: boolean; }) {
  const tier = TIER_CFG[ticket.ticket_tier] ?? { label: ticket.ticket_tier, cls: "badge-silver" };
  const statusCfg = STATUS_CFG[ticket.status] ?? { cls: "text-slate-400 bg-white/5", label: ticket.status };

  return (
    <div className="glass rounded-2xl p-5 card-hover border border-white/8 animate-fade-in relative overflow-hidden">
      {/* Decorative left accent */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-2xl ${
        ticket.ticket_tier === "gold" ? "bg-amber-400" : ticket.ticket_tier === "silver" ? "bg-slate-300" : "bg-orange-600"
      }`} />

      <div className="flex items-start justify-between mb-3">
        <div>
          <span className={`badge ${tier.cls}`}>{tier.label}</span>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusCfg.cls}`}>
          {statusCfg.label}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Seat</span>
          <span className="text-white font-mono font-medium">{ticket.seat_num}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Price</span>
          <span className="text-white font-medium">${ticket.price}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Ticket ID</span>
          <span className="text-slate-500 font-mono text-xs">{ticket.id.slice(0, 8)}…</span>
        </div>
      </div>

      {ticket.status === "booked" && (
        <button onClick={onCancel} disabled={cancelling}
          className="w-full py-2 rounded-xl text-sm font-medium bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors disabled:opacity-50">
          {cancelling ? "Cancelling…" : "Cancel Ticket"}
        </button>
      )}
    </div>
  );
}

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <div className="w-10 h-10 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin" />
    </div>
  );
}
