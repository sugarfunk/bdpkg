"""LLM service with database tracking"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.schemas import LLMRequest, LLMResponse, LLMProvider, LLMCostSummary
from app.models.db_models import LLMRequestLog
from app.services.llm_manager import llm_manager


class LLMService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def query(self, request: LLMRequest) -> LLMResponse:
        """Query LLM and log the request"""
        result = await llm_manager.generate_completion(
            prompt=request.prompt,
            provider=request.provider.value,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            metadata=request.metadata
        )

        # Log the request to database
        await self._log_request(result)

        return LLMResponse(
            provider=request.provider,
            model=result["model"],
            response=result["response"] or "",
            tokens_used=result.get("tokens_used", 0),
            cost=result.get("cost", 0.0),
            metadata=result.get("metadata", {})
        )

    async def _log_request(self, result: dict):
        """Log LLM request to database"""
        log_entry = LLMRequestLog(
            request_id=result["request_id"],
            provider=result["provider"],
            model=result["model"],
            purpose=result.get("metadata", {}).get("purpose"),
            prompt_tokens=result.get("prompt_tokens", 0),
            completion_tokens=result.get("completion_tokens", 0),
            total_tokens=result.get("tokens_used", 0),
            cost=result.get("cost", 0.0),
            latency_ms=result.get("latency_ms", 0),
            success=result.get("success", True),
            error=result.get("error"),
            metadata=result.get("metadata", {})
        )
        self.db.add(log_entry)
        await self.db.commit()

    async def get_cost_summary(self, start_date: datetime, end_date: datetime) -> LLMCostSummary:
        """Get cost summary for a time period"""
        query = select(
            func.sum(LLMRequestLog.cost).label("total_cost"),
            func.sum(LLMRequestLog.total_tokens).label("total_tokens"),
            LLMRequestLog.provider,
            LLMRequestLog.model
        ).where(
            LLMRequestLog.created_at >= start_date,
            LLMRequestLog.created_at <= end_date
        ).group_by(LLMRequestLog.provider, LLMRequestLog.model)

        result = await self.db.execute(query)
        records = result.all()

        total_cost = 0.0
        total_tokens = 0
        by_provider = {}
        by_model = {}

        for record in records:
            cost = float(record.total_cost or 0.0)
            tokens = int(record.total_tokens or 0)

            total_cost += cost
            total_tokens += tokens

            # Group by provider
            if record.provider not in by_provider:
                by_provider[record.provider] = 0.0
            by_provider[record.provider] += cost

            # Group by model
            model_key = f"{record.provider}/{record.model}"
            if model_key not in by_model:
                by_model[model_key] = 0.0
            by_model[model_key] += cost

        return LLMCostSummary(
            total_cost=round(total_cost, 6),
            by_provider=by_provider,
            by_model=by_model,
            total_tokens=total_tokens,
            period_start=start_date,
            period_end=end_date
        )

    async def get_provider_costs(self, provider: LLMProvider, start_date: datetime, end_date: datetime):
        """Get detailed costs for a specific provider"""
        query = select(
            LLMRequestLog.model,
            func.count(LLMRequestLog.id).label("request_count"),
            func.sum(LLMRequestLog.total_tokens).label("total_tokens"),
            func.sum(LLMRequestLog.cost).label("total_cost"),
            func.avg(LLMRequestLog.latency_ms).label("avg_latency")
        ).where(
            LLMRequestLog.provider == provider.value,
            LLMRequestLog.created_at >= start_date,
            LLMRequestLog.created_at <= end_date
        ).group_by(LLMRequestLog.model)

        result = await self.db.execute(query)
        records = result.all()

        return {
            "provider": provider.value,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "models": [
                {
                    "model": record.model,
                    "request_count": record.request_count,
                    "total_tokens": int(record.total_tokens or 0),
                    "total_cost": float(record.total_cost or 0.0),
                    "avg_latency_ms": int(record.avg_latency or 0)
                }
                for record in records
            ]
        }

    async def get_usage_stats(self, start_date: datetime, end_date: datetime):
        """Get usage statistics"""
        query = select(
            func.count(LLMRequestLog.id).label("total_requests"),
            func.sum(LLMRequestLog.total_tokens).label("total_tokens"),
            func.sum(LLMRequestLog.cost).label("total_cost"),
            func.avg(LLMRequestLog.latency_ms).label("avg_latency"),
            func.sum(func.cast(LLMRequestLog.success, func.Integer)).label("successful_requests")
        ).where(
            LLMRequestLog.created_at >= start_date,
            LLMRequestLog.created_at <= end_date
        )

        result = await self.db.execute(query)
        record = result.first()

        if not record:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency_ms": 0
            }

        return {
            "total_requests": record.total_requests or 0,
            "successful_requests": record.successful_requests or 0,
            "total_tokens": int(record.total_tokens or 0),
            "total_cost": float(record.total_cost or 0.0),
            "avg_latency_ms": int(record.avg_latency or 0),
            "success_rate": (record.successful_requests / record.total_requests * 100) if record.total_requests > 0 else 0.0
        }

    async def test_connection(self, provider: LLMProvider, model: str = None):
        """Test LLM connection"""
        return await llm_manager.test_connection(provider.value, model)
