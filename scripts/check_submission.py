#!/usr/bin/env python3
"""Lint for the mechanical failures behind most automatic deductions.

Run from the repository root:  python scripts/check_submission.py
It is a lint, not a grader.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems: list[str] = []
warnings: list[str] = []


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def yaml_files() -> list[Path]:
    return [
        p for p in ROOT.rglob("*")
        if p.suffix in {".yml", ".yaml"} and ".git" not in p.parts and "node_modules" not in p.parts
    ]


# --- required files ---------------------------------------------------------
required = [
    "README.md", "LICENSE", ".gitignore", ".env.example", "compose.yaml", "compose.prod.yaml",
    "backend/Dockerfile", "backend/.dockerignore", "frontend/Dockerfile", "frontend/.dockerignore",
    "frontend/nginx.conf", "k8s/base/kustomization.yaml", "k8s/overlays/dev/kustomization.yaml",
    "k8s/overlays/prod/kustomization.yaml", "load/k6-script.js", "docs/RUNBOOK.md",
    "docs/ENGINEERING-NOTES.md", "docs/AI-USAGE.md",
    ".github/workflows/ci.yml", ".github/workflows/cd.yml", ".github/workflows/release.yml",
]
for f in required:
    if not (ROOT / f).exists():
        problems.append(f"missing required file: {f}")
for n in range(1, 5):
    if not list((ROOT / "docs" / "adr").glob(f"000{n}-*.md")):
        problems.append(f"missing ADR 000{n}-*.md in docs/adr/")

# --- secrets in tracked files ----------------------------------------------
if (ROOT / ".git").exists():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for t in tracked:
        name = Path(t).name
        if name == ".env" or (name.startswith(".env.") and name != ".env.example") or name.endswith((".pem", ".key")):
            problems.append(f"secret-looking file is tracked by git: {t} (-20, rotate the credential)")
    hist = subprocess.run(
        ["git", "log", "--all", "--name-only", "--pretty=format:"], cwd=ROOT, capture_output=True, text=True
    ).stdout.split()
    for h in set(hist):
        if Path(h).name == ".env":
            problems.append(f".env exists in git history: {h} (-20, rotate + write an incident note)")
key_re = re.compile(r"(gsk_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{30,}|sk-[A-Za-z0-9]{20,})")
for p in ROOT.rglob("*"):
    if ".git" not in p.parts and "node_modules" not in p.parts and p.suffix not in {".png", ".jpg", ".zip", ".lock"} and p.is_file():
        if key_re.search(read(p)):
            problems.append(f"possible API key committed in {p.relative_to(ROOT)}")

gi = read(ROOT / ".gitignore")
if not re.search(r"^\.env\s*$", gi, re.M):
    problems.append(".gitignore does not ignore .env")

# --- Dockerfiles ------------------------------------------------------------
for df in ["backend/Dockerfile", "frontend/Dockerfile"]:
    s = read(ROOT / df)
    if not s:
        continue
    if not re.search(r"^USER\s+(?!root)", s, re.M):
        problems.append(f"{df}: no non-root USER")
    if "HEALTHCHECK" not in s:
        problems.append(f"{df}: no HEALTHCHECK")
    if len(re.findall(r"^FROM\s", s, re.M)) < 2:
        problems.append(f"{df}: not multi-stage")
    for m in re.finditer(r"^FROM\s+(\S+)", s, re.M):
        img = m.group(1)
        if img.lower() == "scratch" or "$" in img:
            continue
        if ":" not in img and "@sha256" not in img:
            problems.append(f"{df}: unpinned base image '{img}' (-8)")
        if img.endswith(":latest"):
            problems.append(f"{df}: base image uses :latest (-8)")
    cmd = re.findall(r"^CMD\s+(.*)$", s, re.M)
    if cmd and not cmd[-1].strip().startswith("["):
        problems.append(f"{df}: CMD is not exec form")

# --- compose ----------------------------------------------------------------
dev = read(ROOT / "compose.yaml")
prod = read(ROOT / "compose.prod.yaml")
for name, s in [("compose.yaml", dev), ("compose.prod.yaml", prod)]:
    for m in re.finditer(r"image:\s*(\S+)", s):
        img = m.group(1)
        if "${" in img:
            continue
        if ":" not in img or img.endswith(":latest"):
            problems.append(f"{name}: unpinned image '{img}' (-8)")
    if "internal: true" not in s:
        problems.append(f"{name}: no network with internal: true")
if re.search(r"^\s*build:", prod, re.M):
    problems.append("compose.prod.yaml must not contain build:")
if "${IMAGE_TAG}" not in prod:
    problems.append("compose.prod.yaml should use image: ...:${IMAGE_TAG}")
# published ports on postgres/redis in prod
for svc in ("postgres", "redis"):
    m = re.search(rf"^  {svc}:\n(.*?)(?=^  \S|\Z)", prod, re.M | re.S)
    if m and re.search(r"^\s*ports:", m.group(1), re.M):
        problems.append(f"compose.prod.yaml publishes a port on {svc} (-8)")

# --- kubernetes -------------------------------------------------------------
for p in (ROOT / "k8s").rglob("*.yaml"):
    s = read(p)
    if re.search(r"image:\s*\S+:latest\b", s):
        problems.append(f"{p.relative_to(ROOT)}: deploys :latest (-8)")
    if "kind: Deployment" in s and re.search(r"name:\s*postgres\b", s) and "kind: StatefulSet" not in s:
        problems.append(f"{p.relative_to(ROOT)}: postgres as a Deployment (-8)")
    if re.search(r"type:\s*(NodePort|LoadBalancer)", s) and "postgres" in s:
        problems.append(f"{p.relative_to(ROOT)}: NodePort/LoadBalancer near postgres (-8)")
    if "kind: Secret" in s:
        for m in re.finditer(r"^\s+(GROQ_API_KEY|POSTGRES_PASSWORD):\s*\"?([^\"\n]+)", s, re.M):
            if m.group(2).strip() not in {"changeme", "placeholder", "CHANGE_ME"}:
                problems.append(f"{p.relative_to(ROOT)}: Secret value for {m.group(1)} is not a placeholder (-15)")
        if re.search(r"^data:", s, re.M):
            warnings.append(f"{p.relative_to(ROOT)}: Secret uses base64 'data:'; base64 is not encryption")
base_dep = read(ROOT / "k8s/base/backend.yaml")
if "requests:" not in base_dep:
    problems.append("k8s/base/backend.yaml: no resources.requests (HPA will show <unknown>)")
for probe in ("startupProbe", "livenessProbe", "readinessProbe"):
    if probe not in base_dep:
        problems.append(f"k8s/base/backend.yaml: missing {probe}")

# --- workflows --------------------------------------------------------------
for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
    s = read(wf)
    if not re.search(r"^permissions:", s, re.M):
        problems.append(f"{wf.name}: no top-level permissions: block")
    if wf.name in {"cd.yml", "release.yml"}:
        if ":latest" in s and "kubectl" in s and re.search(r"apply.*latest", s):
            problems.append(f"{wf.name}: appears to deploy :latest (-8)")
    for job in re.finditer(r"^  (build-push|deploy-k8s|build-push-release):\n(.*?)(?=^  \S|\Z)", s, re.M | re.S):
        if wf.name == "cd.yml" and "needs:" not in job.group(2):
            problems.append(f"{wf.name}: job {job.group(1)} has no needs: (-8)")
    for m in re.finditer(r"uses:\s*(\S+)@(\S+)", s):
        if m.group(2) in {"master", "main"} and not m.group(1).startswith("./"):
            warnings.append(f"{wf.name}: action {m.group(1)} pinned to a branch")

# --- localhost service-to-service ------------------------------------------
for p in [ROOT / "compose.yaml", ROOT / "compose.prod.yaml", ROOT / ".env.example", *(ROOT / "k8s").rglob("*.yaml")]:
    for i, line in enumerate(read(p).splitlines(), 1):
        if re.search(r"(localhost|127\.0\.0\.1)", line) and not line.strip().startswith("#"):
            if re.search(r"(URL|HOST|proxy_pass)", line):
                problems.append(f"{p.relative_to(ROOT)}:{i}: localhost used for service-to-service (-8)")

# --- report -----------------------------------------------------------------
for w in warnings:
    print(f"WARN  {w}")
for pr in problems:
    print(f"FAIL  {pr}")
print(f"\n{len(problems)} problem(s), {len(warnings)} warning(s)")
sys.exit(1 if problems else 0)
