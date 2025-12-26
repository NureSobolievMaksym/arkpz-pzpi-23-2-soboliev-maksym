from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    homes = relationship("Home", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")

class Home(Base):
    __tablename__ = "homes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="homes")
    rooms = relationship("Room", back_populates="home")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    floor = Column(Integer, default=1)
    area_sqm = Column(Float, nullable=True)
    home_id = Column(Integer, ForeignKey("homes.id"))
    
    home = relationship("Home", back_populates="rooms")
    devices = relationship("Device", back_populates="room")

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    device_type = Column(String)
    mac_address = Column(String, unique=True, index=True)
    is_online = Column(Boolean, default=False)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="devices")
    measurements = relationship("Measurement", back_populates="device")
    alerts = relationship("Alert", back_populates="device")

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    co2_level = Column(Float, nullable=True)
    power_usage = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    device_id = Column(Integer, ForeignKey("devices.id"))
    
    device = relationship("Device", back_populates="measurements")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String)
    message = Column(String)
    is_resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    device_id = Column(Integer, ForeignKey("devices.id"))
    
    device = relationship("Device", back_populates="alerts")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="audit_logs")