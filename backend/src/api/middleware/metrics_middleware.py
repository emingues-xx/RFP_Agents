"""Middleware para coletar métricas HTTP."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.metrics import (
    http_requests_total,
    http_request_duration_seconds
)
import time
import logging

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para métricas HTTP."""
    
    async def dispatch(self, request: Request, call_next):
        """Processar requisição e coletar métricas."""
        # Ignorar endpoint de métricas para evitar loop
        if request.url.path == "/metrics":
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            # Processar requisição
            response = await call_next(request)
        except Exception as e:
            # Em caso de erro, ainda coletar métricas
            duration = time.time() - start_time
            status = 500
            
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            raise
        
        # Calcular duração
        duration = time.time() - start_time
        
        # Coletar métricas
        method = request.method
        endpoint = request.url.path
        status = response.status_code
        
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        return response

