import { healthSchema, type HealthResponse } from '../schemas/health.schema'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health/`)

  if (!response.ok) {
    throw new Error('Unable to reach backend service.')
  }

  const payload = await response.json()
  return healthSchema.parse(payload)
}
