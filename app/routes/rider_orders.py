from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_rider

router = APIRouter(
    prefix="/rider",
    tags=["Rider Orders"]
)

# ✅ جلب الطلبات الخاصة بالمندوب الحالي
@router.get("/orders", response_model=List[schemas.OrderResponse])
def get_rider_orders(db: Session = Depends(get_db), rider=Depends(get_current_rider)):
    orders = db.query(models.Order).filter(models.Order.rider_id == rider.id).order_by(models.Order.created_at.desc()).all()
    return orders

# ✅ تحديث حالة الطلب إلى تم التوصيل أو تم الإلغاء
@router.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db), rider=Depends(get_current_rider)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.rider_id == rider.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود أو غير مسند إليك")
    
    order.status = status
    db.commit()
    db.refresh(order)
    return order

# ✅ جلب عدد الطلبات التي تم تسليمها من قبل المندوب الحالي
@router.get("/orders/delivered-count")
def delivered_count(db: Session = Depends(get_db), rider=Depends(get_current_rider)):
    count = db.query(models.Order).filter(
        models.Order.rider_id == rider.id,
        models.Order.status == "تم التوصيل"
    ).count()
    return {"delivered": count}
