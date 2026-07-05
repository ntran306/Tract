# Tract — Implementation Spec

The concrete build sheet: exact packages, exact files, exact wiring. Companion to
ARCHITECTURE.md (why) and DATABASE.md (schema). Covers M0–M2; M3/M4 files are
listed where they're already known.

## Prerequisites (user, one-time, all free)

- Node 22+, Python 3.12, git (all present on this machine).
- Supabase account → create project **tract-dev** → collect from dashboard:
  - `Project URL` and `anon` key (Settings → API) → frontend env
  - DB connection string, **Session pooler, port 5432** (Connect → Session mode)
    → backend/workers env. (Transaction pooler :6543 breaks Alembic — don't use it
    for migrations.)
  - JWT verification: new projects use signing keys — JWKS lives at
    `<PROJECT_URL>/auth/v1/.well-known/jwks.json`. (Legacy projects: HS256 secret.)
- Later: HUD API token (M2, free), Resend API key (M4, free).

---

## Frontend

### Create + install

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm i react-router-dom@^7 @tanstack/react-query@^5 @supabase/supabase-js@^2 \
      zustand@^5 recharts@^3 date-fns@^4 clsx tailwind-merge
npm i @radix-ui/react-dropdown-menu @radix-ui/react-dialog @radix-ui/react-tabs \
      @radix-ui/react-avatar @radix-ui/react-tooltip
npm i @fontsource-variable/inter @fontsource-variable/schibsted-grotesk
npm i -D tailwindcss@^4 @tailwindcss/vite vitest jsdom \
      @testing-library/react @testing-library/jest-dom
```

`vite.config.ts`: plugins `[react(), tailwindcss()]`. No dev proxy — the app calls
`VITE_API_URL` directly; CORS is handled by the backend.

### `frontend/.env.example`

```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

### Files (M0–M3)

```
src/
├── main.tsx                     # imports fonts, globals.css, mounts <App/>
├── app/
│   ├── router.tsx               # createBrowserRouter — table below
│   ├── providers.tsx            # QueryClientProvider + MessagingProvider + Theme
│   └── layouts/
│       ├── RootLayout.tsx       # Header + <Outlet/> + <MessagingDock/> (dock lives HERE → persists across tabs)
│       └── ManageLayout.tsx     # Sidebar (Summary / Owned kinds) + <Outlet/>
├── styles/
│   ├── tokens.css               # both themes, values in docs/FRONTEND.md
│   └── globals.css              # @import tailwindcss; base styles, focus ring
├── lib/
│   ├── supabase.ts              # createClient(URL, ANON_KEY)
│   ├── api.ts                   # typed fetch wrapper: baseURL=VITE_API_URL, attaches
│   │                            #   session.access_token as Bearer, throws ApiError
│   └── format.ts                # money(), pct(), dateShort() — all display formatting
├── types/api.ts                 # TS mirrors of backend Pydantic schemas (by hand)
├── components/
│   ├── ui/                      # Button, Card, Input, Select, Dialog, Tabs, Badge, Stat
│   └── shared/                  # Header, Sidebar, EmptyState, MoneyText, TrendChip
├── features/
│   ├── auth/                    # SignInPage, SignUpPage, useSession, RequireAuth, RequireAdmin
│   ├── portfolio/
│   │   ├── summary/SummaryPage.tsx          # + ValueChart, CashFlowChart, InsightsList
│   │   ├── owned/OwnedPage.tsx              # + PropertyCard, PropertyFormDialog, KindTabs
│   │   ├── property/PropertyDetailPage.tsx  # + OverviewTab, TransactionsTab, AnalyticsTab, LeaseTab
│   │   ├── premium/PremiumCard.tsx          # locked card + waitlist POST
│   │   └── queries.ts                       # useProperties, usePortfolioSummary, ... (TanStack)
│   ├── messaging/               # MessagingProvider, Dock, ConversationList, Thread,
│   │                            #   AssistantThread, store.ts (zustand: open state, unread)
│   ├── notifications/           # Bell, NotificationList, useUnread
│   ├── settings/                # SettingsPage + AccountTab, AppearanceTab, NotificationsTab
│   ├── profile/ProfilePage.tsx
│   └── admin/AdminPage.tsx      # users table, flags editor, waitlist counts
└── pages/
    ├── HomePage.tsx             # signed-out landing / signed-in snapshot
    └── AboutPage.tsx
```

### Route table (`app/router.tsx`)

