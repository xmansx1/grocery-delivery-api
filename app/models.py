from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# ✅ المشرف (Admin)
class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# ✅ المحل (Store)
class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False)  # رقم الجوال
    password = Column(String, nullable=False)            # كلمة المرور
    name = Column(String, nullable=False)                # اسم المحل
    is_active = Column(Boolean, default=True)

    # علاقة مع الطلبات
    orders = relationship("Order", back_populates="store")

# ✅ المندوب (Rider)
class Rider(Base):
    __tablename__ = "riders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    status = Column(String, default="متاح ✅")  # "مشغول ⏳" أو "موقوف ⛔️"

    # علاقة مع الطلبات
    orders = relationship("Order", back_populates="rider")

# ✅ الطلب (Order)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    order_text = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    lat = Column(Numeric, nullable=True)
    lng = Column(Numeric, nullable=True)
    amount = Column(Numeric, nullable=True)  # إجمالي مبلغ الطلب
    status = Column(String, default="جديد")  # جديد / قيد التجهيز / خرج للتوصيل / تم التوصيل / تم الإلغاء
    created_at = Column(DateTime, default=datetime.utcnow)

    # مفاتيح العلاقات
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    rider_id = Column(Integer, ForeignKey("riders.id"), nullable=True)

    # علاقات ORM
    store = relationship("Store", back_populates="orders")
    rider = relationship("Rider", back_populates="orders")

# ✅ الإعلانات (Ad)
class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
