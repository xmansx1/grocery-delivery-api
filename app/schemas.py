from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from datetime import datetime

# =========================
# ✅ توثيق التوكن (JWT)
# =========================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: Optional[str] = None
    store_name: Optional[str] = None


# =========================
# ✅ المشرف (Admin)
# =========================
class AdminCreate(BaseModel):
    phone: str
    password: str

class AdminLogin(BaseModel):
    phone: str
    password: str

class AdminResponse(BaseModel):
    id: int
    phone: str

    class Config:
        from_attributes = True


# =========================
# ✅ المحل (Store)
# =========================
class StoreBase(BaseModel):
    name: str
    phone: str
    password: str
    is_active: bool = True  # ✅ لتفادي خطأ "is_active"

class StoreCreate(StoreBase):
    pass

class StoreLogin(BaseModel):
    phone: str
    password: str

class StoreResponse(BaseModel):
    id: int
    name: str
    phone: str
    is_active: bool

    class Config:
        from_attributes = True


# =========================
# ✅ المندوب (Rider)
# =========================
class RiderBase(BaseModel):
    name: str
    phone: str
    status: Optional[Literal["متاح ✅", "مشغول ⏳", "موقوف ⛔️"]] = "متاح ✅"

class RiderCreate(RiderBase):
    password: str 

class RiderResponse(RiderBase):
    id: int

    class Config:
        from_attributes = True


# =========================
# ✅ الطلب (Order)
# =========================
class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    order_text: str
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    amount: Optional[float] = None
    status: Optional[Literal["جديد", "قيد التجهيز", "جاهز للاستلام", "في الطريق", "مكتمل", "ملغى"]] = "جديد"
    store_id: int
    rider_id: Optional[int] = None

class OrderCreate(OrderBase):
    pass

# في ملف schemas.py
from typing import Optional
from pydantic import BaseModel

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    order_text: str
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    store_id: int
    status: Optional[str] = "جديد"  # ✅ أضف هذا السطر لتفادي الخطأ




class OrderUpdate(BaseModel):
    status: Optional[Literal["جديد", "قيد التجهيز", "خرج للتوصيل", "تم التوصيل", "تم الإلغاء"]] = "جديد"
    rider_id: Optional[int] = None
    amount: Optional[float] = None

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    order_text: str
    notes: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    status: str
    amount: Optional[float]
    rider_name: Optional[str] = None  # ✅ من العلاقة
    created_at:  datetime
    class Config:
        orm_mode = True


    class Config:
        orm_mode = True


# =========================
# ✅ الإعلان (Ad)
# =========================
class AdCreate(BaseModel):
    title: str
    content: str
    is_active: bool = True

class AdResponse(BaseModel):
    id: int
    title: str
    content: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
class AssignOrderRequest(BaseModel):
    rider_id: int
    amount: float
