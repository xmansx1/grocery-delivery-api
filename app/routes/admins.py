from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/admins", tags=["Admins"])

# ✅ إعداد تشفير كلمة المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ إنشاء مشرف جديد
@router.post("/", response_model=schemas.AdminResponse)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    existing_admin = db.query(models.Admin).filter(models.Admin.phone == admin.phone).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="رقم الجوال مستخدم بالفعل")

    hashed_password = pwd_context.hash(admin.password)
    new_admin = models.Admin(phone=admin.phone, password=hashed_password)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# ✅ عرض جميع المشرفين (اختياري - للمراجعة فقط)
@router.get("/", response_model=list[schemas.AdminResponse])
def list_admins(db: Session = Depends(get_db)):
    return db.query(models.Admin).all()

