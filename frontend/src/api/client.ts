import type { Complaint, ComplaintCreate, ComplaintListResponse, Stats } from "./types"

const BASE = "/api"

export async function createComplaint(data: ComplaintCreate): Promise<Complaint> {
  const res = await fetch(`${BASE}/complaints`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ? JSON.stringify(err.detail) : `Request failed: ${res.status}`)
  }
  return res.json()
}

export async function listComplaints(params: {
  category?: string
  priority?: string
  status?: string
  page?: number
  page_size?: number
}): Promise<ComplaintListResponse> {
  const query = new URLSearchParams()
  if (params.category) query.set("category", params.category)
  if (params.priority) query.set("priority", params.priority)
  if (params.status) query.set("status", params.status)
  query.set("page", String(params.page ?? 1))
  query.set("page_size", String(params.page_size ?? 20))

  const res = await fetch(`${BASE}/complaints?${query.toString()}`)
  if (!res.ok) throw new Error(`Failed to list complaints: ${res.status}`)
  return res.json()
}

export async function updateStatus(id: string, status: string): Promise<{ ok: true; data: Complaint } | { ok: false; message: string }> {
  const res = await fetch(`${BASE}/complaints/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    return { ok: false, message: err.detail ?? `Request failed: ${res.status}` }
  }
  return { ok: true, data: await res.json() }
}

export async function getStats(): Promise<{ data: Stats; cacheStatus: string | null }> {
  const res = await fetch(`${BASE}/stats`)
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.status}`)
  const cacheStatus = res.headers.get("X-Cache")
  const data = await res.json()
  return { data, cacheStatus }
}
