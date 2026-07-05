import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useSession } from './useSession'

export function RequireAuth() {
  const { session, loading } = useSession()
  const location = useLocation()

  if (loading) return null
  if (!session) return <Navigate to="/auth" state={{ from: location }} replace />
  return <Outlet />
}
