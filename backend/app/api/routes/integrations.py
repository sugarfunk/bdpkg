"""
API routes for data source integrations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session
from app.models.schemas import IntegrationConfig, SyncStatus
from app.services.integration_service import IntegrationService

router = APIRouter()


@router.get("/", response_model=List[IntegrationConfig])
async def list_integrations(
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    List all configured integrations
    """
    integration_service = IntegrationService(db)
    return await integration_service.list_integrations()


@router.get("/{integration_name}", response_model=IntegrationConfig)
async def get_integration(
    integration_name: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get configuration for a specific integration
    """
    integration_service = IntegrationService(db)
    config = await integration_service.get_integration(integration_name)
    if not config:
        raise HTTPException(status_code=404, detail="Integration not found")
    return config


@router.post("/{integration_name}/sync")
async def trigger_sync(
    integration_name: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Trigger manual sync for an integration
    """
    from app.workers.tasks import sync_integration_task

    task = sync_integration_task.delay(integration_name)

    return {
        "message": f"Sync started for {integration_name}",
        "task_id": task.id,
        "integration": integration_name
    }


@router.get("/{integration_name}/status", response_model=SyncStatus)
async def get_sync_status(
    integration_name: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get the latest sync status for an integration
    """
    integration_service = IntegrationService(db)
    status = await integration_service.get_sync_status(integration_name)
    if not status:
        raise HTTPException(status_code=404, detail="No sync status found")
    return status


@router.post("/standard-notes/configure")
async def configure_standard_notes(
    config: dict,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Configure Standard Notes integration
    """
    integration_service = IntegrationService(db)
    return await integration_service.configure_integration("standard_notes", config)


@router.post("/paperless/configure")
async def configure_paperless(
    config: dict,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Configure Paperless-ngx integration
    """
    integration_service = IntegrationService(db)
    return await integration_service.configure_integration("paperless", config)


@router.post("/bookmarks/import")
async def import_bookmarks(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Import bookmarks from browser export file (HTML or JSON)
    """
    from app.workers.tasks import import_bookmarks_task

    # Save uploaded file
    import aiofiles
    import os
    from datetime import datetime

    uploads_dir = "/app/uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bookmarks_{timestamp}_{file.filename}"
    filepath = os.path.join(uploads_dir, filename)

    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Trigger import task
    task = import_bookmarks_task.delay(filepath)

    return {
        "message": "Bookmark import started",
        "task_id": task.id,
        "filename": filename
    }


@router.post("/filesystem/scan")
async def scan_filesystem(
    path: str,
    recursive: bool = True,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Scan filesystem for documents to import
    """
    from app.workers.tasks import scan_filesystem_task

    task = scan_filesystem_task.delay(path, recursive)

    return {
        "message": "Filesystem scan started",
        "task_id": task.id,
        "path": path
    }


@router.post("/manual/quick-capture")
async def quick_capture(
    title: str,
    content: str,
    tags: List[str] = [],
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Quick capture for manual entry
    """
    from app.models.schemas import NodeCreate, NodeType
    from app.services.node_service import NodeService

    node_service = NodeService(db)
    node_data = NodeCreate(
        title=title,
        content=content,
        node_type=NodeType.NOTE,
        source="manual",
        tags=tags
    )

    node = await node_service.create_node(node_data)

    # Trigger analysis
    from app.workers.tasks import analyze_node_task
    analyze_node_task.delay(node.id)

    return node
