from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import logging
from dotenv import load_dotenv

from app.database import get_db
from app.models import Admin, Store, Rider

# ✅ تحميل المتغيرات من .env
load_dotenv()

# ✅ إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ إعدادات المصادقة
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # يوم واحد
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

if not SECRET_KEY:
    logger.error("❌ متغير SECRET_KEY غير مضبوط")
    raise Exception("❌ SECRET_KEY environment variable is not set.")

# ✅ التشفير وفك التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"✅ Token Created (Role: {data.get('role')}, ID: {data.get('sub')})")
    return token

def decode_and_validate_token(token: str):
    try:
        logger.debug(f"🔐 Decoding token: {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id or not role:
            raise ValueError("Missing sub or role in token.")
        return payload
    except (JWTError, ValueError) as e:
        logger.error(f"❌ Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="تعذر التحقق من التوكن",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ✅ استرجاع المشرف
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    payload = decode_and_validate_token(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية كمشرف")
    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
    if not admin:
        raise HTTPException(status_code=404, detail="المشرف غير موجود")
    return admin



# ✅ استرجاع صاحب المحل
def get_current_store(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Store:
    payload = decode_and_validate_token(token)
    if payload["role"] != "store":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية كمحل")
    store = db.query(Store).filter(Store.id == int(payload["sub"])).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")
    return store

# ✅ استرجاع المندوب
def get_current_rider(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Rider:
    payload = decode_and_validate_token(token)
    if payload["role"] != "rider":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية كمندوب")
    rider = db.query(Rider).filter(Rider.id == int(payload["sub"])).first()
    if not rider:
        raise HTTPException(status_code=404, detail="المندوب غير موجود")
    return rider
