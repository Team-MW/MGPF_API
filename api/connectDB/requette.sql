

 -- Table Parking

CREATE TABLE IF NOT EXISTS parking (
  id SERIAL PRIMARY KEY,
  plaque VARCHAR(20) NOT NULL,             -- Plaque d'immatriculation
  proprietaire VARCHAR(255) NOT NULL,      -- Nom du propriétaire
  entreprise VARCHAR(255),                 -- Nom de l’entreprise (facultatif)
  places_selectionnees TEXT,               -- Liste des places (stockée en JSON ou texte)
  date_enregistrement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  admin_id VARCHAR(255)                    -- L’ID du gérant (Clerk)
);

 -- Mise as jours de la table
CREATE TABLE IF NOT EXISTS parking (
    id SERIAL PRIMARY KEY,
    plaque VARCHAR(20) NOT NULL,
    proprietaire VARCHAR(255),
    entreprise VARCHAR(255),
    places_selectionnees TEXT,
    date_enregistrement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parking_id INTEGER REFERENCES parking_id(id) ON DELETE CASCADE
);



 -- Suivis Gardien
CREATE TABLE suivis_gardien (
    id SERIAL PRIMARY KEY,
    plaque VARCHAR(50) NOT NULL,
    statut VARCHAR(50) NOT NULL,
    parking_id INTEGER,
    clerk_id VARCHAR(100),
    type_scan VARCHAR(20), -- "auto" ou "manuel"
    date_heure TIMESTAMP DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS demandes (
    id SERIAL PRIMARY KEY,
    parking VARCHAR(255),
    plaque VARCHAR(50),
    entreprise VARCHAR(255),
    statut VARCHAR(50) DEFAULT 'En attente',
    visiteur_id VARCHAR(255),
    email VARCHAR(255),
    admin_id VARCHAR(255),  --  texte et non pas integer
    date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 -- Gére pouir les demande et aussi pour que l'admin puisse modifier que sont parking
CREATE TABLE IF NOT EXISTS parking_id (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,          -- Nom du parking
    adresse VARCHAR(255),
    admin_id VARCHAR(255) NOT NULL,     -- ID Clerk de l'admin
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




 -- Requet disposition parking

 CREATE TABLE IF NOT EXISTS parking_layouts (
  parking_id INTEGER PRIMARY KEY REFERENCES parking_id(id) ON DELETE CASCADE,
  rows INTEGER NOT NULL,
  cols INTEGER NOT NULL,
  layout JSONB NOT NULL DEFAULT '[]',   -- grille / murs / etc.
  spots  JSONB NOT NULL DEFAULT '[]',   -- [{ "id":"A1", "status":"free|occupied" }, ...]
  updated_at TIMESTAMP DEFAULT NOW()
);

 -- Requet disposition parking 2
CREATE TABLE parking_config (
    id SERIAL PRIMARY KEY,
    parking_id INTEGER UNIQUE,
    rows INTEGER,
    cols INTEGER,
    layout JSONB,
    spots JSONB
);

 --- Droit gardien
CREATE TABLE droits_gardiens (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(100) UNIQUE NOT NULL,  -- ID Clerk du gardien
    parking_id INTEGER NOT NULL REFERENCES parking_id(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'gardien',     -- optionnel (gardien, superviseur...)
    date_attribution TIMESTAMP DEFAULT NOW()
);


-- ins&rer le premier gardien

INSERT INTO droits_gardiens (clerk_id, parking_id, role)
VALUES ('user_340cVVVVmatUaG4Qti8Js62NCYb', 1, 'gardien')
ON CONFLICT (clerk_id)
DO UPDATE SET parking_id = EXCLUDED.parking_id;
