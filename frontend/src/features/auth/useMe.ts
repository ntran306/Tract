import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/api'
import type { Profile } from '../../types/api'
import { useSession } from './useSession'

/** The signed-in user's profile from the backend — proves the full
 *  frontend -> FastAPI -> Supabase JWT -> Postgres loop works. */
export function useMe() {
  const { session } = useSession()
  return useQuery({
    queryKey: ['me'],
    queryFn: () => api<Profile>('/api/v1/auth/me'),
    enabled: Boolean(session),
    staleTime: 60_000,
  })
}
