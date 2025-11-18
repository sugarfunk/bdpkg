"""
API routes for search functionality
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session
from app.models.schemas import SearchQuery, SearchResult
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/", response_model=List[SearchResult])
async def search(
    query: SearchQuery,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Search the knowledge graph using various search methods
    - full_text: Traditional full-text search
    - semantic: Vector-based semantic similarity search
    - natural_language: Natural language query using LLM
    """
    search_service = SearchService(db)
    return await search_service.search(query)


@router.get("/suggest")
async def suggest(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get search suggestions/autocomplete
    """
    search_service = SearchService(db)
    return await search_service.suggest(q, limit)


@router.get("/random")
async def random_discovery(
    count: int = Query(default=5, le=20),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Random discovery mode - surface forgotten/buried insights
    """
    search_service = SearchService(db)
    return await search_service.random_discovery(count)


@router.post("/similar/{node_id}")
async def find_similar(
    node_id: str,
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Find nodes similar to a specific node using semantic similarity
    """
    search_service = SearchService(db)
    return await search_service.find_similar(node_id, limit)
