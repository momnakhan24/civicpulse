import { useEffect, useState } from "react"
import { getStats } from "../api/client"
import type { Stats as StatsType } from "../api/types"

export default function Stats() {
  const [stats, setStats] = useState<StatsType | null>(null)
  const [cacheStatus, setCacheStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await getStats()
      setStats(res.data)
      setCacheStatus(res.cacheStatus)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load stats.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Statistics</h1>
        <button onClick={load} className="px-3 py-1 border rounded text-sm">Refresh</button>
      </div>

      {cacheStatus && (
        <div className={`mb-4 inline-block px-3 py-1 rounded text-sm font-medium ${cacheStatus === "HIT" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
          Cache: {cacheStatus}
        </div>
      )}

      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <div className="p-3 bg-red-100 text-red-700 rounded">{error}</div>}

      {stats && (
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h2 className="font-semibold mb-2">By Category</h2>
            <ul className="space-y-1">
              {Object.entries(stats.by_category).map(([k, v]) => (
                <li key={k} className="flex justify-between border-b py-1">
                  <span>{k}</span>
                  <span className="font-medium">{v}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="font-semibold mb-2">By Priority</h2>
            <ul className="space-y-1">
              {Object.entries(stats.by_priority).map(([k, v]) => (
                <li key={k} className="flex justify-between border-b py-1">
                  <span>{k}</span>
                  <span className="font-medium">{v}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
