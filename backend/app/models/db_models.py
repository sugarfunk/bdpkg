"""
SQLAlchemy database models for PostgreSQL
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from app.core.database import Base


class NodeMetadata(Base):
    """
    Metadata for nodes stored in PostgreSQL for efficient querying
    The actual graph structure is in Neo4j
    """
    __tablename__ = "node_metadata"

    id = Column(String(36), primary_key=True)  # UUID matching Neo4j node ID
    title = Column(String(500), nullable=False, index=True)
    node_type = Column(String(50), nullable=False, index=True)
    source = Column(String(100), index=True)
    source_id = Column(String(255))
    url = Column(Text)
    privacy_level = Column(String(20), default="private", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, default={})

    # Full-text search
    content_vector = Column(Text)  # tsvector for full-text search

    # Indexes
    __table_args__ = (
        Index('idx_node_title_fts', 'title', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}),
        Index('idx_node_created_at', 'created_at'),
        Index('idx_node_type_privacy', 'node_type', 'privacy_level'),
    )

    def __repr__(self):
        return f"<NodeMetadata(id={self.id}, title={self.title}, type={self.node_type})>"


class EdgeMetadata(Base):
    """
    Metadata for edges stored in PostgreSQL
    """
    __tablename__ = "edge_metadata"

    id = Column(String(36), primary_key=True)
    source_id = Column(String(36), nullable=False, index=True)
    target_id = Column(String(36), nullable=False, index=True)
    edge_type = Column(String(50), nullable=False, index=True)
    strength = Column(Float, default=0.5)
    discovered_by = Column(String(50))  # 'user', 'ai', algorithm name
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(JSONB, default={})

    # Indexes
    __table_args__ = (
        Index('idx_edge_source_target', 'source_id', 'target_id'),
        Index('idx_edge_type', 'edge_type'),
    )

    def __repr__(self):
        return f"<EdgeMetadata(id={self.id}, {self.source_id}->{self.target_id}, type={self.edge_type})>"


class TagModel(Base):
    """
    Tags for categorizing nodes
    """
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    parent_tag_id = Column(String(36))  # For hierarchical tags
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Tag(name={self.name}, usage={self.usage_count})>"


class SearchIndex(Base):
    """
    Search index for efficient full-text and semantic search
    """
    __tablename__ = "search_index"

    id = Column(String(36), primary_key=True)
    node_id = Column(String(36), nullable=False, index=True)
    content_hash = Column(String(64))  # SHA-256 hash of content
    embedding = Column(ARRAY(Float))  # Vector embedding for semantic search
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for similarity search
    __table_args__ = (
        Index('idx_search_node_id', 'node_id'),
    )

    def __repr__(self):
        return f"<SearchIndex(node_id={self.node_id})>"


class LLMRequestLog(Base):
    """
    Log of all LLM requests for cost tracking and debugging
    """
    __tablename__ = "llm_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(36), unique=True, index=True)
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    purpose = Column(String(100))  # tagging, connection, insight, etc.
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost = Column(Float)
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(JSONB, default={})

    # Indexes
    __table_args__ = (
        Index('idx_llm_created_at', 'created_at'),
        Index('idx_llm_provider_model', 'provider', 'model'),
    )

    def __repr__(self):
        return f"<LLMRequest(provider={self.provider}, model={self.model}, tokens={self.total_tokens})>"


class LLMCost(Base):
    """
    Aggregated LLM cost tracking by period
    """
    __tablename__ = "llm_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    provider = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_cost_period_provider', 'period_start', 'provider'),
    )

    def __repr__(self):
        return f"<LLMCost(provider={self.provider}, cost=${self.total_cost:.4f})>"


class IntegrationSync(Base):
    """
    Track synchronization status for various integrations
    """
    __tablename__ = "integration_syncs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    integration_name = Column(String(100), nullable=False, index=True)
    sync_status = Column(String(20), nullable=False)  # running, completed, failed
    items_synced = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    error_log = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})

    # Indexes
    __table_args__ = (
        Index('idx_sync_integration_status', 'integration_name', 'sync_status'),
    )

    def __repr__(self):
        return f"<IntegrationSync(integration={self.integration_name}, status={self.sync_status})>"


class InsightModel(Base):
    """
    AI-generated insights
    """
    __tablename__ = "insights"

    id = Column(String(36), primary_key=True)
    insight_type = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    related_node_ids = Column(ARRAY(String), default=[])
    acknowledged = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    metadata = Column(JSONB, default={})

    # Indexes
    __table_args__ = (
        Index('idx_insight_type_acknowledged', 'insight_type', 'acknowledged'),
        Index('idx_insight_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Insight(type={self.insight_type}, title={self.title})>"


class UserPreference(Base):
    """
    User preferences and settings
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), unique=True, index=True)  # For future multi-user support
    preferences = Column(JSONB, default={})
    llm_config = Column(JSONB, default={})
    integration_config = Column(JSONB, default={})
    ui_config = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id})>"
