from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_admin_privileges(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == x_user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

def process_business_logic(measurement: models.Measurement, db: Session):
    max_temp_setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == "MAX_TEMP").first()
    threshold = float(max_temp_setting.value) if max_temp_setting else 28.0

    if measurement.temperature and measurement.temperature > threshold:
        alert = models.Alert(
            severity="HIGH",
            message=f"High temperature detected: {measurement.temperature}°C (Limit: {threshold}°C)",
            device_id=measurement.device_id
        )
        db.add(alert)
        db.commit()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=user.password,
        role=user.role 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    log = models.AuditLog(action="USER_REGISTERED", user_id=db_user.id, details=f"Role: {user.role}")
    db.add(log)
    db.commit()
    return db_user

@app.post("/admin/settings/", response_model=schemas.SystemSetting)
def create_system_setting(setting: schemas.SystemSettingCreate, admin: models.User = Depends(check_admin_privileges), db: Session = Depends(get_db)):
    db_setting = models.SystemSetting(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@app.put("/admin/users/{user_id}/block", response_model=schemas.User)
def block_user(user_id: int, block: bool, admin: models.User = Depends(check_admin_privileges), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_blocked = block
    log = models.AuditLog(
        action="USER_BLOCKED" if block else "USER_UNBLOCKED",
        user_id=admin.id,
        details=f"Target User ID: {user_id}"
    )
    db.add(log)
    db.commit()
    return user

@app.get("/admin/logs/", response_model=List[schemas.AuditLogBase])
def view_audit_logs(admin: models.User = Depends(check_admin_privileges), db: Session = Depends(get_db)):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).all()

@app.post("/measurements/", response_model=schemas.Measurement)
def add_measurement(measurement: schemas.MeasurementCreate, db: Session = Depends(get_db)):
    db_meas = models.Measurement(**measurement.dict())
    db.add(db_meas)
    
    device = db.query(models.Device).filter(models.Device.id == measurement.device_id).first()
    if device:
        device.is_online = True
        device.last_seen = models.datetime.utcnow()
    
    db.commit()
    db.refresh(db_meas)
    
    process_business_logic(db_meas, db)
    
    return db_meas

@app.get("/homes/{home_id}/analytics")
def get_home_analytics(home_id: int, db: Session = Depends(get_db)):
    avg_temp = db.query(func.avg(models.Measurement.temperature)).join(models.Device).join(models.Room).filter(models.Room.home_id == home_id).scalar()
    avg_humid = db.query(func.avg(models.Measurement.humidity)).join(models.Device).join(models.Room).filter(models.Room.home_id == home_id).scalar()
    
    return {
        "home_id": home_id,
        "average_temperature": round(avg_temp, 1) if avg_temp else None,
        "average_humidity": round(avg_humid, 1) if avg_humid else None
    }

@app.post("/homes/", response_model=schemas.Home)
def create_home(home: schemas.HomeCreate, db: Session = Depends(get_db)):
    db_home = models.Home(**home.dict())
    db.add(db_home)
    db.commit()
    db.refresh(db_home)
    return db_home

@app.post("/rooms/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = models.Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.post("/devices/", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = models.Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@app.get("/devices/{device_id}/alerts", response_model=List[schemas.Alert])
def get_device_alerts(device_id: int, db: Session = Depends(get_db)):
    return db.query(models.Alert).filter(models.Alert.device_id == device_id).all()