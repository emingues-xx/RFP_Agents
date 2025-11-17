"""Aplicação FastAPI principal."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.metrics_endpoint import router as metrics_router
from src.api.middleware.metrics_middleware import MetricsMiddleware
from src.utils.metrics import start_metrics_server
import os
import logging

logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="RFP Agents API",
    description="API para sistema de agentes de preenchimento de RFPs",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de métricas
app.add_middleware(MetricsMiddleware)

# Rotas
app.include_router(metrics_router)

# Rotas de aprovação
from src.api.routes.approvals import router as approvals_router
app.include_router(approvals_router)

# Rotas de workflow
from src.api.routes.workflow import router as workflow_router
app.include_router(workflow_router)

# Rotas de RFPs
from src.api.routes.rfps import router as rfps_router
app.include_router(rfps_router)

# Rotas de Queue
from src.api.routes.queue import router as queue_router
app.include_router(queue_router)

# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RFP Agents API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Iniciar servidor de métricas
@app.on_event("startup")
async def startup_event():
    """Evento de startup da aplicação."""
    metrics_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
    try:
        start_metrics_server(metrics_port)
        logger.info(f"Servidor de métricas iniciado na porta {metrics_port}")
    except Exception as e:
        logger.warning(f"Não foi possível iniciar servidor de métricas na porta {metrics_port}: {e}")
        logger.info("Métricas ainda estarão disponíveis via endpoint /metrics")
