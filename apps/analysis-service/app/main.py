from fastapi import FastAPI
import structlog

from app.core.config import settings
from app.api.routes import analyze

logger = structlog.get_logger()

def create_app() -> FastAPI:
    app = FastAPI(title="ReviewSense AI - Analysis Service")

    app.include_router(analyze.router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "analysis-service"}

    @app.on_event("startup")
    async def startup_event():
        logger.info("analysis_service_started", config_loaded=True)

    return app

app = create_app()
