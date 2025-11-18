"""
LLM Manager with multi-provider support using LiteLLM
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import time
from loguru import logger

try:
    import litellm
    from litellm import completion, embedding, acompletion, aembedding
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.warning("LiteLLM not available. Install with: pip install litellm")

from app.core.config import settings


class LLMManager:
    """Manager for multi-LLM provider support"""

    def __init__(self):
        self.setup_providers()

    def setup_providers(self):
        """Setup LiteLLM with provider configurations"""
        if not LITELLM_AVAILABLE:
            return

        # Set API keys
        if settings.ANTHROPIC_API_KEY:
            litellm.anthropic_key = settings.ANTHROPIC_API_KEY

        if settings.OPENAI_API_KEY:
            litellm.openai_key = settings.OPENAI_API_KEY

        if settings.GOOGLE_API_KEY:
            litellm.google_api_key = settings.GOOGLE_API_KEY

        # Configure Ollama
        litellm.ollama_url = settings.OLLAMA_BASE_URL

        # Enable verbose logging if DEBUG
        if settings.DEBUG:
            litellm.set_verbose = True

        logger.info("LLM providers configured")

    def get_model_string(self, provider: str, model: str) -> str:
        """Get LiteLLM model string for the provider"""
        model_mappings = {
            "anthropic": f"claude/{model}" if not model.startswith("claude/") else model,
            "openai": model,
            "ollama": f"ollama/{model}",
            "gemini": f"gemini/{model}",
        }
        return model_mappings.get(provider, model)

    async def generate_completion(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion using the specified LLM provider

        Args:
            prompt: The user prompt
            provider: LLM provider (anthropic, openai, ollama, gemini)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt
            metadata: Additional metadata

        Returns:
            Dictionary with response, tokens used, cost, etc.
        """
        if not LITELLM_AVAILABLE:
            raise RuntimeError("LiteLLM is not installed")

        # Use defaults if not specified
        provider = provider or settings.DEFAULT_LLM_PROVIDER

        # Get appropriate model based on provider
        if not model:
            if provider == "anthropic":
                model = "claude-3-5-sonnet-20241022"
            elif provider == "openai":
                model = "gpt-4-turbo-preview"
            elif provider == "ollama":
                model = settings.OLLAMA_MODEL
            elif provider == "gemini":
                model = "gemini-pro"

        model_string = self.get_model_string(provider, model)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        request_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            logger.info(f"Generating completion with {model_string}")

            response = await acompletion(
                model=model_string,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            result = {
                "request_id": request_id,
                "provider": provider,
                "model": model,
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if hasattr(response, "usage") else None,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, "usage") else None,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, "usage") else None,
                "cost": self.calculate_cost(provider, model, response.usage) if hasattr(response, "usage") else 0.0,
                "latency_ms": latency_ms,
                "success": True,
                "error": None,
                "metadata": metadata or {}
            }

            logger.info(f"Completion generated successfully in {latency_ms}ms")
            return result

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"LLM completion failed: {e}")

            return {
                "request_id": request_id,
                "provider": provider,
                "model": model,
                "response": None,
                "tokens_used": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost": 0.0,
                "latency_ms": latency_ms,
                "success": False,
                "error": str(e),
                "metadata": metadata or {}
            }

    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> Optional[list]:
        """Generate embeddings for text"""
        if not LITELLM_AVAILABLE:
            raise RuntimeError("LiteLLM is not installed")

        try:
            response = await aembedding(
                model=f"openai/{model}",
                input=[text]
            )
            return response.data[0]["embedding"]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def calculate_cost(self, provider: str, model: str, usage) -> float:
        """Calculate cost based on token usage"""
        # Simplified cost calculation - expand with actual pricing
        cost_per_1k_tokens = {
            "anthropic": {
                "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
                "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            },
            "openai": {
                "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
                "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            },
            "ollama": {
                "default": {"input": 0.0, "output": 0.0}  # Local, no cost
            },
            "gemini": {
                "gemini-pro": {"input": 0.00025, "output": 0.0005}
            }
        }

        if provider == "ollama":
            return 0.0

        pricing = cost_per_1k_tokens.get(provider, {}).get(model, {"input": 0.0, "output": 0.0})

        if not hasattr(usage, "prompt_tokens"):
            return 0.0

        input_cost = (usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * pricing["output"]

        return round(input_cost + output_cost, 6)

    async def test_connection(self, provider: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Test connection to an LLM provider"""
        try:
            result = await self.generate_completion(
                prompt="Hello! Please respond with 'OK' to confirm the connection.",
                provider=provider,
                model=model,
                temperature=0.1,
                max_tokens=10
            )

            return {
                "success": result["success"],
                "message": "Connection successful" if result["success"] else "Connection failed",
                "error": result.get("error"),
                "latency_ms": result.get("latency_ms"),
                "model": result.get("model")
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Connection failed",
                "error": str(e)
            }

    def should_use_local_llm(self, tags: list) -> bool:
        """Determine if local LLM should be used based on privacy settings"""
        if not settings.USE_LOCAL_LLM_FOR_SENSITIVE:
            return False

        sensitive_tags = set(settings.SENSITIVE_TAGS)
        content_tags = set(tags)

        return bool(sensitive_tags & content_tags)

    async def generate_tags(self, title: str, content: str, existing_tags: list = []) -> list:
        """Generate tags for content using LLM"""
        system_prompt = """You are a helpful assistant that generates relevant tags for knowledge management.
Generate 5-10 specific, relevant tags for the given content.
Return ONLY a comma-separated list of tags, nothing else.
Tags should be concise (1-3 words) and relevant to the content."""

        prompt = f"""Title: {title}

Content:
{content[:1000]}  # Limit content length

Existing tags: {', '.join(existing_tags) if existing_tags else 'None'}

Generate relevant tags:"""

        result = await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=settings.TAGGING_LLM_PROVIDER,
            model=settings.TAGGING_LLM_MODEL,
            temperature=0.3,
            max_tokens=100,
            metadata={"purpose": "tagging"}
        )

        if result["success"]:
            tags_text = result["response"].strip()
            tags = [tag.strip() for tag in tags_text.split(",")]
            return [tag for tag in tags if tag]  # Filter empty tags
        else:
            logger.error(f"Tag generation failed: {result.get('error')}")
            return []

    async def extract_entities(self, content: str) -> Dict[str, list]:
        """Extract named entities from content"""
        system_prompt = """Extract named entities from the text.
Return a JSON object with these keys:
- people: list of person names
- companies: list of company/organization names
- technologies: list of technologies, tools, or frameworks
- locations: list of places or locations
- concepts: list of key concepts or topics

Return ONLY valid JSON, nothing else."""

        prompt = f"""Extract entities from this text:

{content[:2000]}"""

        result = await self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=settings.TAGGING_LLM_PROVIDER,
            model=settings.TAGGING_LLM_MODEL,
            temperature=0.1,
            max_tokens=500,
            metadata={"purpose": "entity_extraction"}
        )

        if result["success"]:
            import json
            try:
                entities = json.loads(result["response"])
                return entities
            except json.JSONDecodeError:
                logger.error("Failed to parse entity extraction JSON")
                return {"people": [], "companies": [], "technologies": [], "locations": [], "concepts": []}
        else:
            return {"people": [], "companies": [], "technologies": [], "locations": [], "concepts": []}


# Global LLM manager instance
llm_manager = LLMManager()
