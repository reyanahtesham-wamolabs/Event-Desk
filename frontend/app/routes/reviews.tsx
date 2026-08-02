import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { api, type Review } from "../lib/api";
import { useAuth } from "../context/AuthContext";

function Stars({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {[1,2,3,4,5].map(i => (
        <span key={i} style={{ color: i <= rating ? "#f59e0b" : "#374151" }}>★</span>
      ))}
    </div>
  );
}

export default function ReviewsPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [editRating, setEditRating] = useState(5);
  const [msg, setMsg] = useState({ text: "", err: false });

  useEffect(() => {
    if (!authLoading && !user) navigate("/auth");
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (user) fetchReviews();
  }, [user]);

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const data = await api.get<Review[]>("/reviews/my-reviews");
      setReviews(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const showMsg = (text: string, err = false) => {
    setMsg({ text, err });
    setTimeout(() => setMsg({ text: "", err: false }), 3000);
  };

  const deleteReview = async (id: string) => {
    if (!confirm("Delete this review?")) return;
    setDeleting(id);
    try {
      await api.delete(`/reviews/${id}`);
      setReviews(prev => prev.filter(r => r.id !== id));
      showMsg("Review deleted.");
    } catch (e: unknown) { showMsg((e as Error).message, true); }
    setDeleting(null);
  };

  const startEdit = (r: Review) => {
    setEditing(r.id);
    setEditText(r.review);
    setEditRating(r.rating);
  };

  const saveEdit = async (id: string) => {
    try {
      const updated = await api.patch<Review>(`/reviews/${id}`, { review: editText, rating: editRating });
      setReviews(prev => prev.map(r => r.id === id ? updated : r));
      setEditing(null);
      showMsg("Review updated!");
    } catch (e: unknown) { showMsg((e as Error).message, true); }
  };

  if (authLoading || loading) return <PageLoader />;
  if (!user) return null;

  const avgRating = reviews.length > 0
    ? (reviews.reduce((a, r) => a + r.rating, 0) / reviews.length).toFixed(1)
    : "—";

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-black text-white">My Reviews</h1>
        <p className="text-slate-400 mt-1">
          {reviews.length} review{reviews.length !== 1 ? "s" : ""} · Avg rating: <span className="text-amber-400 font-semibold">{avgRating}</span>
          {reviews.length > 0 && <span className="text-amber-400"> ★</span>}
        </p>
      </div>

      {msg.text && (
        <div className={`mb-4 px-4 py-3 rounded-xl text-sm font-medium animate-slide-down ${
          msg.err ? "bg-red-500/15 border border-red-500/30 text-red-300" : "bg-green-500/15 border border-green-500/30 text-green-300"
        }`}>
          {msg.text}
        </div>
      )}

      {reviews.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-6xl mb-4">⭐</p>
          <p className="text-xl font-semibold text-white mb-2">No reviews yet</p>
          <p className="text-slate-400 mb-6">Attend events and share your experience</p>
          <button onClick={() => navigate("/")} className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-colors">
            Browse Events
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map(review => (
            <div key={review.id} className="glass rounded-2xl p-5 card-hover border border-white/8 animate-fade-in">
              {editing === review.id ? (
                <div className="space-y-3">
                  {/* Star selector */}
                  <div className="flex gap-1">
                    {[1,2,3,4,5].map(i => (
                      <button key={i} type="button" onClick={() => setEditRating(i)}
                        className="text-2xl transition-colors"
                        style={{ color: i <= editRating ? "#f59e0b" : "#374151" }}>
                        ★
                      </button>
                    ))}
                  </div>
                  <textarea value={editText} onChange={e => setEditText(e.target.value)} rows={3}
                    className="w-full glass border border-white/15 rounded-xl px-4 py-3 text-sm text-slate-200 outline-none focus:border-blue-500 resize-none" />
                  <div className="flex gap-2">
                    <button onClick={() => saveEdit(review.id)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors">
                      Save
                    </button>
                    <button onClick={() => setEditing(null)}
                      className="px-4 py-2 glass hover:bg-white/10 text-slate-300 text-sm font-medium rounded-lg transition-colors">
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-3">
                    <Stars rating={review.rating} />
                    <div className="flex items-center gap-2">
                      <button onClick={() => startEdit(review)}
                        className="p-1.5 text-slate-500 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button onClick={() => deleteReview(review.id)} disabled={deleting === review.id}
                        className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">{review.review}</p>
                  <div className="mt-3 flex items-center gap-3 text-xs text-slate-600">
                    <span className="font-mono">{review.id.slice(0, 8)}…</span>
                    {review.reply_id && (
                      <span className="flex items-center gap-1 text-blue-400/60">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                        </svg>
                        Reply to another review
                      </span>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
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
