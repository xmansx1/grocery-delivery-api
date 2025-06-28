from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import auth, stores, admins, store_auth
from app.routes import store_orders, dashboard, ads

app = FastAPI()

# ✅ إعداد CORS لحل مشكلة Blocked by CORS policy
origins = [
    "https://grocery-delivery-frontend.onrender.com",  # واجهة الموقع على Render
    "http://localhost:8000",                           # للتطوير المحلي
    "http://127.0.0.1:5500",                           # لتصفح ملفات HTML مباشرة
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # يجب أن تكون قائمة دومينات صريحة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول تلقائيًا إذا لم تكن موجودة
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

from fastapi import Request, Response

@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
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
