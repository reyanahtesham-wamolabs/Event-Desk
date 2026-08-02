import React from "react";
import type { Event } from "../lib/api";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

const CATEGORY_ICONS: Record<string, string> = {
  music: "🎵", sports: "⚽", conference: "💼", theater: "🎭", other: "✨",
};

interface Props {
  event: Event;
  onClick: () => void;
  showOrganizer?: boolean;
}

export default function EventCard({ event, onClick }: Props) {
  const available = event.tickets.filter(t => !t.user_id).length;

  return (
    <div
      onClick={onClick}
      className="glass rounded-2xl p-5 card-hover cursor-pointer group border border-white/8 animate-fade-in"
    >
      {/* Category & Status */}
      <div className="flex items-center justify-between mb-3">
        <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium uppercase tracking-widest">
          <span>{CATEGORY_ICONS[event.category] ?? "✨"}</span>
          {event.category}
        </span>
        <span className={`badge badge-${event.status}`}>{event.status}</span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-blue-300 transition-colors line-clamp-2">
        {event.title}
      </h3>

      {/* Description */}
      {event.description && (
        <p className="text-sm text-slate-400 mb-3 line-clamp-2">{event.description}</p>
      )}

      {/* Tags */}
      {event.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {event.tags.slice(0, 3).map(tag => (
            <span key={tag.id} className="px-2 py-0.5 rounded-full bg-white/5 text-slate-400 text-xs">
              #{tag.name}
            </span>
          ))}
          {event.tags.length > 3 && (
            <span className="px-2 py-0.5 rounded-full bg-white/5 text-slate-500 text-xs">+{event.tags.length - 3}</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-white/8">
        <div className="flex items-center gap-1.5 text-sm text-slate-400">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {formatDate(event.event_time)}
        </div>
        <div className="flex items-center gap-1.5 text-sm">
          <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          <span className={available > 0 ? "text-green-400" : "text-red-400"}>
            {available} available
          </span>
        </div>
      </div>
    </div>
  );
}
