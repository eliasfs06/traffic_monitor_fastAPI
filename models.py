from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class TrafficRaw(Base):
    __tablename__ = "traffic_raw"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String)
    timestamp = Column(DateTime)
    street_id = Column(String)
    vehicle_count = Column(Integer)
    congestion_level = Column(String)

class TrafficStatus(Base):
    __tablename__ = "traffic_status"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String)
    timestamp = Column(DateTime)
    street_id = Column(String)
    congestion_level = Column(String)

class DeviceHealth(Base):
    __tablename__ = "device_health"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String)
    timestamp = Column(DateTime)
    status = Column(String)
    uptime_s = Column(Integer)
