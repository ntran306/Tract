# Tract — Playbook: phases, your actions, and how changes flow

Companion to ROADMAP.md (what we build) and IMPLEMENTATION.md (how it's wired).
This file is about *process*: what YOU do at each phase, and the pipeline every
change rides through.

## The change pipeline (applies to every phase)

```
feature branch ──PR──▶ dev ──merge──▶ qa ──merge──▶ prod
                 │        │             │              │
                 CI       deploys       manual         deploys production
                 gates    previews      verification   (Vercel + Render)
```

1. **Work happens on feature branches off `dev`** (`feat/properties-crud`,
   `fix/theme-flash`). Direct pushes to dev are fine for docs; code goes through
   a PR so CI (ruff + pytest, oxlint + vitest + build) gates it.
2. **PR review, even solo:** run `/code-review` on the branch before merging —
   it's the cheapest bug filter you have. For risky changes, `/security-review`.
3. **`dev` is always runnable.** If a merge breaks dev, fixing it is the next task,
   nothing else.
4. **`qa` is the verification gate, not an environment.** Merging dev → qa means
   "I'm about to ship this set." On qa: run the app locally against `tract-dev`,
   click through the affected flows (webapp-testing skill can automate this),
   check the migration ran clean. Free tier gives qa no separate infra — the gate
   is the discipline, not the hardware.
5. **`prod` deploys.** Merging qa → prod triggers Vercel (frontend) and Render
   (backend) deploys from the prod branch (wired in M4). Prod migrations are run
   deliberately (below), never automatically.

### Database changes (the strictest rule set)

- Every schema change = a new Alembic migration on the feature branch. **Never
  edit a migration that has been applied anywhere.**
- Merge to dev → run `alembic upgrade head` against `tract-dev` yourself (one
  command, from `backend/`).
- Ship to prod → run `alembic upgrade head` against `tract-prod` *before* the
  code deploy goes live (additive migrations first; destructive ones in a later
  release once nothing references the old shape).
- Rollback posture: prefer roll-forward (a new fixing migration) over
  `alembic downgrade` on real data.

### Env vars & secrets (adding one, every time)

1. Add to `backend/.env.example` or `frontend/.env.example` with a comment.
2. Add to `backend/app/core/config.py` (Settings) if backend.
3. Set it in: your local `.env` / `.env.local` → GitHub Actions secrets (if
   workers/CI need it) → Render env (backend, M4+) → Vercel env (frontend, M4+).
4. Never commit real values. `VITE_*` vars ship to the browser — anon key yes,
   service keys never.

### Release & rollback

- Frontend: Vercel keeps every deploy — rollback is one click to the previous one.
- Backend: Render redeploys the previous commit (or `git revert` on prod).
- Schema: roll forward. If a release mixes schema + code, revert code first;
  additive schema can stay.

---

## Phase-by-phase: what you personally do

### Now — unblock the M0 smoke test (≈15 min, free)
- [ ] Create Supabase account → new project **tract-dev** (nearest region).
- [ ] Dashboard → Settings → API: copy Project URL + anon key →
      `frontend/.env.local`; Project URL also → `backend/.env`.
- [ ] Dashboard → Connect → Session pooler URI (port 5432) → `DATABASE_URL`
      in `backend/.env`.
- [ ] Dashboard → Authentication → Sign In / Up: enable Email provider; for dev,
      turn OFF "Confirm email" (turn back on before real users).
- [ ] Tell me — I run `alembic upgrade head`, you sign up in the app, and
      `/auth/me` returning your profile proves the whole loop.

### M1 — Properties & transactions (no external actions)
- Your job is **using it**: add your real properties and a month of transactions,
  and complain loudly about every annoying part of the forms. That feedback is
  the milestone's acceptance test.
- Change flow note: M1 adds the first post-001 migrations — the dev-migration
  habit starts here.

### M2 — Analytics & market data
- [ ] Register a free HUD API token (huduser.gov → FMR API) → `backend/.env`
      **and** GitHub repo → Settings → Secrets → Actions: `HUD_API_TOKEN`,
      plus `DATABASE_URL` (the workers' cron workflow needs both).
- Sanity-check the analytics against your own mental math — if a cap rate looks
  wrong to you, it's a bug (the real-estate-finance skill defines the formulas).

### M3 — Messaging & assistant (no external actions)
- Stub assistant costs $0 and ships by default.
- [ ] Optional: if you want the real Claude assistant, create an Anthropic API
      key, set `ANTHROPIC_API_KEY` + `AGENT_PROVIDER=claude` in Render/`.env`.
      Haiku pricing makes each message a fraction of a cent — but it's YOUR key
      and YOUR bill; the flag exists so you can turn it off instantly.

### M4 — Email, deploys, going live
- [ ] Resend account → API key → `RESEND_API_KEY` (Render env + GH secret).
      Start on Resend's shared onboarding domain; buy a domain later if wanted.
- [ ] Vercel account → import the GitHub repo → root dir `frontend`, production
      branch `prod` → set `VITE_*` env vars.
- [ ] Render account → new Web Service from the repo → root `backend`, branch
      `prod`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
      → set backend env vars. Add the Vercel URL to `CORS_ORIGINS`.
- [ ] Create Supabase project **tract-prod**; I run migrations against it;
      its keys go in Vercel/Render env — prod never shares tract-dev.
- [ ] **LICENSE decision** (still open): all-rights-reserved notice or FSL —
      must land before you share the repo/site anywhere public.
- [ ] Turn Supabase email confirmation back ON (tract-prod).

### v1.5 — Marketplace (listings + requests)
- No accounts needed. Your job shifts to policy: write the 5-line house rules
  (what listings are allowed, what gets removed) before opening user-generated
  content to anyone but yourself. Admin moderation ships in this phase.

### v2 — Payments (only when real users exist)
- [ ] Stripe account + Stripe **Connect** (Express accounts) — Stripe holds
      funds and handles KYC; we never touch money directly.
- [ ] Talk to an actual lawyer/accountant before charging a platform fee.
      (Flag, not advice: rent-collection platforms sit near regulated
      money-transmission; Connect's application-fee model is the standard way
      to stay on the right side, but this is a real go/no-go gate.)

---

## Standing robustness habits (start now, they're all free)

- **Dependabot + CodeQL**: enable in GitHub repo settings (free on public
  repos) — dependency and code scanning on autopilot.
- **Error tracking**: Sentry free tier on backend + frontend at M4 — you cannot
  fix crashes you never hear about.
- **Uptime**: UptimeRobot free pinging `/healthz` at M4. Accept Render
  cold-starts until they actually annoy users; don't burn effort pre-warming.
- **Account security**: 2FA on GitHub, Supabase, Vercel, Render, Resend. The
  platform accounts ARE the product's security boundary.
- **Backups**: Supabase free tier has no point-in-time recovery. Before real
  users' data matters (M4/v1.5), either upgrade the prod project or set up a
  weekly `pg_dump` to a private encrypted location — never to public repo
  artifacts.
- **PII discipline**: real tenant names/emails only ever in tract-prod, never
  in dev/test data.
