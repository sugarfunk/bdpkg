"""
API routes for graph visualization and queries
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session
from app.models.schemas import GraphQuery, GraphResponse, EdgeCreate, Edge
from app.services.graph_service import GraphService

router = APIRouter()


@router.post("/query", response_model=GraphResponse)
async def query_graph(
    query: GraphQuery,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Query the knowledge graph for visualization
    """
    graph_service = GraphService(db)
    return await graph_service.query_graph(query)


@router.post("/edges", response_model=Edge, status_code=201)
async def create_edge(
    edge_data: EdgeCreate,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Create a new edge/connection between nodes
    """
    graph_service = GraphService(db)
    return await graph_service.create_edge(edge_data)


@router.delete("/edges/{edge_id}", status_code=204)
async def delete_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Delete an edge
    """
    graph_service = GraphService(db)
    success = await graph_service.delete_edge(edge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Edge not found")


@router.get("/statistics")
async def get_graph_statistics(
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get overall graph statistics
    """
    graph_service = GraphService(db)
    return await graph_service.get_statistics()


@router.get("/clusters")
async def detect_clusters(
    min_size: int = 3,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Detect and return clusters in the knowledge graph
    """
    graph_service = GraphService(db)
    return await graph_service.detect_clusters(min_size=min_size)


@router.post("/shortest-path")
async def find_shortest_path(
    source_id: str,
    target_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Find the shortest path between two nodes
    """
    graph_service = GraphService(db)
    path = await graph_service.find_shortest_path(source_id, target_id)
    if not path:
        raise HTTPException(status_code=404, detail="No path found between nodes")
    return {"path": path}
