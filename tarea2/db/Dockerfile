FROM pgrouting/pgrouting:latest
# Imagen oficial que ya trae PostgreSQL + PostGIS + pgRouting compilados y
# listos (evita depender del repo apt.postgresql.org para la version de
# pgRouting, que se encontro caido/archivado para Debian bullseye).

COPY init_extensions.sql /docker-entrypoint-initdb.d/01_extensions.sql
COPY schema.sql /docker-entrypoint-initdb.d/02_schema.sql
