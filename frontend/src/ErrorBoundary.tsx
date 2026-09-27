import { Component, type ReactNode } from "react"

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-xl mx-auto p-6 text-center">
          <h1 className="text-xl font-bold text-red-700">Something went wrong</h1>
          <p className="text-gray-600 mt-2">Please refresh the page and try again.</p>
        </div>
      )
    }
    return this.props.children
  }
}
