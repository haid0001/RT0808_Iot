# Plateforme IoT – GPS Tracking Thread (Simulation)

Projet réalisé dans le cadre du TP « Architecture IoT complète avec OpenThread ».

Ce projet implémente une architecture IoT complète en 5 couches intégrant :

- API REST (FastAPI)
- CoAP (communication capteurs)
- MQTT (temps réel)
- PostgreSQL (stockage)
- WebUI Leaflet (visualisation)
- Docker Compose (orchestration)

---

# 🧱 Architecture

## Couche 1 – Réseau Thread simulé

- 1 Leader (simulation)
- 1 Router (simulation)
- 3 End Devices :
  - GPS (CoAP)
  - Batterie (CoAP)
  - Température (CoAP)

## Couche 2 – Transport

- CoAP (UDP) pour communication Backend ↔ Capteurs
- MQTT pour diffusion temps réel
- HTTP REST pour communication WebUI ↔ Backend

## Couche 3 – Backend

- FastAPI
- Validation stricte des données
- Calcul distance (formule de Haversine)
- Authentification device (clé partagée)
- Gestion des erreurs CoAP
- Historique complet des mesures

## Couche 4 – Base de données

- PostgreSQL
- Stockage des runners, sessions, measurements

## Couche 5 – WebUI

- Page 1 : Enregistrement coureur
- Page 2 : Carte Leaflet temps réel
- Indicateurs distance, batterie, température

---

# 🚀 QUICK START

## 1️ Lancer le projet

À la racine du projet :

```bash
docker compose up --build


Attendre que tous les services soient démarrés.

2️ Accéder aux interfaces

Backend: http://localhost:8000/docs

Frontend : http://localhost:3000

3️ Tester le fonctionnement complet : http://localhost:3000

Entrer un nom + email Cliquer sur "Démarrer Tracking"

Cela crée automatiquement un runner , une session , Puis redirection vers la carte.

Étape B – Lancer la collecte capteurs ,dans Swagger (http://localhost:8000/docs) :

Endpoint :

POST /api/poll/{session_id}
Ajouter le header obligatoire : THREAD_SECRET_2026

Exécuter plusieurs fois , observer la carte , Sur la page tracking, le marqueur se déplace
la distance augmente , La batterie diminue progressivement , la température varie légèrement , la trajectoire est dessinée

Authentification Device
Les capteurs sont protégés par une clé partagée :
THREAD_SECRET_2026
Elle doit être envoyée dans le header .

Tests automatisés
Dans le container backend (ouvrez un autre terminal)

docker exec -it tracking_backend bash
pytest
Résultat attendu :

4 passed : Tests API , Tests validation , Test End-to-End (CoAP → Backend → DB)

```
