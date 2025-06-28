from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ✅ مشرف (Admin)
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
        orm_mode = True

# ✅ التوكن (JWT)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ✅ المحل (Store)
class StoreBase(BaseModel):
    name: str
    phone: str
    password: str
    is_active: Optional[bool] = True

class StoreCreate(StoreBase):
    pass

class StoreResponse(StoreBase):
    id: int

    class Config:
        orm_mode = True

# ✅ المندوب (Rider)
class RiderBase(BaseModel):
    name: str
    phone: str
    status: Optional[str] = "متاح ✅"

class RiderCreate(RiderBase):
    pass

class RiderResponse(RiderBase):
    id: int

    class Config:
        orm_mode = True

# ✅ الطلب (Order)
# ✅ الطلب (Order)
class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    order_text: str
    notes: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    amount: Optional[float] = None  # تعديل الاسم هنا
    status: Optional[str] = "جديد"
    store_id: int
    rider_id: Optional[int] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    rider_id: Optional[int] = None
    amount: Optional[float] = None  # تعديل الاسم هنا أيضاً

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
    rider: Optional[RiderResponse]  # هذا بدل assigned_rider

    class Config:
        orm_mode = True


class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    rider_id: Optional[int] = None
    total_amount: Optional[float] = None

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    store: Optional[StoreResponse]
    assigned_rider: Optional[RiderResponse]

    class Config:
        orm_mode = True

class StoreLogin(BaseModel):
    username: str
    password: str
    
class StoreResponse(BaseModel):
    id: int
    name: str
    phone: str
    is_active: bool

    class Config:
        orm_mode = True