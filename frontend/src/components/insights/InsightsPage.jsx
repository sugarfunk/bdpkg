export default function InsightsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">AI Insights</h1>
        <p className="mt-2 text-gray-400">
          AI-discovered connections, patterns, and recommendations
        </p>
      </div>

      <div className="card">
        <div className="text-gray-400 text-center py-12">
          <p>No insights yet. The AI will discover connections as you add more content!</p>
        </div>
      </div>
    </div>
  )
}
