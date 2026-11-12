-- Schéma reconstitué à partir des requêtes du code (main.py, routes/*).
-- Les fichiers requette.sql / requet_definitif.sql ne correspondent plus au code.

CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(255) UNIQUE,
    nom VARCHAR(255),
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS parking_id (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    admin_id VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS parking (
    id SERIAL PRIMARY KEY,
    plaque VARCHAR(50) UNIQUE NOT NULL,
    proprietaire VARCHAR(100),
    entreprise VARCHAR(100),
    places_selectionnees TEXT,
    admin_id VARCHAR(100),
    parking_id INTEGER REFERENCES parking_id(id) ON DELETE CASCADE,
    date_enregistrement TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS demandes (
    id SERIAL PRIMARY KEY,
    parking_id INTEGER NOT NULL REFERENCES parking_id(id) ON DELETE CASCADE,
    plaque VARCHAR(50) NOT NULL,
    entreprise VARCHAR(100) NOT NULL,
    statut VARCHAR(50) DEFAULT 'En attente',
    visiteur_id VARCHAR(100),
    email VARCHAR(100),
    admin_id VARCHAR(100),
    date_creation TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS suivis_gardien (
    id SERIAL PRIMARY KEY,
    plaque VARCHAR(50) NOT NULL,
    statut VARCHAR(50) NOT NULL,
    date_detection TIMESTAMP DEFAULT NOW(),
    parking_id INTEGER REFERENCES parking_id(id) ON DELETE CASCADE,
    clerk_id VARCHAR(100),
    type_scan VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS droits_gardiens (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(100) UNIQUE NOT NULL,
    parking_id INTEGER REFERENCES parking_id(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'gardien'
);

CREATE TABLE IF NOT EXISTS parking_layouts (
    parking_id INTEGER PRIMARY KEY REFERENCES parking_id(id) ON DELETE CASCADE,
    rows INTEGER DEFAULT 6,
    cols INTEGER DEFAULT 6,
    layout TEXT,
    spots TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tables ORM (models.py), utilisées par /plaques
CREATE TABLE IF NOT EXISTS parkings (
    id SERIAL PRIMARY KEY,
    nom VARCHAR NOT NULL,
    adresse VARCHAR,
    admin_id INTEGER
);

CREATE TABLE IF NOT EXISTS plaques (
    id SERIAL PRIMARY KEY,
    numero VARCHAR,
    proprietaire VARCHAR NOT NULL,
    entreprise VARCHAR,
    place_numero VARCHAR,
    parking_id INTEGER REFERENCES parkings(id),
    date_enregistrement TIMESTAMP DEFAULT NOW()
);
