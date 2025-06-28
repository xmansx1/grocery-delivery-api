from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/store-auth", tags=["Store Auth"])

# ✅ إعداد التشفير وسر التوكن
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 ساعة

# ✅ تسجيل الدخول للمحل
@router.post("/login", response_model=schemas.Token)
def login_store(data: schemas.AdminLogin, db: Session = Depends(get_db)):
    store = db.query(models.Store).filter(models.Store.name == data.phone).first()  # نفترض الاسم مكان الهاتف
    if not store:
        raise HTTPException(status_code=401, detail="المحل غير موجود")

    # كلمة المرور ليست موجودة في نموذج Store حاليًا
    raise HTTPException(status_code=403, detail="نموذج المحل لا يحتوي على كلمة مرور")

    # access_token = jwt.encode({"sub": str(store.id), "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
    # return {"access_token": access_token, "token_type": "bearer"}
