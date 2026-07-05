# Tract

A real estate portfolio manager: track your properties (rentals, Airbnbs, flips,
and your own home), log income and expenses, and understand your cash flow, value,
and savings opportunities — with in-app messaging and an AI assistant.

**Status:** planning complete, build starting. See the docs:

- [Architecture & system design](docs/ARCHITECTURE.md) — stack, monorepo layout, data flow, deployment
- [Database schema](docs/DATABASE.md) — PostgreSQL/Supabase tables, enums, RLS
- [Frontend plan](docs/FRONTEND.md) — routes, components, design system (green/beige + dark mode)
- [Roadmap](docs/ROADMAP.md) — milestones M0–M4, v1.5 marketplace, premium prototype
- [Playbook](docs/PLAYBOOK.md) — change pipeline, per-phase user actions, ops habits
- [Backlog](docs/BACKLOG.md) — prioritized future work: requests board, media, payments
- [Decision log](docs/DECISIONS.md) — why things are the way they are

## Stack

React + Vite + TypeScript · FastAPI · Supabase (Postgres/Auth/Realtime) ·
GitHub Actions cron workers · Resend — all free-tier.

## Repo layout

```
frontend/   React app
backend/    FastAPI API (all writes, analytics, AI assistant)
workers/    Scheduled jobs (FHFA/HUD data refresh, email)
docs/       Planning & architecture docs
```

Branches: `dev` (work happens here) → `qa` (review gate) → `prod` (deploys).
