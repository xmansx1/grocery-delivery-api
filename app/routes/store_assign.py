from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from urllib.parse import quote

from app.database import get_db
from app.models import Order, Rider
from app.utils.jwt import get_current_store

store_router = APIRouter(prefix="/store", tags=["Store"])


# ✅ نموذج البيانات المستلمة من المحل
class AssignPayload(BaseModel):
    amount: float
    rider_id: int


# ✅ دالة تنسيق رقم الجوال السعودي لواتساب
def format_phone_number(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0") and len(phone) == 10:
        return f"966{phone[1:]}"
    elif phone.startswith("966") and len(phone) == 12:
        return phone
    raise ValueError("📵 رقم الجوال غير صالح")


@store_router.post("/assign/{order_id}")
def assign_order_to_rider(
    order_id: int,
    payload: AssignPayload,
    db: Session = Depends(get_db),
    store=Depends(get_current_store)
):
    # ✅ جلب الطلب
    order = db.query(Order).filter(Order.id == order_id, Order.store_id == store.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    # ✅ التحقق من المندوب
    rider = db.query(Rider).filter(Rider.id == payload.rider_id, Rider.status == "متاح ✅").first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير متاح حالياً")

    # ✅ تحديث الطلب
    order.rider_id = rider.id
    order.amount = payload.amount
    order.status = "قيد التوصيل"
    db.commit()
    db.refresh(order)

    # ✅ روابط الموقع الجغرافي
    location_link = "غير متوفر"
    if order.lat is not None and order.lng is not None:
        location_link = f"https://maps.google.com/?q={order.lat},{order.lng}"

    # ✅ تنسيق الأرقام
    try:
        rider_phone = format_phone_number(rider.phone)
        customer_phone = format_phone_number(order.customer_phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    whatsapp_rider_link = f"https://wa.me/{rider_phone}?text={quote(msg_rider, safe='')}"

    # ✅ رسالة للعميل
    msg_customer = (
        f"🚚 تم تحويل طلبك إلى مندوب التوصيل\n"
        f"📦 الطلب: {order.order_text}\n"
        f"💵 المبلغ: {order.amount} ريال\n"
        f"📞 المندوب: {rider.name} - {rider.phone}"
    )
    whatsapp_customer_link = f"https://wa.me/{customer_phone}?text={quote(msg_customer, safe='')}"

    # ✅ سجل للمطور (اختياري)
    print("✅ روابط واتساب:")
    print("📤 مندوب:", whatsapp_rider_link)
    print("📤 عميل:", whatsapp_customer_link)

    return {
        "message": "✅ تم إسناد الطلب وتوليد روابط واتساب",
        "rider_whatsapp": whatsapp_rider_link,
        "customer_whatsapp": whatsapp_customer_link
    }
