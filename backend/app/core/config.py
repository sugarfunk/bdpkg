"""
Application configuration using Pydantic settings
"""
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Personal Knowledge Graph Builder"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Neo4j Graph Database
    NEO4J_URI: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="knowledge-graph-pass", env="NEO4J_PASSWORD")

    # PostgreSQL
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="knowledge_graph", env="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="kg_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="kg_secure_pass", env="POSTGRES_PASSWORD")

    @property
    def postgres_url(self) -> str:
        """Build PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def postgres_async_url(self) -> str:
        """Build async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # LLM Configuration
    # Default LLM provider (anthropic, openai, ollama, gemini)
    DEFAULT_LLM_PROVIDER: str = Field(default="anthropic", env="DEFAULT_LLM_PROVIDER")

    # Provider for specific tasks
    TAGGING_LLM_PROVIDER: str = Field(default="anthropic", env="TAGGING_LLM_PROVIDER")
    TAGGING_LLM_MODEL: str = Field(default="claude-3-haiku-20240307", env="TAGGING_LLM_MODEL")

    CONNECTION_LLM_PROVIDER: str = Field(default="anthropic", env="CONNECTION_LLM_PROVIDER")
    CONNECTION_LLM_MODEL: str = Field(default="claude-3-5-sonnet-20241022", env="CONNECTION_LLM_MODEL")

    INSIGHT_LLM_PROVIDER: str = Field(default="anthropic", env="INSIGHT_LLM_PROVIDER")
    INSIGHT_LLM_MODEL: str = Field(default="claude-3-5-sonnet-20241022", env="INSIGHT_LLM_MODEL")

    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")

    # Ollama (local LLM)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL: str = Field(default="llama2", env="OLLAMA_MODEL")

    # Privacy Settings
    USE_LOCAL_LLM_FOR_SENSITIVE: bool = Field(default=True, env="USE_LOCAL_LLM_FOR_SENSITIVE")
    SENSITIVE_TAGS: List[str] = Field(
        default=["personal", "anxiety", "therapy", "procurement-contract", "confidential", "private"],
        env="SENSITIVE_TAGS"
    )

    # Encryption
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")

    # Integration Settings
    # Standard Notes
    STANDARD_NOTES_URL: Optional[str] = Field(default=None, env="STANDARD_NOTES_URL")
    STANDARD_NOTES_EMAIL: Optional[str] = Field(default=None, env="STANDARD_NOTES_EMAIL")
    STANDARD_NOTES_PASSWORD: Optional[str] = Field(default=None, env="STANDARD_NOTES_PASSWORD")

    # Paperless-ngx
    PAPERLESS_URL: Optional[str] = Field(default=None, env="PAPERLESS_URL")
    PAPERLESS_TOKEN: Optional[str] = Field(default=None, env="PAPERLESS_TOKEN")

    # Email
    EMAIL_IMAP_SERVER: Optional[str] = Field(default=None, env="EMAIL_IMAP_SERVER")
    EMAIL_IMAP_PORT: int = Field(default=993, env="EMAIL_IMAP_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")

    # Todoist
    TODOIST_API_KEY: Optional[str] = Field(default=None, env="TODOIST_API_KEY")

    # Background Processing
    BACKGROUND_SYNC_INTERVAL: int = Field(default=300, env="BACKGROUND_SYNC_INTERVAL")  # seconds
    CONNECTION_DISCOVERY_INTERVAL: int = Field(default=3600, env="CONNECTION_DISCOVERY_INTERVAL")  # seconds

    # File Processing
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".md", ".txt", ".pdf", ".docx", ".html", ".json"],
        env="ALLOWED_EXTENSIONS"
    )

    # Search
    SEMANTIC_SEARCH_THRESHOLD: float = Field(default=0.7, env="SEMANTIC_SEARCH_THRESHOLD")
    MAX_SEARCH_RESULTS: int = Field(default=50, env="MAX_SEARCH_RESULTS")

    # Graph Settings
    MAX_GRAPH_DEPTH: int = Field(default=3, env="MAX_GRAPH_DEPTH")
    MIN_CONNECTION_STRENGTH: float = Field(default=0.5, env="MIN_CONNECTION_STRENGTH")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
