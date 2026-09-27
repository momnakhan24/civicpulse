import { useState } from "react"
import { createComplaint } from "../api/client"
import type { Complaint } from "../api/types"

export default function Submit() {
  const [text, setText] = useState("")
  const [location, setLocation] = useState("")
  const [contact, setContact] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<Complaint | null>(null)

  function validate(): string | null {
    if (text.trim().length < 10) return "Complaint text must be at least 10 characters."
    if (text.trim().length > 2000) return "Complaint text must be under 2000 characters."
    if (location.trim().length < 3) return "Location must be at least 3 characters."
    return null
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setResult(null)

    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)
    try {
      const complaint = await createComplaint({
        text: text.trim(),
        location: location.trim(),
        reporter_contact: contact.trim() || null,
      })
      setResult(complaint)
      setText("")
      setLocation("")
      setContact("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Report a Complaint</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Complaint details</label>
          <textarea
            className="w-full border rounded p-2"
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe the issue in detail..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Location</label>
          <input
            className="w-full border rounded p-2"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. Block 5, Gulshan"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Contact (optional)</label>
          <input
            className="w-full border rounded p-2"
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            placeholder="Phone or email"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Analyzing your complaint..." : "Submit Complaint"}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-300 rounded space-y-1">
          <p className="font-semibold text-green-800">Complaint submitted successfully</p>
          <p><span className="font-medium">Category:</span> {result.category}</p>
          <p><span className="font-medium">Priority:</span> {result.priority}</p>
          <p><span className="font-medium">Summary:</span> {result.ai_summary}</p>
          <p><span className="font-medium">Triaged by:</span> {result.triaged_by}</p>
        </div>
      )}
    </div>
  )
}
