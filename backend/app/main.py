import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import PaperFlowException
from app.services.storage import storage_service
from app.api.routes import health, jobs, tools

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("paperflow")

async def periodic_cleanup_task():
    """Background task to periodically delete expired temporary job files."""
    while True:
        try:
            await asyncio.sleep(settings.CLEANUP_INTERVAL_MINUTES * 60)
            cleaned = storage_service.cleanup_expired_jobs()
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired job workspace(s).")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during periodic cleanup: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start periodic cleanup
    cleanup_task = asyncio.create_task(periodic_cleanup_task())
    logger.info(f"{settings.BRAND_NAME} API started successfully on {settings.API_HOST}:{settings.API_PORT}")
    yield
    # Shutdown
    cleanup_task.cancel()
    logger.info(f"{settings.BRAND_NAME} API shutdown.")

app = FastAPI(
    title=f"{settings.BRAND_NAME} PDF Tools API",
    description="Production-ready PDF processing, conversion, compression, and document intelligence service.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Safe Exception Handlers
@app.exception_handler(PaperFlowException)
async def paperflow_exception_handler(request: Request, exc: PaperFlowException):
    logger.warning(f"PaperFlowException: {exc.message} (Path: {request.url.path})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "status": "error"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log full diagnostic details server-side without leaking stack traces publicly
    logger.exception(f"Unhandled exception at {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing your request.", "status": "error"}
    )

# Include API Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(tools.router, prefix="/api", tags=["Tools"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
