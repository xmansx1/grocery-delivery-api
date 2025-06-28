from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads, riders
from app.routes import public_stores

app = FastAPI()

# ✅ إعداد CORS بشكل صحيح
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://grocery-delivery-frontend.onrender.com",  # رابط موقعك المنشور
        "http://127.0.0.1:5500",  # للتطوير المحلي
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول
models.Base.metadata.create_all(bind=engine)

# ✅ تضمين جميع الراوترات
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)
app.include_router(ads.router)
app.include_router(riders.router)
app.include_router(public_stores.router)

# ✅ نقطة الفحص
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}
