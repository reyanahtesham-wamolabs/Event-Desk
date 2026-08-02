import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/events.tsx"),
  route("auth", "routes/auth.tsx"),
  route("my-tickets", "routes/my-tickets.tsx"),
  route("my-events", "routes/my-events.tsx"),
  route("reviews", "routes/reviews.tsx"),
] satisfies RouteConfig;
