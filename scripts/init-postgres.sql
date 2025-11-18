-- Initialize PostgreSQL database for Knowledge Graph Builder

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For GIN indexes

-- Create custom types
DO $$ BEGIN
    CREATE TYPE node_type_enum AS ENUM (
        'note', 'document', 'person', 'concept', 'project',
        'company', 'vendor', 'technology', 'location', 'event',
        'task', 'topic', 'book', 'article', 'bookmark', 'email', 'rss_item'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE privacy_level_enum AS ENUM ('public', 'private', 'sensitive', 'encrypted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE knowledge_graph TO kg_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kg_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kg_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO kg_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO kg_user;

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Note: Tables will be created automatically by SQLAlchemy based on the models
