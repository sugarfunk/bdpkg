"""
Neo4j graph schema setup and management
"""
from loguru import logger
from neo4j import AsyncGraphDatabase


class Neo4jSchema:
    """Neo4j schema management"""

    @staticmethod
    async def initialize_schema(driver):
        """Initialize Neo4j schema with constraints and indexes"""
        async with driver.session() as session:
            # Create constraints
            constraints = [
                # Unique node IDs
                "CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE",
                "CREATE CONSTRAINT tag_name_unique IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE",
                "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
                "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
            ]

            for constraint in constraints:
                try:
                    await session.run(constraint)
                    logger.info(f"Created constraint: {constraint[:50]}...")
                except Exception as e:
                    logger.warning(f"Constraint might already exist: {e}")

            # Create indexes for better performance
            indexes = [
                "CREATE INDEX node_type_idx IF NOT EXISTS FOR (n:Node) ON (n.node_type)",
                "CREATE INDEX node_created_idx IF NOT EXISTS FOR (n:Node) ON (n.created_at)",
                "CREATE INDEX node_title_idx IF NOT EXISTS FOR (n:Node) ON (n.title)",
                "CREATE FULLTEXT INDEX node_content_fulltext IF NOT EXISTS FOR (n:Node) ON EACH [n.title, n.content]",
                "CREATE INDEX tag_usage_idx IF NOT EXISTS FOR (t:Tag) ON (t.usage_count)",
                "CREATE INDEX edge_type_idx IF NOT EXISTS FOR ()-[r:CONNECTED_TO]-() ON (r.edge_type)",
                "CREATE INDEX edge_strength_idx IF NOT EXISTS FOR ()-[r:CONNECTED_TO]-() ON (r.strength)",
            ]

            for index in indexes:
                try:
                    await session.run(index)
                    logger.info(f"Created index: {index[:50]}...")
                except Exception as e:
                    logger.warning(f"Index might already exist: {e}")

            logger.info("Neo4j schema initialization complete")

    @staticmethod
    async def create_node(session, node_id: str, data: dict):
        """Create a node in Neo4j"""
        query = """
        CREATE (n:Node {
            id: $id,
            title: $title,
            content: $content,
            node_type: $node_type,
            source: $source,
            source_id: $source_id,
            url: $url,
            privacy_level: $privacy_level,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at),
            metadata: $metadata
        })
        RETURN n
        """
        result = await session.run(query, id=node_id, **data)
        return await result.single()

    @staticmethod
    async def get_node(session, node_id: str):
        """Get a node by ID"""
        query = """
        MATCH (n:Node {id: $id})
        OPTIONAL MATCH (n)-[r:TAGGED_WITH]->(t:Tag)
        RETURN n, collect(t.name) as tags, count(r) as tag_count
        """
        result = await session.run(query, id=node_id)
        return await result.single()

    @staticmethod
    async def update_node(session, node_id: str, data: dict):
        """Update a node"""
        set_clauses = []
        params = {"id": node_id}

        for key, value in data.items():
            if value is not None:
                set_clauses.append(f"n.{key} = ${key}")
                params[key] = value

        if not set_clauses:
            return None

        set_clauses.append("n.updated_at = datetime()")
        query = f"""
        MATCH (n:Node {{id: $id}})
        SET {', '.join(set_clauses)}
        RETURN n
        """
        result = await session.run(query, **params)
        return await result.single()

    @staticmethod
    async def delete_node(session, node_id: str):
        """Delete a node and all its relationships"""
        query = """
        MATCH (n:Node {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted_count
        """
        result = await session.run(query, id=node_id)
        record = await result.single()
        return record["deleted_count"] > 0 if record else False

    @staticmethod
    async def create_edge(session, source_id: str, target_id: str, edge_data: dict):
        """Create an edge between two nodes"""
        query = """
        MATCH (source:Node {id: $source_id})
        MATCH (target:Node {id: $target_id})
        CREATE (source)-[r:CONNECTED_TO {
            id: $edge_id,
            edge_type: $edge_type,
            strength: $strength,
            discovered_by: $discovered_by,
            created_at: datetime(),
            metadata: $metadata
        }]->(target)
        RETURN r
        """
        result = await session.run(query, source_id=source_id, target_id=target_id, **edge_data)
        return await result.single()

    @staticmethod
    async def delete_edge(session, edge_id: str):
        """Delete an edge"""
        query = """
        MATCH ()-[r:CONNECTED_TO {id: $id}]-()
        DELETE r
        RETURN count(r) as deleted_count
        """
        result = await session.run(query, id=edge_id)
        record = await result.single()
        return record["deleted_count"] > 0 if record else False

    @staticmethod
    async def add_tags_to_node(session, node_id: str, tags: list):
        """Add tags to a node"""
        for tag_name in tags:
            query = """
            MATCH (n:Node {id: $node_id})
            MERGE (t:Tag {name: $tag_name})
            ON CREATE SET t.usage_count = 1, t.created_at = datetime()
            ON MATCH SET t.usage_count = t.usage_count + 1
            MERGE (n)-[:TAGGED_WITH]->(t)
            """
            await session.run(query, node_id=node_id, tag_name=tag_name)

    @staticmethod
    async def get_node_connections(session, node_id: str, max_depth: int = 2):
        """Get all connections for a node up to max_depth"""
        query = """
        MATCH path = (start:Node {id: $node_id})-[r:CONNECTED_TO*1..$max_depth]-(connected:Node)
        WITH start, connected, relationships(path) as rels, length(path) as depth
        RETURN
            connected.id as node_id,
            connected.title as title,
            connected.node_type as node_type,
            depth,
            [rel in rels | {type: rel.edge_type, strength: rel.strength}] as relationship_chain
        ORDER BY depth
        """
        result = await session.run(query, node_id=node_id, max_depth=max_depth)
        return [record async for record in result]

    @staticmethod
    async def get_graph_statistics(session):
        """Get overall graph statistics"""
        query = """
        MATCH (n:Node)
        OPTIONAL MATCH (n)-[r:CONNECTED_TO]-()
        WITH count(DISTINCT n) as node_count,
             count(DISTINCT r) as edge_count,
             n.node_type as type
        RETURN
            sum(node_count) as total_nodes,
            sum(edge_count)/2 as total_edges,
            collect({type: type, count: node_count}) as node_types
        """
        result = await session.run(query)
        return await result.single()

    @staticmethod
    async def detect_communities(session, min_size: int = 3):
        """Detect communities/clusters using Louvain algorithm"""
        # First, project the graph
        project_query = """
        CALL gds.graph.project(
            'knowledge-graph',
            'Node',
            {
                CONNECTED_TO: {
                    orientation: 'UNDIRECTED',
                    properties: 'strength'
                }
            }
        )
        """

        # Run Louvain community detection
        louvain_query = """
        CALL gds.louvain.stream('knowledge-graph', {
            relationshipWeightProperty: 'strength'
        })
        YIELD nodeId, communityId
        WITH gds.util.asNode(nodeId) as node, communityId
        WHERE node:Node
        RETURN communityId, collect({
            id: node.id,
            title: node.title,
            node_type: node.node_type
        }) as nodes, count(*) as size
        HAVING size >= $min_size
        ORDER BY size DESC
        """

        try:
            # Try to drop existing projection
            await session.run("CALL gds.graph.drop('knowledge-graph', false)")
        except:
            pass

        try:
            await session.run(project_query)
            result = await session.run(louvain_query, min_size=min_size)
            communities = [record async for record in result]

            # Clean up projection
            await session.run("CALL gds.graph.drop('knowledge-graph')")

            return communities
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return []

    @staticmethod
    async def find_shortest_path(session, source_id: str, target_id: str):
        """Find shortest path between two nodes"""
        query = """
        MATCH path = shortestPath(
            (source:Node {id: $source_id})-[r:CONNECTED_TO*]-(target:Node {id: $target_id})
        )
        RETURN [node in nodes(path) | {
            id: node.id,
            title: node.title,
            node_type: node.node_type
        }] as path_nodes,
        [rel in relationships(path) | {
            type: rel.edge_type,
            strength: rel.strength
        }] as path_edges,
        length(path) as path_length
        """
        result = await session.run(query, source_id=source_id, target_id=target_id)
        return await result.single()

    @staticmethod
    async def find_similar_nodes(session, node_id: str, limit: int = 10):
        """Find nodes similar to the given node based on tags and connections"""
        query = """
        MATCH (source:Node {id: $node_id})-[:TAGGED_WITH]->(tag:Tag)<-[:TAGGED_WITH]-(similar:Node)
        WHERE source <> similar
        WITH similar, count(tag) as common_tags
        OPTIONAL MATCH (source)-[r:CONNECTED_TO]-(similar)
        WITH similar, common_tags, count(r) as direct_connections
        RETURN
            similar.id as id,
            similar.title as title,
            similar.node_type as node_type,
            common_tags,
            direct_connections,
            (common_tags * 2 + direct_connections * 5) as similarity_score
        ORDER BY similarity_score DESC
        LIMIT $limit
        """
        result = await session.run(query, node_id=node_id, limit=limit)
        return [record async for record in result]

    @staticmethod
    async def query_graph_for_visualization(session, query_params: dict):
        """Query graph for visualization with filters"""
        conditions = []
        params = {}

        if query_params.get("node_types"):
            conditions.append("n.node_type IN $node_types")
            params["node_types"] = query_params["node_types"]

        if query_params.get("center_node_id"):
            # Get subgraph around a specific node
            depth = query_params.get("max_depth", 2)
            query = f"""
            MATCH path = (center:Node {{id: $center_id}})-[r:CONNECTED_TO*0..{depth}]-(n:Node)
            WHERE r IS NULL OR ALL(rel in r WHERE rel.strength >= $min_strength)
            WITH DISTINCT n, center
            MATCH (n)-[edge:CONNECTED_TO]-(connected:Node)
            WHERE edge.strength >= $min_strength
            RETURN DISTINCT
                n.id as node_id,
                n.title as title,
                n.node_type as node_type,
                labels(n) as labels,
                collect(DISTINCT {{
                    source: n.id,
                    target: connected.id,
                    type: edge.edge_type,
                    strength: edge.strength,
                    id: edge.id
                }}) as edges
            LIMIT $max_nodes
            """
            params["center_id"] = query_params["center_node_id"]
        else:
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            query = f"""
            MATCH (n:Node)
            {where_clause}
            OPTIONAL MATCH (n)-[r:CONNECTED_TO]-(connected:Node)
            WHERE r.strength >= $min_strength
            RETURN DISTINCT
                n.id as node_id,
                n.title as title,
                n.node_type as node_type,
                labels(n) as labels,
                collect(DISTINCT {{
                    source: n.id,
                    target: connected.id,
                    type: r.edge_type,
                    strength: r.strength,
                    id: r.id
                }}) as edges
            LIMIT $max_nodes
            """

        params["min_strength"] = query_params.get("min_connection_strength", 0.3)
        params["max_nodes"] = query_params.get("max_nodes", 100)

        result = await session.run(query, **params)
        return [record async for record in result]
