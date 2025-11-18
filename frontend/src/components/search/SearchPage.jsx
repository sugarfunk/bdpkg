export default function SearchPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Search</h1>
        <p className="mt-2 text-gray-400">
          Search your knowledge graph using full-text, semantic, or natural language queries
        </p>
      </div>

      <div className="card">
        <input
          type="text"
          placeholder="Search your knowledge..."
          className="input w-full"
        />
        <div className="mt-4 text-gray-400 text-center py-12">
          <p>Enter a search query to find nodes in your knowledge graph</p>
        </div>
      </div>
    </div>
  )
}
