from fastapi import APIRouter

from application.services.health_service import HealthService

router = APIRouter(tags=["health"])
service = HealthService()


@router.get("/health")
def health_check() -> dict[str, str]:
    return service.ping()
