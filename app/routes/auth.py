from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Literal
import os
from dotenv import load_dotenv
from pydantic import BaseModel

from app.database import get_db
from app.models import Admin, Store
from app.schemas import Token, StoreLogin

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# إعداد التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# إعدادات JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ نموذج موحد لتسجيل الدخول
class LoginRequest(BaseModel):
    phone: str
    password: str
    user_type: Literal["admin", "store"]

# ✅ تسجيل دخول مشرف أو صاحب محل
@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    if data.user_type == "admin":
        user = db.query(Admin).filter(Admin.phone == data.phone).first()
    elif data.user_type == "store":
        user = db.query(Store).filter(Store.phone == data.phone).first()
    else:
        raise HTTPException(status_code=400, detail="نوع المستخدم غير صالح")

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="رقم الجوال أو كلمة المرور غير صحيحة")

    token_data = {
        "sub": str(user.id),
        "role": data.user_type,
    }
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ تسجيل دخول مخصص للمحل (إن أردت الإبقاء عليه أيضًا)
@router.post("/store-login", response_model=Token)
def login_store(data: StoreLogin, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.phone == data.phone).first()
    if not store or not verify_password(data.password, store.password):
        raise HTTPException(status_code=401, detail="رقم الجوال أو كلمة المرور غير صحيحة")

    token_data = {"sub": str(store.id), "role": "store"}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
