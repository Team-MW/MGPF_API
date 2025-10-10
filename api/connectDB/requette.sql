

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
