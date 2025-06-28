from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.jwt import get_current_admin
from app import models

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "غير موجود"}}
)

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    total_orders = db.query(models.Order).count()
    total_stores = db.query(models.Store).count()
    total_riders = db.query(models.Rider).count()
    processing_orders = db.query(models.Order).filter(models.Order.status == "قيد التجهيز").count()
    completed_orders = db.query(models.Order).filter(models.Order.status == "تم التوصيل").count()

    return {
        "orders": total_orders,
        "stores": total_stores,
        "riders": total_riders,
        "processing": processing_orders,
        "completed": completed_orders
    }
