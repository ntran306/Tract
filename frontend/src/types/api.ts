/** Hand-maintained mirrors of backend Pydantic schemas (backend/app/schemas). */

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
