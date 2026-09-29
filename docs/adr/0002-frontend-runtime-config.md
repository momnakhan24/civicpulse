# 0002 — Frontend runtime configuration

## Status
Accepted

## Context
Vite bakes `import.meta.env` values into static JavaScript at build time. If the backend's URL
is baked in at build time, the resulting image is tied to one environment, which breaks
build-once-deploy-many: the same frontend image would need to be rebuilt for dev, staging, and
production instead of just redeployed.

Two options were on the table:
1. Generate a `/config.js` file from environment variables when the container starts, and have
   the frontend read `window.APP_CONFIG.API_URL` at runtime.
2. Proxy `/api` through nginx inside the frontend container, so the frontend never needs an
   absolute backend URL at all — it just calls `/api/...` on its own origin.

## Decision
We chose **option 2: nginx reverse-proxies `/api` to the backend service.**

The frontend's dev server already proxies `/api` to the backend during local development
(`vite.config.ts`), so this keeps dev and production behaviourally identical — no
environment-specific code path to maintain, and no risk of the two drifting apart. `nginx.conf`
proxies `location /api/` to `http://backend:8000/api/` (the Compose/Kubernetes service name),
and the SPA's own routes fall back to `index.html` for client-side routing.

## Consequences
- The frontend image is genuinely environment-agnostic: the exact same image built once in CI
  runs unchanged in `compose.yaml`, `compose.prod.yaml`, and every Kubernetes overlay — the only
  thing that changes between environments is what `backend` resolves to on that network.
- No `/config.js` generation step, no extra container startup logic, no risk of a stale baked-in
  URL if we forget to rebuild.
- Trade-off: the frontend container's nginx must always be able to resolve a service literally
  named `backend`. If we ever needed the frontend to talk to a differently-named backend per
  environment, we'd have to template `nginx.conf` at container start instead — we accepted this
  constraint because our service naming is consistent across all environments.
