-- Extensiones necesarias para el proyecto (PostGIS ya viene activada por la
-- imagen base, pero se deja explicita por claridad). pgRouting depende de
-- PostGIS, por eso el orden importa.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;
