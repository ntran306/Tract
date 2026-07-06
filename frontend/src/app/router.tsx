import { createBrowserRouter, Navigate } from 'react-router-dom'
import { RootLayout } from './layouts/RootLayout'
import { ManageLayout } from './layouts/ManageLayout'
import { RequireAuth } from '../features/auth/RequireAuth'
import { AuthPage } from '../features/auth/AuthPage'
import { SummaryPage } from '../features/portfolio/SummaryPage'
import { OwnedPage } from '../features/portfolio/OwnedPage'
import { PropertyDetailPage } from '../features/portfolio/PropertyDetailPage'
import { HomePage } from '../pages/HomePage'
import { AboutPage } from '../pages/AboutPage'
import { StubPage } from '../pages/StubPage'

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/about', element: <AboutPage /> },
      { path: '/auth', element: <AuthPage /> },
      {
        element: <RequireAuth />,
        children: [
          {
            path: '/manage',
            element: <ManageLayout />,
            children: [
              { index: true, element: <Navigate to="/manage/summary" replace /> },
              { path: 'summary', element: <SummaryPage /> },
              { path: 'owned', element: <OwnedPage /> },
              { path: 'owned/:id', element: <PropertyDetailPage /> },
            ],
          },
          { path: '/profile', element: <StubPage title="Profile" milestone="M4" /> },
          { path: '/settings', element: <StubPage title="Settings" milestone="M4" /> },
          { path: '/admin', element: <StubPage title="Admin" milestone="M4" /> },
        ],
      },
    ],
  },
])
