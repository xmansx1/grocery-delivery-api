from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# ✅ نموذج المستخدم (للمشرفين)
class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# ✅ نموذج المحل
class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False)  # 📱 رقم الجوال لتسجيل الدخول
    password = Column(String, nullable=False)            # 🔐 كلمة المرور
    name = Column(String, nullable=False)                # 🏪 اسم المحل
    is_active = Column(Boolean, default=True)

    # علاقة عكسية مع الطلبات
    orders = relationship("Order", back_populates="store")


# ✅ نموذج المندوب
# ✅ نموذج المندوب
class Rider(Base):
    __tablename__ = "riders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    status = Column(String, default="متاح ✅")

    orders = relationship("Order", back_populates="rider")

# ✅ نموذج الطلب
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    order_text = Column(Text, nullable=False)
    notes = Column(Text)
    lat = Column(Numeric)
    lng = Column(Numeric)
    amount = Column(Numeric)  # ✅ بدل total_amount
    status = Column(String, default="جديد")
    created_at = Column(DateTime, default=datetime.utcnow)

    store_id = Column(Integer, ForeignKey("stores.id"))
    rider_id = Column(Integer, ForeignKey("riders.id"), nullable=True)

    store = relationship("Store", back_populates="orders")
    rider = relationship("Rider", back_populates="orders")

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)