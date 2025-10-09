-- ==============================================
-- 🧱 Création du schéma de base de données MGPF
-- Multi-parkings, multi-admins, multi-entreprises
-- ==============================================

-- Supprime tout (optionnel si tu veux repartir propre)
DROP TABLE IF EXISTS parking_config CASCADE;
DROP TABLE IF EXISTS plaques CASCADE;
DROP TABLE IF EXISTS demandes CASCADE;
DROP TABLE IF EXISTS entreprises CASCADE;
DROP TABLE IF EXISTS parkings CASCADE;
DROP TABLE IF EXISTS admins CASCADE;

-- ==============================================
-- 👑 Table des administrateurs (liés à Clerk)
-- ==============================================
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 🅿️ Table des parkings
-- Chaque admin peut avoir plusieurs parkings
-- ==============================================
CREATE TABLE parkings (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    localisation VARCHAR(255),
    admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 🏢 Table des entreprises
-- Plusieurs entreprises peuvent partager un parking
-- ==============================================
CREATE TABLE entreprises (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    parking_id INTEGER NOT NULL REFERENCES parkings(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 📩 Table des demandes d’accès (page Visiteur)
-- ==============================================
CREATE TABLE demandes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    plaque VARCHAR(50) NOT NULL,
    entreprise_id INTEGER REFERENCES entreprises(id) ON DELETE CASCADE,
    parking_id INTEGER REFERENCES parkings(id) ON DELETE CASCADE,
    date_visite VARCHAR(50),
    heure_visite VARCHAR(50),
    statut VARCHAR(50) DEFAULT 'En attente',
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 🚗 Table des plaques autorisées
-- ==============================================
CREATE TABLE plaques (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    proprietaire VARCHAR(255) NOT NULL,
    entreprise_id INTEGER REFERENCES entreprises(id) ON DELETE CASCADE,
    parking_id INTEGER REFERENCES parkings(id) ON DELETE CASCADE,
    date_enregistrement TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 🧩 Table de configuration du parking (drag & drop)
-- ==============================================
CREATE TABLE parking_config (
    id SERIAL PRIMARY KEY,
    parking_id INTEGER NOT NULL REFERENCES parkings(id) ON DELETE CASCADE,
    layout JSONB NOT NULL,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- 🔍 Index utiles pour les performances
-- ==============================================
CREATE INDEX idx_plaques_numero_parking ON plaques(numero, parking_id);
CREATE INDEX idx_demandes_parking ON demandes(parking_id);
CREATE INDEX idx_entreprises_parking ON entreprises(parking_id);

-- ==============================================
-- ✅ Test rapide : insère un admin + parking exemple
-- ==============================================
INSERT INTO admins (clerk_id, nom, email)
VALUES ('user_12345', 'Admin Test', 'admin@test.com');

INSERT INTO parkings (nom, localisation, admin_id)
VALUES ('Parking Bellefontaine', 'Toulouse', 1);

INSERT INTO entreprises (nom, parking_id)
VALUES ('Ecofute', 1),
       ('MetaDX', 1);

-- ==============================================
-- Vérifie que tout fonctionne :
-- ==============================================
-- \dt             --> liste les tables
-- SELECT * FROM admins;
-- SELECT * FROM parkings;




DIAGRAM.IO 

// ========== ENUMS ==========
Enum user_role {
  super_admin
  admin
  gardien
}

Enum place_statut {
  libre
  occupee
  reservee
}

// ========== TABLES ==========


// ========== Entreprise ==========
Table structures {
  id int [pk, increment]
  nom varchar
  adresse varchar
}


// ========== Personne qui ==========
// ========== super_admin  ==========
// ========== admin        ==========
// ========== gardien      ==========
// ========== Personne qui ==========
// ========== Personne qui ==========
Table users {
  id int [pk, increment]
  email varchar [unique]
  mot_de_passe varchar
  nom varchar
  prenom varchar
  role user_role
  structure_id int [ref: > structures.id, null]
}


// ========== Personne qui ==========
// ========== super_admin  ==========
// ========== admin        ==========
// ========== gardien      ==========
// ========== Personne qui ==========
// ========== Personne qui ==========
Table parkings {
  id int [pk, increment]
  nom varchar
  description text [null]
  localisation varchar [null]
  structure_id int [ref: > structures.id]
}

Table places {
  id int [pk, increment]
  parking_id int [ref: > parkings.id]
  numero_place varchar
  statut place_statut [default: 'libre']
  couleur_code varchar [null]
  plaque_associee varchar [null]
  visiteur_id int [ref: > visiteurs.id, null]
  entreprise_id int [ref: > structures.id, null]
}

Table vehicules {
  id int [pk, increment]
  plaque varchar [unique]
  utilisateur_id int [ref: > users.id, null]
  structure_id int [ref: > structures.id]
}

Table visiteurs {
  id int [pk, increment]
  nom varchar
  prenom varchar
  plaque varchar [null]
  structure_id int [ref: > structures.id]
  date_visite date
  recurrent boolean [default: false]
}

Table entrees {
  id int [pk, increment]
  plaque varchar
  utilisateur_id int [ref: > users.id, null]
  visiteur_id int [ref: > visiteurs.id, null]
  date_heure_entree datetime
  place_id int [ref: > places.id]
  gardien_id int [ref: > users.id]
  structure_id int [ref: > structures.id]
}

Table journaux {
  id int [pk, increment]
  date date
  structure_id int [ref: > structures.id]
  snapshot_json text
}

Table stats_journalieres {
  id int [pk, increment]
  structure_id int [ref: > structures.id]
  date date
  nb_entrees int [default: 0]
  nb_visiteurs int [default: 0]
  nb_livreurs int [default: 0]
}
