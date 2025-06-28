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

# ✅ تحديث حالة الطلب
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

    # البحث عن المندوب المتاح المحدد
    rider_id = payload.get("rider_id")
    amount = payload.get("amount")

    if not rider_id or not amount:
        raise HTTPException(status_code=400, detail="يجب تحديد رقم المندوب وقيمة المبلغ")

    rider = db.query(models.Rider).filter(models.Rider.id == rider_id, models.Rider.status == "متاح ✅").first()
    if not rider:
        raise HTTPException(status_code=400, detail="المندوب غير متاح حالياً")

    # تحديث الطلب
    order.status = "خرج للتوصيل"
    order.rider_id = rider.id
    order.amount = amount

    db.commit()
    db.refresh(order)

    # ✅ إشعار المندوب
    send_whatsapp_message(rider.phone, f"""
🚚 طلب جديد للتوصيل
رقم الطلب: {order.id}
العميل: {order.customer_name}
الجوال: {order.customer_phone}
المبلغ المطلوب: {order.amount} ريال
الموقع: https://www.google.com/maps?q={order.lat},{order.lng}
""")

    # ✅ إشعار العميل
    send_whatsapp_message(order.customer_phone, f"""
📦 تم إسناد طلبك رقم {order.id} إلى مندوب التوصيل، وهو في الطريق إليك الآن.
""")

    return order

# ✅ دالة الإرسال - عدلها لاحقًا لاستخدام Twilio أو روابط واتساب
def send_whatsapp_message(phone: str, message: str):
    print(f"📤 إرسال واتساب إلى {phone}:\n{message}")
