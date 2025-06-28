from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_store

router = APIRouter(prefix="/store", tags=["Store Orders"])

# ✅ جلب الطلبات الخاصة بالمحل
@router.get("/orders", response_model=list[schemas.OrderResponse])
def get_store_orders(db: Session = Depends(get_db), store=Depends(get_current_store)):
    return db.query(models.Order).filter(models.Order.store_id == store.id).order_by(models.Order.created_at.desc()).all()

# ✅ تحديث حالة الطلب (قيد التجهيز، تم الإلغاء، إلخ)
@router.post("/status/{order_id}", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, payload: dict, db: Session = Depends(get_db), store=Depends(get_current_store)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.store_id == store.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    order.status = payload.get("status")
    db.commit()
    db.refresh(order)
    return order

# ✅ إسناد الطلب إلى مندوب + إشعار واتساب
@router.post("/assign/{order_id}", response_model=schemas.OrderResponse)
def assign_order_to_rider(order_id: int, payload: dict, db: Session = Depends(get_db), store=Depends(get_current_store)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.store_id == store.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    # اختيار أول مندوب متاح
    rider = db.query(models.Rider).filter(models.Rider.status == "متاح ✅").first()
    if not rider:
        raise HTTPException(status_code=400, detail="لا يوجد مندوب متاح حالياً")

    # تحديث الطلب
    order.status = "قيد التوصيل"
    order.rider_id = rider.id
    order.amount = payload.get("amount")

    db.commit()
    db.refresh(order)

    # إرسال إشعار واتساب (بشكل مبسط)
    send_whatsapp_message(rider.phone, f"""
📦 طلب جديد للتوصيل:
👤 {order.customer_name}
📞 {order.customer_phone}
🧾 {order.order_text}
💵 {order.amount} ريال
📍 https://www.google.com/maps?q={order.lat},{order.lng}
""")

    return order

# ✅ دالة وهمية للإرسال - عدلها حسب مشروعك
def send_whatsapp_message(phone: str, message: str):
    print(f"📤 إرسال واتساب إلى {phone}:\n{message}")
