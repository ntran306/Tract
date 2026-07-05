import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined

export const supabaseConfigured = Boolean(url && anonKey)

if (!supabaseConfigured) {
  console.warn(
    'Supabase env vars missing — copy frontend/.env.example to .env.local and fill it in. ' +
      'The app renders, but sign-in will not work until then.',
  )
}

// Placeholder values keep the app rendering when unconfigured; auth calls just fail.
export const supabase = createClient(
  url ?? 'http://localhost:54321',
  anonKey ?? 'unconfigured',
)
