# app/routes/admin_orders.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth_admin import get_current_admin

router = APIRouter(prefix="/orders", tags=["Admin Orders"])

@router.get("/", response_model=list[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()

@router.put("/{order_id}/status")
def update_order_status(order_id: int, payload: dict, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return {"detail": "الطلب غير موجود"}
    order.status = payload["status"]
    db.commit()
    return {"message": "✅ تم التحديث بنجاح"}
