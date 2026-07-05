# Tract — Database Schema (PostgreSQL / Supabase)

Conventions: `uuid` PKs via `gen_random_uuid()`, `timestamptz` for all timestamps,
`numeric(12,2)` for money (USD only in v1), snake_case, soft rules enforced in the
API, hard rules enforced here. SQLAlchemy models in `backend/app/models/` are the
source of truth; Alembic owns migrations. RLS is enabled on every table.

## Enums

```sql
create type user_role         as enum ('user', 'admin');
create type property_kind     as enum ('my_home', 'rental', 'airbnb', 'flip', 'other');
create type property_status   as enum ('active', 'sold', 'archived');
create type txn_kind          as enum ('income', 'expense');
create type txn_category      as enum (
  -- income
  'rent', 'airbnb_payout', 'other_income',
  -- expenses
  'mortgage', 'property_tax', 'insurance', 'hoa', 'utilities',
  'repairs', 'maintenance', 'cleaning', 'management_fee',
  'renovation', 'listing_fee', 'other_expense'
);
create type valuation_source  as enum ('manual', 'purchase_price', 'hpi_estimate', 'rentcast');
create type conversation_kind as enum ('dm', 'agent', 'inquiry');
create type sender_type       as enum ('user', 'agent', 'system');
create type listing_status    as enum ('draft', 'active', 'paused', 'closed');   -- v1.5
create type notification_kind as enum ('message', 'system', 'digest');
```

## Identity

### profiles
Extends Supabase's managed `auth.users` (standard Supabase pattern — never add app
columns to `auth.users` itself). Row created by a DB trigger on signup.

```sql
create table profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  display_name text not null,
  avatar_url   text,
  role         user_role not null default 'user',
  email_mirror boolean not null default true,   -- "email me unread messages"
  email_digest boolean not null default false,  -- monthly digest opt-in
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);
```

## Portfolio core

### properties
One row per property. `my_home` is just a kind — same table, same analytics
machinery, different UI framing (cost-of-ownership instead of ROI).

```sql
create table properties (
  id             uuid primary key default gen_random_uuid(),
  owner_id       uuid not null references profiles(id) on delete cascade,
  kind           property_kind not null,
  status         property_status not null default 'active',
  nickname       text not null,                -- "Maple St duplex"
  address_line1  text, address_line2 text,
  city           text, state char(2), zip text,
  beds           smallint, baths numeric(3,1), sqft integer, year_built smallint,
  purchase_price numeric(12,2),
  purchase_date  date,
  sold_price     numeric(12,2),
  sold_date      date,
  -- manual loan fields → equity & refi analytics (all optional)
  loan_balance   numeric(12,2),
  interest_rate  numeric(5,3),                 -- 6.875 = 6.875%
  monthly_payment numeric(12,2),
  down_payment   numeric(12,2),                -- → cash-on-cash return
  notes          text,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create index on properties (owner_id, kind);
```

Constraint (API-enforced, not DB): at most one `my_home` property per user.

### property_valuations
Append-only value history. "Current value" = latest row per property.

```sql
create table property_valuations (
  id          uuid primary key default gen_random_uuid(),
  property_id uuid not null references properties(id) on delete cascade,
  source      valuation_source not null,
  value       numeric(12,2) not null,
  valued_at   date not null,
  note        text,
  created_at  timestamptz not null default now()
);
create index on property_valuations (property_id, valued_at desc);
```

On property creation the API inserts a `purchase_price`-sourced row so every
property has a baseline. The HPI worker/endpoint adds `hpi_estimate` rows on demand;
`rentcast` rows are premium-prototype only.

### transactions
The heart of the app — every dollar in or out, manually entered.

```sql
create table transactions (
  id           uuid primary key default gen_random_uuid(),
  property_id  uuid not null references properties(id) on delete cascade,
  kind         txn_kind not null,
  category     txn_category not null,
  amount       numeric(12,2) not null check (amount > 0),  -- sign comes from kind
  occurred_on  date not null,
  description  text,
  is_recurring boolean not null default false,             -- UI template flag; each month still gets a real row
  created_at   timestamptz not null default now()
);
create index on transactions (property_id, occurred_on desc);
```

### leases
Rental tenancies. Airbnb income needs no lease — payouts are just transactions.

```sql
create table leases (
  id           uuid primary key default gen_random_uuid(),
  property_id  uuid not null references properties(id) on delete cascade,
  tenant_name  text not null,
  tenant_email text, tenant_phone text,
  rent         numeric(12,2) not null,
  deposit      numeric(12,2),
  start_date   date not null,
  end_date     date,
  is_active    boolean not null default true,
  notes        text
);
create index on leases (property_id) where is_active;
```

