# Tract — Frontend Plan

React 18 + Vite + TypeScript. Tailwind v4 with CSS-variable design tokens. TanStack
Query for server state, Zustand for the one piece of true client state (messaging
dock). Radix primitives under our own styled components for accessible dropdowns,
dialogs, tabs. Recharts for charts.

## Routes & layout

```
/                     Home — signed-out: landing; signed-in: snapshot dashboard
/about                About — reachable ONLY by clicking the logo (not in nav)
/auth                 Sign in / sign up (Supabase)
/manage               → redirects to /manage/summary
/manage/summary       Portfolio analytics (the money page)
/manage/owned         Property grid; kind filter tabs: All · My Home · Rentals · Airbnb · Flips · Other
/manage/owned/:id     Property detail — tabs: Overview · Transactions · Analytics · Lease(rental only)
/profile              Public-ish profile card
/settings             Tabs: Account · Appearance (theme + animations toggle) · Notifications
/admin                Dev-only: users table, feature flags, waitlist counts
```

**Header (every page):** logo left (click → /about — this is the only path to
About), nav center-left: Home, Manage. Right: notifications bell, avatar → dropdown
(Profile, Settings, theme toggle, Sign out).

**Manage layout:** persistent left sidebar — Summary, Owned (with kind sub-items).
Sidebar collapses to icons on tablet, bottom tabs on mobile.

**Messaging dock (global):** floating button bottom-right rendered in the root
layout — persists across ALL routes, per the product requirement. Opens a slide-up
panel with two tabs: **Chats** (user DMs) and **Assistant** (pinned AI
conversation). Unread badge on the button. Realtime inserts via one Supabase channel
subscription owned by a `MessagingProvider` at the root; dock open/closed state and
unread counts live in the Zustand store.

**Premium prototype surfaces:** a locked "Automate" card on Summary and on each
property's Analytics tab — lock icon, one-sentence pitch ("Auto-refresh this
property's value monthly"), and a **Join waitlist** button posting to
`/premium/waitlist`. No payment UI anywhere.

## Feature-folder structure

```
frontend/src/
├── app/                # router.tsx, providers.tsx, RootLayout, ManageLayout
├── components/
│   ├── ui/             # Button, Card, Input, Select, Dialog, Tabs, Badge, Stat
│   └── shared/         # Header, Sidebar, EmptyState, MoneyText, TrendChip
├── features/
│   ├── auth/           # sign in/up forms, useSession, guards
│   ├── portfolio/      # summary/, owned/, property/ (detail tabs), premium/
│   ├── messaging/      # Dock, ConversationList, Thread, AssistantThread, store.ts
│   ├── notifications/  # bell, list, useUnread
│   ├── settings/       # account, appearance (theme), notification prefs
│   ├── profile/
│   └── admin/
├── lib/                # supabase.ts, api.ts (typed fetch wrapper), format.ts (money/date)
├── hooks/
├── styles/             # tokens.css (both themes), globals.css
└── types/              # API response types (mirror backend/app/schemas)
```

Conventions: components fetch via feature-level query hooks (`usePortfolioSummary()`),
never raw fetch in components. All money renders through `<MoneyText>` (tabular
figures, sign-aware color). All API types live in `types/` and mirror Pydantic
schemas by hand until codegen is worth it.

## Design system — "professional light green & beige"

Personality: a well-organized ledger in a sunlit office. Calm, financial, warm —
closer to a wealth-management tool than a listings site. Data minimal: few numbers,
big, well-labeled; charts show one idea each.

### Tokens (styles/tokens.css)

```css
:root {                              /* Light — beige paper, sage green */
  --bg:            #F6F2E8;          /* warm beige page */
  --surface:       #FCFAF4;          /* cards */
  --surface-raised:#FFFFFF;          /* modals, dock */
  --border:        #E3DCC9;
  --text:          #1E2921;          /* deep green-black */
  --text-muted:    #5F6B60;
  --primary:       #4C7A5E;          /* professional sage green */
  --primary-strong:#3B6149;          /* hover / active */
  --primary-soft:  #E7EFE7;          /* selected fills, chart area */
  --positive:      #3E7D51;          /* income, gains */
  --negative:      #B4533A;          /* expenses, losses — warm rust, fits beige */
  --warning:       #B98A2F;
  --focus-ring:    #4C7A5E;
}

[data-theme="dark"] {                /* Dark — deep green-charcoal, warm off-white */
  --bg:            #121813;
  --surface:       #1A211B;
  --surface-raised:#212A22;
  --border:        #2E382F;
  --text:          #EAE7DA;          /* echoes the beige */
  --text-muted:    #9AA69B;
  --primary:       #7CAE8C;
  --primary-strong:#93C2A2;
  --primary-soft:  #24352A;
  --positive:      #6FB884;
  --negative:      #D08067;
  --warning:       #CFA35C;
  --focus-ring:    #7CAE8C;
}
```

