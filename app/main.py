from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins
from .routes import store_auth
from app.routes import store_orders
from app.routes import dashboard

app = FastAPI()

# ✅ إعداد CORS للسماح بالوصول من الواجهة الأمامية على Render + التجربة المحلية
origins = [
    "https://grocery-delivery-frontend.onrender.com",  # موقع الواجهة الأمامية على Render
    "http://localhost:8000",                           # للتطوير المحلي
    "http://127.0.0.1:5500",                           # لتجربة صفحات HTML محليًا
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول تلقائيًا من النماذج
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل مسارات الراوترات
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)

# ✅ مسار اختبار بسيط
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}
