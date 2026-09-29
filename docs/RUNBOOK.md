# Runbook

## Deploy

**Local (Compose):**
```bash
cp .env.example .env
docker compose up --build -d
```

**Kubernetes (dev, k3d/kind):**
```bash
kubectl apply -k k8s/overlays/dev
kubectl rollout status deployment/backend -n civicpulse
```

**Production** happens automatically via `cd.yml` on every push to `main`: it builds and pushes
both images to GHCR tagged with the commit SHA, then applies `k8s/overlays/prod` with that exact
tag against an ephemeral cluster in CI. To deploy to a real cluster, point `kubectl` at it and
run the same `kustomize edit set image ... && kubectl apply -k k8s/overlays/prod` sequence from
`cd.yml`.

## Roll back

Two ways — use the fast one during an incident, the declarative one once things are calm:

1. **Fast (imperative)** — the 3 a.m. answer:
   ```bash
   kubectl rollout undo deployment/backend -n civicpulse
   kubectl rollout undo deployment/frontend -n civicpulse
   ```

2. **Declarative (auditable)** — the correct answer once the fire is out. Find the previous
   commit SHA that was deployed (check the `cd.yml` run history or `git log`), then:
   ```bash
   cd k8s/overlays/prod
   kustomize edit set image \
     ghcr.io/momnakhan24/civicpulse-backend=ghcr.io/momnakhan24/civicpulse-backend:<previous-sha> \
     ghcr.io/momnakhan24/civicpulse-frontend=ghcr.io/momnakhan24/civicpulse-frontend:<previous-sha>
   kubectl apply -k k8s/overlays/prod
   ```
   This leaves the repository's manifests matching what's actually running — the imperative
   rollback doesn't, so follow it up with this once you know which SHA you want to stay on.

## Read logs

All services log JSON to stdout — never to a file.

```bash
# Compose
docker compose logs -f backend

# Kubernetes
kubectl logs -n civicpulse -l app=backend -f
```

Every log line carries a `request_id` (from the `X-Request-ID` header, or generated if absent) —
grep for it to follow one request across the stack. A triage fallback logs one `WARNING` line
with the complaint id, the provider that failed, and the error class.

## When triage starts failing

1. Check `/api/meta/providers` — it lists the active provider and the last 20 triage outcomes
   (provider, latency, fallback y/n).
2. Grep backend logs for `WARNING` + `triage` to see which provider is failing and why (timeout,
   429, malformed JSON).
3. If the LLM provider is rate-limited or down, the system already falls back automatically to
   `RuleBasedTriage` (`triaged_by = "rules:fallback"`) — citizens still get a 201, just a less
   precise triage. This is expected behaviour, not an incident on its own.
4. If fallbacks are happening for every request, check:
   - `GROQ_API_KEY` is valid and not exhausted (check the provider's dashboard/limits page).
   - The provider's status page for an outage.
   - Whether the `internal: true` network change accidentally cut the backend off from the
     internet (see ADR on the AI layer network trade-off).
5. To force a specific provider while debugging, set `TRIAGE_PROVIDER` (`llm | ollama | rules |
   simulated`) and redeploy/restart.

## Health checks quick reference

- `GET /health` — liveness only, never touches the database. A restart loop here means the
  process itself is broken, not the database.
- `GET /ready` — readiness, checks Postgres and Redis. 503 names which dependency failed.
