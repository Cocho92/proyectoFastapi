from fastapi import APIRouter

from app.api.routes import items, login, private, tasks, users, utils,errores_pami,internaciones_op, pami_verification
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(tasks.router)
api_router.include_router(errores_pami.router)
api_router.include_router(internaciones_op.router)
api_router.include_router(pami_verification.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
