# Tract — Roadmap

Milestones are ordered so the app is usable at the end of every one. Build on `dev`,
merge to `qa` as a review gate, `prod` deploys.

## M0 — Skeleton (repo becomes runnable)
- Monorepo scaffolding: `frontend/` (Vite + React + TS + Tailwind + tokens),
  `backend/` (FastAPI + SQLAlchemy + Alembic + health route), `workers/` package,
  CI workflow (lint, typecheck, test on PR).
- Supabase project `tract-dev`: schema migration 001 (all tables from
  docs/DATABASE.md), RLS policies, signup trigger → `profiles`.
- Frontend↔backend↔DB hello-world: sign up, sign in, `GET /auth/me`.

## M1 — Portfolio core (the product exists)
- Properties CRUD (all kinds incl. My Home), property detail Overview.
- Transactions CRUD with quick-add + recurring templates.
- Valuations: manual entry + purchase-price baseline.
- Manage layout (sidebar), Owned grid with kind tabs, empty states.

## M2 — Analytics (the product is worth using)
- `services/analytics.py`: cash flow, NOI, cap rate, cash-on-cash, expense
  breakdown, trends (uses .claude/skills/real-estate-finance definitions).
- Summary page with charts; property Analytics tab; My Home cost-of-ownership +
  rent-vs-own.
- Workers + data: `refresh_hpi` (FHFA) and `refresh_fmr` (HUD) jobs, market
  endpoints, HPI-based value estimates, FMR benchmark chips.

## M3 — Messaging + assistant
- Conversations/messages API, RLS, Supabase Realtime subscription.
- Global messaging dock (Chats + Assistant tabs), unread tracking, notifications
  bell.
- Agent StubProvider wired to analytics ("what's my cash flow this month?").
  ClaudeProvider behind flag, off by default.

## M4 — Polish + email + admin + deploy
- Resend integration: `notify_unread` mirroring worker, monthly digest, settings
  opt-outs.
- Settings (account/appearance/notifications), profile page, About page.
- Admin page: users, flags, waitlist. Premium waitlist cards live.
- Deploy: Vercel (frontend), Render (backend), `tract-prod` Supabase project.

## v1.5 — Marketplace (deferred by decision)
- Listings UI (create from a rental property), public browse/search on Home for
  signed-in users, inquiry conversations (`kind='inquiry'`).
- Moderation basics in admin. Revisit RLS for public listing reads.

## Premium prototype (design now, build later — explicitly NOT implemented)
Locked UI + waitlist only. Candidate features, in order of likely value:
1. **Auto-valuation** — monthly RentCast AVM refresh per property (50 free
   calls/mo caps this; real version needs paid tier or BYO key).
2. **Data import** — CSV/bank-export ingestion into transactions.
3. **STR comps** — AirDNA/AirROI-style "what could this earn on Airbnb" benchmark.

## Open items (decisions pending)
- **LICENSE file** — repo is public with no license (= all rights reserved by
  default). Earlier discussion favored an explicit "all rights reserved" notice or
  FSL. Add one before sharing the repo anywhere.
- HUD API key (free registration) needed before M2's `refresh_fmr`.
- Supabase org/project creation (user action, free).
- Resend account + sender domain (user action, free) before M4.
