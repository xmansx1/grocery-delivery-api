from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_admin

router = APIRouter(prefix="/stores", tags=["Stores"])

# ✅ إنشاء محل جديد
@router.post("/", response_model=schemas.StoreResponse)
def create_store(
    data: schemas.StoreCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    new_store = models.Store(**data.dict())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store

# ✅ جلب جميع المحلات
@router.get("/", response_model=List[schemas.StoreResponse])
def get_stores(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(models.Store).all()

# ✅ تحديث بيانات محل
@router.put("/{store_id}", response_model=schemas.StoreResponse)
def update_store(
    store_id: int,
    data: schemas.StoreCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")

    for field, value in data.dict().items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store

# ✅ تغيير حالة المحل (تفعيل / إيقاف مؤقت)
@router.put("/{store_id}/status", response_model=schemas.StoreResponse)
def toggle_store_status(
    store_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")

    store.is_active = is_active
    db.commit()
    db.refresh(store)
    return store

# ✅ حذف محل نهائيًا
@router.delete("/{store_id}")
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")

    db.delete(store)
    db.commit()
    return {"detail": "✅ تم حذف المحل بنجاح"}
