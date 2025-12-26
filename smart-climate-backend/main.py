from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    log = models.AuditLog(action="USER_REGISTERED", user_id=db_user.id)
    db.add(log)
    db.commit()
    return db_user

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
    return db_meas

@app.post("/alerts/", response_model=schemas.Alert)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_data(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/homes/{home_id}/statistics")
def get_home_stats(home_id: int, db: Session = Depends(get_db)):
    home = db.query(models.Home).filter(models.Home.id == home_id).first()
    if not home:
        raise HTTPException(404, "Home not found")
    
    total_devices = sum(len(room.devices) for room in home.rooms)
    active_alerts = db.query(models.Alert).join(models.Device).join(models.Room).filter(
        models.Room.home_id == home_id, models.Alert.is_resolved == False
    ).count()
    
    return {
        "home_name": home.name,
        "total_rooms": len(home.rooms),
        "total_devices": total_devices,
        "active_alerts": active_alerts
    }