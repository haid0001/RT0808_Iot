# Plateforme IoT GPS Tracking

Architecture IoT complète avec :

- CoAP (capteur simulé)
- MQTT (temps réel)
- FastAPI (backend)
- PostgreSQL (persistance)
- Leaflet (visualisation)
- Docker Compose (orchestration)

## Architecture

Couche 1 : Capteur CoAP simulé (aiocoap)  
Couche 2 : Transport UDP (CoAP)  
Couche 3 : Backend FastAPI  
Couche 4 : PostgreSQL  
Couche 5 : WebUI Leaflet + MQTT

## Lancement

```bash
docker compose up --build
```

Backend :
http://localhost:8000/docs

Frontend :
http://localhost:3000