## Messaging

### conversations / conversation_participants / messages

```sql
create table conversations (
  id              uuid primary key default gen_random_uuid(),
  kind            conversation_kind not null,
  listing_id      uuid references listings(id),   -- only for kind='inquiry' (v1.5)
  created_by      uuid not null references profiles(id),
  created_at      timestamptz not null default now(),
  last_message_at timestamptz
);

create table conversation_participants (
  conversation_id uuid not null references conversations(id) on delete cascade,
  profile_id      uuid not null references profiles(id) on delete cascade,
  joined_at       timestamptz not null default now(),
  last_read_at    timestamptz,                    -- unread = messages after this
  primary key (conversation_id, profile_id)
);

create table messages (
  id              uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references conversations(id) on delete cascade,
  sender_id       uuid references profiles(id),   -- null when sender_type != 'user'
  sender_type     sender_type not null default 'user',
  body            text not null,
  created_at      timestamptz not null default now()
);
create index on messages (conversation_id, created_at desc);
```

Realtime is enabled on `messages` (postgres_changes INSERT) — this is the only
table the frontend subscribes to for chat. Each user gets exactly one `agent`
conversation, created lazily on first assistant use.

## Notifications

```sql
create table notifications (
  id         uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles(id) on delete cascade,
  kind       notification_kind not null,
  title      text not null,
  body       text,
  link_path  text,                        -- in-app route, e.g. /manage/owned/<id>
  read_at    timestamptz,
  emailed_at timestamptz,                 -- set by notify_unread worker (mirroring)
  created_at timestamptz not null default now()
);
create index on notifications (profile_id, created_at desc) where read_at is null;
```

## Marketplace (v1.5 — schema now, no UI)

```sql
create table listings (
  id             uuid primary key default gen_random_uuid(),
  property_id    uuid not null references properties(id) on delete cascade,
  status         listing_status not null default 'draft',
  headline       text not null,
  description    text,
  rent_asked     numeric(12,2) not null,
  available_from date,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
```

Inquiries reuse messaging: a browsing user starts a `kind='inquiry'` conversation
referencing the listing. No separate inquiries table.

## Market data (populated by workers, read-only to users)

```sql
create table market_fmr (           -- HUD Fair Market Rents, yearly
  id        uuid primary key default gen_random_uuid(),
  year      smallint not null,
  area_code text not null,          -- HUD area / county FIPS
  area_name text not null,
  state     char(2) not null,
  bedrooms  smallint not null,      -- 0–4
  rent      numeric(12,2) not null,
  unique (year, area_code, bedrooms)
);

create table market_hpi (           -- FHFA House Price Index, quarterly
  id           uuid primary key default gen_random_uuid(),
  level        text not null,       -- 'state' | 'msa'
  region_code  text not null,
  region_name  text not null,
  period       date not null,       -- quarter start
  index_value  numeric(10,2) not null,
  unique (level, region_code, period)
);
```

HPI estimate = `purchase_price × (index(latest) / index(purchase quarter))` for the
property's state (metro-level when we map zips → MSA later). Always stored/displayed
as `source='hpi_estimate'` and labeled as an index-based estimate in the UI.

## Premium prototype & flags

```sql
create table premium_waitlist (
  id         uuid primary key default gen_random_uuid(),
  profile_id uuid not null references profiles(id) on delete cascade,
  feature    text not null,         -- 'auto_valuation' | 'data_import' | 'str_comps'
  created_at timestamptz not null default now(),
  unique (profile_id, feature)
);

create table app_settings (         -- feature flags, admin-editable
  key        text primary key,      -- 'agent_provider', 'marketplace_enabled', ...
  value      jsonb not null,
  updated_at timestamptz not null default now()
);
```

## Row Level Security strategy

Writes go through FastAPI (service role, bypasses RLS), but RLS still protects the
frontend's direct read paths (realtime) and acts as defense-in-depth:

- `profiles`: user can select/update own row.
- `properties`, `property_valuations`, `transactions`, `leases`: select where
  `owner_id = auth.uid()` (via join for child tables). No insert/update/delete
  policies for the anon/authenticated role — writes are API-only.
- `conversations`/`messages`/`conversation_participants`: select where the user is
  a participant. This is what makes the realtime subscription safe.
- `notifications`: select own.
- `market_fmr`, `market_hpi`: select for all authenticated users.
- `listings` (v1.5): select where `status='active'`, plus owner sees own.
- `premium_waitlist`, `app_settings`: no client access; API only.
- Admin: role checked in FastAPI from `profiles.role` — admins do not get special
  RLS powers client-side.
