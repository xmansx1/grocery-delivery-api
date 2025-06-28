from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Literal
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from app.database import get_db
from app.models import Admin, Store, Rider
from app.schemas import Token

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# ✅ إعداد تشفير كلمة المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ إعداد التوقيع
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # يوم واحد

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail="مفتاح التشفير غير معرف في .env")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ نموذج موحد لتسجيل الدخول للمشرف والمحل
class LoginRequest(BaseModel):
    phone: str
    password: str
    user_type: Literal["admin", "store"]

# ✅ نموذج تسجيل دخول المندوب
class RiderLoginRequest(BaseModel):
    phone: str
    password: str

# ✅ تسجيل دخول المشرف أو صاحب المحل
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

    token_data = {"sub": str(user.id), "role": data.user_type}
    access_token = create_access_token(token_data)

    # ✅ تجهيز الاستجابة بناءً على نوع المستخدم
    response = {
        "access_token": access_token,
        "token_type": "bearer"
    }

    if data.user_type == "store":
        response["store_name"] = user.name
    elif data.user_type == "admin":
        response["name"] = "المشرف"

    return response

# ✅ تسجيل دخول المندوب
@router.post("/rider-login", response_model=Token)
def login_rider(data: RiderLoginRequest, db: Session = Depends(get_db)):
    rider = db.query(Rider).filter(Rider.phone == data.phone).first()
    if not rider or not verify_password(data.password, rider.password):
        raise HTTPException(status_code=401, detail="رقم الجوال أو كلمة المرور غير صحيحة")

    token_data = {"sub": str(rider.id), "role": "rider"}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": rider.name
    }
