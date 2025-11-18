import { Routes, Route } from 'react-router-dom'
import Dashboard from './components/dashboard/Dashboard'
import GraphView from './components/graph/GraphView'
import SearchPage from './components/search/SearchPage'
import InsightsPage from './components/insights/InsightsPage'
import SettingsPage from './components/SettingsPage'
import Navbar from './components/Navbar'

function App() {
  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
