from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv # استيراد load_dotenv
import logging # استيراد مكتبة logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin, Store, Rider # ✅ تأكد من استيراد Rider أيضاً إذا كنت تتحقق من المندوبين

# ✅ هذا السطر يكفي، تأكد أنه في بداية الملف
load_dotenv() 

# ✅ إعداد الـ logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ✅ إعدادات JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # يوم كامل (يمكن زيادته للتجربة)

# ✅ التحقق من وجود SECRET_KEY عند بدء التطبيق
if SECRET_KEY is None:
    logger.error("SECRET_KEY environment variable is not set. JWT operations will fail.")
    raise Exception("SECRET_KEY environment variable is not set.")

# ✅ إعداد التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ دالة التشفير (للاستخدام عند إنشاء المستخدمين)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ✅ التحقق من كلمة المرور (للاستخدام عند تسجيل الدخول)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ إنشاء التوكن
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Created token for sub: {data.get('sub')}, role: {data.get('role')} (Snippet: {encoded_jwt[:10]}...)")
    return encoded_jwt

# ✅ دالة موحدة لفك تشفير التوكن والتحقق الأولي
def decode_and_validate_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Decoding token snippet: {token[:10]}...") # سجل التوكن الوارد
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        if user_id is None or user_role is None:
            logger.warning("Token payload missing 'sub' or 'role'.")
            raise credentials_exception
        logger.info(f"Token decoded: User ID={user_id}, Role={user_role}")
        return payload
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token decoding: {e}")
        raise credentials_exception

# ✅ استرجاع المشرف الحالي
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    payload = decode_and_validate_token(token) # استخدام الدالة الموحدة
    
    if payload.get("role") != "admin":
        logger.warning(f"Unauthorized access attempt: Expected 'admin' role, got '{payload.get('role')}'")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ليس لديك صلاحية كمشرف")

    user_id = payload.get("sub")
    admin = db.query(Admin).filter(Admin.id == int(user_id)).first()
    if not admin:
        logger.warning(f"Admin with ID {user_id} not found in DB after token validation.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المشرف غير موجود")
    return admin

# ✅ استرجاع المحل الحالي (تم تصحيح التكرار)
# تم حذف الدالة get_current_store المكررة السابقة.
def get_current_store(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Store:
    payload = decode_and_validate_token(token) # استخدام الدالة الموحدة
    
    if payload.get("role") != "store":
        logger.warning(f"Unauthorized access attempt: Expected 'store' role, got '{payload.get('role')}'")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ليس لديك صلاحية كمحل")

    user_id = payload.get("sub")
    store = db.query(Store).filter(Store.id == int(user_id)).first()
    if not store:
        logger.warning(f"Store with ID {user_id} not found in DB after token validation.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المحل غير موجود")
    return store

# ✅ يمكنك إضافة دالة مشابهة لـ get_current_rider إذا كنت تستخدم توكنات للمندوبين
# def get_current_rider(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Rider:
#     payload = decode_and_validate_token(token)
#     if payload.get("role") != "rider":
#         logger.warning(f"Unauthorized access attempt: Expected 'rider' role, got '{payload.get('role')}'")
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ليس لديك صلاحية كمندوب")
#     user_id = payload.get("sub")
#     rider = db.query(Rider).filter(Rider.id == int(user_id)).first()
#     if not rider:
#         logger.warning(f"Rider with ID {user_id} not found in DB after token validation.")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المندوب غير موجود")
#     return rider
