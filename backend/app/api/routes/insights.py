"""
API routes for AI-generated insights
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session
from app.models.schemas import Insight, InsightType
from app.services.insight_service import InsightService

router = APIRouter()


@router.get("/", response_model=List[Insight])
async def list_insights(
    insight_type: Optional[InsightType] = None,
    acknowledged: Optional[bool] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    List AI-generated insights
    """
    insight_service = InsightService(db)
    return await insight_service.list_insights(
        insight_type=insight_type,
        acknowledged=acknowledged,
        limit=limit,
        offset=offset
    )


@router.get("/{insight_id}", response_model=Insight)
async def get_insight(
    insight_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get a specific insight
    """
    insight_service = InsightService(db)
    insight = await insight_service.get_insight(insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight


@router.post("/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Mark an insight as acknowledged
    """
    insight_service = InsightService(db)
    insight = await insight_service.acknowledge_insight(insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"message": "Insight acknowledged", "insight_id": insight_id}


@router.delete("/{insight_id}", status_code=204)
async def delete_insight(
    insight_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Delete an insight
    """
    insight_service = InsightService(db)
    success = await insight_service.delete_insight(insight_id)
    if not success:
        raise HTTPException(status_code=404, detail="Insight not found")


@router.post("/generate/connections")
async def generate_connections(
    node_id: Optional[str] = None,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Trigger AI connection discovery
    """
    from app.workers.tasks import discover_connections_task

    if node_id:
        task = discover_connections_task.delay(node_id=node_id)
    else:
        task = discover_connections_task.delay()

    return {
        "message": "Connection discovery started",
        "task_id": task.id
    }


@router.post("/generate/digest")
async def generate_digest(
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Generate insights digest for the last N days
    """
    from app.workers.tasks import generate_digest_task

    task = generate_digest_task.delay(days=days)

    return {
        "message": "Digest generation started",
        "task_id": task.id,
        "days": days
    }


@router.get("/gaps/analyze")
async def analyze_knowledge_gaps(
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Analyze knowledge gaps (areas with few connections)
    """
    insight_service = InsightService(db)
    return await insight_service.analyze_knowledge_gaps()
