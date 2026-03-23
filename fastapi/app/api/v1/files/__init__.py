from fastapi import APIRouter

from app.api.v1.files import upload

router = APIRouter(prefix="/files")
router.include_router(upload.router, tags=["文件管理"])
