import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router";
import { useAuth } from "../context/AuthContext";
import NotificationPanel from "./NotificationPanel";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [notifOpen, setNotifOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/auth");
  };

  const navLinks = [
    { to: "/", label: "Events", show: !!user },
    { to: "/my-tickets", label: "My Tickets", show: !!user },
    { to: "/my-events", label: "My Events", show: user?.role === "organizer" || user?.role === "admin" },
    { to: "/reviews", label: "Reviews", show: !!user },
  ];

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 glass-strong">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 flex-shrink-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm">E</div>
            <span className="font-bold text-white text-lg hidden sm:block">Event<span className="text-blue-400">Desk</span></span>
          </Link>

          {/* Desktop links */}
          {user && (
            <div className="hidden md:flex items-center gap-1">
              {navLinks.filter(l => l.show).map(link => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === link.to
                      ? "bg-blue-600/20 text-blue-400"
                      : "text-slate-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          )}

          {/* Right side */}
          <div className="flex items-center gap-2">
            {user ? (
              <>
                {/* Notifications */}
                <button
                  onClick={() => setNotifOpen(o => !o)}
                  className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                  aria-label="Notifications"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </button>

                {/* User menu */}
                <div className="relative">
                  <button
                    onClick={() => setMenuOpen(o => !o)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors"
                  >
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white text-xs font-bold">
                      {user.name[0].toUpperCase()}
                    </div>
                    <span className="text-sm text-slate-300 hidden sm:block max-w-[100px] truncate">{user.name}</span>
                    <svg className="w-3.5 h-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {menuOpen && (
                    <div className="absolute right-0 top-full mt-2 w-48 glass-strong rounded-xl shadow-xl animate-slide-down z-50">
                      <div className="p-3 border-b border-white/10">
                        <p className="text-sm font-medium text-white truncate">{user.name}</p>
                        <p className="text-xs text-slate-400 truncate">{user.email}</p>
                        <span className="badge badge-published mt-1">{user.role}</span>
                      </div>
                      {navLinks.filter(l => l.show).map(link => (
                        <Link key={link.to} to={link.to} onClick={() => setMenuOpen(false)}
                          className="block px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors first:mt-1">
                          {link.label}
                        </Link>
                      ))}
                      <div className="border-t border-white/10 mt-1 p-1">
                        <button onClick={handleLogout}
                          className="w-full text-left px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors">
                          Sign out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <Link to="/auth" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </nav>

      {/* Click-outside overlay */}
      {menuOpen && <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />}

      {/* Notification panel */}
      <NotificationPanel open={notifOpen} onClose={() => setNotifOpen(false)} />
    </>
  );
}
