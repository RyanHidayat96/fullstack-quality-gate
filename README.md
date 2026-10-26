> **Case Study Submission: Fullstack Engineer (SDET Depth)**  
> **Reviewer Tour:** Begin with [Reviewer Start Here](assessment/08-reviewer-start-here.md), then inspect [Platform Audit](assessment/01-audit.md), [Quality System & Red-to-Green](assessment/02-quality-system.md), [Release Decision](assessment/03-release-decision.md), and [Live Defense Guide](assessment/08-live-defense.md).  
> **Workflow Gate Demonstrations:** [PR #1 (Gate Blocked / RED)](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/1) | [PR #2 (Gate Passed / GREEN)](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/2) | [Release Tag v1.0.0 CI Run](https://github.com/RyanHidayat96/fullstack-quality-gate/actions/runs/40277694610).  
> **Current Release Decision:** **BLOCKED / DO NOT SHIP** (fail-closed release gate evaluated via `scripts/release_gate.py`).
> **Current verification:** [Status and known gaps](assessment/09-current-status.md) · [PR #3 expanded test execution](https://github.com/RyanHidayat96/fullstack-quality-gate/pull/3). Phase handoff logs are historical snapshots, not live GitHub status.

---

# Architecture & Specification
Please refer to [Architecture Notes](assessment/architecture-notes.md) and [Audit Findings](assessment/01-audit.md) for platform architecture and specifications.

# The Platform

A two-service application used for the Product Engineer case study. It is provided as a single repository so the whole thing clones, runs, and releases as one unit.

```
.
├── api/    # Backend service (Ruby on Rails, PostgreSQL, Redis/Sidekiq)
└── web/    # Frontend web app (React 18 + TypeScript, Vite, Tailwind)
```

The two services run together: the web app talks to the API over REST and WebSocket.

## Running it locally

Each service has its own setup guide. Run the API first, then the web app pointed at it.

1. **API** — see [`api/README.md`](api/README.md). Rails app; needs Ruby (see `api/.ruby-version`), PostgreSQL, and Redis. It serves on `http://localhost:3001`.
2. **Web** — see [`web/README.md`](web/README.md). Vite app; `npm install`, copy `.env.example` to `.env`, point `VITE_API_BASE_URL` at the API, then `npm run dev`. It serves on `http://localhost:5173`.

## Notes for the case study

- This is the codebase you assess, harden, and release. Treat it as a version about to ship to a client.
- Work in the `/assessment` folder at the repo root for your written deliverables; code changes go in `api/` or `web/`.
- See the case-study brief you were given for what to produce and how it is evaluated.
