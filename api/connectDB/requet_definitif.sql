CREATE TABLE parking_id (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    admin_id VARCHAR(100) NOT NULL  -- Clerk ID de l’admin relié à ce parking
);


CREATE TABLE parking (
    id SERIAL PRIMARY KEY,
    plaque VARCHAR(50) UNIQUE NOT NULL,
    proprietaire VARCHAR(100),
    entreprise VARCHAR(100),
    places_selectionnees TEXT,
    admin_id VARCHAR(100),       -- Clerk ID de l’admin propriétaire
    parking_id INTEGER,          -- Référence au parking_id
    date_enregistrement TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (parking_id) REFERENCES parking_id(id) ON DELETE CASCADE
);


CREATE TABLE demandes (
    id SERIAL PRIMARY KEY,
    parking_id INTEGER NOT NULL,
    plaque VARCHAR(50) NOT NULL,
    entreprise VARCHAR(100) NOT NULL,
    statut VARCHAR(50) DEFAULT 'En attente',
    visiteur_id VARCHAR(100),     -- Clerk ID du visiteur
    email VARCHAR(100),
    admin_id VARCHAR(100),        -- L’admin responsable du parking choisi
    date_creation TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (parking_id) REFERENCES parking_id(id) ON DELETE CASCADE
);


CREATE TABLE suivis_gardien (
    id SERIAL PRIMARY KEY,
    plaque VARCHAR(50) NOT NULL,
    statut VARCHAR(50) NOT NULL,          -- "Autorisé" / "Refusé"
    date_detection TIMESTAMP DEFAULT NOW(),
    parking_id INTEGER,
    gardien_id VARCHAR(100),              -- Clerk ID du gardien
    FOREIGN KEY (parking_id) REFERENCES parking_id(id) ON DELETE CASCADE
);
