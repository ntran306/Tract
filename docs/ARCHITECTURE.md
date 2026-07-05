# Tract — System Architecture

Tract is a real estate portfolio manager: users track properties they own (rentals,
Airbnbs, flips, and their own home), log income/expenses, and get analytics on value,
cash flow, and savings opportunities. A messaging system (user↔user and user↔AI
assistant) is available across the whole app. A public rental marketplace is planned
for v1.5 but designed into the schema now.

## Stack (all free-tier)

| Layer      | Choice                              | Why |
|------------|-------------------------------------|-----|
| Frontend   | React 18 + Vite + TypeScript        | Fast dev loop, typed API layer |
| Styling    | Tailwind CSS v4 + design tokens     | Tokens carry the green/beige theme + dark mode |
| Data fetch | TanStack Query                      | Caching, optimistic updates, request dedupe |
| Routing    | React Router v7                     | Library mode, nested layouts for Manage sidebar |
| Backend    | FastAPI (Python 3.12) + SQLAlchemy 2 + Alembic | All writes, business rules, analytics, AI agent |
| Database   | Supabase Postgres (free tier)       | Postgres + Auth + Realtime + Storage in one free service |
| Auth       | Supabase Auth                       | Email/password now, OAuth later; never hand-roll auth |
| Realtime   | Supabase Realtime (postgres_changes on `messages`) | Live messaging without running WebSockets on a free host that sleeps |
| Email      | Resend free tier (3k/mo)            | Transactional: resets, message mirroring, digests |
| Workers    | Python package run by GitHub Actions cron | Only genuinely free way to run scheduled jobs |
| AI agent   | Pluggable: stub provider (default) / Claude Haiku when key present | No free Anthropic tier; stub answers structured questions from our own analytics service at $0 |
| Frontend hosting | Vercel free                   | Auto-deploy from GitHub, previews per branch |
| Backend hosting  | Render free web service       | Sleeps after ~15 min idle — acceptable for a project; cold start ~30–60s |

## Monorepo layout

One repository (this one). Splitting later is easy; merging repos later is painful.

```
Tract/
├── frontend/            # React app (see docs/FRONTEND.md)
├── backend/             # FastAPI app
│   ├── app/
│   │   ├── main.py
│   │   ├── core/        # config, settings, JWT verification, dependencies
│   │   ├── api/v1/      # routers (one file per resource)
│   │   ├── models/      # SQLAlchemy models — single source of schema truth
│   │   ├── schemas/     # Pydantic request/response models
│   │   ├── services/    # analytics.py, agent.py, email.py, market_data.py
│   │   └── db.py
│   ├── alembic/         # migrations
│   ├── tests/
│   └── pyproject.toml
├── workers/             # background jobs (see "Workers" below)
│   ├── jobs/
│   │   ├── refresh_hpi.py      # quarterly — FHFA HPI CSV → market_hpi
│   │   ├── refresh_fmr.py      # yearly — HUD FMR API → market_fmr
│   │   ├── notify_unread.py    # every 15 min — email-mirror unread messages
│   │   └── send_digests.py     # monthly portfolio digest
│   └── pyproject.toml   # installs backend as editable dep to reuse models
├── docs/                # this folder — architecture, schema, roadmap, decisions
├── .github/workflows/   # ci.yml (lint/typecheck/test), cron-*.yml (workers)
└── .claude/skills/      # project-scoped Claude skills incl. real-estate-finance
```

## Data flow rules

These are the load-bearing conventions — do not drift from them:

1. **All writes go through FastAPI.** The frontend never inserts/updates Supabase
   tables directly. Validation, business rules, and side effects (notifications,
   emails) live in one place.
2. **Reads:** analytics and lists come from FastAPI. The frontend talks to Supabase
   directly for exactly two things: **auth** (Supabase JS handles sessions) and
   **realtime subscriptions** on `messages`/`notifications` (receiving only).
3. **Row Level Security is ON** for every table even though writes go through the
   API — it's the safety net that makes the realtime read path safe. Policies:
   owners see their own rows; conversation participants see their conversations;
   service role (backend) bypasses.
4. **Workers never serve requests.** They are scheduled scripts that read/write the
   DB and send email. Anything request/response-shaped belongs in FastAPI.
5. **Money is `numeric(12,2)`, USD only in v1.** No floats, ever.

## Auth flow

1. Frontend signs in via Supabase JS → gets a JWT (auto-refreshed).
2. Every FastAPI request carries `Authorization: Bearer <jwt>`.
3. FastAPI dependency verifies the JWT signature (Supabase JWT secret) and loads the
   `profiles` row; `role = 'admin'` gates `/api/v1/admin/*`.
4. Two roles only: `user` and `admin`. Admin is for devs — no granular permissions.

