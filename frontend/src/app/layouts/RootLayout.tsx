import { Outlet } from 'react-router-dom'
import { Header } from '../../components/shared/Header'
import { MessagingDock } from '../../features/messaging/MessagingDock'

export function RootLayout() {
  return (
    <div className="min-h-screen bg-bg text-text">
      <Header />
      <Outlet />
      {/* Persists across all tabs — messaging + AI assistant live here (M3). */}
      <MessagingDock />
    </div>
  )
}
