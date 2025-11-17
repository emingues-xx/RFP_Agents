"""Endpoint de métricas para Prometheus."""
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()


@router.get("/metrics")
async def metrics():
    """Endpoint de métricas Prometheus."""
    return Response(
        content=generate_latest(registry=None),
        media_type=CONTENT_TYPE_LATEST
    )