## API surface (v1)

```
/api/v1/auth/me                      GET
/api/v1/properties                   GET POST        /{id} GET PATCH DELETE
/api/v1/properties/{id}/valuations   GET POST
/api/v1/properties/{id}/lease        GET PUT DELETE
/api/v1/transactions                 GET POST        /{id} PATCH DELETE   (?property_id=, ?from=, ?to=)
/api/v1/analytics/portfolio          GET             summary page payload
/api/v1/analytics/property/{id}      GET             per-property analytics
/api/v1/analytics/my-home            GET             rent-vs-own, cost of ownership
/api/v1/market/fmr                   GET             ?zip= or ?area= — HUD fair market rent
/api/v1/market/hpi                   GET             ?state= — index series + appreciation factor
/api/v1/conversations                GET POST        /{id}/messages GET POST
/api/v1/agent/message                POST            AI assistant (stub or Claude)
/api/v1/notifications                GET             /{id}/read POST
/api/v1/premium/waitlist             POST            join waitlist for a premium feature
/api/v1/admin/users                  GET             /admin/flags GET PUT   /admin/waitlist GET
```

## Messaging & AI agent

- A conversation has `kind`: `dm` (user↔user), `agent` (user↔assistant), or
  `inquiry` (v1.5, attached to a listing).
- Sending: POST to FastAPI → insert message → Supabase Realtime pushes the insert to
  subscribed participants. Receiving requires no polling.
- The messaging dock is a global overlay (not a route) rendered in the root layout,
  so it persists across every tab. The AI assistant is a pinned conversation inside
  the same dock.
- Agent providers behind one interface in `services/agent.py`:
  - **StubProvider (default):** pattern-matches structured questions ("what's my
    cash flow this month", "which property costs me the most") and answers by
    calling the analytics service directly. Deterministic, free, honest.
  - **ClaudeProvider:** Claude Haiku with tool-use over the same analytics
    functions. Enabled only when `ANTHROPIC_API_KEY` is set. Costs real money
    (fractions of a cent per message) — feature-flagged via `app_settings`.

## Email ("in-app emailing")

Scope decision (see DECISIONS.md): transactional + mirroring, not an email client.
- Password reset / verification: Supabase Auth's built-in emails.
- Message mirroring: `notify_unread` worker emails users who have unread messages
  older than ~15 min and haven't been active. Per-user opt-out in settings.
- Monthly digest: portfolio snapshot email. Opt-in.
- All app-sent email goes through one `services/email.py` wrapper around Resend.

## Free data sources (legal, keyless or free-key)

| Source | What | Cadence | Used for |
|--------|------|---------|----------|
| FHFA House Price Index (CSV download, no key) | Price index by state/metro since 1975 | Quarterly | **HPI-based value estimate:** `purchase_price × (HPI_now / HPI_at_purchase)` — labeled as an index estimate, not an appraisal |
| HUD Fair Market Rents API (free key) | FMR by area + bedroom count | Yearly | "Your rent vs. area FMR" benchmark on rentals and My Home |
| RentCast (50 free calls/mo) | Per-address AVM + rent estimate | On demand | Reserved for the **premium prototype** — not wired into v1 flows |

Everything else (actual rents received, Airbnb payouts, expenses, mortgage details,
current value if the user knows better) is **manual entry by design** — that is the
product's honest v1 contract. Zillow has no public API and prohibits scraping; we do
not scrape anyone.

## Environments & deployment

Branches: `feature/* → dev → qa → prod` (already created).

| Env | Frontend | Backend | Database |
|-----|----------|---------|----------|
| dev | Vercel preview deploys (every push to dev) | Run locally (`uvicorn`) | Supabase project `tract-dev` |
| qa  | Vercel preview on qa branch | Same Render service as prod, or local | `tract-dev` (shared) |
| prod| Vercel production (prod branch) | Render free web service (prod branch) | Supabase project `tract-prod` (create when first deploying prod) |

Free-tier honesty: there is one free Render instance, so qa does not get its own
backend. QA is a merge gate (CI + review), not a separate infrastructure tier, until
the project outgrows free hosting.

CI (GitHub Actions on every PR): ruff + pyright on backend/workers, eslint + tsc on
frontend, pytest + vitest. Cron workflows run workers on schedule with
`DATABASE_URL` and `RESEND_API_KEY` as repo secrets.

## Non-goals for v1 (explicit)

- No public marketplace/browse (v1.5 — schema exists, UI doesn't).
- No payments/subscriptions — premium is a waitlist prototype only.
- No document/receipt uploads (needs storage rules — later).
- No multi-currency, no i18n.
- No mobile app; responsive web only.
- No scraping of any site, period.
