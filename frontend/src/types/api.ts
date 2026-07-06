/** Hand-maintained mirrors of backend Pydantic schemas (backend/app/schemas).
 *  Money fields arrive as strings ("300000.00") — Decimal serialization. */

export type UserRole = 'user' | 'admin'

export interface Profile {
  id: string
  display_name: string
  avatar_url: string | null
  role: UserRole
  email_mirror: boolean
  email_digest: boolean
  created_at: string
}

export type PropertyKind = 'my_home' | 'rental' | 'airbnb' | 'flip' | 'other'
export type PropertyStatus = 'active' | 'sold' | 'archived'
export type ValuationSource = 'manual' | 'purchase_price' | 'hpi_estimate' | 'rentcast'

export interface Property {
  id: string
  kind: PropertyKind
  status: PropertyStatus
  nickname: string
  address_line1: string | null
  address_line2: string | null
  city: string | null
  state: string | null
  zip_code: string | null
  beds: number | null
  baths: string | null
  sqft: number | null
  year_built: number | null
  purchase_price: string | null
  purchase_date: string | null
  sold_price: string | null
  sold_date: string | null
  loan_balance: string | null
  interest_rate: string | null
  monthly_payment: string | null
  down_payment: string | null
  notes: string | null
  created_at: string
  latest_value: string | null
  latest_value_source: ValuationSource | null
}

export interface PropertyCreatePayload {
  kind: PropertyKind
  nickname: string
  address_line1?: string
  city?: string
  state?: string
  zip_code?: string
  beds?: number
  baths?: string
  sqft?: number
  year_built?: number
  purchase_price?: string
  purchase_date?: string
  loan_balance?: string
  interest_rate?: string
  monthly_payment?: string
  down_payment?: string
  notes?: string
}

export interface Valuation {
  id: string
  source: ValuationSource
  value: string
  valued_at: string
  note: string | null
  created_at: string
}

export type TxnKind = 'income' | 'expense'
export type TxnCategory =
  | 'rent'
  | 'airbnb_payout'
  | 'other_income'
  | 'mortgage'
  | 'property_tax'
  | 'insurance'
  | 'hoa'
  | 'utilities'
  | 'repairs'
  | 'maintenance'
  | 'cleaning'
  | 'management_fee'
  | 'renovation'
  | 'listing_fee'
  | 'other_expense'

export interface Transaction {
  id: string
  property_id: string
  kind: TxnKind
  category: TxnCategory
  amount: string
  occurred_on: string
  description: string | null
  is_recurring: boolean
  created_at: string
}

export interface TransactionCreatePayload {
  property_id: string
  kind: TxnKind
  category: TxnCategory
  amount: string
  occurred_on: string
  description?: string
  is_recurring?: boolean
}

export interface Lease {
  id: string
  tenant_name: string
  tenant_email: string | null
  tenant_phone: string | null
  rent: string
  deposit: string | null
  start_date: string
  end_date: string | null
  notes: string | null
  is_active: boolean
}

export interface LeaseUpsertPayload {
  tenant_name: string
  tenant_email?: string
  tenant_phone?: string
  rent: string
  deposit?: string
  start_date: string
  end_date?: string
  notes?: string
}
