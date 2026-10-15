-- Esquema de la base de datos - Ruteo resiliente de drones BVLOS
-- Gran Valparaiso. Ver db/diagrama_bd.png para el diagrama visual.

-- ============================================================
-- INFRAESTRUCTURA (grafo vial real, OSM via Geofabrik)
-- ============================================================

CREATE TABLE infraestructura_nodos (
    id      BIGINT PRIMARY KEY,         -- id interno que usa pgRouting
    osmid   BIGINT,                     -- id original en OpenStreetMap
    lon     DOUBLE PRECISION NOT NULL,
    lat     DOUBLE PRECISION NOT NULL,
    geom    GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX idx_infraestructura_nodos_geom ON infraestructura_nodos USING GIST (geom);

CREATE TABLE infraestructura_aristas (
    id          BIGINT PRIMARY KEY,
    osmid       BIGINT,
    source      BIGINT NOT NULL REFERENCES infraestructura_nodos(id),
    target      BIGINT NOT NULL REFERENCES infraestructura_nodos(id),
    highway     TEXT,                   -- tipo de via (primary, residential, etc.)
    surface     TEXT,                   -- tipo de superficie (asphalt, unpaved, etc.)
    oneway      BOOLEAN DEFAULT FALSE,
    length_m    DOUBLE PRECISION NOT NULL,  -- costo base para pgr_dijkstra (fase 2)
    geom        GEOMETRY(LineString, 4326) NOT NULL
);
CREATE INDEX idx_infraestructura_aristas_geom ON infraestructura_aristas USING GIST (geom);
CREATE INDEX idx_infraestructura_aristas_source ON infraestructura_aristas (source);
CREATE INDEX idx_infraestructura_aristas_target ON infraestructura_aristas (target);

-- ============================================================
-- NODOS ESPECIALES (origen del dron / puntos de carga)
-- ============================================================

CREATE TABLE nodo_carabineros (
    id              SERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    tipo            TEXT,               -- Comisaria, Tenencia, Subcomisaria, Reten
    comuna          TEXT NOT NULL,
    es_comisaria    BOOLEAN NOT NULL DEFAULT FALSE,
    es_punto_carga  BOOLEAN NOT NULL DEFAULT TRUE,
    nodo_vial_id    BIGINT REFERENCES infraestructura_nodos(id), -- nodo mas cercano del grafo
    geom            GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX idx_nodo_carabineros_geom ON nodo_carabineros USING GIST (geom);

-- ============================================================
-- METADATA (una tabla por fuente, carga independiente)
-- ============================================================

CREATE TABLE metadata_viento (
    id                  SERIAL PRIMARY KEY,
    comuna              TEXT NOT NULL,
    sector              TEXT,
    elevacion_m         DOUBLE PRECISION,
    viento_medio_kmh    DOUBLE PRECISION,
    racha_media_kmh     DOUBLE PRECISION,
    racha_max_kmh       DOUBLE PRECISION,
    direccion_deg       DOUBLE PRECISION,  -- de donde sopla, en grados
    geom                GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX idx_metadata_viento_geom ON metadata_viento USING GIST (geom);

CREATE TABLE metadata_tendido_electrico (
    id      SERIAL PRIMARY KEY,
    tipo    TEXT NOT NULL,              -- line (alta/media tension) | minor_line (distribucion)
    geom    GEOMETRY(LineString, 4326) NOT NULL
);
CREATE INDEX idx_metadata_tendido_geom ON metadata_tendido_electrico USING GIST (geom);

CREATE TABLE metadata_relieve (
    id              SERIAL PRIMARY KEY,
    arista_id       BIGINT REFERENCES infraestructura_aristas(id),
    elev_u_m        DOUBLE PRECISION,
    elev_v_m        DOUBLE PRECISION,
    desnivel_m      DOUBLE PRECISION,
    pendiente_pct   DOUBLE PRECISION
);

CREATE TABLE metadata_poblacion (
    id          SERIAL PRIMARY KEY,
    comuna      TEXT NOT NULL,
    manzent     TEXT,                   -- id de manzana censal (MANZENT_I)
    total_pers  INTEGER,
    total_vivi  INTEGER,
    geom        GEOMETRY(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX idx_metadata_poblacion_geom ON metadata_poblacion USING GIST (geom);

-- ============================================================
-- AMENAZAS (una tabla por fuente)
-- ============================================================

CREATE TABLE amenaza_firms (
    id              SERIAL PRIMARY KEY,
    fecha           DATE,
    confianza       TEXT,
    dentro_chile    BOOLEAN NOT NULL,
    geom            GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX idx_amenaza_firms_geom ON amenaza_firms USING GIST (geom);

CREATE TABLE amenaza_conaf_ignicion (
    id              SERIAL PRIMARY KEY,
    label           INTEGER,            -- limite superior del decil (10,20,...,100)
    rango_pi        TEXT,               -- ej. "21-30"
    dia_pronostico  INTEGER,            -- 0 a 4 (pronostico a 5 dias)
    geom            GEOMETRY(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX idx_amenaza_conaf_ignicion_geom ON amenaza_conaf_ignicion USING GIST (geom);

CREATE TABLE amenaza_conaf_areas_protegidas (
    id          SERIAL PRIMARY KEY,
    nombre      TEXT,
    categoria   TEXT,
    sup_ha      DOUBLE PRECISION,
    geom        GEOMETRY(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX idx_amenaza_conaf_asp_geom ON amenaza_conaf_areas_protegidas USING GIST (geom);

CREATE TABLE amenaza_sismos (
    id              SERIAL PRIMARY KEY,
    usgs_id         TEXT UNIQUE,
    magnitud        DOUBLE PRECISION,
    profundidad_km  DOUBLE PRECISION,
    fecha           TIMESTAMP,
    lugar           TEXT,
    geom            GEOMETRY(Point, 4326) NOT NULL
);
CREATE INDEX idx_amenaza_sismos_geom ON amenaza_sismos USING GIST (geom);
