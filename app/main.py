from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ إضافة دعم CORS
from .database import engine
from . import models
from .routes import auth, stores, admins
from .routes import store_auth
from app.routes import store_orders
from app.routes import dashboard

app = FastAPI()

# ✅ إعداد CORS للسماح بطلبات من الواجهة الأمامية
origins = [
    "https://grocery-delivery-frontend.onrender.com",  # رابط موقعك على Render
    "http://localhost:8000",  # لتجربة محلية
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # السماح فقط بالنطاقات المذكورة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول تلقائيًا من النماذج
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل الراوترات
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)

# ✅ مسار اختبار
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}
