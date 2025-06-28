from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads

app = FastAPI()

# ✅ إعداد CORS لحل مشكلة: blocked by CORS policy
origins = [
    "https://grocery-delivery-frontend.onrender.com",  # واجهة الموقع على Render
    "http://localhost:8000",                           # للواجهة أثناء التطوير
    "http://127.0.0.1:5500",                           # لتصفح HTML من الجهاز مباشرة
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # لا تستخدم "*" مع allow_credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول عند بدء التشغيل
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل الراوترات
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)
app.include_router(ads.router)

# ✅ مسار اختبار جاهزية
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}
