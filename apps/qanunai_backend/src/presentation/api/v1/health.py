from fastapi import APIRouter

from application.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])
service = HealthService()


@router.get("/")
def health_check() -> dict[str, str]:
    return service.ping()
