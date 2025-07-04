from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/public",
    tags=["Public Order"]
)

@router.post("/order")
def create_public_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        store_id=order.store_id,
        order_text=order.order_text,
        notes=order.notes,
        lat=order.lat,
        lng=order.lng,
        amount=order.amount  # ✅ تمرير القيمة إذا كانت موجودة
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"message": "✅ تم استلام الطلب", "order_id": new_order.id}