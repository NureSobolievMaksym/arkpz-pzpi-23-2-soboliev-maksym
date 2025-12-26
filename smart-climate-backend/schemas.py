from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

# --- System Settings ---
class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSetting(SystemSettingBase):
    id: int
    class Config:
        from_attributes = True

# --- Logs ---
class AuditLogBase(BaseModel):
    action: str
    details: Optional[str] = None
    timestamp: datetime
    user_id: int
    class Config:
        from_attributes = True

# --- Measurements ---
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

# --- Alerts ---
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

# --- Devices ---
class DeviceBase(BaseModel):
    name: str
    device_type: str
    mac_address: str

class DeviceCreate(DeviceBase):
    room_id: int

class Device(DeviceBase):
    id: int
    is_online: bool = False  # Додано дефолтне значення
    measurements: List[Measurement] = []
    alerts: List[Alert] = []
    class Config:
        from_attributes = True

# --- Rooms ---
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

# --- Homes ---
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

# --- Users ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    is_blocked: Optional[bool] = None
    role: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool = True      # <-- ВИПРАВЛЕНО: Додано значення за замовчуванням
    is_blocked: bool = False    # <-- ВИПРАВЛЕНО: Додано значення за замовчуванням
    role: str
    homes: List[Home] = []
    class Config:
        from_attributes = True