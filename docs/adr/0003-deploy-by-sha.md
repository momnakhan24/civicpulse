# 0003 — Deploy by commit SHA, never by `:latest`

## Status
Accepted

## Context
`:latest` is a mutable pointer — it can silently point at a different image tomorrow than it
does today. If a Kubernetes manifest deploys `civicpulse-backend:latest`, "what is production
running?" has no fixed answer: two people applying the same manifest hours apart could deploy
different code without either of them making a change. It also breaks rollback — there's no
previous `:latest` to go back to, only whatever the registry happens to hold now.

## Decision
Every image `cd.yml` builds is tagged with the immutable `${{ github.sha }}` (in addition to a
floating `:latest`, which is pushed for convenience/manual pulls but **never deployed**). The
Kubernetes overlay in `k8s/overlays/prod` starts with a placeholder tag; `cd.yml` runs
`kustomize edit set image <repo>=<repo>:${{ github.sha }}` immediately before `kubectl apply -k`,
so the manifest that actually gets applied always references one specific, reproducible image.

`compose.prod.yaml` follows the same rule: it reads `image: ghcr.io/.../civicpulse-backend:${IMAGE_TAG}`
from the environment, and `IMAGE_TAG` is set to a commit SHA when deploying, never left as
`latest`.

## Consequences
- "What is production running?" always has a one-word answer: `git show <sha>` on the tag that's
  currently deployed.
- Rollback (`docs/RUNBOOK.md`) is well-defined: redeploy the manifest with the previous SHA, and
  you get back exactly the code that was running before, byte for byte.
- Cost: one extra `kustomize edit set image` step in the pipeline, and the small discipline of
  never manually running `kubectl set image ... :latest` by hand during an incident — the
  runbook's imperative rollback path (`kubectl rollout undo`) exists precisely so nobody is
  tempted to do that under pressure.
