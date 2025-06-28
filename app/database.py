from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# ✅ تحميل متغيرات البيئة من ملف .env
load_dotenv()

# ✅ قراءة رابط قاعدة البيانات من البيئة
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ التأكد من وجود الرابط
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL غير موجود. تأكد من إضافته في ملف .env أو في Render.")

# ✅ إنشاء محرك قاعدة البيانات
engine = create_engine(DATABASE_URL)

# ✅ إعداد جلسة الاتصال
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ القاعدة الأساسية لإنشاء الجداول
Base = declarative_base()

# ✅ دالة توفر الجلسة لاستخدامها في Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
