# app/routes/admin_orders.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth_admin import get_current_admin

router = APIRouter(prefix="/orders", tags=["Admin Orders"])

@router.get("/", response_model=list[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    orders = db.query(models.Order).all()

    results = []
    for order in orders:
        results.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "order_text": order.order_text,
            "notes": order.notes,
            "lat": order.lat,
            "lng": order.lng,
            "amount": order.amount,
            "status": order.status,
            "created_at": order.created_at,
            "store_name": order.store.name if order.store else None,
            "rider_name": order.rider.name if order.rider else None
        })
    
    return results

@router.put("/{order_id}/status")
def update_order_status(order_id: int, payload: dict, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return {"detail": "الطلب غير موجود"}
    order.status = payload["status"]
    db.commit()
    return {"message": "✅ تم التحديث بنجاح"}
