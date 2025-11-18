import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['graph-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/graph/statistics')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="mt-2 text-gray-400">
          Overview of your personal knowledge graph
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Nodes"
          value={stats?.total_nodes || 0}
          icon="📊"
        />
        <StatCard
          title="Total Connections"
          value={stats?.total_edges || 0}
          icon="🔗"
        />
        <StatCard
          title="New Insights"
          value={0}
          icon="💡"
        />
        <StatCard
          title="Active Integrations"
          value={0}
          icon="🔄"
        />
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="text-gray-400">
          <p>No recent activity yet. Start by adding some notes or connecting your integrations!</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickAction title="Add Note" icon="📝" />
          <QuickAction title="Import Bookmarks" icon="🔖" />
          <QuickAction title="Scan Documents" icon="📄" />
          <QuickAction title="Discover Connections" icon="🔍" />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  )
}

function QuickAction({ title, icon }) {
  return (
    <button className="card hover:bg-gray-700 transition-colors cursor-pointer text-center">
      <div className="text-3xl mb-2">{icon}</div>
      <p className="text-sm font-medium">{title}</p>
    </button>
  )
}
