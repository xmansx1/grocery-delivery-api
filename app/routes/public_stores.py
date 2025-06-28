from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/public",
    tags=["Public"]
)

@router.get("/stores", response_model=list[schemas.StoreResponse])
def get_active_stores(db: Session = Depends(get_db)):
    return db.query(models.Store).filter(models.Store.is_active == True).all()
