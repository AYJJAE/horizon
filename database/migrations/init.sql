-- Horizon Exoplanet Platform — PostgreSQL initialization
-- This runs automatically when the Docker container first starts

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The tables are created by SQLAlchemy's init_db() on startup.
-- This file is a placeholder for any additional seed data.

-- Sample seed: nothing required, app handles all schema creation.
SELECT 1;
