import { useQuery } from '@tanstack/react-query'

import { Button } from '@/components/ui/button'

import { fetchHealth } from '../api/fetch-health'

export function HealthStatusCard() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['health-status'],
    queryFn: fetchHealth,
  })

  return (
    <section className="mx-auto mt-20 max-w-xl rounded-xl border border-slate-700 bg-slate-900 p-6">
      <h1 className="mb-2 text-2xl font-semibold">QanunAI Frontend</h1>
      <p className="mb-4 text-slate-300">React + TanStack Query + shadcn/ui + Zod + ai-elements-ready setup.</p>

      {isLoading && <p className="text-slate-300">Checking backend health…</p>}
      {isError && <p className="text-red-300">Backend is unreachable.</p>}
      {data && (
        <p className="mb-4 text-emerald-300">
          Backend status: <strong>{data.status}</strong>
        </p>
      )}

      <Button variant="secondary" onClick={() => refetch()}>
        Refresh status
      </Button>
    </section>
  )
}
