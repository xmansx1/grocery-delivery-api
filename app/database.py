from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# ✅ تحميل متغيرات البيئة من ملف .env
load_dotenv()

# ✅ قراءة الإعدادات من المتغيرات البيئية
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# ✅ إعداد رابط الاتصال بقاعدة البيانات
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
