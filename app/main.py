from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models

from app.routes import (
    auth, stores, admins, store_auth, store_orders,
    dashboard, ads, riders, public_stores, public_store_login,
    public_order, rider_orders, store_assign, admin_orders
)

# ✅ إنشاء التطبيق
app = FastAPI()

# ✅ إعداد CORS — تأكد أن هذا القسم قبل أي include_router
origins = [
    "https://grocery-delivery-frontend.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول من النماذج
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل الراوترات بعد CORS
app.include_router(auth.router)
app.include_router(stores.store_router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)
app.include_router(ads.router)
app.include_router(riders.router)
app.include_router(public_stores.router)
app.include_router(public_store_login.router)
app.include_router(public_order.router)
app.include_router(rider_orders.router)
app.include_router(store_assign.router)
app.include_router(admin_orders.router)

# ✅ نقطة تحقق بسيطة
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}
