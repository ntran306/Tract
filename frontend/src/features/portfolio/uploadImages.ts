import { supabase } from '../../lib/supabase'
import { api } from '../../lib/api'
import type { PropertyImage } from '../../types/api'

const BUCKET = 'property-images'

/** Upload files straight to Supabase Storage (bytes never touch our API), then
 *  record each object key against the property via the backend. Files are keyed
 *  under `${propertyId}/` so the API's folder guard accepts them. */
export async function uploadPropertyImages(
  propertyId: string,
  files: File[],
): Promise<PropertyImage[]> {
  const out: PropertyImage[] = []
  for (const file of files) {
    const ext = file.name.split('.').pop() ?? 'jpg'
    const path = `${propertyId}/${crypto.randomUUID()}.${ext}`
    const { error } = await supabase.storage.from(BUCKET).upload(path, file, {
      cacheControl: '3600',
      upsert: false,
    })
    if (error) throw new Error(`Upload failed: ${error.message}`)
    const image = await api<PropertyImage>(`/api/v1/properties/${propertyId}/images`, {
      method: 'POST',
      body: JSON.stringify({ storage_path: path }),
    })
    out.push(image)
  }
  return out
}
