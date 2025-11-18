# Personal Knowledge Graph Builder

A self-hosted personal knowledge management system that creates visual knowledge graphs by connecting information from multiple sources and uses AI to discover non-obvious connections and insights.

## Features

### Core Functionality

- **Knowledge Graph Visualization**: Interactive node-based visualization with zoom, pan, filter, and search capabilities
- **Multi-Source Integration**: Connect Standard Notes, Paperless-ngx, bookmarks, file system, RSS feeds, email, and more
- **AI-Powered Insights**: Automatic connection discovery, pattern recognition, and insight generation
- **Multi-LLM Support**: Use Anthropic Claude, OpenAI, Google Gemini, or local Ollama models
- **Privacy-First**: Self-hosted with configurable privacy levels and local LLM support for sensitive content
- **Smart Search**: Full-text, semantic, and natural language search capabilities

### Key Features

- Interactive graph visualization with clustering
- Automatic tag generation and entity extraction
- Connection discovery between seemingly unrelated content
- Knowledge gap analysis
- Daily/weekly insight digests
- Privacy mode for sensitive content
- Cost tracking for LLM usage
- Multiple visualization modes (graph, list, timeline, heatmap)

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Neo4j** - Graph database for knowledge relationships
- **PostgreSQL** - Metadata and full-text search
- **Redis** - Caching and Celery broker
- **Celery** - Background task processing
- **LiteLLM** - Multi-LLM support

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Cytoscape.js** - Graph visualization
- **TailwindCSS** - Styling
- **React Query** - Data fetching

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 4GB RAM
- (Optional) API keys for LLM providers

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bdpkg
```

2. Copy the environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

### Initial Setup

1. Configure your LLM providers in the Settings page
2. Add API keys in the `.env` file
3. Set up integrations (Standard Notes, Paperless, etc.)
4. Start adding content or sync your existing data

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `DEFAULT_LLM_PROVIDER` - Default LLM provider (anthropic, openai, ollama, gemini)
- `USE_LOCAL_LLM_FOR_SENSITIVE` - Use only local models for sensitive content
- `SENSITIVE_TAGS` - Tags that mark content as sensitive

### LLM Configuration

The system supports multiple LLM providers with task-specific configuration:

- **Tagging**: Fast, cheap model (e.g., Claude Haiku)
- **Connections**: Powerful model (e.g., Claude Sonnet)
- **Insights**: Powerful model (e.g., Claude Sonnet)

Configure in `.env`:
```bash
TAGGING_LLM_PROVIDER=anthropic
TAGGING_LLM_MODEL=claude-3-haiku-20240307
CONNECTION_LLM_PROVIDER=anthropic
CONNECTION_LLM_MODEL=claude-3-5-sonnet-20241022
```

### Privacy Settings

Content tagged with sensitive tags will automatically use local LLM models (Ollama) to ensure privacy.

Default sensitive tags:
- personal
- anxiety
- therapy
- procurement-contract
- confidential
- private

## Integrations

### Standard Notes
1. Configure in Settings or `.env`
2. Provide server URL, email, and password
3. Trigger sync from the Integrations page

### Paperless-ngx
1. Get API token from Paperless
2. Configure URL and token in Settings
3. Sync documents and metadata

### Bookmarks
1. Export bookmarks from your browser (HTML or JSON)
2. Upload via the Integrations page
3. Bookmarks will be imported as nodes

### File System
1. Provide path to scan
2. Supported formats: .md, .txt, .pdf, .docx
3. Files will be indexed and analyzed

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs

Key endpoints:
- `/api/v1/nodes` - Node management
- `/api/v1/graph` - Graph queries and visualization
- `/api/v1/search` - Search functionality
- `/api/v1/insights` - AI insights
- `/api/v1/integrations` - Integration management
- `/api/v1/llm` - LLM configuration and costs

## Development

### Project Structure

```
bdpkg/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core configuration
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   ├── workers/          # Celery tasks
│   │   └── integrations/     # Integration code
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API clients
│   │   └── styles/           # CSS
│   ├── Dockerfile
│   └── package.json
├── docs/                     # Documentation
├── config/                   # Configuration files
├── scripts/                  # Utility scripts
└── docker-compose.yml
```

### Running in Development

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Celery Worker:
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

Celery Beat:
```bash
cd backend
celery -A app.workers.celery_app beat --loglevel=info
```

### Testing

```bash
cd backend
pytest
```

## Use Cases

### Procurement Professional
- Track vendor relationships and contract terms
- Connect negotiations across years
- Link technical requirements to business outcomes

### Personal Development
- Track anxiety management techniques
- Connect therapy insights to life situations
- Monitor thought pattern changes

### Business Management
- Connect client requests to solutions
- Track what works for different client types
- Link marketing ideas to implementations

### Technical Knowledge
- Connect troubleshooting across services
- Track technology evaluations
- Link infrastructure decisions to outcomes

## Roadmap

### Phase 1 (Current)
- [x] Project structure and Docker setup
- [ ] Core data models and graph schema
- [ ] Multi-LLM support implementation
- [ ] Basic integrations (Standard Notes, Paperless)
- [ ] Graph visualization

### Phase 2
- [ ] Advanced AI connection discovery
- [ ] Full search implementation
- [ ] Insight generation engine
- [ ] All integrations complete

### Phase 3
- [ ] Web clipper browser extension
- [ ] Mobile app
- [ ] Advanced visualization modes
- [ ] Collaboration features

## Contributing

This is a personal project, but suggestions and contributions are welcome!

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please use the GitHub issue tracker.

## Acknowledgments

Built with:
- FastAPI
- React
- Neo4j
- PostgreSQL
- Cytoscape.js
- And many other amazing open source projects
