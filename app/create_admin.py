from .database import SessionLocal
from .models import Admin
from passlib.context import CryptContext

# ✅ إعداد تشفير كلمة المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ بيانات المشرف
phone = "0560000000"
plain_password = "admin123"

# ✅ تشفير كلمة المرور
hashed_password = pwd_context.hash(plain_password)

# ✅ إنشاء الجلسة
db = SessionLocal()

# ✅ إنشاء المشرف
admin = Admin(phone=phone, password=hashed_password)
db.add(admin)
db.commit()
db.refresh(admin)
db.close()

print("✅ تم إنشاء المشرف بنجاح:")
print(f"📱 رقم الجوال: {phone}")
print(f"🔑 كلمة المرور: {plain_password}")
