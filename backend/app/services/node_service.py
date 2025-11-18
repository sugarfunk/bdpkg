"""
Node service for managing knowledge graph nodes
"""
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.db_models import NodeMetadata
from app.models.schemas import Node, NodeCreate, NodeUpdate, NodeType


class NodeService:
    """Service for node operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_node(self, node_data: NodeCreate) -> Node:
        """Create a new node"""
        node_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Create in PostgreSQL
        db_node = NodeMetadata(
            id=node_id,
            title=node_data.title,
            node_type=node_data.node_type.value,
            source=node_data.source,
            source_id=node_data.source_id,
            url=node_data.url,
            privacy_level=node_data.privacy_level.value,
            created_at=now,
            updated_at=now,
            metadata=node_data.metadata
        )

        self.db.add(db_node)
        await self.db.commit()
        await self.db.refresh(db_node)

        # TODO: Create in Neo4j
        # TODO: Generate embeddings
        # TODO: Create tag relationships

        return Node(
            id=db_node.id,
            title=db_node.title,
            content=node_data.content,
            node_type=NodeType(db_node.node_type),
            source=db_node.source,
            source_id=db_node.source_id,
            url=db_node.url,
            privacy_level=node_data.privacy_level,
            created_at=db_node.created_at,
            updated_at=db_node.updated_at,
            tags=node_data.tags,
            metadata=db_node.metadata,
            connection_count=0
        )

    async def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        result = await self.db.execute(
            select(NodeMetadata).where(NodeMetadata.id == node_id)
        )
        db_node = result.scalar_one_or_none()

        if not db_node:
            return None

        # TODO: Get content from Neo4j
        # TODO: Get tags
        # TODO: Get connection count

        return Node(
            id=db_node.id,
            title=db_node.title,
            content=None,  # TODO: Get from Neo4j
            node_type=NodeType(db_node.node_type),
            source=db_node.source,
            source_id=db_node.source_id,
            url=db_node.url,
            privacy_level=db_node.privacy_level,
            created_at=db_node.created_at,
            updated_at=db_node.updated_at,
            tags=[],  # TODO: Get from Neo4j
            metadata=db_node.metadata,
            connection_count=0  # TODO: Calculate from Neo4j
        )

    async def update_node(self, node_id: str, node_data: NodeUpdate) -> Optional[Node]:
        """Update a node"""
        result = await self.db.execute(
            select(NodeMetadata).where(NodeMetadata.id == node_id)
        )
        db_node = result.scalar_one_or_none()

        if not db_node:
            return None

        # Update fields
        update_data = node_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field not in ["tags", "content"]:
                setattr(db_node, field, value)

        db_node.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(db_node)

        # TODO: Update in Neo4j
        # TODO: Update tags
        # TODO: Re-generate embeddings if content changed

        return await self.get_node(node_id)

    async def delete_node(self, node_id: str) -> bool:
        """Delete a node"""
        result = await self.db.execute(
            delete(NodeMetadata).where(NodeMetadata.id == node_id)
        )

        # TODO: Delete from Neo4j
        # TODO: Delete embeddings
        # TODO: Delete edges

        return result.rowcount > 0

    async def list_nodes(
        self,
        node_type: Optional[NodeType] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Node]:
        """List nodes with optional filtering"""
        query = select(NodeMetadata)

        if node_type:
            query = query.where(NodeMetadata.node_type == node_type.value)

        # TODO: Filter by tag (requires Neo4j query)

        query = query.limit(limit).offset(offset).order_by(NodeMetadata.created_at.desc())

        result = await self.db.execute(query)
        db_nodes = result.scalars().all()

        return [
            Node(
                id=node.id,
                title=node.title,
                content=None,
                node_type=NodeType(node.node_type),
                source=node.source,
                source_id=node.source_id,
                url=node.url,
                privacy_level=node.privacy_level,
                created_at=node.created_at,
                updated_at=node.updated_at,
                tags=[],
                metadata=node.metadata,
                connection_count=0
            )
            for node in db_nodes
        ]

    async def get_node_connections(self, node_id: str, max_depth: int = 2):
        """Get all connections for a node"""
        # TODO: Implement using Neo4j
        return {
            "node_id": node_id,
            "connections": [],
            "depth": max_depth
        }
