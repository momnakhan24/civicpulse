import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import Stats from "../Stats"
import * as apiClient from "../../api/client"

describe("Stats page", () => {
  it("renders cache status and stats after loading", async () => {
    vi.spyOn(apiClient, "getStats").mockResolvedValue({
      data: { by_category: { water: 3 }, by_priority: { high: 2 } },
      cacheStatus: "HIT",
    })

    render(<Stats />)

    expect(await screen.findByText(/cache: hit/i)).toBeInTheDocument()
    expect(screen.getByText("water")).toBeInTheDocument()
  })
})
