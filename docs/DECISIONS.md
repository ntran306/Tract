# Tract — Decision Log

Short records of decisions with reasoning, so future sessions don't re-litigate.
Newest last.

**D1 — No ECC / third-party skill packs.** Investigated "Everything Claude Code";
star growth implausible for its age with near-zero issue activity, copycat repo
swarm, auto-executing hooks. Only Anthropic's official `anthropics/skills` repo and
custom-written skills are used, project-scoped under `.claude/skills/`.

**D2 — License: source-visible, not open source (pending file).** Goal is "people
can see it, not copy it." Standard OSS licenses all grant copying. Choice narrowed
to explicit all-rights-reserved notice or FSL. No LICENSE committed yet — do this
before publicizing the repo.

**D3 — No scraping; free-data-or-manual.** Zillow's API is dead to the public and
its ToS bans scraping. Data strategy: FHFA HPI (free CSV) + HUD FMR (free API) for
area context, manual entry for everything else, RentCast (50 free calls/mo)
reserved for the premium prototype.

**D4 — Monorepo, not three repos.** (User initially wanted frontend/backend/workers
as separate repositories.) Solo project; one CI, atomic cross-cutting PRs, no
version drift. `frontend/`, `backend/`, `workers/` are top-level folders instead.

**D5 — Portfolio-first; marketplace at v1.5.** A two-sided marketplace with zero
users is dead weight; portfolio tracking is useful to one user on day one. Listings
and inquiry-conversation schema designed now so v1.5 is additive, not a migration.

**D6 — Supabase + FastAPI hybrid.** Supabase free tier supplies Postgres, auth
(never hand-rolled), and managed realtime — which matters because free FastAPI
hosting (Render) sleeps, making self-hosted WebSockets flaky. FastAPI owns all
writes, business logic, analytics, and the AI agent. Frontend touches Supabase
directly only for auth and realtime message reads.

**D7 — "Workers handle DB stuff" corrected.** API owns request-time DB access;
workers own scheduled background jobs (FHFA/HUD refreshes, email mirroring,
digests), run free via GitHub Actions cron. Workers never serve requests.

**D8 — Email = transactional + mirroring, not a client.** Resend free tier.
Password resets (Supabase built-in), unread-message mirroring, opt-in monthly
digest. No inbox/compose/receive — building an email client was ruled out for v1.

**D9 — AI agent is pluggable because it isn't free.** No free Anthropic API tier.
StubProvider (default): deterministic answers to structured portfolio questions by
calling the analytics service — $0. ClaudeProvider (Haiku + tool use over the same
analytics functions) enabled only when a key is configured, behind a feature flag.

**D10 — Money is numeric(12,2), USD, manual-entry-as-contract.** No floats, no
multi-currency in v1. The app is honest about what it can't fetch legally/freely:
users type it in, and the UI treats good manual entry as a feature, not a gap.

**D15 — FHFA HPI = free state-level value estimates; FMR = rent benchmark.**
`workers/jobs/refresh_hpi.py` pulls the FHFA monthly master CSV (free, no key) at
`fhfa.gov/hpi/download/monthly/hpi_master.csv`, filtering to
traditional/all-transactions/quarterly State rows (index_nsa) into market_hpi.
Estimate = purchase_price × latest_index / index_at_purchase_quarter, rounded to
$1,000, stored as source='hpi_estimate' — never clobbers a newer manual value.
FMR (`refresh_fmr.py`, HUD /fmr/statedata, needs free HUD_API_TOKEN) powers the
rent-vs-FMR chip, which stays hidden (endpoint 404s) until the token/worker run.
Both scheduled in .github/workflows/cron-market.yml (needs DATABASE_URL +
HUD_API_TOKEN repo secrets).

**D16 — Config loads backend/.env by absolute path.** pydantic-settings resolved
`.env` relative to CWD, so workers run from the repo root fell back to the
localhost default DB. config.py now points env_file at an absolute
`backend/.env`; CI/prod still override via real env vars.

**D12 — Property photos: owner uploads to a public Storage bucket (prototype).**
`property_images` table + Supabase Storage bucket `property-images` (migration
004). Files upload client-side straight to Storage (bytes never touch the API);
the API records the object key and builds public URLs. Bucket is PUBLIC for
prototype simplicity — house exterior photos are low-sensitivity. Hardening to a
private bucket with signed URLs + per-owner read policies, and deleting storage
objects on image/property delete (currently orphaned), are v2 items.

**D13 — User animation toggle lives in Settings (M4), mechanism ready now.**
`data-motion="off"` on <html> neutralizes all animation/transition (globals.css),
mirroring reduced-motion. Lets users pick the polished animated view or a flat
static one. Full wiring (MotionProvider + control + pre-paint script) is M4;
groundwork landed early so it's a small addition.

**D14 — Three demo accounts for prototyping.** Seeded via
backend/scripts/seed_demo.py (idempotent): Alex Rivera (5-property portfolio),
Sam Chen (rents out one condo, rents where he lives), Jordan Lee (just a home).
Emails are +aliases of the owner's gmail (Supabase rejects example.com), shared
password documented with the script. Re-running wipes and reseeds their data.

**D11 — Maps: Leaflet + OSM, not Google; imagery: owner uploads, never scraped.**
Google Maps requires a credit-card billing account even at free-tier usage —
wrong default for this project; Leaflet + OpenStreetMap costs $0 with no key
(swap tile provider later if traffic demands). Addresses geocode once at save
time via the free US Census Geocoder into stored lat/lon. House photos come from
owners uploading their own; listing-site photos are copyrighted and off-limits.
Street View is a possible paid add-on later (its ToS forbids caching). Details
in BACKLOG.md v1.5.
