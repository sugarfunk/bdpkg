"""
API routes for tag management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session
from app.models.schemas import Tag, TagCreate
from app.services.tag_service import TagService

router = APIRouter()


@router.post("/", response_model=Tag, status_code=201)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Create a new tag
    """
    tag_service = TagService(db)
    return await tag_service.create_tag(tag_data)


@router.get("/", response_model=List[Tag])
async def list_tags(
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    List all tags
    """
    tag_service = TagService(db)
    return await tag_service.list_tags(limit=limit, offset=offset)


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get a specific tag
    """
    tag_service = TagService(db)
    tag = await tag_service.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Delete a tag
    """
    tag_service = TagService(db)
    success = await tag_service.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.get("/hierarchy/tree")
async def get_tag_hierarchy(
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get hierarchical tag tree
    """
    tag_service = TagService(db)
    return await tag_service.get_tag_hierarchy()


@router.get("/popular/top")
async def get_popular_tags(
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get most popular tags by usage count
    """
    tag_service = TagService(db)
    return await tag_service.get_popular_tags(limit=limit)
