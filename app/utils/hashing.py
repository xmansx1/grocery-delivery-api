# app/utils/hashing.py

from passlib.context import CryptContext

# إعداد سياق التشفير باستخدام Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ دالة لتشفير كلمة المرور
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ✅ دالة للتحقق من كلمة المرور
def verify(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
