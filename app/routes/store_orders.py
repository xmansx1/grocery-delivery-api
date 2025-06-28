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

# ✅ دالة المساعدة لإسناد الطلب
def assign_order_logic(order: models.Order, rider: models.Rider, amount: float):
    order.rider_id = rider.id
    order.amount = amount
    order.status = "قيد التوصيل"
    return order

# ✅ إسناد الطلب إلى مندوب + توليد روابط واتساب
@router.post("/assign/{order_id}")
def assign_order_to_rider(
    order_id: int,
    data: schemas.AssignOrderRequest,
    db: Session = Depends(get_db),
    store=Depends(get_current_store)
):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.store_id == store.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")

    rider = db.query(models.Rider).filter(models.Rider.id == data.rider_id, models.Rider.status == "متاح ✅").first()
    if not rider:
        raise HTTPException(status_code=400, detail="المندوب غير متاح حالياً")

    assign_order_logic(order, rider, data.amount)
    db.commit()

    # روابط واتساب
    rider_message = f"🚚 طلب جديد\nالعميل: {order.customer_name}\nالجوال: {order.customer_phone}\nالطلب: {order.order_text}\nالمبلغ: {data.amount} ريال\nالموقع: https://maps.google.com/?q={order.lat},{order.lng}"
    customer_message = f"📦 تم إرسال طلبك للتوصيل وسيتم التواصل معك قريبًا"

    return {
        "success": True,
        "rider_whatsapp": f"https://wa.me/{rider.phone}?text={rider_message}",
        "customer_whatsapp": f"https://wa.me/{order.customer_phone}?text={customer_message}"
    }

# ✅ Alias بديل لقبول الطلبات من /orders/{id}/assign
@router.post("/orders/{order_id}/assign")
def alias_assign_order(
    order_id: int,
    data: schemas.AssignOrderRequest,
    db: Session = Depends(get_db),
    store=Depends(get_current_store)
):
    return assign_order_to_rider(order_id, data, db, store)

# ✅ جلب المناديب المتاحين فقط
@router.get("/available-riders")
def get_available_riders(db: Session = Depends(get_db), store=Depends(get_current_store)):
    riders = db.query(models.Rider).filter(models.Rider.status == "متاح ✅").all()
    return [{"id": r.id, "name": r.name, "phone": r.phone} for r in riders]

# ✅ دالة إرسال واتساب (اختيارية)
def send_whatsapp_message(phone: str, message: str):
    print(f"📤 إرسال واتساب إلى {phone}:\n{message}")
