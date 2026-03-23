from app.api.v1.information import profile
from fastapi import APIRouter

router = APIRouter(prefix="/information")
router.include_router(profile.router, tags=["个人中心"])
