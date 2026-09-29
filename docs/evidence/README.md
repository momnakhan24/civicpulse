# Evidence

Drop screenshots and captures here. The rubric expects:

- `branch-protection.png` — GitHub settings showing main protected (PR, CI required, 1 approval)
- `merge-conflict.md` (+ screenshots) — the deliberate conflict, markers, resolution, 2–4 sentences on why that version won
- `red-check-blocked-merge.png` and `green-check.png` — failing test blocking a PR, then fixed
- `hpa-watch.txt` — output of `kubectl get hpa -n civicpulse -w` during the k6 run
- `hpa-scaling-chart.png` — replicas vs offered load over time
- `vpa-recommendation.txt` — output of `kubectl describe vpa backend-vpa -n civicpulse`
- `network-isolation.png` — `docker compose exec frontend ping postgres` failing
- `build-context-sizes.txt` — frontend/backend build-context size before and after `.dockerignore`
- `image-sizes.txt` — `docker images` output for both images
