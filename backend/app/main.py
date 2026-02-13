from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from .database import engine, Base, SessionLocal
from . import models
from pydantic import BaseModel
import math
import json
import paho.mqtt.client as mqtt
import asyncio
from aiocoap import Context, Message
from aiocoap.numbers.codes import Code
DEVICE_SECRET = "THREAD_SECRET_2026"
from fastapi import Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MQTT SETUP ----------------

mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt", 1883, 60)
mqtt_client.loop_start()

# ---------------- DB INIT ----------------

Base.metadata.create_all(bind=engine)


# ---------------- DB DEPENDENCY ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- SCHEMAS ----------------

class RunnerCreate(BaseModel):
    name: str
    email: str


class SessionCreate(BaseModel):
    runner_id: int


class MeasurementCreate(BaseModel):
    session_id: int
    lat: float
    lon: float
    battery: float
    temperature: float


# ---------------- UTILS ----------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # mètres

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# async def fetch_coap_data():
#     protocol = await Context.create_client_context()

#     request = Message(code=Code.GET, uri="coap://sensor_gps:5683/gps")

#     response = await protocol.request(request).response

#     return json.loads(response.payload.decode())

async def fetch_gps():
    try:
        protocol = await Context.create_client_context()
        request = Message(code=Code.GET, uri="coap://sensor_gps:5683/gps")
        response = await protocol.request(request).response
        return json.loads(response.payload.decode())
    except Exception as e:
        return {"error": "GPS sensor unavailable"}



async def fetch_battery():
    try:
        protocol = await Context.create_client_context()
        request = Message(code=Code.GET, uri="coap://sensor_battery:5683/battery")
        response = await protocol.request(request).response
        return json.loads(response.payload.decode())
    except Exception as e:
        return {"error": "Battery sensor unavailable"}


async def fetch_temperature():
    try:
        protocol = await Context.create_client_context()
        request = Message(code=Code.GET, uri="coap://sensor_temperature:5683/temperature")
        response = await protocol.request(request).response
        return json.loads(response.payload.decode())
    except Exception as e:
        return {"error": "Temperature sensor unavailable"}


# ---------------- ROUTES ----------------

@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except OperationalError:
        return {"status": "error", "database": "not connected"}


@app.post("/api/runners")
def create_runner(runner: RunnerCreate, db: Session = Depends(get_db)):
    new_runner = models.Runner(
        name=runner.name,
        email=runner.email
    )
    db.add(new_runner)
    db.commit()
    db.refresh(new_runner)
    return new_runner


@app.post("/api/sessions")
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    new_session = models.TrackingSession(
        runner_id=session.runner_id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@app.post("/api/measurements")
def create_measurement(data: MeasurementCreate, db: Session = Depends(get_db)):

    # -------- VALIDATION STRICTE --------

    if not (-90 <= data.lat <= 90):
        return {"error": "Latitude invalide"}

    if not (-180 <= data.lon <= 180):
        return {"error": "Longitude invalide"}

    if not (0 <= data.battery <= 100):
        return {"error": "Batterie invalide"}

    if not (-40 <= data.temperature <= 60):
        return {"error": "Température invalide"}

    session = db.query(models.TrackingSession).filter(
        models.TrackingSession.id == data.session_id
    ).first()

    if not session:
        return {"error": "Session non trouvée"}

    # -------- CALCUL DISTANCE --------

    last_measure = db.query(models.Measurement).filter(
        models.Measurement.session_id == data.session_id
    ).order_by(models.Measurement.id.desc()).first()

    distance = 0

    if last_measure:
        distance = haversine(
            last_measure.lat,
            last_measure.lon,
            data.lat,
            data.lon
        )
        session.total_distance += distance

    # -------- STOCKAGE --------

    new_measure = models.Measurement(
        session_id=data.session_id,
        lat=data.lat,
        lon=data.lon,
        battery=data.battery,
        temperature=data.temperature
    )

    db.add(new_measure)
    db.commit()
    db.refresh(new_measure)

    # -------- MQTT PUBLICATION --------

    topic = f"/tracking/{data.session_id}/gps"

    payload = {
        "lat": data.lat,
        "lon": data.lon,
        "battery": data.battery,
        "temperature": data.temperature,
        "total_distance": round(session.total_distance, 2)
    }

    mqtt_client.publish(topic, json.dumps(payload))

    return {
        "measurement_id": new_measure.id,
        "distance_added_m": round(distance, 2),
        "total_distance_m": round(session.total_distance, 2)
    }
@app.post("/api/poll/{session_id}")
async def poll_sensor(
    session_id: int,
    db: Session = Depends(get_db),
    x_device_key: str = Header(None)
):

    if x_device_key != DEVICE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized device")

    gps = await fetch_gps()
    if "error" in gps:
        return {"error": "GPS sensor unavailable"}

    battery = await fetch_battery()
    if "error" in battery:
        return {"error": "Battery sensor unavailable"}

    temperature = await fetch_temperature()
    if "error" in temperature:
        return {"error": "Temperature sensor unavailable"}


    measurement_data = MeasurementCreate(
        session_id=session_id,
        lat=gps["lat"],
        lon=gps["lon"],
        battery=battery["battery"],
        temperature=temperature["temperature"]
    )

    return create_measurement(measurement_data, db)


@app.get("/api/sessions/{session_id}/history")
def get_history(session_id: int, db: Session = Depends(get_db)):

    measurements = db.query(models.Measurement).filter(
        models.Measurement.session_id == session_id
    ).order_by(models.Measurement.timestamp.asc()).all()

    return [
        {
            "lat": m.lat,
            "lon": m.lon,
            "battery": m.battery,
            "temperature": m.temperature,
            "timestamp": m.timestamp
        }
        for m in measurements
    ]

