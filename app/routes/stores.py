from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_admin, get_current_store

router = APIRouter(prefix="/stores", tags=["Stores"])

# ✅ إعداد التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ إنشاء محل جديد
@router.post("/", response_model=schemas.StoreResponse)
def create_store(
    data: schemas.StoreCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # تحقق من تكرار الجوال
    existing = db.query(models.Store).filter(models.Store.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="رقم الجوال مستخدم بالفعل")

    hashed_password = pwd_context.hash(data.password)
    new_store = models.Store(
        name=data.name,
        phone=data.phone,
        password=hashed_password,
        is_active=data.is_active
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store

# ✅ جلب جميع المحلات
@router.get("/", response_model=List[schemas.StoreResponse])
def get_stores(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
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

    update_data = data.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = pwd_context.hash(update_data["password"])

    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store

# ✅ تغيير حالة المحل
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

# ✅ حذف محل
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

# ✅ جلب الطلبات الخاصة بالمحل
@router.get("/orders", response_model=List[schemas.OrderResponse])
def get_store_orders(db: Session = Depends(get_db), store=Depends(get_current_store)):
    orders = db.query(models.Order)\
        .filter(models.Order.store_id == store.id)\
        .order_by(models.Order.created_at.desc())\
        .all()

    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "order_text": order.order_text,
            "notes": order.notes,
            "lat": float(order.lat) if order.lat else None,
            "lng": float(order.lng) if order.lng else None,
            "status": order.status,
            "amount": order.amount,
            "rider_name": order.rider.name if order.rider else None,
            "created_at": order.created_at.isoformat()
        })
    return result
