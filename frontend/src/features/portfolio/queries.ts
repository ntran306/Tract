import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../lib/api'
import type {
  PortfolioSummary,
  Lease,
  LeaseUpsertPayload,
  Property,
  PropertyCreatePayload,
  PropertyKind,
  Transaction,
  TransactionCreatePayload,
  Valuation,
} from '../../types/api'

const BASE = '/api/v1'

export function useProperties(kind?: PropertyKind | null) {
  return useQuery({
    queryKey: ['properties', kind ?? 'all'],
    queryFn: () =>
      api<Property[]>(`${BASE}/properties${kind ? `?kind=${kind}` : ''}`),
    staleTime: 30_000,
  })
}

export function useProperty(id: string) {
  return useQuery({
    queryKey: ['property', id],
    queryFn: () => api<Property>(`${BASE}/properties/${id}`),
    staleTime: 30_000,
  })
}

function useInvalidateProperties() {
  const qc = useQueryClient()
  return (id?: string) => {
    void qc.invalidateQueries({ queryKey: ['properties'] })
    if (id) void qc.invalidateQueries({ queryKey: ['property', id] })
  }
}

export function useCreateProperty() {
  const invalidate = useInvalidateProperties()
  return useMutation({
    mutationFn: (payload: PropertyCreatePayload) =>
      api<Property>(`${BASE}/properties`, { method: 'POST', body: JSON.stringify(payload) }),
    onSuccess: () => invalidate(),
  })
}

export function useUpdateProperty(id: string) {
  const invalidate = useInvalidateProperties()
  return useMutation({
    mutationFn: (payload: Partial<PropertyCreatePayload> & { status?: string }) =>
      api<Property>(`${BASE}/properties/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => invalidate(id),
  })
}

export function useDeleteProperty() {
  const invalidate = useInvalidateProperties()
  return useMutation({
    mutationFn: (id: string) => api<void>(`${BASE}/properties/${id}`, { method: 'DELETE' }),
    onSuccess: () => invalidate(),
  })
}

export function useValuations(propertyId: string) {
  return useQuery({
    queryKey: ['valuations', propertyId],
    queryFn: () => api<Valuation[]>(`${BASE}/properties/${propertyId}/valuations`),
  })
}

export function useAddValuation(propertyId: string) {
  const qc = useQueryClient()
  const invalidate = useInvalidateProperties()
  return useMutation({
    mutationFn: (payload: { value: string; valued_at: string; note?: string }) =>
      api<Valuation>(`${BASE}/properties/${propertyId}/valuations`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['valuations', propertyId] })
      invalidate(propertyId)
    },
  })
}

export function useTransactions(propertyId: string) {
  return useQuery({
    queryKey: ['transactions', propertyId],
    queryFn: () =>
      api<Transaction[]>(`${BASE}/transactions?property_id=${propertyId}&limit=200`),
  })
}

export function useCreateTransaction(propertyId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: TransactionCreatePayload) =>
      api<Transaction>(`${BASE}/transactions`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['transactions', propertyId] }),
  })
}

export function useDeleteTransaction(propertyId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api<void>(`${BASE}/transactions/${id}`, { method: 'DELETE' }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['transactions', propertyId] }),
  })
}

export function useLease(propertyId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['lease', propertyId],
    queryFn: async () => {
      try {
        return await api<Lease>(`${BASE}/properties/${propertyId}/lease`)
      } catch (e) {
        if ((e as { status?: number }).status === 404) return null
        throw e
      }
    },
    enabled,
  })
}

export function useUpsertLease(propertyId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: LeaseUpsertPayload) =>
      api<Lease>(`${BASE}/properties/${propertyId}/lease`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['lease', propertyId] }),
  })
}

export function useDeleteLease(propertyId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api<void>(`${BASE}/properties/${propertyId}/lease`, { method: 'DELETE' }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['lease', propertyId] }),
  })
}

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ['portfolio-summary'],
    queryFn: () => api<PortfolioSummary>(`${BASE}/analytics/portfolio`),
    staleTime: 30_000,
  })
}

export function useHpiEstimate(propertyId: string) {
  const qc = useQueryClient()
  const invalidate = useInvalidateProperties()
  return useMutation({
    mutationFn: () =>
      api<Valuation>(`${BASE}/properties/${propertyId}/hpi-estimate`, { method: 'POST' }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['valuations', propertyId] })
      invalidate(propertyId)
    },
  })
}

export interface RentBenchmark {
  rent: string
  fmr: string
  area_name: string
  bedrooms: number
  delta_pct: string
}

/** Rent vs area FMR. Returns null until HUD FMR data exists (404) so the chip
 *  simply hides now and lights up automatically once the FMR worker has run. */
export function useRentBenchmark(state: string | null, bedrooms: number | null, rent: string | null) {
  const enabled = Boolean(state && bedrooms != null && rent)
  return useQuery({
    queryKey: ['rent-benchmark', state, bedrooms, rent],
    enabled,
    queryFn: async () => {
      try {
        return await api<RentBenchmark>(
          `${BASE}/market/rent-benchmark?state=${state}&bedrooms=${bedrooms}&rent=${rent}`,
        )
      } catch (e) {
        if ((e as { status?: number }).status === 404) return null
        throw e
      }
    },
  })
}
