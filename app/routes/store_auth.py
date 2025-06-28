from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/store-auth", tags=["Store Auth"])

# ✅ إعداد تشفير كلمة المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ إعداد سر التوقيع
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ✅ دالة لإنشاء التوكن
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ مسار تسجيل دخول المحل
@router.post("/login", response_model=schemas.Token)
def store_login(data: schemas.StoreLogin, db: Session = Depends(get_db)):
    store = db.query(models.Store).filter(models.Store.username == data.username).first()
    if not store or not pwd_context.verify(data.password, store.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="اسم المستخدم أو كلمة المرور غير صحيحة")

    access_token = create_access_token(data={"sub": f"{store.id}", "role": "store"})
    return {"access_token": access_token, "token_type": "bearer"}