| Path | Element | Guard |
|---|---|---|
| `/` | HomePage | — |
| `/about` | AboutPage (linked ONLY from logo) | — |
| `/auth` | SignInPage / SignUpPage | redirect if signed in |
| `/manage` | ManageLayout → redirect `/manage/summary` | RequireAuth |
| `/manage/summary` | SummaryPage | RequireAuth |
| `/manage/owned` | OwnedPage (`?kind=` filter) | RequireAuth |
| `/manage/owned/:id` | PropertyDetailPage | RequireAuth (owner via API 404) |
| `/profile` | ProfilePage | RequireAuth |
| `/settings` | SettingsPage | RequireAuth |
| `/admin` | AdminPage | RequireAdmin |

All under RootLayout, so the messaging dock renders on every route.

### Realtime wiring (MessagingProvider)

On session: `supabase.realtime.setAuth(access_token)` then one channel:
`postgres_changes` INSERT on `public.messages` (RLS restricts to the user's
conversations) → push into TanStack Query cache + bump unread in zustand store.
Same pattern, second subscription, for `notifications`.

---

## Backend

### `backend/pyproject.toml`

```toml
[project]
name = "tract-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115", "uvicorn[standard]>=0.30",
  "sqlalchemy>=2.0", "alembic>=1.13", "psycopg[binary]>=3.2",
  "pydantic>=2.9", "pydantic-settings>=2.5",
  "pyjwt[crypto]>=2.9",            # crypto → ES256 for Supabase JWKS
  "httpx>=0.27",
]
[project.optional-dependencies]
dev   = ["pytest>=8", "pytest-asyncio", "ruff", "httpx"]
agent = ["anthropic>=0.40"]        # ClaudeProvider only
email = ["resend>=2"]              # M4
```

### Setup + run (Windows)

```powershell
cd backend
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head                      # applies migrations to Supabase
uvicorn app.main:app --reload --port 8000
```

### `backend/.env.example`

```
DATABASE_URL=postgresql+psycopg://postgres.<ref>:<password>@<region>.pooler.supabase.com:5432/postgres
SUPABASE_URL=                # for JWKS: <url>/auth/v1/.well-known/jwks.json
SUPABASE_JWT_SECRET=         # only for legacy HS256 projects; leave empty for JWKS
CORS_ORIGINS=http://localhost:5173
AGENT_PROVIDER=stub          # stub | claude
ANTHROPIC_API_KEY=           # optional, only if AGENT_PROVIDER=claude
HUD_API_TOKEN=               # M2
RESEND_API_KEY=              # M4
```

### Files

```
backend/
├── app/
│   ├── main.py                  # FastAPI(), CORSMiddleware(CORS_ORIGINS), GET /healthz,
│   │                            #   app.include_router(v1.router, prefix="/api/v1")
│   ├── db.py                    # engine, SessionLocal, Base
│   ├── core/
│   │   ├── config.py            # Settings(BaseSettings) ← .env
│   │   ├── security.py          # verify_jwt(): PyJWKClient(JWKS) ES256, fallback HS256
│   │   │                        #   if SUPABASE_JWT_SECRET set; audience="authenticated"
│   │   └── deps.py              # get_db, get_current_user (jwt→profiles row), require_admin
│   ├── models/                  # SQLAlchemy — one file per DATABASE.md section
│   │   ├── profile.py  property.py  valuation.py  transaction.py  lease.py
│   │   ├── conversation.py  message.py  notification.py  listing.py
│   │   └── market.py  premium.py  app_setting.py
│   ├── schemas/                 # Pydantic mirrors (Create/Update/Read per model)
│   ├── api/v1/
│   │   ├── router.py            # aggregates all routers (table below)
│   │   ├── auth.py  properties.py  transactions.py  leases.py
│   │   ├── analytics.py  market.py  conversations.py  agent.py
│   │   └── notifications.py  premium.py  admin.py
│   └── services/
│       ├── analytics.py         # ALL money math — implements .claude/skills/real-estate-finance
│       ├── agent.py             # AgentProvider protocol; StubProvider, ClaudeProvider
│       ├── market_data.py       # FMR/HPI lookups, HPI estimate calc
│       └── email.py             # send() wrapper around Resend (M4)
├── alembic/
│   ├── env.py                   # wired to app.db.Base.metadata + DATABASE_URL
│   └── versions/
│       ├── 001_initial.py       # enums + all tables (DATABASE.md)
│       ├── 002_rls.py           # RLS enable + policies + realtime publication (raw SQL)
│       └── 003_auth_trigger.py  # handle_new_user() → profiles insert on signup
└── tests/                       # pytest + httpx AsyncClient; test_analytics.py first
```

