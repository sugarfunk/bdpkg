"""
API routes for Personal Knowledge Graph Builder
"""
from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include sub-routers
from app.api.routes import (
    nodes,
    graph,
    search,
    insights,
    integrations,
    llm,
    tags
)

# Include all route modules
api_router.include_router(nodes.router, prefix="/nodes", tags=["Nodes"])
api_router.include_router(graph.router, prefix="/graph", tags=["Graph"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(llm.router, prefix="/llm", tags=["LLM"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])

__all__ = ["api_router"]
