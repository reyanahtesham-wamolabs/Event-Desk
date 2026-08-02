import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router";
import { api, type Event, type EventStatus } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import EventCard from "../components/EventCard";
import EventModal from "../components/EventModal";
import CreateEventModal from "../components/CreateEventModal";

const STATUSES: (EventStatus | "")[] = ["", "draft", "published", "cancelled", "completed"];

export default function MyEventsPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [creating, setCreating] = useState(false);
  const [statusFilter, setStatusFilter] = useState<EventStatus | "">("");

  useEffect(() => {
    if (!authLoading) {
      if (!user) navigate("/auth");
      else if (user.role === "attendee") navigate("/");
    }
  }, [user, authLoading, navigate]);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (statusFilter) params.status = statusFilter;
      const data = await api.get<Event[]>("/events/mine", params);
      setEvents(data);
    } catch { /* ignore */ }
    setLoading(false);
  }, [statusFilter]);

  useEffect(() => {
    if (user && user.role !== "attendee") fetchEvents();
  }, [user, fetchEvents]);

  if (authLoading || loading) return <PageLoader />;
  if (!user) return null;

  const stats = {
    total: events.length,
    published: events.filter(e => e.status === "published").length,
    draft: events.filter(e => e.status === "draft").length,
    totalTickets: events.reduce((a, e) => a + e.total_tickets, 0),
    booked: events.reduce((a, e) => a + e.tickets.filter(t => t.user_id).length, 0),
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-black text-white">My Events</h1>
          <p className="text-slate-400 mt-1">Manage your organized events</p>
        </div>
        <button onClick={() => setCreating(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors animate-pulse-glow">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Event
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Events", value: stats.total, icon: "🎪" },
          { label: "Published", value: stats.published, icon: "✅" },
          { label: "Drafts", value: stats.draft, icon: "📝" },
          { label: "Tickets Sold", value: `${stats.booked}/${stats.totalTickets}`, icon: "🎟️" },
        ].map(s => (
          <div key={s.label} className="glass rounded-2xl p-5">
            <p className="text-2xl mb-2">{s.icon}</p>
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-xs text-slate-500 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Status filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1">
        {STATUSES.map(s => (
          <button key={s || "all"} onClick={() => setStatusFilter(s)}
            className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-colors capitalize ${
              statusFilter === s ? "bg-blue-600 text-white" : "glass text-slate-400 hover:text-white"
            }`}>
            {s || "All Statuses"}
          </button>
        ))}
      </div>

      {/* Events grid */}
      {events.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-6xl mb-4">🎪</p>
          <p className="text-xl font-semibold text-white mb-2">No events yet</p>
          <p className="text-slate-400 mb-6">Create your first event to get started</p>
          <button onClick={() => setCreating(true)} className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors">
            Create Event
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {events.map((event, i) => (
            <div key={event.id} style={{ animationDelay: `${i * 50}ms` }}>
              <EventCard event={event} onClick={() => setSelectedEvent(event)} />
            </div>
          ))}
        </div>
      )}

      {selectedEvent && (
        <EventModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onUpdate={() => { fetchEvents(); setSelectedEvent(null); }}
        />
      )}
      {creating && (
        <CreateEventModal
          onClose={() => setCreating(false)}
          onCreated={() => { fetchEvents(); setCreating(false); }}
        />
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
