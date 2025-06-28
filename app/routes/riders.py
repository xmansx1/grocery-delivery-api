from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_admin  # تأكد أن هذا المسار صحيح

router = APIRouter(prefix="/riders", tags=["Riders"])

# ✅ تشفير كلمة المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ إضافة مندوب جديد
@router.post("/", response_model=schemas.RiderResponse)
def create_rider(data: schemas.RiderCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    existing = db.query(models.Rider).filter(models.Rider.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="❌ رقم الجوال مستخدم من قبل مندوب آخر")

    hashed_password = pwd_context.hash(data.password)

    new_rider = models.Rider(
        name=data.name,
        phone=data.phone,
        password=hashed_password,
        status=data.status
    )
    db.add(new_rider)
    db.commit()
    db.refresh(new_rider)
    return new_rider

# ✅ جلب جميع المناديب
@router.get("/", response_model=List[schemas.RiderResponse])
def get_riders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Rider).order_by(models.Rider.id.desc()).all()

# ✅ تعديل جميع بيانات المندوب (اختياري - لم تستخدمه الواجهة حتى الآن)
@router.put("/{rider_id}", response_model=schemas.RiderResponse)
def update_rider(rider_id: int, data: schemas.RiderCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")

    update_data = data.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = pwd_context.hash(update_data["password"])

    for key, value in update_data.items():
        setattr(rider, key, value)

    db.commit()
    db.refresh(rider)
    return rider

# ✅ تغيير الحالة فقط
@router.put("/{rider_id}/status", response_model=schemas.RiderResponse)
def update_rider_status(rider_id: int, status: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")

    rider.status = status
    db.commit()
    db.refresh(rider)
    return rider

# ✅ حذف المندوب
@router.delete("/{rider_id}")
def delete_rider(rider_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")

    db.delete(rider)
    db.commit()
    return {"detail": "✅ تم حذف المندوب بنجاح"}
