# Engineering Notes

_Questions 4 and 8 are left for the two of us to fill in together once we've actually run the
full test suite and hit our first real incident — 4 belongs with the AI layer, and 8 needs a
real war story from whoever hits it first. Everything below is the infra/DevOps half._

## 1. Three things that differ between your laptop and a CI runner

1. **No Docker daemon warm cache.** A CI runner pulls every base image cold every run.
   `backend/Dockerfile` and `frontend/Dockerfile` both order `COPY package.json`/`COPY
   pyproject.toml` before `COPY . .` specifically so the dependency-install layer can still be
   cached between runs even though the runner itself is ephemeral (line: `COPY package.json
   package-lock.json ./` before `RUN npm ci` in `frontend/Dockerfile`).
2. **No local `.env`.** Your laptop has a real `.env` with real values; CI never does. `ci.yml`'s
   `test-backend` job sets `DATABASE_URL`/`REDIS_URL`/`TRIAGE_PROVIDER` directly as job `env:`
   entries instead, pointing at the ephemeral `services:` containers CI spins up for that job.
3. **No GPU, no internet-independent Ollama model cache.** A laptop running `TRIAGE_PROVIDER=ollama`
   has the model already pulled into the `ollama_models` volume; a CI runner starts from nothing
   every time. This is exactly why `ci.yml` pins `TRIAGE_PROVIDER: simulated` for every test job —
   see question 4.

## 2. Where does our pipeline sit on the CI/CD maturity ladder?

We're at **"automated CI with a gated deploy"** — `ci.yml` runs on every PR and blocks merge on
failure (lint, type-check, both test suites, image build, Trivy scan, manifest validation, and a
real Compose integration test), and `cd.yml` only runs after `main` receives a change that has
already passed all of that again. We are not yet at continuous deployment in the strict sense
(deploy-on-every-merge-with-no-human-gate) because `main` requires a PR approval before anything
merges — a human is still in the loop before code ships, just not after.

The next rung up would be **progressive delivery** — canary or blue/green rollout with automated
rollback triggered by real production metrics, rather than our current all-at-once rolling
update. That buys faster, safer releases at the cost of needing real traffic-shaping
infrastructure (a service mesh or an ingress controller with weighted routing) that this
assignment's scope doesn't require.

## 3. The exact line guaranteeing build-once-deploy-many, and what breaks without it

The line is in `docs/adr/0002-frontend-runtime-config.md`'s decision: nginx proxies `/api/` to a
service literally named `backend` (`frontend/nginx.conf`, `location /api/ { proxy_pass
http://backend:8000/api/; }`), so no environment-specific value is baked into the image at build
time. The backend has the equivalent guarantee via `envFrom: configMapRef/secretRef` in
`k8s/base/backend.yaml` — the image itself carries zero configuration.

Without this, the frontend image would need `VITE_API_URL` set at `npm run build` time, meaning a
different image per environment. That breaks the entire premise of `cd.yml`: it builds one image
per commit and the same digest is meant to be promotable through dev → prod. If build-once
weren't true, "the image we tested in CI" and "the image running in prod" could legitimately be
different artifacts, which defeats the point of the SHA-pinning in ADR 0003.

## 5. HPA lag

_TODO: fill in with real numbers after running `load/k6-script.js` against the dev cluster while
watching `kubectl get hpa -n civicpulse -w`. Record: seconds between the ramp starting and CPU
utilization crossing 60%, and seconds between that and a new replica reaching Ready. Attach the
`kubectl get hpa -w` capture and a replicas-vs-load chart per the rubric._

Expected sources of lag, to look for once we have real data: the metrics-server scrape interval,
the HPA controller's own sync period (default 15s), and pod startup time (our `startupProbe` in
`k8s/base/backend.yaml` allows up to 60s before the pod is considered up). The scale-up
`stabilizationWindowSeconds: 0` in `k8s/base/hpa.yaml` means we aren't intentionally adding delay
on the scale-out side — whatever lag we measure is coming from those three sources, not from our
own tuning.

## 6. Why VPA is in Off mode

`k8s/base/vpa.yaml` runs `updateMode: "Off"` — recommend only, never evict or resize
automatically. The comment in that file explains the failure mode: our HPA scales on CPU
*utilization*, which is `usage ÷ request`. If VPA ran in `Auto` mode on the same Deployment, it
would raise `resources.requests.cpu` based on observed usage — which immediately *lowers*
computed utilization for the same real load, which tells the HPA to scale *in*. Fewer pods then
means more load per remaining pod, which pushes VPA to raise the request again, which drops
utilization again... the two controllers chase the same signal in opposite directions and never
settle. Recommender mode plus a human deciding when to actually bump `requests` (informed by
`kubectl describe vpa backend-vpa`) avoids the loop entirely.

## 7. Where does the `internal: true` network leave the LLM-calling service?

`k8s`/Compose both split into two networks (`edge`, `internal`); `internal: true` on the Compose
network (and the Kubernetes equivalent via NetworkPolicy, not yet added — see below) means
nothing on it can reach the public internet, including Groq. Our `backend` service is
deliberately the *only* service that joins both networks (`compose.yaml`, `backend.networks: [edge,
internal]`) — it gets its database/cache access via `internal` and its outbound route to Groq via
`edge`, since `edge` is a normal (non-internal) bridge network with a route out.

One open item, honestly logged rather than fixed: the Kubernetes manifests currently rely on
there being no explicit `NetworkPolicy` blocking egress, so `backend` can already reach Groq by
default. If we wanted the same explicit segmentation on Kubernetes that Compose's `internal: true`
gives us, we'd add a `NetworkPolicy` that denies all egress from `frontend` and allows it from
`backend`, and a second one restricting ingress on `postgres`/`redis` to pods labeled `app:
backend` only. We ran out of assignment scope to add and test that policy — noting it here rather
than silently leaving it out.
