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
        from_attributes = True


# =========================
# ✅ المحل (Store)
# =========================

class StoreBase(BaseModel):
    name: str
    phone: str
    password: str
    is_active: bool = True

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
    status: Optional[Literal["متاح", "مشغول", "موقوف"]] = "متاح"

class RiderCreate(RiderBase):
    password: str

class RiderResponse(BaseModel):
    id: int
    name: str
    phone: str
    status: Literal["متاح", "مشغول", "موقوف"]

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
    status: Optional[str] = "جديد"
    store_id: int
    rider_id: Optional[int] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = "جديد"
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
    created_at: datetime
    store_name: Optional[str]
    rider_name: Optional[str]

    class Config:
        from_attributes = True


# =========================
# ✅ الإسناد إلى مندوب
# =========================

class AssignOrderRequest(BaseModel):
    rider_id: int
    amount: float


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
