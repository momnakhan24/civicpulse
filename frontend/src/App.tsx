import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom"
import Submit from "./pages/Submit"
import Dashboard from "./pages/Dashboard"
import Stats from "./pages/Stats"

function NavBar() {
  const location = useLocation()
  const linkClass = (path: string) =>
    `px-4 py-2 rounded ${location.pathname === path ? "bg-blue-600 text-white" : "text-gray-700 hover:bg-gray-100"}`

  return (
    <nav className="border-b p-4 flex gap-2 mb-4">
      <Link to="/" className={linkClass("/")}>Submit</Link>
      <Link to="/dashboard" className={linkClass("/dashboard")}>Dashboard</Link>
      <Link to="/stats" className={linkClass("/stats")}>Stats</Link>
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Submit />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/stats" element={<Stats />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
