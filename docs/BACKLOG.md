# Tract — Backlog

Prioritized. Items graduate from here into a milestone when work starts; nothing
below v1 changes what M1–M4 ship. Each item carries its design sketch and its
honest cost/legal notes so future-us doesn't re-research it.

**Grooming rules:** an item is ready to build only when it has (1) schema impact
listed, (2) API surface listed, (3) a cost/abuse story. Otherwise it stays here.

---

## v1.5 — Marketplace: listings + requests

### Listings & browse (already designed)
Schema exists (`listings`, inquiry conversations). Ship: create-listing from a
rental property, public browse/search on Home, inquiry → conversation flow,
admin moderation list. RLS for public reads already written in migration 002.

### NEW — Requests board ("wanted" posts)
The reverse marketplace: a user posts *what they're looking for* — "looking to
rent 2BR near Austin under $1,800" / "looking to buy a duplex, ~$400k" — and
owners respond, opening a negotiation conversation.

- **Schema:** `requests` table: id, profile_id, kind (`rent`|`buy`), city/state/zip,
  budget_min, budget_max, beds_min, description, status (`open`|`matched`|`closed`),
  created_at. RLS: open requests readable by authenticated users; owner edits own.
- **API:** CRUD `/api/v1/requests` + `POST /requests/{id}/respond` → creates a
  `kind='inquiry'` conversation between responder and requester (reuses the whole
  messaging stack — zero new realtime work).
- **UI:** a "Requests" tab beside listings in browse; respond button; my-requests
  under Profile.
- **Search:** filters (kind, area, budget, beds) as SQL where-clauses with a
  debounced (300 ms) query — no search engine needed until thousands of rows.
- **Anti-abuse (required before launch):** rate-limit posts (e.g., 3 open
  requests/user), report button writing to a moderation queue, admin close/remove.
- **Why this is a good idea:** it gives the marketplace a demand side that works
  even with few listings — a requests board is useful at 10 users in a way an
  empty listings grid is not.

### Negotiation affordances (bargaining)
Keep bargaining inside conversations, but add structure: an **offer message
type** — amount + optional terms, with accept/decline/counter actions rendered
as buttons in the thread.
- **Schema:** `offers`: id, conversation_id, from_profile_id, amount, terms text,
  status (`open`|`accepted`|`declined`|`countered`|`expired`), created_at.
  Message rows reference an offer_id to render the card.
- Accepted offer = recorded agreement both parties can see — and later (v2) the
  thing a payment or a document checklist attaches to.

---

## v2 — Media in messages (images first, video later)

Send photos in conversations (the listing walkthrough, the broken faucet).

- **Storage:** Supabase Storage, private `attachments` bucket. **Client uploads
  directly to storage via signed upload URLs** — media bytes never pass through
  FastAPI, so backend bandwidth/cost stays ~zero. The message row stores only
  the storage path + metadata.
- **Schema:** `message_attachments`: id, message_id, storage_path, mime,
  bytes, width, height. Storage RLS: readable only by conversation participants
  (mirrors messages policy).
- **Cost discipline (free tier: 1 GB storage, capped egress):**
  - Compress client-side before upload (browser-image-compression → WebP,
    ~1600px max, target ≤300 KB).
  - Generate a thumbnail variant at upload; threads render thumbnails,
    full image loads on tap.
  - Serve via signed URLs with long client-side cache; lazy-load offscreen.
  - Per-message cap (e.g., 4 images), per-user quota tracked in DB.
- **Video: defer.** Video destroys a free storage tier fastest of anything.
  When it earns its way in: 60-second / 25 MB cap, same pipeline — or premium-gate
  it (below). Until then, users paste a YouTube/Drive link.
- **Privacy flag:** user-uploaded photos of homes + people are PII-adjacent —
  delete attachments when a conversation/account is deleted (cascade job), and
  say so in the privacy note.

## v2 — Payments (rent first; a platform fee only when it's earned)

The honest framing: **we never build payment rails and we never hold money.**
Stripe Connect (Express) is the industry answer — tenants pay, Stripe routes to
the landlord's connected account, Stripe owns KYC/AML/chargebacks.

- **Phase P1 — rent collection:** landlord connects Stripe from Settings; a
  lease gets a "collect by card/ACH" toggle; tenant pays from a link/portal.
  ACH is the right rail for rent (Stripe: 0.8% capped at $5, vs ~2.9% + 30¢
  for cards — cards on a $2,000 rent ≈ $58, ACH ≈ $5).
  - **Schema:** `payment_accounts` (profile_id, stripe_account_id, status),
    `payments` (lease_id, payer/payee, amount, rail, stripe_ids, status,
    occurred_on) — and a paid payment auto-creates the matching `transactions`
    row, so analytics stay one source of truth.
  - **Webhooks:** new endpoint + signature verification; payments are the first
    place where idempotency actually matters — build it in from the start.
- **Phase P2 — platform fee:** Connect `application_fee_amount` on each charge
  (e.g., 0.5–1%). Flip it on only when volume exists; a fee on ten payments a
  month is noise, and undercutting nothing.
- **What we will NOT do:** process home purchases. Six-figure transfers belong
  to escrow/title. What Tract can own is everything *around* the purchase: the
  accepted offer record, a document checklist, deadline reminders, and the
  final numbers landing in the buyer's portfolio automatically.
- **Legal flag (decision gate, not advice):** rent collection + fees sits near
  regulated money-transmission; Connect's model is the standard way platforms
  stay compliant, but get a real lawyer's sign-off before P2 goes live.

## v2 — Premium prototype → real features
Waitlist cards exist from M4. When any feature has real waitlist demand:
auto-valuation (RentCast, needs paid tier or BYO key), CSV/bank import
(Plaid costs real money per link — price it), STR comps. Video messaging is
also a natural premium gate.

---

## Icebox (revisit when something changes)

- **Search upgrade** (Postgres full-text / pg_trgm) — when request/listing
  volume makes LIKE-queries feel bad.
- **Receipt OCR** into transactions — fun, costs API money, premium candidate.
- **Native mobile** — responsive web is the answer until users say otherwise.
- **Multi-currency / i18n** — explicitly out until there's a non-US user.
- **Public API for landlords' tools** — needs auth keys, rate limits, docs;
  far future.

## Efficiency principles (apply to everything above)

Standing rules that keep the free tier free:
1. One screen = one API call where possible (portfolio summary is a single
   payload, not six requests).
2. TanStack Query `staleTime` on everything; realtime subscriptions instead of
   polling, always.
3. Debounce every search input (300 ms); paginate every list (cursor, 25/page).
4. Media bytes go client → storage directly, never through the API.
5. Cache-friendly market data: FMR/HPI endpoints send long `Cache-Control`
   (the data changes quarterly/yearly).
6. Rate-limit the API (slowapi) before opening any user-generated-content
   surface — protects both abuse and the Render free instance.