Theme = `data-theme` attribute on `<html>`; choices: light / dark / system, stored
per user in settings and localStorage. Never flash-of-wrong-theme: inline script in
index.html reads localStorage before paint.

### Type & shape

- Headings: **Schibsted Grotesk** (600/500) — geometric but warm, not the default
  Inter-everywhere look. Body/UI: **Inter** (400/500). Financial figures always
  `font-variant-numeric: tabular-nums`.
- Radius: 10px cards, 8px controls. Borders over shadows; when shadows, barely-there
  (`0 1px 2px rgb(0 0 0 / 0.04)`).
- Density: generous whitespace on marketing/About; comfortable-compact in Manage
  (this is a tool, not a brochure).

### Iconography

Icons come from **lucide-react** (16–18 px, default stroke). Rules:
- Buttons lead with an icon wherever it aids scanning — icon **with** words for
  actions ("＋ Add property", "→ Start tracking"), icon-only where the meaning is
  universal (sun/moon theme toggle, ✕ close, bell).
- Every icon-only button carries `aria-label` and `title` — no unlabeled mystery
  buttons, ever.
- Primary/destructive CTAs always keep words; an icon alone never guards an
  irreversible action.
- One icon per button; icons inherit `currentColor` so they theme for free.

### Motion — "clean, simple, minimal"

- Standard transition: 160ms ease-out, opacity/transform only. Dock slide-up: 220ms
  `cubic-bezier(0.2, 0, 0, 1)`.
- Header nav selection: a 2px underline that grows from the center on select and
  retracts back to the center on deselect (220ms both ways) — no pill backgrounds
  in the header; pills stay in the Manage sidebar. Manage is hidden entirely when
  signed out.
- Charts animate once on mount (400ms), never on data refetch.
- No scroll-triggered animation, no parallax, no skeleton shimmer loops (static
  skeletons are fine).
- `prefers-reduced-motion: reduce` disables all non-essential motion — enforced
  globally in globals.css.
- **User motion toggle (Settings → Appearance, M4):** a switch lets users turn
  animations off for a flatter, static view, independent of the OS setting. The
  CSS mechanism already exists — `data-motion="off"` on `<html>` neutralizes all
  animations/transitions (mirrors the reduced-motion rules). M4 wires a
  `MotionProvider` (localStorage `tract-motion`, default `on`) plus an inline
  pre-paint script like the theme one, and the toggle control. Choices: `on`
  (default, the sanctioned animations) / `off` (static).

### Accessibility floor (non-negotiable)

Visible focus rings everywhere (`--focus-ring`, 2px offset), all dropdowns/dialogs
are Radix (keyboard + ARIA correct), color contrast ≥ 4.5:1 for text in both themes
(the token values above pass), charts never encode meaning by color alone (labels +
sign).

## Key screens (v1)

1. **Home (signed in):** greeting, 3 stat cards (portfolio value · this month's cash
   flow · unread messages), recent transactions list, shortcut buttons (Add
   property, Add transaction, Open assistant).
2. **Manage → Summary:** portfolio value over time (HPI-adjusted line), cash flow by
   month (bar, income vs expense), per-property table (value, monthly cash flow, cap
   rate), "insights" list fed by the analytics service (e.g., "Maple St expenses up
   32% vs 3-mo avg").
3. **Manage → Owned:** card grid with kind filter tabs; each card: nickname, kind
   badge, latest value, monthly cash flow chip. Empty states that teach ("Add your
   first property — start with the home you live in").
4. **Property detail:** Overview (facts + valuation history sparkline + add
   valuation), Transactions (table + quick-add row, recurring templates), Analytics
   (NOI, cap rate, cash-on-cash, expense breakdown donut, FMR comparison for
   rentals; cost-of-ownership + rent-vs-own for My Home), Lease (rental only).
5. **Messaging dock:** conversation list with unread markers → thread view;
   Assistant tab with suggested prompts ("How did my portfolio do this month?").
6. **About:** short story of Tract, what's manual and why (honesty as a feature),
   "not financial advice" note.
