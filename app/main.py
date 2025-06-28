from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads

app = FastAPI()

# ✅ إعداد CORS الرسمي لنطاق الواجهة فقط
FRONTEND_ORIGIN = "https://grocery-delivery-frontend.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # ✅ لا تستخدم ["*"] مع allow_credentials=True
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول من النماذج
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل جميع الراوترات
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)
app.include_router(ads.router)

# ✅ مسار فحص الجاهزية
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}

# ✅ Middleware إضافي يدوي لتجاوز مشاكل preflight إذا Render تجاهل إعدادات CORS
@app.middleware("http")
async def custom_cors_fallback(request: Request, call_next):
    # التعامل مع OPTIONS مسبقًا
    if request.method == "OPTIONS":
        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": FRONTEND_ORIGIN,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        })

    # السماح بالهيدر في كل الردود الأخرى
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
