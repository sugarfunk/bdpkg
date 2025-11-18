export default function GraphView() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Knowledge Graph</h1>
        <p className="mt-2 text-gray-400">
          Interactive visualization of your knowledge graph
        </p>
      </div>

      <div className="card">
        <div className="h-[600px] flex items-center justify-center text-gray-400">
          <div className="text-center">
            <p className="text-xl mb-4">Graph visualization coming soon!</p>
            <p className="text-sm">
              This will display an interactive node-based visualization using Cytoscape.js
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
