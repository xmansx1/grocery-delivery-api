from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_rider

router = APIRouter()

rider_router = APIRouter(prefix="/rider", tags=["Rider Orders"])

# ✅ جلب الطلبات الخاصة بالمندوب الحالي
@rider_router.get("/orders", response_model=List[schemas.OrderResponse])
def get_rider_orders(
    db: Session = Depends(get_db),
    rider=Depends(get_current_rider)
):
    return db.query(models.Order).filter(
        models.Order.rider_id == rider.id
    ).order_by(models.Order.created_at.desc()).all()

# ✅ تحديث حالة الطلب إلى "تم التوصيل" أو "تم الإلغاء"
@rider_router.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(
    order_id: int,
    status: str = Query(..., regex="^(تم التوصيل|تم الإلغاء)$"),
    db: Session = Depends(get_db),
    rider=Depends(get_current_rider)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.rider_id == rider.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود أو غير مسند إليك")

    order.status = status
    db.commit()
    db.refresh(order)
    return order

# ✅ عدد الطلبات التي تم توصيلها
@rider_router.get("/orders/delivered-count")
def delivered_count(
    db: Session = Depends(get_db),
    rider=Depends(get_current_rider)
):
    count = db.query(models.Order).filter(
        models.Order.rider_id == rider.id,
        models.Order.status == "تم التوصيل"
    ).count()
    return {"delivered": count}
