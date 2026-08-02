import React, { useState, useEffect, useCallback } from "react";
import { api, type Event, type Review, type Ticket, type TicketTier } from "../lib/api";
import { useAuth } from "../context/AuthContext";

interface Props { event: Event; onClose: () => void; onUpdate: () => void; }

function Stars({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {[1,2,3,4,5].map(i => (
        <span key={i} className={i <= rating ? "star-filled" : "star-empty"}>★</span>
      ))}
    </div>
  );
}

function SelectStars({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  const [hover, setHover] = useState(0);
  return (
    <div className="flex gap-1">
      {[1,2,3,4,5].map(i => (
        <button key={i} type="button"
          onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(0)}
          onClick={() => onChange(i)}
          className="text-2xl transition-colors"
          style={{ color: i <= (hover || value) ? "#f59e0b" : "#374151" }}>
          ★
        </button>
      ))}
    </div>
  );
}

const TIER_CONFIG: Record<TicketTier, { label: string; cls: string }> = {
  gold: { label: "🥇 Gold", cls: "badge-gold" },
  silver: { label: "🥈 Silver", cls: "badge-silver" },
  bronze: { label: "🥉 Bronze", cls: "badge-bronze" },
};

export default function EventModal({ event: initialEvent, onClose, onUpdate }: Props) {
  const { user } = useAuth();
  const [event, setEvent] = useState(initialEvent);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [tab, setTab] = useState<"info" | "tickets" | "reviews">("info");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Review form
  const [reviewText, setReviewText] = useState("");
  const [rating, setRating] = useState(5);
  const [replyTo, setReplyTo] = useState<Review | null>(null);
  const [replyText, setReplyText] = useState("");

  // Edit form
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(event.title);
  const [editDesc, setEditDesc] = useState(event.description ?? "");

  const canManage = user && (user.id === event.organizer_id || user.role === "admin");
  const canBook = user?.role === "attendee" || user?.role === "admin";

  const loadReviews = useCallback(async () => {
    try {
      const data = await api.get<Review[]>(`/events/${event.id}/reviews`);
      setReviews(data);
    } catch { /* ignore */ }
  }, [event.id]);

  const refreshEvent = useCallback(async () => {
    try {
      const e = await api.get<Event>(`/events/${event.id}`);
      setEvent(e);
    } catch { /* ignore */ }
  }, [event.id]);

  useEffect(() => {
    if (tab === "reviews") loadReviews();
  }, [tab, loadReviews]);

  const showMsg = (msg: string, isError = false) => {
    if (isError) setError(msg); else setSuccess(msg);
    setTimeout(() => { setError(""); setSuccess(""); }, 3500);
  };

  const purchaseTier = async (tier: TicketTier) => {
    setLoading(true);
    try {
      await api.post(`/events/${event.id}/purchase-any`, { tier });
      showMsg("🎟️ Ticket booked! You'll receive a confirmation notification.");
      await refreshEvent();
      onUpdate();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const purchaseSpecific = async (ticketId: string) => {
    setLoading(true);
    try {
      await api.post(`/tickets/${ticketId}/purchase`);
      showMsg("🎟️ Seat reserved successfully!");
      await refreshEvent();
      onUpdate();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const publishEvent = async () => {
    setLoading(true);
    try {
      await api.post(`/events/${event.id}/publish`);
      showMsg("Event published!");
      await refreshEvent();
      onUpdate();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const cancelEvent = async () => {
    if (!confirm("Cancel this event? All ticket holders will be notified.")) return;
    setLoading(true);
    try {
      await api.post(`/events/${event.id}/cancel`);
      showMsg("Event cancelled. Notifications sent to ticket holders.");
      await refreshEvent();
      onUpdate();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const saveEdit = async () => {
    setLoading(true);
    try {
      await api.patch(`/events/${event.id}`, { title: editTitle, description: editDesc });
      setEditing(false);
      showMsg("Event updated!");
      await refreshEvent();
      onUpdate();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const submitReview = async () => {
    if (!reviewText.trim()) return;
    setLoading(true);
    try {
      await api.post(`/events/${event.id}/reviews`, { review: reviewText, rating });
      setReviewText(""); setRating(5);
      showMsg("Review submitted! Use @username to mention others.");
      await loadReviews();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const submitReply = async () => {
    if (!replyText.trim() || !replyTo) return;
    setLoading(true);
    try {
      await api.post(`/reviews/${replyTo.id}/reply`, { review: replyText });
      setReplyText(""); setReplyTo(null);
      showMsg("Reply posted!");
      await loadReviews();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  const deleteEvent = async () => {
    if (!confirm("Permanently delete this event?")) return;
    setLoading(true);
    try {
      await api.delete(`/events/${event.id}`);
      onUpdate(); onClose();
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setLoading(false);
  };

  // Group tickets by tier
  const byTier = event.tickets.reduce<Record<TicketTier, Ticket[]>>(
    (acc, t) => { (acc[t.ticket_tier] = acc[t.ticket_tier] || []).push(t); return acc; },
    {} as Record<TicketTier, Ticket[]>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto glass-strong rounded-2xl shadow-2xl animate-fade-in">
        {/* Header */}
        <div className="sticky top-0 glass-strong z-10 px-6 py-4 flex items-start justify-between border-b border-white/10">
          <div className="flex-1 mr-4">
            {editing ? (
              <input value={editTitle} onChange={e => setEditTitle(e.target.value)}
                className="w-full bg-white/5 border border-white/20 rounded-lg px-3 py-1.5 text-white text-xl font-bold outline-none focus:border-blue-500" />
            ) : (
              <h2 className="text-xl font-bold text-white leading-tight">{event.title}</h2>
            )}
            <div className="flex items-center gap-2 mt-1">
              <span className={`badge badge-${event.status}`}>{event.status}</span>
              <span className="text-xs text-slate-400 capitalize">{event.category}</span>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-slate-500 hover:text-white hover:bg-white/10 rounded-lg transition-colors flex-shrink-0">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Alert messages */}
        {(error || success) && (
          <div className={`mx-6 mt-4 px-4 py-3 rounded-xl text-sm font-medium animate-slide-down ${
            error ? "bg-red-500/15 border border-red-500/30 text-red-300" : "bg-green-500/15 border border-green-500/30 text-green-300"
          }`}>
            {error || success}
          </div>
        )}

        {/* Manager actions */}
        {canManage && (
          <div className="px-6 pt-4 flex flex-wrap gap-2">
            {event.status === "draft" && (
              <button onClick={publishEvent} disabled={loading}
                className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50">
                Publish Event
              </button>
            )}
            {event.status === "published" && (
              <button onClick={cancelEvent} disabled={loading}
                className="px-4 py-2 bg-red-600/80 hover:bg-red-600 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50">
                Cancel Event
              </button>
            )}
            {!editing ? (
              <button onClick={() => setEditing(true)}
                className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white text-sm font-medium rounded-lg transition-colors">
                Edit
              </button>
            ) : (
              <>
                <button onClick={saveEdit} disabled={loading}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50">
                  Save
                </button>
                <button onClick={() => setEditing(false)}
                  className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white text-sm font-medium rounded-lg transition-colors">
                  Cancel
                </button>
              </>
            )}
            <button onClick={deleteEvent} disabled={loading}
              className="px-4 py-2 bg-red-900/40 hover:bg-red-900/70 text-red-300 text-sm font-medium rounded-lg transition-colors disabled:opacity-50">
              Delete
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="px-6 pt-4 flex gap-1 border-b border-white/10 pb-0">
          {(["info", "tickets", "reviews"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
                tab === t ? "border-blue-500 text-blue-400" : "border-transparent text-slate-400 hover:text-white"
              }`}>
              {t}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Info Tab */}
          {tab === "info" && (
            <div className="space-y-4 animate-fade-in">
              {editing ? (
                <textarea value={editDesc} onChange={e => setEditDesc(e.target.value)} rows={4}
                  className="w-full bg-white/5 border border-white/20 rounded-xl px-4 py-3 text-slate-200 text-sm outline-none focus:border-blue-500 resize-none" />
              ) : (
                event.description && <p className="text-slate-300 text-sm leading-relaxed">{event.description}</p>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div className="glass rounded-xl p-4">
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Date & Time</p>
                  <p className="text-white font-medium text-sm">
                    {new Date(event.event_time).toLocaleDateString("en-US", {
                      weekday: "long", year: "numeric", month: "long", day: "numeric",
                    })}
                  </p>
                  <p className="text-slate-400 text-sm">
                    {new Date(event.event_time).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                  </p>
                </div>
                <div className="glass rounded-xl p-4">
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Total Tickets</p>
                  <p className="text-2xl font-bold text-white">{event.total_tickets}</p>
                  <p className="text-sm text-green-400">{event.tickets.filter(t => !t.user_id).length} available</p>
                </div>
              </div>

              {event.tags.length > 0 && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Tags</p>
                  <div className="flex flex-wrap gap-2">
                    {event.tags.map(t => (
                      <span key={t.id} className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs">
                        #{t.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tickets Tab */}
          {tab === "tickets" && (
            <div className="space-y-4 animate-fade-in">
              {(["gold", "silver", "bronze"] as TicketTier[]).map(tier => {
                const tierTickets = byTier[tier] ?? [];
                const available = tierTickets.filter(t => !t.user_id);
                if (!tierTickets.length) return null;
                const cfg = TIER_CONFIG[tier];
                const samplePrice = tierTickets[0]?.price ?? 0;
                return (
                  <div key={tier} className="glass rounded-xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className={`badge ${cfg.cls}`}>{cfg.label}</span>
                        <span className="text-slate-400 text-sm">${samplePrice}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-slate-400">{available.length}/{tierTickets.length} available</span>
                        {canBook && event.status === "published" && available.length > 0 && (
                          <button onClick={() => purchaseTier(tier)} disabled={loading}
                            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition-colors disabled:opacity-50">
                            Book Any
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Individual seats */}
                    <div className="grid grid-cols-5 gap-1.5">
                      {tierTickets.map(t => (
                        <button
                          key={t.id}
                          disabled={!!t.user_id || !canBook || event.status !== "published" || loading}
                          onClick={() => purchaseSpecific(t.id)}
                          title={t.user_id ? "Taken" : `Seat ${t.seat_num} — $${t.price}`}
                          className={`p-2 rounded-lg text-xs font-medium transition-all ${
                            t.user_id
                              ? "bg-white/5 text-slate-600 cursor-not-allowed"
                              : "bg-blue-500/15 text-blue-400 hover:bg-blue-500/30 hover:scale-105 cursor-pointer"
                          }`}
                        >
                          {t.seat_num}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
              {event.tickets.length === 0 && (
                <p className="text-center text-slate-500 py-8">No tickets created yet.</p>
              )}
            </div>
          )}

          {/* Reviews Tab */}
          {tab === "reviews" && (
            <div className="space-y-4 animate-fade-in">
              {/* Submit review */}
              {canBook && event.status !== "draft" && (
                <div className="glass rounded-xl p-4">
                  <p className="text-sm font-medium text-white mb-3">Leave a Review</p>
                  <p className="text-xs text-slate-500 mb-2">Tip: Use @username to mention someone</p>
                  <SelectStars value={rating} onChange={setRating} />
                  <textarea value={reviewText} onChange={e => setReviewText(e.target.value)}
                    placeholder="Share your experience… @mention users with @username"
                    rows={3} className="mt-3 w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-sm text-slate-200 outline-none focus:border-blue-500 resize-none" />
                  <button onClick={submitReview} disabled={loading || !reviewText.trim()}
                    className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50">
                    Submit Review
                  </button>
                </div>
              )}

              {/* Reviews list */}
              {reviews.length === 0 ? (
                <p className="text-center text-slate-500 py-8">No reviews yet. Be the first!</p>
              ) : (
                reviews.map(r => (
                  <div key={r.id} className="glass rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Stars rating={r.rating} />
                      {canManage && (
                        <button onClick={() => setReplyTo(replyTo?.id === r.id ? null : r)}
                          className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                          {replyTo?.id === r.id ? "Cancel" : "Reply"}
                        </button>
                      )}
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed">{r.review}</p>
                    {replyTo?.id === r.id && (
                      <div className="mt-3 flex gap-2">
                        <input value={replyText} onChange={e => setReplyText(e.target.value)}
                          placeholder="Write a reply… @mention users"
                          className="flex-1 bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-blue-500" />
                        <button onClick={submitReply} disabled={loading}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition-colors disabled:opacity-50">
                          Reply
                        </button>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
