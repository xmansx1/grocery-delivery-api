from pydantic import BaseModel
from typing import Optional, List, Literal
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
        # ✅ تم التحديث: orm_mode تم استبداله بـ from_attributes
        from_attributes = True


# =========================
# ✅ المحل (Store)
# =========================

class StoreBase(BaseModel):
    name: str
    phone: str
    password: str
    is_active: Optional[bool] = True

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
        # ✅ تم التحديث: orm_mode تم استبداله بـ from_attributes
        from_attributes = True


# =========================
# ✅ المندوب (Rider)
# =========================

class RiderBase(BaseModel):
    name: str
    phone: str
    # ✅ تحسين: استخدام Literal لتحديد القيم المسموح بها للحالة
    status: Optional[Literal["متاح ✅", "مشغول 🔴", "غير متاح ⚪"]] = "متاح ✅"

class RiderCreate(RiderBase):
    pass

class RiderResponse(RiderBase):
    id: int

    class Config:
        # ✅ تم التحديث: orm_mode تم استبداله بـ from_attributes
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
    # ✅ تحسين: استخدام Literal لتحديد القيم المسموح بها للحالة
    status: Optional[Literal["جديد", "قيد التجهيز", "جاهز للاستلام", "في الطريق", "مكتمل", "ملغى"]] = "جديد"
    store_id: int
    rider_id: Optional[int] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    # ✅ تحسين: استخدام Literal لتحديد القيم المسموح بها للحالة
    status: Optional[Literal["جديد", "قيد التجهيز", "جاهز للاستلام", "في الطريق", "مكتمل", "ملغى"]] = None
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
    amount: Optional[float]
    status: str
    rider_id: Optional[int]
    created_at: datetime
    # ملاحظة: تأكد أن RiderResponse و StoreResponse تحتويان على from_attributes = True
    # وإلا فإن تضمينهما هنا سيسبب مشاكل إذا كانت تستقبل بيانات ORM
    rider: Optional[RiderResponse]
    store: Optional[StoreResponse]

    class Config:
        # ✅ تم التحديث: orm_mode تم استبداله بـ from_attributes
        from_attributes = True


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
        # ✅ تم التحديث: orm_mode تم استبداله بـ from_attributes
        from_attributes = True