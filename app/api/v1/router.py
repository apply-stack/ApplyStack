from fastapi import APIRouter

from app.api.v1.routes import accounts, meta
from app.core.config import get_settings

router = APIRouter(prefix=get_settings().api_v1_prefix)

router.include_router(meta.router)
router.include_router(accounts.router)
