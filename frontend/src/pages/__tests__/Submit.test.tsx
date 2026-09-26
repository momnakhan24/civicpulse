import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import Submit from "../Submit"
import * as apiClient from "../../api/client"

describe("Submit page", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it("renders the form fields", () => {
    render(<Submit />)
    expect(screen.getByPlaceholderText(/describe the issue/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/block 5/i)).toBeInTheDocument()
  })

  it("shows a validation error when text is too short", () => {
    render(<Submit />)
    fireEvent.change(screen.getByPlaceholderText(/describe the issue/i), { target: { value: "short" } })
    fireEvent.change(screen.getByPlaceholderText(/block 5/i), { target: { value: "Test City" } })
    fireEvent.click(screen.getByText("Submit Complaint"))
    expect(screen.getByText(/at least 10 characters/i)).toBeInTheDocument()
  })

  it("shows loading state and result after successful submit", async () => {
    vi.spyOn(apiClient, "createComplaint").mockResolvedValue({
      id: "123",
      text: "Burst pipe flooding the street",
      location: "Test City",
      reporter_contact: null,
      category: "water",
      priority: "high",
      status: "open",
      ai_summary: "Burst pipe flooding",
      triaged_by: "simulated",
      triage_latency_ms: 5,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    })

    render(<Submit />)
    fireEvent.change(screen.getByPlaceholderText(/describe the issue/i), { target: { value: "Burst pipe flooding the street" } })
    fireEvent.change(screen.getByPlaceholderText(/block 5/i), { target: { value: "Test City" } })
    fireEvent.click(screen.getByText("Submit Complaint"))

    expect(await screen.findByText(/submitted successfully/i)).toBeInTheDocument()
    expect(screen.getByText(/water/i)).toBeInTheDocument()
  })

  it("shows an error message when the API call fails", async () => {
    vi.spyOn(apiClient, "createComplaint").mockRejectedValue(new Error("Rate limit exceeded"))

    render(<Submit />)
    fireEvent.change(screen.getByPlaceholderText(/describe the issue/i), { target: { value: "Burst pipe flooding the street" } })
    fireEvent.change(screen.getByPlaceholderText(/block 5/i), { target: { value: "Test City" } })
    fireEvent.click(screen.getByText("Submit Complaint"))

    expect(await screen.findByText(/rate limit exceeded/i)).toBeInTheDocument()
  })
})
