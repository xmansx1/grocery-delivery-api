from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from urllib.parse import quote

from app.database import get_db
from app.models import Order, Rider
from app.utils.jwt import get_current_store

store_router = APIRouter(prefix="/store", tags=["Store"])

class AssignPayload(BaseModel):
    amount: float
    rider_id: int

@store_router.post("/assign/{order_id}")
def assign_order_to_rider(
    order_id: int,
    payload: AssignPayload,
    db: Session = Depends(get_db),
    store=Depends(get_current_store)
):
    amount = payload.amount
    rider_id = payload.rider_id

    # ✅ التأكد من وجود الطلب والمندوب
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.store_id == store.id
    ).first()

    rider = db.query(Rider).filter(
        Rider.id == rider_id,
        Rider.status == "متاح ✅"
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير متاح")

    # ✅ تحديث الطلب
    order.rider_id = rider.id
    order.amount = amount
    order.status = "قيد التوصيل"
   
    db.commit()
    db.refresh(order)

    # ✅ توليد رابط الموقع
    location_link = f"https://maps.google.com/?q={order.lat},{order.lng}" if order.lat is not None and order.lng is not None else "غير متوفر"

    # ✅ رسالة للمندوب
    msg_rider = (
        f"🚚 تم إسناد طلب جديد لك\n"
        f"👤 العميل: {order.customer_name}\n"
        f"📞 الجوال: {order.customer_phone}\n"
        f"📦 الطلب: {order.order_text}\n"
        f"💵 المبلغ: {order.amount} ريال\n"
        f"📍 الموقع: {location_link}\n"
        f"🔢 رقم الطلب: {order.id}"
    )
    whatsapp_rider_link = f"https://wa.me/966{rider.phone[1:]}?text={quote(msg_rider)}"

    # ✅ رسالة للعميل
    msg_customer = (
        f"🚚 تم تحويل طلبك إلى مندوب التوصيل\n"
        f"📦 الطلب: {order.order_text}\n"
        f"💵 المبلغ: {order.amount} ريال\n"
        f"📞 المندوب: {rider.name} - {rider.phone}"
    )
    whatsapp_customer_link = f"https://wa.me/966{order.customer_phone[1:]}?text={quote(msg_customer)}"

    return {
        "message": "✅ تم إسناد الطلب وتوليد روابط واتساب",
        "rider_whatsapp": whatsapp_rider_link,
        "customer_whatsapp": whatsapp_customer_link
    }
