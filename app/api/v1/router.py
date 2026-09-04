from fastapi import APIRouter

from app.api.v1.routes import meta
from app.core.config import get_settings

router = APIRouter(prefix=get_settings().api_v1_prefix)

router.include_router(meta.router)
