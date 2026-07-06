---
name: tract-ui
description: Tract's concrete UI system — design tokens, lucide iconography rules, the sanctioned animation list, component conventions, and the accessibility floor. Use this for ANY frontend work in this repo: new pages, components, buttons, charts, loading/empty states, or styling tweaks — even one-line CSS changes. Pairs with the frontend-design skill (which covers aesthetic direction); this one covers Tract-specific execution so the UI stays consistent, clean, and professional across sessions.
---

# Tract UI System

Tract's personality: **a well-organized ledger in a sunlit office** — calm,
financial, warm. Closer to a wealth-management tool than a listings site. Every
addition should read as quietly confident, never flashy. When in doubt: fewer
elements, more whitespace, one clear number.

## Tokens (the only colors that exist)

Defined in `frontend/src/styles/tokens.css`, exposed as Tailwind classes via
`@theme inline` in `globals.css`. **Never hardcode a hex value in a component.**

| Class | Role |
|---|---|
| `bg-bg` / `bg-surface` / `bg-surface-raised` | page / cards / modals & popovers |
| `border-border` | all borders (borders over shadows) |
| `text-text` / `text-text-muted` | primary / secondary text |
| `bg-primary` `text-primary` `bg-primary-strong` `bg-primary-soft` | sage green actions; `-soft` for selected fills & hovers |
| `text-primary-contrast` | text on primary buttons |
| `text-positive` / `text-negative` / `text-warning` | income & gains / expenses & losses / caution — never encode meaning by color alone |

Typography: headings `font-display` (Schibsted Grotesk), body Inter (default).
**All financial figures get the `tabular` class** (tabular-nums). Radius: 10px
cards (`rounded-[10px]`), 8px controls (`rounded-lg`). Shadows barely-there.

## Iconography (lucide-react)

- Sizes: 16 inside buttons/menu items, 17–18 standalone. One icon per button.
- Action buttons: icon **with** words (`<LogIn size={16} /> Sign in`). Icon
  leads except "forward motion" CTAs where an ArrowRight trails.
- Icon-only is allowed solely for universal actions (theme sun/moon, ✕ close,
  bell) and **must** carry `aria-label` + `title`.
- Words alone guard destructive/irreversible actions — an icon never does.
- Icons inherit `currentColor`; never give an icon its own color class unless
  it's a status icon using positive/negative/warning.

## Sanctioned animations — the complete list

Motion exists to explain state changes, not to decorate. Current whitelist:

1. **Hover/focus color transitions** — 150ms ease-out (`transition-colors`).
2. **Button press** — `active:scale-[0.98]`, transform+color transition only.
3. **Header nav underline** — grows from center on select, retracts to center
   on deselect, 220ms `cubic-bezier(0.2,0,0,1)` (`.nav-link` in globals.css).
4. **Popover/dropdown pop-in** — `pop-in` keyframes, 150ms
   (`data-[state=open]:animate-[pop-in_150ms_ease-out]` on Radix content).
5. **Charts** — animate once on mount (400ms), never on refetch.
6. **Messaging dock slide-up** — 220ms `cubic-bezier(0.2,0,0,1)` (M3).

Adding a new animation is allowed when ALL of these hold:
- It communicates a state change the user caused (appear, select, expand).
- Opacity/transform only; ≤ 250ms; ease-out or the 0.2,0,0,1 curve.
- It fires once per state change — no loops, no scroll-triggered effects,
  no skeleton shimmer (static skeletons are fine).
- Add it to this list in the same PR — an animation not on this list is a bug.

`prefers-reduced-motion` is handled globally in globals.css — never write a
per-component reduced-motion override, and never bypass the global rule.

## Component conventions

- Primitives live in `components/ui/` (Button, Card, Input…) — extend those,
  don't fork one-off styled elements. Overlays/dropdowns/tabs are always Radix
  under our styling (keyboard + ARIA come free).
- Buttons: `variant="primary"` (one per view, the main action), `secondary`
  (bordered), `ghost` (toolbars). If a view seems to need two primaries, the
  view is doing too much.
- Money renders through `lib/format.ts` (`money` whole dollars in dashboards,
  `moneyExact` cents in transaction tables, `pct` one decimal) — never inline
  `toFixed`/`Intl` in components.
- Empty states use `EmptyState` and must teach: say what goes here and how to
  get it ("Add your first property — start with the home you live in").
- Estimates are labeled inline where the number appears ("index-based
  estimate") — Tract's credibility is the product (real-estate-finance skill).
- Data fetching via feature-level TanStack Query hooks (`queries.ts` per
  feature); components never call `fetch`/`api()` directly.

## Accessibility floor (non-negotiable, applies to every change)

- Visible focus: global `:focus-visible` ring — never `outline: none` without
  replacement.
- Text contrast ≥ 4.5:1 in BOTH themes — check dark mode before calling
  anything done; verify with preview_inspect, not by eyeballing screenshots.
- Every interactive element reachable and operable by keyboard.
- Charts and status chips carry text/sign, not color alone.

## Definition of done for UI work

1. Renders correctly in **both themes** (toggle it in the preview).
2. No hardcoded colors, no unsanctioned animation, icons follow the rules.
3. Focus states visible; icon-only buttons labeled.
4. Screenshot verified via the preview tools before claiming completion.
