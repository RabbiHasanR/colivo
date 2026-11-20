-- Runs once, when the postgres container starts with an empty data volume.
-- The test database is separate so tests never touch development data;
-- pytest builds its schema with `alembic upgrade head` (specs/testing.md).
-- Its name must match the database in TEST_DATABASE_URL (.env.example).
CREATE DATABASE colivo_test;
