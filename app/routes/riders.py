from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_admin

router = APIRouter(prefix="/riders", tags=["Riders"])

# ✅ إضافة مندوب جديد
@router.post("/", response_model=schemas.RiderResponse)
def create_rider(data: schemas.RiderCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    if db.query(models.Rider).filter(models.Rider.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="رقم الجوال مستخدم بالفعل")
    
    new_rider = models.Rider(**data.dict())
    db.add(new_rider)
    db.commit()
    db.refresh(new_rider)
    return new_rider

# ✅ جلب جميع المناديب
@router.get("/", response_model=List[schemas.RiderResponse])
def get_riders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Rider).all()

# ✅ تعديل بيانات مندوب
@router.put("/{rider_id}", response_model=schemas.RiderResponse)
def update_rider(rider_id: int, data: schemas.RiderCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")
    
    for key, value in data.dict().items():
        setattr(rider, key, value)
    
    db.commit()
    db.refresh(rider)
    return rider

# ✅ تغيير حالة المندوب فقط
@router.put("/{rider_id}/status", response_model=schemas.RiderResponse)
def update_rider_status(rider_id: int, status: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")
    
    rider.status = status
    db.commit()
    db.refresh(rider)
    return rider

# ✅ حذف مندوب
@router.delete("/{rider_id}")
def delete_rider(rider_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")
    
    db.delete(rider)
    db.commit()
    return {"detail": "✅ تم حذف المندوب بنجاح"}
