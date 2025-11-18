"""
Database connection managers for Neo4j and PostgreSQL
"""
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from neo4j import GraphDatabase, AsyncGraphDatabase
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from loguru import logger

from .config import settings


# SQLAlchemy Base
Base = declarative_base()


class Neo4jConnection:
    """Neo4j database connection manager"""

    def __init__(self):
        self._driver = None
        self._async_driver = None

    def connect(self):
        """Initialize Neo4j driver"""
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def connect_async(self):
        """Initialize async Neo4j driver"""
        try:
            self._async_driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info(f"Connected to Neo4j (async) at {settings.NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j (async): {e}")
            raise

    def close(self):
        """Close Neo4j driver"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    async def close_async(self):
        """Close async Neo4j driver"""
        if self._async_driver:
            await self._async_driver.close()
            logger.info("Neo4j async connection closed")

    def get_session(self):
        """Get a new Neo4j session"""
        if not self._driver:
            self.connect()
        return self._driver.session()

    def get_async_session(self):
        """Get a new async Neo4j session"""
        if not self._async_driver:
            raise RuntimeError("Async driver not initialized. Call connect_async() first.")
        return self._async_driver.session()

    def verify_connectivity(self):
        """Verify Neo4j connection"""
        try:
            with self.get_session() as session:
                result = session.run("RETURN 1 as num")
                record = result.single()
                return record["num"] == 1
        except Exception as e:
            logger.error(f"Neo4j connectivity check failed: {e}")
            return False


class PostgresConnection:
    """PostgreSQL database connection manager"""

    def __init__(self):
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None

    def connect(self):
        """Initialize PostgreSQL engine"""
        try:
            self._engine = create_engine(
                settings.postgres_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG
            )
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )
            logger.info(f"Connected to PostgreSQL at {settings.POSTGRES_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    async def connect_async(self):
        """Initialize async PostgreSQL engine"""
        try:
            self._async_engine = create_async_engine(
                settings.postgres_async_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DEBUG
            )
            self._async_session_factory = async_sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info(f"Connected to PostgreSQL (async) at {settings.POSTGRES_HOST}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL (async): {e}")
            raise

    def close(self):
        """Close PostgreSQL engine"""
        if self._engine:
            self._engine.dispose()
            logger.info("PostgreSQL connection closed")

    async def close_async(self):
        """Close async PostgreSQL engine"""
        if self._async_engine:
            await self._async_engine.dispose()
            logger.info("PostgreSQL async connection closed")

    def get_session(self):
        """Get a new PostgreSQL session"""
        if not self._session_factory:
            self.connect()
        return self._session_factory()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a new async PostgreSQL session"""
        if not self._async_session_factory:
            await self.connect_async()

        async with self._async_session_factory() as session:
            yield session

    def create_tables(self):
        """Create all tables"""
        if not self._engine:
            self.connect()
        Base.metadata.create_all(bind=self._engine)
        logger.info("PostgreSQL tables created")

    async def create_tables_async(self):
        """Create all tables (async)"""
        if not self._async_engine:
            await self.connect_async()
        async with self._async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL tables created (async)")


# Global database connection instances
neo4j_db = Neo4jConnection()
postgres_db = PostgresConnection()


async def get_neo4j_session():
    """Dependency for getting Neo4j session"""
    session = neo4j_db.get_async_session()
    try:
        yield session
    finally:
        await session.close()


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting PostgreSQL session"""
    async for session in postgres_db.get_async_session():
        yield session


async def init_databases():
    """Initialize all database connections"""
    logger.info("Initializing database connections...")

    # Connect to Neo4j
    neo4j_db.connect()
    await neo4j_db.connect_async()

    # Verify Neo4j connectivity
    if neo4j_db.verify_connectivity():
        logger.info("Neo4j connection verified")
    else:
        logger.error("Neo4j connection verification failed")

    # Connect to PostgreSQL
    postgres_db.connect()
    await postgres_db.connect_async()

    # Create PostgreSQL tables
    await postgres_db.create_tables_async()

    logger.info("Database initialization complete")


async def close_databases():
    """Close all database connections"""
    logger.info("Closing database connections...")
    neo4j_db.close()
    await neo4j_db.close_async()
    postgres_db.close()
    await postgres_db.close_async()
    logger.info("All database connections closed")
