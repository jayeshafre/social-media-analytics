-- sql/schema/00_create_superset_db.sql
-- ─────────────────────────────────────────────────────────
-- Creates the separate database Superset uses for its own
-- metadata (dashboards, charts, users, datasources).
--
-- This runs automatically when postgres container starts
-- for the first time via /docker-entrypoint-initdb.d/
--
-- Your analytics data stays in social_media_analytics.
-- Superset's config lives in superset_meta.
-- ─────────────────────────────────────────────────────────

SELECT 'CREATE DATABASE superset_meta'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'superset_meta'
)\gexec