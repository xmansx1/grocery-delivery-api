from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/ads", tags=["الإعلانات"])

# ✅ جلب جميع الإعلانات الفعّالة فقط
@router.get("/", response_model=list[schemas.AdResponse])
def get_active_ads(db: Session = Depends(get_db)):
    return db.query(models.Ad).filter(models.Ad.is_active == True).order_by(models.Ad.created_at.desc()).all()

# ✅ إضافة إعلان جديد
@router.post("/", response_model=schemas.AdResponse)
def create_ad(ad: schemas.AdCreate, db: Session = Depends(get_db)):
    new_ad = models.Ad(**ad.dict())
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

# ✅ تعديل تفعيل/تعطيل
@router.put("/{ad_id}")
def toggle_ad(ad_id: int, payload: dict, db: Session = Depends(get_db)):
    ad = db.query(models.Ad).get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="الإعلان غير موجود")
    ad.is_active = payload.get("is_active", True)
    db.commit()
    return {"message": "تم التحديث"}

# ✅ حذف إعلان
@router.delete("/{ad_id}")
def delete_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(models.Ad).get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="الإعلان غير موجود")
    db.delete(ad)
    db.commit()
    return {"message": "تم الحذف"}
