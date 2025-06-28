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

    rider_id = payload.get("rider_id")
    amount = payload.get("amount")

    if not rider_id or not amount:
        raise HTTPException(status_code=400, detail="يجب تحديد رقم المندوب وقيمة المبلغ")

    rider = db.query(models.Rider).filter(models.Rider.id == rider_id, models.Rider.status == "متاح ✅").first()
    if not rider:
        raise HTTPException(status_code=400, detail="المندوب غير متاح حالياً")

    order.status = "خرج للتوصيل"
    order.rider_id = rider.id
    order.amount = amount

    db.commit()
    db.refresh(order)

    send_whatsapp_message(rider.phone, f"""
🚚 طلب جديد للتوصيل
رقم الطلب: {order.id}
العميل: {order.customer_name}
الجوال: {order.customer_phone}
المبلغ المطلوب: {order.amount} ريال
الموقع: https://www.google.com/maps?q={order.lat},{order.lng}
""")

    send_whatsapp_message(order.customer_phone, f"""
📦 تم إسناد طلبك رقم {order.id} إلى مندوب التوصيل، وهو في الطريق إليك الآن.
""")

    return order


# ✅ إرجاع المناديب المتاحين فقط
@router.get("/available-riders")
def get_available_riders(
    db: Session = Depends(get_db),
    current_store=Depends(get_current_store)
):
    riders = db.query(models.Rider).filter(models.Rider.status == "متاح ✅").all()
    return [{"id": r.id, "name": r.name, "phone": r.phone} for r in riders]


# ✅ دالة إرسال واتساب (تجريبية)
def send_whatsapp_message(phone: str, message: str):
    print(f"📤 إرسال واتساب إلى {phone}:\n{message}")
