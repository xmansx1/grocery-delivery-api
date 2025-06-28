from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads

app = FastAPI()

# ✅ إعداد CORS بشكل رسمي لتطبيق السياسات الصحيحة
origins = [
    "https://grocery-delivery-frontend.onrender.com",  # واجهة المستخدم على Render
    "http://localhost:8000",                           # التطوير المحلي
    "http://127.0.0.1:5500",                           # ملفات HTML محليًا
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # يجب أن تكون محددة (ليست "*")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول تلقائيًا
models.Base.metadata.create_all(bind=engine)

# ✅ تسجيل جميع الراوترات
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(admins.router)
app.include_router(store_auth.router)
app.include_router(store_orders.router)
app.include_router(dashboard.router)
app.include_router(ads.router)

# ✅ مسار فحص جاهزية الـ API
@app.get("/")
def root():
    return {"message": "🚀 API جاهز للعمل!"}

# ✅ Middleware إضافي يدوي لحل مشاكل preflight (في حال Render تجاهل CORS الرسمي)
@app.middleware("http")
async def custom_cors_fallback(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": "https://grocery-delivery-frontend.onrender.com",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        })

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://grocery-delivery-frontend.onrender.com"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
