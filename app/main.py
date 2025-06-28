from fastapi import FastAPI
from .database import engine
from . import models
from .routes import auth, stores, admins  # ✅ استيراد موحد
from .routes import store_auth
from app.routes import store_orders
from app.routes import dashboard

app = FastAPI()

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
