# Tract — Multi-Agent Workflow

How to split work across specialized agents in future sessions. Three standing
priorities rank above feature speed, in this order: **security**, **data
visualization quality**, **ease of use**.

## The agent roster

| Agent | Scope (files) | Charter |
|---|---|---|
| **Database/Security** | `backend/alembic/`, RLS policies, storage policies, `docs/SECURITY*` | Owns the schema and everything Supabase's linter checks. Every table RLS-enabled (incl. tool-created ones like `alembic_version` — bitten once, see D17). Storage policies scoped to owners, not just `authenticated`. Runs the RLS audit query below at the end of every schema change. |
| **Backend** | `backend/app/` | API + services. All money math via `services/analytics.py` following the real-estate-finance skill. Ownership scoping (owner-filtered queries, 404 not 403), pydantic validation on every input, tests for every endpoint incl. a cross-user isolation test. |
| **Frontend/DataViz** | `frontend/src/` | UI per the tract-ui skill (tokens, icons, sanctioned animations) + frontend-design for new surfaces. Charts: Recharts, themed via CSS vars, one idea per chart, animate once, minimum-data rules (no chart from one point). Ease of use: empty states teach, labels over cleverness, both themes verified. |
| **Security reviewer** (cross-cutting) | read-only | Runs /security-review on the diff before qa merges; checks the OWASP-shaped list below. |

## Ground rules for every agent

1. **No git commands** — agents leave changes in the working tree; the
   coordinating session reviews, integrates, and commits. Prevents conflicting
   commits from parallel agents.
2. **Disjoint file scopes** (table above). An agent needing a change outside its
   scope writes a TODO note in its final report instead of editing.
3. **Contracts first**: when backend + frontend work runs in parallel, the
   coordinator fixes the API contract (paths + response shapes) in both prompts
   before spawning.
4. **Verify before reporting**: backend agents run pytest + ruff; frontend
   agents run build + lint + vitest. "It should work" doesn't count.
5. Each agent reads the relevant skill first: real-estate-finance (money),
   tract-ui (frontend), legal-flag-check fires on data/licensing surfaces.

## Security checklist (the reviewer's list, and everyone's habit)

- [ ] Every `public` table has RLS enabled — run after ANY migration:
      `select tablename from pg_tables where schemaname='public' and not rowsecurity;`
      (must return zero rows; Supabase's dashboard linter is the backstop)
- [ ] Storage policies scope writes/deletes to the owner, not all `authenticated`
- [ ] New endpoints: auth dependency present, ownership filter in the query,
      404 (not 403) for foreign ids, pydantic bounds on every field
- [ ] No secrets in code, commits, or `VITE_*` vars (anon key is the only
      browser-safe credential); `.env*` stays gitignored
- [ ] Service-role key never leaves the backend/worker environment
- [ ] Cross-user isolation test exists for every new resource
- [ ] Rate limiting before any user-generated-content surface opens (M3/v1.5)
- [ ] Dependencies: Dependabot + CodeQL enabled on the repo (one-time, free)

## Data-visualization principles (the DataViz agent's charter)

- One chart, one idea; the headline number is text, the chart is context.
- Colors only from tokens (`var(--primary)`, `--positive`, `--negative`);
  meaning never carried by color alone.
- Minimum-data rules from the real-estate-finance skill: don't render charts
  or ratios below their data threshold — show what's missing instead.
- Every estimate labeled with its source, inline, every time.
- Animate once on mount (400ms), never on refetch; respect the motion toggle.

## Ease-of-use principles

- Empty states teach the next action; errors say what to do, not what broke.
- Manual entry is the product's contract: minimize keystrokes (quick-add rows,
  repeat-today buttons, sensible defaults like local-today dates).
- Icons accompany words on actions; icon-only needs aria-label + title.
- New-user path stays under 2 minutes: sign up → add property → see value.

## Standing division for upcoming milestones

- **M2 polish**: Backend (property analytics endpoint) + Frontend (Analytics
  tab, My Home view) in parallel; DB/Security audits storage policies.
- **M3 messaging**: Backend (conversations/agent endpoints + rate limits) →
  then Frontend (dock UI + realtime). DB/Security reviews realtime RLS before
  the dock ships.
- **M4 deploy**: DB/Security owns prod project setup + secrets matrix;
  Backend/Frontend split email + settings surfaces.
