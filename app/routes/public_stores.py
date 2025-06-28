from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/public",
    tags=["Public"]
)

# ✅ جلب المحلات الفعالة فقط
@router.get("/stores", response_model=list[schemas.StoreResponse])
def get_active_stores(db: Session = Depends(get_db)):
    return db.query(models.Store).filter(models.Store.is_active == True).all()

# ✅ استقبال طلب جديد من العميل
@router.post("/order", status_code=status.HTTP_201_CREATED)
def create_order(data: schemas.OrderCreate, db: Session = Depends(get_db)):
    store = db.query(models.Store).filter(models.Store.id == data.store_id, models.Store.is_active == True).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود أو غير مفعل")

    new_order = models.Order(
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        order_text=data.order_text,
        notes=data.notes,
        lat=data.lat,
        lng=data.lng,
        store_id=data.store_id,
        status=data.status or "جديد"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {"message": "✅ تم استلام الطلب بنجاح"}
