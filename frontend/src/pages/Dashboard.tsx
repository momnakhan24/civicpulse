import { useEffect, useState } from "react"
import { listComplaints, updateStatus } from "../api/client"
import type { Complaint } from "../api/types"

const STATUS_OPTIONS = ["open", "in_progress", "resolved", "rejected"]

export default function Dashboard() {
  const [items, setItems] = useState<Complaint[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [categoryFilter, setCategoryFilter] = useState("")
  const [priorityFilter, setPriorityFilter] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await listComplaints({
        category: categoryFilter || undefined,
        priority: priorityFilter || undefined,
        status: statusFilter || undefined,
        page,
        page_size: 10,
      })
      setItems(res.items)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load complaints.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, categoryFilter, priorityFilter, statusFilter])

  async function handleStatusChange(id: string, newStatus: string) {
    setError(null)
    const result = await updateStatus(id, newStatus)
    if (!result.ok) {
      setError(result.message)
      return
    }
    load()
  }

  const totalPages = Math.max(1, Math.ceil(total / 10))

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Operations Dashboard</h1>

      <div className="flex gap-3 mb-4">
        <select className="border rounded p-2" value={categoryFilter} onChange={(e) => { setPage(1); setCategoryFilter(e.target.value) }}>
          <option value="">All Categories</option>
          <option value="water">Water</option>
          <option value="electricity">Electricity</option>
          <option value="sanitation">Sanitation</option>
          <option value="roads">Roads</option>
          <option value="streetlights">Streetlights</option>
          <option value="other">Other</option>
        </select>

        <select className="border rounded p-2" value={priorityFilter} onChange={(e) => { setPage(1); setPriorityFilter(e.target.value) }}>
          <option value="">All Priorities</option>
          <option value="high">High</option>
          <option value="normal">Normal</option>
          <option value="low">Low</option>
        </select>

        <select className="border rounded p-2" value={statusFilter} onChange={(e) => { setPage(1); setStatusFilter(e.target.value) }}>
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>}
      {loading && <p className="text-gray-500">Loading...</p>}

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b text-left">
            <th className="p-2">Text</th>
            <th className="p-2">Category</th>
            <th className="p-2">Priority</th>
            <th className="p-2">Status</th>
            <th className="p-2">Change Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b">
              <td className="p-2 max-w-xs truncate">{item.text}</td>
              <td className="p-2">{item.category}</td>
              <td className="p-2">{item.priority}</td>
              <td className="p-2">{item.status}</td>
              <td className="p-2">
                <select
                  className="border rounded p-1"
                  value=""
                  onChange={(e) => {
                    if (e.target.value) handleStatusChange(item.id, e.target.value)
                  }}
                >
                  <option value="">Change to...</option>
                  {STATUS_OPTIONS.filter((s) => s !== item.status).map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex gap-2 mt-4 items-center">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          Previous
        </button>
        <span>Page {page} of {totalPages}</span>
        <button
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
          className="px-3 py-1 border rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  )
}
