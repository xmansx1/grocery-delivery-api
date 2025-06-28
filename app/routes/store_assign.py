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


class StatusPayload(BaseModel):
    status: str


# ✅ دالة تنسيق رقم الجوال
def format_phone_number(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0") and len(phone) == 10:
        return f"966{phone[1:]}"
    elif phone.startswith("966") and len(phone) == 12:
        return phone
    else:
        raise ValueError("📵 رقم الجوال غير صالح، تأكد أنه يبدأ بـ 0 أو يحتوي على 966")


# ✅ إسناد الطلب إلى مندوب
@store_router.post("/assign/{order_id}")
def assign_order_to_rider(
    order_id: int,
    payload: AssignPayload,
    db: Session = Depends(get_db),
    store=Depends(get_current_store)
):
    amount = payload.amount
    rider_id = payload.rider_id

    order = db.query(Order).filter(Order.id == order_id, Order.store_id == store.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    rider = db.query(Rider).filter(Rider.id == rider_id, Rider.status == "متاح ✅").first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير متاح")

    order.rider_id = rider.id
    order.amount = amount
    order.status = "قيد التوصيل"
    db.commit()
    db.refresh(order)

    # ✅ توليد رابط الموقع
    location_link = f"https://maps.google.com/?q={order.lat},{order.lng}" if order.lat and order.lng else "غير متوفر"

    try:
        rider_phone = format_phone_number(rider.phone)
        customer_phone = format_phone_number(order.customer_phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    msg_rider = (
        f"🚚 طلب جديد من {store.name}\n"
        f"👤 العميل: {order.customer_name}\n"
        f"📞 الجوال: {order.customer_phone}\n"
        f"📦 الطلب: {order.order_text}\n"
        f"💵 المبلغ: {order.amount} ريال\n"
        f"📍 الموقع: {location_link}\n"
        f"🔢 رقم الطلب: {order.id}"
    )
    whatsapp_rider = f"https://wa.me/{rider_phone}?text={quote(msg_rider)}"

    msg_customer = (
        f"📦 طلبك من {store.name} في الطريق إليك 🚚\n"
        f"🔢 رقم الطلب: {order.id}"
    )
    whatsapp_customer = f"https://wa.me/{customer_phone}?text={quote(msg_customer)}"

    return {
        "message": "✅ تم إسناد الطلب وتوليد روابط واتساب",
        "rider_whatsapp": whatsapp_rider,
        "customer_whatsapp": whatsapp_customer
    }


# ✅ تحديث حالة الطلب (مثل: قيد التجهيز)
@store_router.post("/status/{order_id}")
def update_order_status(
    order_id: int,
    payload: StatusPayload,
    db: Session = Depends(get_db),
    store=Depends(get_current_store)
):
    status = payload.status

    order = db.query(Order).filter(Order.id == order_id, Order.store_id == store.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    order.status = status
    db.commit()

    if status == "قيد التجهيز":
        try:
            phone = format_phone_number(order.customer_phone)
            msg = (
                f"📦 طلبك من {store.name}\n"
                f"تم استلامه وجاري التجهيز ✅\n"
                f"🔢 رقم الطلب: {order.id}"
            )
            whatsapp_link = f"https://wa.me/{phone}?text={quote(msg)}"
            return {
                "message": "✅ تم التحديث والإرسال للعميل",
                "whatsapp_link": whatsapp_link
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {"message": "✅ تم تحديث الحالة"}
