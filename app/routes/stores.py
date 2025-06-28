from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext # ✅ استيراد CryptContext

from app import models, schemas
from app.database import get_db
from app.utils.jwt import get_current_admin # تأكد من أن هذا المسار صحيح

router = APIRouter(prefix="/stores", tags=["Stores"])

# ✅ إعداد تشفير كلمة المرور (نفس الإعداد في auth.py)
# تأكد أن هذا المتغير هو نفسه المستخدم في auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ✅ إنشاء محل جديد
@router.post("/", response_model=schemas.StoreResponse)
def create_store(
    data: schemas.StoreCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # ✅ الخطوة المفقودة: تجزئة كلمة المرور
    hashed_password = pwd_context.hash(data.password)

    # ✅ التأكد من عدم تكرار رقم الجوال
    existing_store = db.query(models.Store).filter(models.Store.phone == data.phone).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="رقم الجوال مستخدم بالفعل لمحل آخر")
    
    # ✅ إنشاء كائن Store باستخدام كلمة المرور المجزأة
    # استخدام .copy(update=...) لتجنب تمرير كلمة المرور النصية مباشرة
    new_store = models.Store(
        name=data.name,
        phone=data.phone,
        password=hashed_password, # ✅ استخدام كلمة المرور المجزأة
        is_active=data.is_active # تمرير is_active إذا كانت جزءًا من النموذج
    )

    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store

# ✅ جلب جميع المحلات
@router.get("/", response_model=List[schemas.StoreResponse])
def get_stores(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(models.Store).all()

# ✅ تحديث بيانات محل
@router.put("/{store_id}", response_model=schemas.StoreResponse)
def update_store(
    store_id: int,
    data: schemas.StoreCreate, # قد تحتاج لنموذج StoreUpdate إذا كنت لا تريد تحديث كل الحقول
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")

    # ✅ ملاحظة هامة: إذا كنت تسمح بتحديث كلمة المرور هنا، يجب تجزئتها أيضًا
    update_data = data.dict(exclude_unset=True) # لجلب الحقول التي تم تعيينها فقط
    if "password" in update_data and update_data["password"]:
        update_data["password"] = pwd_context.hash(update_data["password"])

    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store

# ✅ تغيير حالة المحل (تفعيل / إيقاف مؤقت)
@router.put("/{store_id}/status", response_model=schemas.StoreResponse)
def toggle_store_status(
    store_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")

    store.is_active = is_active
    db.commit()
    db.refresh(store)
    return store

# ✅ حذف محل نهائيًا
@router.delete("/{store_id}")
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    store = db.query(models.Store).filter(models.Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="المحل غير موجود")

    db.delete(store)
    db.commit()
    return {"detail": "✅ تم حذف المحل بنجاح"}