from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MeasurementBase(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_level: Optional[float] = None

class MeasurementCreate(MeasurementBase):
    device_id: int

class Measurement(MeasurementBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    severity: str
    message: str

class AlertCreate(AlertBase):
    device_id: int

class Alert(AlertBase):
    id: int
    is_resolved: bool
    timestamp: datetime
    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    name: str
    device_type: str
    mac_address: str

class DeviceCreate(DeviceBase):
    room_id: int

class Device(DeviceBase):
    id: int
    is_online: bool
    measurements: List[Measurement] = []
    alerts: List[Alert] = []
    class Config:
        from_attributes = True

class RoomBase(BaseModel):
    name: str
    floor: int
    area_sqm: float

class RoomCreate(RoomBase):
    home_id: int

class Room(RoomBase):
    id: int
    devices: List[Device] = []
    class Config:
        from_attributes = True

class HomeBase(BaseModel):
    name: str
    address: str

class HomeCreate(HomeBase):
    owner_id: int

class Home(HomeBase):
    id: int
    rooms: List[Room] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    homes: List[Home] = []
    class Config:
        from_attributes = True