### Router registration (`api/v1/router.py`)

| Router file | Prefix | Endpoints (verb path → service call) |
|---|---|---|
| auth.py | `/auth` | GET `/me` → current profile |
| properties.py | `/properties` | GET ``/``, POST ``/``, GET/PATCH/DELETE `/{id}`, GET/POST `/{id}/valuations` (create inserts purchase-price baseline valuation) |
| leases.py | `/properties/{id}/lease` | GET, PUT, DELETE (rental kind only) |
| transactions.py | `/transactions` | GET (`?property_id&from&to&category`), POST, PATCH/DELETE `/{id}` |
| analytics.py | `/analytics` | GET `/portfolio` → `services.analytics.portfolio_summary(user)`; GET `/property/{id}`; GET `/my-home` |
| market.py | `/market` | GET `/fmr?zip=&bedrooms=`, GET `/hpi?state=` → `services.market_data` |
| conversations.py | `/conversations` | GET ``/``, POST ``/`` (dm), GET `/{id}/messages` (paginated), POST `/{id}/messages` (insert → Realtime delivers) |
| agent.py | `/agent` | POST `/message` → provider from `AGENT_PROVIDER` flag; persists into the user's `kind='agent'` conversation |
| notifications.py | `/notifications` | GET ``/``, POST `/{id}/read` |
| premium.py | `/premium` | POST `/waitlist` {feature} |
| admin.py | `/admin` | GET `/users`, GET/PUT `/flags`, GET `/waitlist` — all behind require_admin |

### Key response shapes (contract for `types/api.ts`)

```jsonc
// GET /api/v1/analytics/portfolio
{
  "total_value": 812000, "total_equity": 331000,
  "cash_flow_month": 1240, "cash_flow_series": [{"month":"2026-06","income":4100,"expense":2860}],
  "properties": [{"id":"…","nickname":"Maple St","kind":"rental",
                  "value":412000,"value_source":"hpi_estimate",
                  "cash_flow_month":610,"cap_rate":5.4}],
  "insights": [{"text":"Maple St repairs 38% above 3-mo avg","amount":420,"property_id":"…"}]
}
// POST /api/v1/agent/message  → { "conversation_id":"…", "reply":"…", "provider":"stub" }
```

---

## Workers

```
workers/                         # plain package — run from repo root with backend's venv
├── __init__.py
├── lib/db.py                    # session from DATABASE_URL (imports backend models)
└── jobs/
    ├── refresh_hpi.py           # download FHFA state HPI CSV (no key) → upsert market_hpi
    ├── refresh_fmr.py           # HUD FMR API (HUD_API_TOKEN) → upsert market_fmr
    ├── notify_unread.py         # unread msgs >15min & not emailed → Resend, set emailed_at
    └── send_digests.py          # monthly summary email to email_digest opt-ins
```

Install/run: `pip install -e ./backend` once, then from the repo root
`python -m workers.jobs.refresh_hpi`. No separate workers install — it reuses the
backend's models and dependencies.

### `.github/workflows/`

| File | Trigger | Does |
|---|---|---|
| `ci.yml` | PR + push to dev/qa/prod | backend: ruff + pytest; frontend: eslint + tsc + vitest |
| `cron-market.yml` | `0 6 1 */3 *` (quarterly) + manual | refresh_hpi; refresh_fmr yearly via month guard |
| `cron-email.yml` | `*/15 * * * *` (M4, disabled until then) | notify_unread; digests on 1st of month |

Secrets: `DATABASE_URL`, `HUD_API_TOKEN`, `RESEND_API_KEY`.

---

## Supabase project setup (exact order)

1. Create project `tract-dev` (region near you) → copy URL/keys into env files.
2. `alembic upgrade head` from `backend/` — creates enums, tables, RLS, trigger,
   and adds `messages`, `notifications` to the `supabase_realtime` publication
   (all in migrations; the dashboard is never the source of truth).
3. Dashboard → Auth → enable Email provider (confirm-email off for dev).
4. Smoke test: sign up in the app → `profiles` row appears → `GET /api/v1/auth/me`.

## Local dev = two terminals

```
# 1
cd backend && .venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --port 8000
# 2
cd frontend && npm run dev        # http://localhost:5173
```
