import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";
import type { Route } from "./+types/root";
import "./app.css";
import Navbar from "./components/Navbar";
import { AuthProvider } from "./context/AuthContext";

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>EventDesk — Discover & Manage Events</title>
        <meta name="description" content="Discover amazing events, book tickets, leave reviews, and stay notified." />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen" style={{ background: "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,94,242,0.15), transparent), #09090f" }}>
        <Navbar />
        <main className="pt-16">
          <Outlet />
        </main>
      </div>
    </AuthProvider>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "Oops!";
  let details = "An unexpected error occurred.";

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? "404" : "Error";
    details = error.status === 404 ? "The requested page could not be found." : error.statusText || details;
  } else if (import.meta.env.DEV && error instanceof Error) {
    details = error.message;
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4" style={{ background: "#09090f" }}>
      <div className="text-center">
        <h1 className="text-6xl font-black text-white mb-4">{message}</h1>
        <p className="text-slate-400 mb-8">{details}</p>
        <a href="/" className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-colors">
          Go Home
        </a>
      </div>
    </main>
  );
}
