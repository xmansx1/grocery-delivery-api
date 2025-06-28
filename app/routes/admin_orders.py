from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.auth_admin import get_current_admin
from typing import List

router = APIRouter()

@router.get("/admin/orders", response_model=List[schemas.OrderResponse])
def get_all_orders(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return orders
