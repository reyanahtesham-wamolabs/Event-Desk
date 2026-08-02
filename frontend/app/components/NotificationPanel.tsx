import React, { useEffect, useState, useCallback } from "react";
import { api, type Notification, type NotificationType } from "../lib/api";

const TYPE_CONFIG: Record<string, { label: string; icon: string; cls: string }> = {
  ticket_confirmation: { label: "Booking", icon: "🎟️", cls: "notif-ticket" },
  event_cancelled:    { label: "Cancelled", icon: "❌", cls: "notif-event" },
  event_update:       { label: "Event", icon: "📢", cls: "notif-event" },
  event_reminder:     { label: "Reminder", icon: "⏰", cls: "notif-event" },
  review_reply:       { label: "Reply", icon: "💬", cls: "notif-review" },
  review_mention:     { label: "Mention", icon: "@", cls: "notif-mention" },
};

const ALL_TYPES: (NotificationType | "")[] = [
  "", "ticket_confirmation", "event_cancelled", "event_update", "review_reply", "review_mention"
];

interface Props { open: boolean; onClose: () => void; }

export default function NotificationPanel({ open, onClose }: Props) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<NotificationType | "">("");
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filter) params.type = filter;
      const data = await api.get<Notification[]>("/notifications/my-notifications", params);
      setNotifications(data);
    } catch { /* ignore */ }
    setLoading(false);
  }, [filter]);

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open, fetchNotifications]);

  const markRead = async (id: string) => {
    await api.patch(`/notifications/${id}/read`);
    setNotifications(n => n.map(x => x.id === id ? { ...x, is_read: true } : x));
  };

  const markUnread = async (id: string) => {
    await api.patch(`/notifications/${id}/unread`);
    setNotifications(n => n.map(x => x.id === id ? { ...x, is_read: false } : x));
  };

  const deleteNotif = async (id: string) => {
    await api.delete(`/notifications/${id}`);
    setNotifications(n => n.filter(x => x.id !== id));
  };

  const clearAll = async () => {
    await api.delete("/notifications");
    setNotifications([]);
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />
      <div className="fixed top-16 right-4 z-50 w-96 max-w-[calc(100vw-2rem)] glass-strong rounded-2xl shadow-2xl animate-slide-down overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-white/10 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-white">Notifications</h2>
            {unreadCount > 0 && (
              <p className="text-xs text-blue-400">{unreadCount} unread</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {notifications.length > 0 && (
              <button onClick={clearAll} className="text-xs text-slate-400 hover:text-red-400 transition-colors">
                Clear all
              </button>
            )}
            <button onClick={onClose} className="p-1 text-slate-500 hover:text-white transition-colors rounded-lg hover:bg-white/5">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Filter chips */}
        <div className="px-4 py-2 flex gap-1.5 overflow-x-auto">
          {ALL_TYPES.map(t => (
            <button
              key={t || "all"}
              onClick={() => setFilter(t)}
              className={`flex-shrink-0 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filter === t
                  ? "bg-blue-600 text-white"
                  : "bg-white/5 text-slate-400 hover:bg-white/10"
              }`}
            >
              {t ? (TYPE_CONFIG[t]?.label ?? t) : "All"}
            </button>
          ))}
        </div>

        {/* List */}
        <div className="overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="p-6 text-center text-slate-500 text-sm">Loading…</div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-3xl mb-2">🔔</p>
              <p className="text-slate-400 text-sm">No notifications yet</p>
            </div>
          ) : (
            notifications.map(n => {
              const cfg = TYPE_CONFIG[n.type] ?? { label: n.type, icon: "📌", cls: "notif-ticket" };
              return (
                <div
                  key={n.id}
                  className={`flex gap-3 p-4 border-b border-white/5 transition-colors hover:bg-white/3 ${
                    !n.is_read ? "bg-blue-500/5" : ""
                  }`}
                >
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${cfg.cls}`}>
                    {cfg.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${cfg.cls}`}>{cfg.label}</span>
                      {!n.is_read && <span className="w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />}
                    </div>
                    <p className="text-sm text-slate-300 leading-snug">{n.message}</p>
                  </div>
                  <div className="flex-shrink-0 flex flex-col gap-1">
                    {n.is_read ? (
                      <button onClick={() => markUnread(n.id)} title="Mark unread"
                        className="p-1 text-slate-500 hover:text-blue-400 transition-colors rounded">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8" />
                        </svg>
                      </button>
                    ) : (
                      <button onClick={() => markRead(n.id)} title="Mark read"
                        className="p-1 text-slate-500 hover:text-green-400 transition-colors rounded">
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </button>
                    )}
                    <button onClick={() => deleteNotif(n.id)} title="Delete"
                      className="p-1 text-slate-500 hover:text-red-400 transition-colors rounded">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </>
  );
}
