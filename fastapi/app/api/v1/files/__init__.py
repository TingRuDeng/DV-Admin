from app.api.v1.files import upload
from fastapi import APIRouter

router = APIRouter(prefix="/files")
router.include_router(upload.router, tags=["文件管理"])
