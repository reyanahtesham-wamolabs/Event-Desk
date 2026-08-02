import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router";
import { api, type Event, type EventCategory } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import EventCard from "../components/EventCard";
import EventModal from "../components/EventModal";
import CreateEventModal from "../components/CreateEventModal";

const CATEGORIES: (EventCategory | "")[] = ["", "music", "sports", "conference", "theater", "other"];
const CATEGORY_LABELS: Record<string, string> = {
  "": "All", music: "🎵 Music", sports: "⚽ Sports", conference: "💼 Conference", theater: "🎭 Theater", other: "✨ Other",
};

export default function EventsPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [creating, setCreating] = useState(false);
  const [category, setCategory] = useState<EventCategory | "">("");
  const [search, setSearch] = useState("");

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (category) params.category = category;
      const data = await api.get<Event[]>("/events", params);
      setEvents(data);
    } catch { /* ignore */ }
    setLoading(false);
  }, [category]);

  useEffect(() => {
    if (!authLoading && !user) navigate("/auth");
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (user) fetchEvents();
  }, [user, fetchEvents]);

  const filtered = events.filter(e =>
    search === "" ||
    e.title.toLowerCase().includes(search.toLowerCase()) ||
    e.description?.toLowerCase().includes(search.toLowerCase())
  );

  const canCreate = user?.role === "organizer" || user?.role === "admin";

  if (authLoading) return <LoadingScreen />;
  if (!user) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Hero banner */}
      <div className="relative rounded-3xl overflow-hidden mb-10 p-8 sm:p-12"
        style={{ background: "linear-gradient(135deg, rgba(59,94,242,0.3) 0%, rgba(139,92,246,0.2) 100%)", border: "1px solid rgba(59,94,242,0.2)" }}>
        <div className="relative z-10">
          <p className="text-blue-400 text-sm font-semibold uppercase tracking-widest mb-2">Welcome back, {user.name.split(" ")[0]}</p>
          <h1 className="text-3xl sm:text-4xl font-black text-white mb-3">Discover Events</h1>
          <p className="text-slate-400 max-w-lg">Find and book tickets to the best events. Concerts, conferences, sports, and more.</p>
        </div>
        {/* decorative orbs */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/3 w-48 h-48 bg-violet-600/10 rounded-full blur-3xl" />
      </div>

      {/* Filters row */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        {/* Search */}
        <div className="relative flex-1">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search events…"
            className="w-full pl-10 pr-4 py-2.5 glass rounded-xl text-sm text-white placeholder-slate-500 outline-none focus:border-blue-500 border border-white/10 focus:border-blue-500"
          />
        </div>

        {/* Category filters */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {CATEGORIES.map(cat => (
            <button key={cat || "all"} onClick={() => setCategory(cat)}
              className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                category === cat ? "bg-blue-600 text-white" : "glass text-slate-400 hover:text-white"
              }`}>
              {CATEGORY_LABELS[cat]}
            </button>
          ))}
        </div>

        {canCreate && (
          <button onClick={() => setCreating(true)}
            className="flex-shrink-0 flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl transition-colors animate-pulse-glow">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Event
          </button>
        )}
      </div>

      {/* Events grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton rounded-2xl h-52" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-6xl mb-4">🎪</p>
          <p className="text-xl font-semibold text-white mb-2">No events found</p>
          <p className="text-slate-400">Try a different search or category filter</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((event, i) => (
            <div key={event.id} style={{ animationDelay: `${i * 50}ms` }}>
              <EventCard event={event} onClick={() => setSelectedEvent(event)} />
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
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

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <div className="text-center">
        <div className="w-12 h-12 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin mx-auto mb-4" />
        <p className="text-slate-400 text-sm">Loading…</p>
      </div>
    </div>
  );
}
