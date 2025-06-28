from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads

app = FastAPI()

# ✅ إعداد CORS الرسمي لنطاق الواجهة فقط
# تأكد تمامًا من أن هذا هو الرابط الدقيق للواجهة الأمامية
FRONTEND_ORIGIN = "https://grocery-delivery-frontend.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # ✅ لا تستخدم ["*"] مع allow_credentials=True
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

# ✅ مسار فحص الجاهزية (Health Check)
# هذا المسار مفيد للتحقق من أن الـ API يعمل بشكل صحيح
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}

# تم إزالة أو التعليق على middleware اليدوي "custom_cors_fallback"
# لأن CORSMiddleware من FastAPI يتعامل مع طلبات CORS (بما في ذلك OPTIONS preflight) بشكل صحيح.
# وجودهما معًا يمكن أن يسبب تضاربًا أو مشكلات في بعض الحالات.