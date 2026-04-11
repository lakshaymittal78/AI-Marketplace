-- Initialize pgvector extension on database creation
CREATE EXTENSION IF NOT EXISTS vector;
-- Verify it was created
SELECT * FROM pg_extension WHERE extname = 'vector';

