from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin, Store
from dotenv import load_dotenv

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# إعدادات JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # يوم كامل

# إعداد التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ دالة التشفير
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ✅ التحقق من كلمة المرور
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ إنشاء التوكن
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ استخراج معرف المستخدم من التوكن
def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        return None

# ✅ دالة فك التوكن والتحقق من المحل
def get_current_store(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Store:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="لا يمكن التحقق من هوية المحل",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        store_id: str = payload.get("sub")
        if store_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    store = db.query(Store).filter(Store.id == int(store_id)).first()
    if store is None:
        raise credentials_exception
    return store

# ✅ دالة مساعدة لاستخراج البيانات من التوكن
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توكن غير صالح")

# ✅ استرجاع المشرف الحالي
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية كمشرف")

    user_id = payload.get("sub")
    admin = db.query(Admin).filter(Admin.id == int(user_id)).first()
    if not admin:
        raise HTTPException(status_code=404, detail="المشرف غير موجود")
    return admin

# ✅ استرجاع المحل الحالي
def get_current_store(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Store:
    payload = decode_token(token)
    if payload.get("role") != "store":
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية كمحل")

    user_id = payload.get("sub")
    store = db.query(Store).filter(Store.id == int(user_id)).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")
    return store