"""
API routes for node management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session, get_neo4j_session
from app.models.schemas import Node, NodeCreate, NodeUpdate, NodeType
from app.services.node_service import NodeService

router = APIRouter()


@router.post("/", response_model=Node, status_code=201)
async def create_node(
    node_data: NodeCreate,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Create a new node in the knowledge graph
    """
    node_service = NodeService(db)
    return await node_service.create_node(node_data)


@router.get("/{node_id}", response_model=Node)
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get a specific node by ID
    """
    node_service = NodeService(db)
    node = await node_service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/{node_id}", response_model=Node)
async def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Update an existing node
    """
    node_service = NodeService(db)
    node = await node_service.update_node(node_id, node_data)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.delete("/{node_id}", status_code=204)
async def delete_node(
    node_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Delete a node
    """
    node_service = NodeService(db)
    success = await node_service.delete_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")


@router.get("/", response_model=List[Node])
async def list_nodes(
    node_type: Optional[NodeType] = None,
    tag: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    List nodes with optional filtering
    """
    node_service = NodeService(db)
    return await node_service.list_nodes(
        node_type=node_type,
        tag=tag,
        limit=limit,
        offset=offset
    )


@router.get("/{node_id}/connections")
async def get_node_connections(
    node_id: str,
    max_depth: int = Query(default=2, ge=1, le=5),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get all connections for a specific node
    """
    node_service = NodeService(db)
    return await node_service.get_node_connections(node_id, max_depth)


@router.post("/{node_id}/analyze")
async def analyze_node(
    node_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Trigger AI analysis for a specific node
    (tagging, entity extraction, connection discovery)
    """
    node_service = NodeService(db)
    node = await node_service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Trigger async analysis
    from app.workers.tasks import analyze_node_task
    task = analyze_node_task.delay(node_id)

    return {
        "message": "Analysis started",
        "task_id": task.id,
        "node_id": node_id
    }
