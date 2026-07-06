import { BedDouble, Building2, Hammer, House, KeyRound } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { PropertyKind, TxnCategory, TxnKind } from '../../types/api'

export const KIND_META: Record<PropertyKind, { label: string; icon: LucideIcon }> = {
  my_home: { label: 'My Home', icon: House },
  rental: { label: 'Rental', icon: KeyRound },
  airbnb: { label: 'Airbnb', icon: BedDouble },
  flip: { label: 'Flip', icon: Hammer },
  other: { label: 'Other', icon: Building2 },
}

export const INCOME_CATEGORIES: TxnCategory[] = ['rent', 'airbnb_payout', 'other_income']

export const EXPENSE_CATEGORIES: TxnCategory[] = [
  'mortgage',
  'property_tax',
  'insurance',
  'hoa',
  'utilities',
  'repairs',
  'maintenance',
  'cleaning',
  'management_fee',
  'renovation',
  'listing_fee',
  'other_expense',
]

export const CATEGORY_LABELS: Record<TxnCategory, string> = {
  rent: 'Rent',
  airbnb_payout: 'Airbnb payout',
  other_income: 'Other income',
  mortgage: 'Mortgage',
  property_tax: 'Property tax',
  insurance: 'Insurance',
  hoa: 'HOA',
  utilities: 'Utilities',
  repairs: 'Repairs',
  maintenance: 'Maintenance',
  cleaning: 'Cleaning',
  management_fee: 'Management fee',
  renovation: 'Renovation',
  listing_fee: 'Listing fee',
  other_expense: 'Other expense',
}

export function categoriesFor(kind: TxnKind): TxnCategory[] {
  return kind === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES
}

export const SOURCE_LABELS: Record<string, string> = {
  manual: 'manual entry',
  purchase_price: 'purchase price',
  hpi_estimate: 'index-based estimate',
  rentcast: 'AVM estimate',
}
