from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Runner(Base):
    __tablename__ = "runners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("TrackingSession", back_populates="runner")


class TrackingSession(Base):
    __tablename__ = "tracking_sessions"

    id = Column(Integer, primary_key=True, index=True)
    runner_id = Column(Integer, ForeignKey("runners.id"))
    total_distance = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow)

    runner = relationship("Runner", back_populates="sessions")
    measurements = relationship("Measurement", back_populates="session")


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tracking_sessions.id"))
    lat = Column(Float)
    lon = Column(Float)
    battery = Column(Float)
    temperature = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("TrackingSession", back_populates="measurements")
