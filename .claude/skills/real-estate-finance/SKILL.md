---
name: real-estate-finance
description: Canonical formulas, conventions, and edge-case rules for all real estate financial analytics in Tract — cash flow, NOI, cap rate, cash-on-cash return, expense ratios, DSCR, HPI-based appreciation estimates, FMR benchmarks, STR metrics (ADR/occupancy/RevPAR), flip metrics (ARV, 70% rule), and rent-vs-own analysis. Use this whenever writing or reviewing analytics code (backend/app/services/analytics.py), building Summary/Analytics UI, designing the AI assistant's answers about money, or any calculation involving property income, expenses, value, or returns — even if the user just says "add a stat" or "show ROI".
---

# Real Estate Finance — Tract's Analytics Rules

One source of truth for every money calculation in Tract. If code or UI disagrees
with this file, one of them is wrong — fix whichever it is deliberately.

## Global conventions

- **Money is `Decimal`/`numeric(12,2)`, never float.** Round only at display time.
- **Monthly is the native period.** Annualize by ×12 from a monthly figure (or sum
  12 real months when available — prefer real sums over ×12 when ≥12 months of data
  exist). Label every figure with its period ("/mo", "/yr").
- **Sign convention:** incomes positive, expenses positive in storage (`kind`
  carries direction); *computed* net figures may be negative and display red/rust.
- **Never show more precision than the inputs justify.** HPI estimates round to the
  nearest $1,000. Percentages: one decimal place. Currency: whole dollars in
  dashboards, cents only in transaction tables.
- **Estimates are labeled.** Anything derived from an index or benchmark says so
  inline ("index-based estimate", "HUD FMR benchmark") — Tract's credibility is the
  product.
- **Insufficient data → say so, don't fake it.** Metrics have minimum-data rules
  (below). Render an empty-state with what's missing ("Add 3 months of transactions
  to see trends"), never a misleading number from one data point.

## Core metrics (rental / airbnb / other)

**Monthly cash flow** = sum(income txns) − sum(expense txns), per calendar month.
The headline number. Requires ≥1 transaction; show "partial month" chip for the
current month.

**NOI (annual)** = operating income − operating expenses, **excluding**: mortgage
payments (debt service, not operating), renovation/capex (`renovation` category),
and one-off purchase/sale costs. Include: property_tax, insurance, hoa, utilities,
repairs, maintenance, cleaning, management_fee, listing_fee.

**Cap rate** = NOI / current value. Current value = latest `property_valuations`
row. Requires ≥6 months of transactions (annualized) — below that, don't show it.

**Cash-on-cash return** = annual pre-tax cash flow (NOI − annual debt service) /
cash invested. Cash invested = `down_payment` (+ renovation txns to date if the
user marks them as part of acquisition — v1 simplification: down_payment only).
Requires `down_payment` set; otherwise show "add your down payment to unlock".

**Expense ratio** = operating expenses / operating income. Flag > 50% as high for
long-term rentals (the "50% rule" heuristic — call it a heuristic).

**DSCR** = NOI / annual debt service (12 × `monthly_payment`). Only when
`monthly_payment` set. Below 1.2, chip it as "tight" — lenders typically want ≥1.2.

**Equity (estimate)** = current value − `loan_balance`. Both inputs manual/estimated
— label accordingly.

## HPI-based value estimate (the free auto-valuation)

`est_value = purchase_price × (HPI_latest / HPI_at_purchase_quarter)` using the
property's **state** index (metro when zip→MSA mapping lands). Rules:
- Requires purchase_price and purchase_date; round to nearest $1,000.
- Store as `property_valuations` row, `source='hpi_estimate'`.
- Display: "≈ $412,000 · index-based estimate" — never as "your home's value".
- Never overwrite or outrank a newer `manual` valuation; latest row wins regardless
  of source, and the UI shows the source of the number it's using.

## FMR benchmark (rentals & My Home)

Compare actual rent (active lease `rent`, or My Home user-entered rent) to HUD FMR
for the area + bedroom count. Display as a chip: "12% above area FMR". Rules: match
on bedrooms exactly (cap at 4+ = 4), use latest FMR year, and phrase neutrally —
above FMR isn't "bad", it's information.

## STR metrics (airbnb kind)

From `airbnb_payout` transactions plus (v1) user-entered nights booked per month:
- **ADR** = payout total / nights booked.
- **Occupancy** = nights booked / nights in month.
- **RevPAR** = payout total / nights *available* (= ADR × occupancy).
If nights aren't entered, show payout totals only — do not infer occupancy.
**Break-even occupancy** = monthly operating costs (incl. debt service here, since
the owner pays it regardless) / (ADR × days in month).

## Flip metrics (flip kind)

- **Total invested** = purchase_price + renovation txns + holding costs (all expense
  txns during hold).
- **Projected/realized profit** = (sold_price or latest valuation) − total invested
  − (if sold) listing/closing fees.
- **70% rule check** (heuristic, label it): purchase + renovation ≤ 70% × ARV, where
  ARV = latest valuation. Chip: "meets/exceeds 70% rule".
- Annualized return uses actual hold duration; under 3 months of hold, show absolute
  profit only (annualizing tiny windows produces nonsense).

## My Home analytics (applies to every user)

- **True monthly cost of ownership** = mortgage + property_tax + insurance + hoa +
  utilities + maintenance (12-mo average where available).
- **Rent-vs-own context** = cost of ownership vs area FMR for equivalent bedrooms:
  "Owning costs $340/mo more than area fair-market rent" — context, not advice.
- **Appreciation** = HPI estimate vs purchase price, absolute + annualized %.
- If the user is a renter (my_home with rent transactions, no purchase_price):
  compare their rent to FMR and track rent growth over time instead.

## Trends & insights (Summary page "insights" feed)

An insight fires only when it clears a materiality bar — noise kills trust:
- Expense category > 25% above its trailing 3-month average AND > $100 absolute.
- Cash flow sign flip (positive→negative month).
- Lease ending within 60 days.
- Vacancy signal: rental with no rent income for a complete calendar month.
Each insight: one sentence, the number that triggered it, link to the property.
Maximum 5 shown; order by dollar impact.

## AI assistant answers about money

The assistant (stub or Claude) answers ONLY from computed analytics — it never does
its own arithmetic on raw transactions, never estimates values itself, and echoes
the same labels ("index-based estimate"). If a metric is unavailable, it says what's
missing, mirroring the UI's empty-state rule. No investment advice: it reports and
explains Tract's numbers, and may explain what a metric means generally.

## Not financial advice

Every analytics surface (Summary, property Analytics, assistant) carries one quiet
footer line: "Estimates for your own tracking — not an appraisal, tax, or
investment advice." Don't repeat it per-widget; once per page.
