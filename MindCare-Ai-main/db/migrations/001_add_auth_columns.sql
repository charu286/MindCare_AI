-- Migration: add auth columns to users (run once on existing DBs)
-- mysql -u root -p mindcare_ai < db/migrations/001_add_auth_columns.sql
-- Skip if schema.sql was run from scratch (columns already exist).

ALTER TABLE users ADD COLUMN email VARCHAR(255) UNIQUE NULL;
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL;
ALTER TABLE users ADD COLUMN is_anonymous BOOLEAN DEFAULT TRUE;
