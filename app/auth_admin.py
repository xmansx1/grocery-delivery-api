from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.database import get_db
from sqlalchemy.orm import Session
from app import models
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: int = payload.get("sub")
        if admin_id is None:
            raise HTTPException(status_code=401, detail="رمز التوثيق غير صالح")
    except JWTError:
        raise HTTPException(status_code=401, detail="فشل التحقق من التوكن")

    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=401, detail="المشرف غير موجود")

    return admin
