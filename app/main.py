from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads
from app.routes import riders

app = FastAPI()

# ✅ إعداد CORS الرسمي لنطاقات الواجهة الأمامية
# تم تحديث allow_origins لتشمل روابط التطوير المحلية و رابط الواجهة الأمامية المنشورة.
# هذا يحل مشكلة CORS عند الاتصال من البيئة المحلية.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://grocery-delivery-frontend.onrender.com",  # رابط الواجهة الأمامية المنشورة على Render
        "http://127.0.0.1:5500",  # رابط التطوير المحلي (غالباً Live Server)
        "http://localhost:5500",   # رابط localhost للتطوير المحلي أيضاً
        "http://127.0.0.1:8000",   # منفذ محلي آخر قد يستخدم للتطوير
        "http://localhost:8000"    # منفذ localhost آخر قد يستخدم للتطوير
    ],
    allow_credentials=True,
    allow_methods=["*"],  # السماح بجميع طرق HTTP (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # السماح بجميع الترويسات في الطلبات
)

# ✅ إنشاء الجداول من النماذج
# تأكد أن هذا السطر يتم تنفيذه لإنشاء الجداول في قاعدة البيانات عند بدء التطبيق
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل جميع الراوترات (نقاط النهاية API)
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)
app.include_router(ads.router)
app.include_router(riders.router)

# ✅ مسار فحص الجاهزية (Health Check)
# هذا المسار مفيد للتحقق من أن الـ API يعمل بشكل صحيح
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}

# تم إزالة أو التعليق على middleware اليدوي "custom_cors_fallback"
# لأن CORSMiddleware من FastAPI يتعامل مع طلبات CORS (بما في ذلك OPTIONS preflight) بشكل صحيح.
# وجودهما معًا يمكن أن يسبب تضاربًا أو مشكلات في بعض الحالات.
