from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/store-auth", tags=["Store Auth"])

# ✅ إعداد التشفير وسر التوكن
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 ساعة

# ✅ تسجيل الدخول للمحل
@router.post("/login", response_model=schemas.Token)
def login_store(data: schemas.AdminLogin, db: Session = Depends(get_db)):
    # ✅ البحث باستخدام رقم الجوال (وليس الاسم)
    store = db.query(models.Store).filter(models.Store.phone == data.phone).first()
    if not store:
        raise HTTPException(status_code=401, detail="المحل غير موجود")

    # ✅ التحقق من كلمة المرور
    if not pwd_context.verify(data.password, store.password):
        raise HTTPException(status_code=403, detail="كلمة المرور غير صحيحة")

    # ✅ إنشاء التوكن
    to_encode = {
        "sub": str(store.id),
        "role": "store",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "store_name": store.name
    }
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "store_name": store.name
    }
