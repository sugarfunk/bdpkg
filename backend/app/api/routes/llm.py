"""
API routes for LLM management and cost tracking
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_postgres_session
from app.models.schemas import LLMRequest, LLMResponse, LLMCostSummary, LLMProvider
from app.services.llm_service import LLMService

router = APIRouter()


@router.post("/query", response_model=LLMResponse)
async def query_llm(
    request: LLMRequest,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Direct LLM query endpoint (for testing and development)
    """
    llm_service = LLMService(db)
    return await llm_service.query(request)


@router.get("/providers")
async def list_providers():
    """
    List all available LLM providers and their configured models
    """
    from app.core.config import settings

    providers = {
        "anthropic": {
            "enabled": bool(settings.ANTHROPIC_API_KEY),
            "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            "default": settings.DEFAULT_LLM_PROVIDER == "anthropic"
        },
        "openai": {
            "enabled": bool(settings.OPENAI_API_KEY),
            "models": ["gpt-4-turbo-preview", "gpt-3.5-turbo"],
            "default": settings.DEFAULT_LLM_PROVIDER == "openai"
        },
        "ollama": {
            "enabled": True,  # Assume Ollama is always available locally
            "models": [settings.OLLAMA_MODEL],
            "default": settings.DEFAULT_LLM_PROVIDER == "ollama",
            "url": settings.OLLAMA_BASE_URL
        },
        "gemini": {
            "enabled": bool(settings.GOOGLE_API_KEY),
            "models": ["gemini-pro"],
            "default": settings.DEFAULT_LLM_PROVIDER == "gemini"
        }
    }

    return {
        "providers": providers,
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "task_specific": {
            "tagging": {
                "provider": settings.TAGGING_LLM_PROVIDER,
                "model": settings.TAGGING_LLM_MODEL
            },
            "connections": {
                "provider": settings.CONNECTION_LLM_PROVIDER,
                "model": settings.CONNECTION_LLM_MODEL
            },
            "insights": {
                "provider": settings.INSIGHT_LLM_PROVIDER,
                "model": settings.INSIGHT_LLM_MODEL
            }
        }
    }


@router.get("/costs", response_model=LLMCostSummary)
async def get_costs(
    days: int = Query(default=7, ge=1, le=365),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get LLM cost summary for the specified period
    """
    llm_service = LLMService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    return await llm_service.get_cost_summary(start_date, end_date)


@router.get("/costs/by-provider")
async def get_costs_by_provider(
    provider: LLMProvider,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get detailed cost breakdown for a specific provider
    """
    llm_service = LLMService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    return await llm_service.get_provider_costs(provider, start_date, end_date)


@router.get("/usage/stats")
async def get_usage_stats(
    days: int = Query(default=7, ge=1, le=365),
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Get LLM usage statistics
    """
    llm_service = LLMService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    return await llm_service.get_usage_stats(start_date, end_date)


@router.post("/test-connection")
async def test_llm_connection(
    provider: LLMProvider,
    model: Optional[str] = None,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Test connection to a specific LLM provider
    """
    llm_service = LLMService(db)
    result = await llm_service.test_connection(provider, model)

    return {
        "provider": provider,
        "model": model,
        "success": result["success"],
        "message": result.get("message", "Connection successful"),
        "error": result.get("error")
    }
