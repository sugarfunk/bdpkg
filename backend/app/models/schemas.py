"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph"""
    NOTE = "note"
    DOCUMENT = "document"
    PERSON = "person"
    CONCEPT = "concept"
    PROJECT = "project"
    COMPANY = "company"
    VENDOR = "vendor"
    TECHNOLOGY = "technology"
    LOCATION = "location"
    EVENT = "event"
    TASK = "task"
    TOPIC = "topic"
    BOOK = "book"
    ARTICLE = "article"
    BOOKMARK = "bookmark"
    EMAIL = "email"
    RSS_ITEM = "rss_item"


class EdgeType(str, Enum):
    """Types of relationships between nodes"""
    REFERENCES = "references"
    SIMILAR_TO = "similar_to"
    DERIVED_FROM = "derived_from"
    RELATED_TO = "related_to"
    MENTIONS = "mentions"
    CONTAINS = "contains"
    PART_OF = "part_of"
    AUTHORED_BY = "authored_by"
    TAGGED_WITH = "tagged_with"
    OCCURRED_BEFORE = "occurred_before"
    OCCURRED_AFTER = "occurred_after"
    CAUSES = "causes"
    CAUSED_BY = "caused_by"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    DEPENDS_ON = "depends_on"


class PrivacyLevel(str, Enum):
    """Privacy levels for content"""
    PUBLIC = "public"
    PRIVATE = "private"
    SENSITIVE = "sensitive"  # Use only local LLMs
    ENCRYPTED = "encrypted"  # Encrypted storage


class InsightType(str, Enum):
    """Types of AI-generated insights"""
    CONNECTION = "connection"
    PATTERN = "pattern"
    CONTRADICTION = "contradiction"
    GAP = "gap"
    TREND = "trend"
    RECOMMENDATION = "recommendation"
    SUMMARY = "summary"


# Base Models
class NodeBase(BaseModel):
    """Base node model"""
    title: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    node_type: NodeType
    source: Optional[str] = None  # Where the node came from
    source_id: Optional[str] = None  # ID in the source system
    url: Optional[str] = None
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NodeCreate(NodeBase):
    """Create a new node"""
    tags: List[str] = Field(default_factory=list)


class NodeUpdate(BaseModel):
    """Update an existing node"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    node_type: Optional[NodeType] = None
    url: Optional[str] = None
    privacy_level: Optional[PrivacyLevel] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class Node(NodeBase):
    """Full node model with ID and timestamps"""
    id: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = Field(default_factory=list)
    embedding: Optional[List[float]] = None
    connection_count: int = 0

    class Config:
        from_attributes = True


# Edge Models
class EdgeBase(BaseModel):
    """Base edge model"""
    edge_type: EdgeType
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EdgeCreate(EdgeBase):
    """Create a new edge"""
    source_id: str
    target_id: str
    discovered_by: Optional[str] = None  # 'user', 'ai', or specific algorithm


class Edge(EdgeBase):
    """Full edge model"""
    id: str
    source_id: str
    target_id: str
    created_at: datetime
    discovered_by: Optional[str] = None

    class Config:
        from_attributes = True


# Tag Models
class TagCreate(BaseModel):
    """Create a new tag"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None
    parent_tag: Optional[str] = None


class Tag(TagCreate):
    """Full tag model"""
    id: str
    usage_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# Search Models
class SearchQuery(BaseModel):
    """Search query parameters"""
    query: str = Field(..., min_length=1)
    search_type: str = Field(default="full_text")  # full_text, semantic, natural_language
    node_types: Optional[List[NodeType]] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    privacy_levels: Optional[List[PrivacyLevel]] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)


class SearchResult(BaseModel):
    """Search result"""
    node: Node
    score: float
    highlights: Optional[List[str]] = None
    explanation: Optional[str] = None


# Graph Query Models
class GraphQuery(BaseModel):
    """Query for graph visualization"""
    center_node_id: Optional[str] = None
    node_types: Optional[List[NodeType]] = None
    tags: Optional[List[str]] = None
    max_depth: int = Field(default=2, ge=1, le=5)
    min_connection_strength: float = Field(default=0.3, ge=0.0, le=1.0)
    max_nodes: int = Field(default=100, le=500)
    include_clusters: bool = True


class GraphNode(BaseModel):
    """Node in graph response"""
    id: str
    title: str
    node_type: NodeType
    tags: List[str]
    metadata: Dict[str, Any]


class GraphEdge(BaseModel):
    """Edge in graph response"""
    id: str
    source: str
    target: str
    edge_type: EdgeType
    strength: float


class GraphCluster(BaseModel):
    """Detected cluster in graph"""
    id: str
    name: str
    node_ids: List[str]
    size: int
    density: float


class GraphResponse(BaseModel):
    """Graph visualization response"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    clusters: Optional[List[GraphCluster]] = None
    statistics: Dict[str, Any] = Field(default_factory=dict)


# Insight Models
class Insight(BaseModel):
    """AI-generated insight"""
    id: str
    insight_type: InsightType
    title: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    related_node_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    acknowledged: bool = False


class InsightCreate(BaseModel):
    """Create a new insight"""
    insight_type: InsightType
    title: str
    description: str
    confidence: float
    related_node_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Integration Models
class IntegrationConfig(BaseModel):
    """Configuration for an integration"""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)
    last_sync: Optional[datetime] = None
    sync_interval: int = 300  # seconds


class SyncStatus(BaseModel):
    """Status of a sync operation"""
    integration: str
    status: str  # running, completed, failed
    items_synced: int = 0
    errors: List[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: Optional[datetime] = None


# LLM Models
class LLMProvider(str, Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"


class LLMRequest(BaseModel):
    """LLM request"""
    provider: LLMProvider
    model: str
    prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """LLM response"""
    provider: LLMProvider
    model: str
    response: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMCostSummary(BaseModel):
    """Summary of LLM costs"""
    total_cost: float
    by_provider: Dict[str, float]
    by_model: Dict[str, float]
    total_tokens: int
    period_start: datetime
    period_end: datetime
