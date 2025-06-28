from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

# ✅ جلب جميع الطلبات
@router.get("/", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()

# ✅ تحديث حالة الطلب أو البيانات المرتبطة به
@router.put("/{order_id}", response_model=schemas.OrderResponse)
def update_order(order_id: int, data: schemas.OrderCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order

# ✅ تحديث حالة الطلب فقط
@router.put("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status_value: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    
    order.status = status_value
    db.commit()
    db.refresh(order)
    return order

# ✅ إسناد الطلب إلى مندوب
@router.put("/{order_id}/assign", response_model=schemas.OrderResponse)
def assign_order_to_rider(order_id: int, rider_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    rider = db.query(models.Rider).filter(models.Rider.id == rider_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")
    
    order.rider_id = rider_id
    db.commit()
    db.refresh(order)
    return order
