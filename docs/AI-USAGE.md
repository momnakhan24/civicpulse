# AI usage disclosure

## Tools
- Claude (Anthropic), used by Member 2 in a chat interface.

## What it wrote or shaped
- `frontend/Dockerfile`, `frontend/nginx.conf`, `frontend/.dockerignore`
- `compose.yaml`, `compose.prod.yaml`, root `.env.example`
- `k8s/` base and overlays (Kustomize)
- `.github/workflows/ci.yml`, `cd.yml`, `release.yml`
- `load/k6-script.js`, `scripts/check_submission.py`
- Drafts of `README.md`, `docs/RUNBOOK.md`, `docs/adr/0002-*.md`, `docs/adr/0003-*.md`, and the infrastructure half of `docs/ENGINEERING-NOTES.md`

## What we changed afterwards and why
_Fill this in honestly as you test. Examples of what belongs here: version pins you replaced,
commands that failed on your machine and how you fixed them, manifest values you tuned after the
VPA recommendation, any generated claim you found to be wrong._

## Verification
Everything generated was run/tested by us before submission; anything we could not explain at
viva was rewritten or removed.
