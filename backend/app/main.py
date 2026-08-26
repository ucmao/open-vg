from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .models.base import engine, init_db
from .utils.logger import logger, log_request, log_error
from .utils.responses import error_response

load_dotenv()

# Import routes
from .routes import auth, user, upload, generation, webhook, works, payment, admin, comments, blog, admin_auth, media, follows, topic, seo, admin_seo, admin_works, admin_users, admin_comments, admin_finance, admin_recharge_discount, admin_system, admin_sockpuppets, recharge, notifications, admin_category_pages, admin_effects_pages, admin_moderation, admin_workflows, checkin, invitation, admin_promotions, promotions, admin_carousel, carousel, admin_generate_pages, overseas_parser
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting VidGen API...")
    try:
        auto_create = os.getenv("AUTO_CREATE_TABLES", "false").strip().lower() in {
            "1", "true", "yes", "on"
        }
        environment = os.getenv("ENVIRONMENT", "development").strip().lower()
        if auto_create:
            if environment == "production":
                raise RuntimeError("AUTO_CREATE_TABLES is forbidden in production")
            init_db()
            logger.warning("AUTO_CREATE_TABLES enabled for local development")
        else:
            from .utils.migrations import verify_database_at_head
            verify_database_at_head(engine)
            logger.info("Database migration state verified")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Run Security Warning Checks
    try:
        from .utils.security_checker import check_security_warnings
        check_security_warnings()
    except Exception as sec_err:
        logger.warning(f"Security check failed: {sec_err}")

    from .services.realtime import realtime_subscriber
    await realtime_subscriber.start()

    yield
    
    # Shutdown
    await realtime_subscriber.stop()
    logger.info("Shutting down VidGen API...")


# Create FastAPI application
app = FastAPI(
    title="VidGen API",
    description="Create Beyond Limits — Remix Reality, Join the Movement. API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Ensure static directories exist
os.makedirs("static/generated", exist_ok=True)
os.makedirs("static/thumbnails", exist_ok=True)
os.makedirs("static/user-upload", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_FRONTEND_URL = os.getenv("ADMIN_FRONTEND_URL", "http://localhost:3001")
BACKEND_URL = os.getenv("BACKEND_URL", "")  # API (, API )

#  CORS
cors_origins = [
    FRONTEND_URL,
    "http://localhost:3000",  # Web frontend
    ADMIN_FRONTEND_URL,
    "http://localhost:3001",  # Admin frontend
]

# API , ( API )
if BACKEND_URL:
    cors_origins.append(BACKEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to log request timing and add process time header.
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        # Log request
        log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=process_time
        )
        
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        log_error(e, f"{request.method} {request.url.path}")
        raise


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with standardized response.
    """
    errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # Skip 'body'
        errors[field] = error["msg"]
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return error_response(
        message="Validation error",
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors.
    """
    log_error(exc, "Database error")
    
    return error_response(
        message="Database error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions.
    """
    log_error(exc, f"{request.method} {request.url.path}")
    
    return error_response(
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "success": True,
        "message": "AIGC Creative Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "success": True,
        "status": "healthy",
        "timestamp": time.time()
    }


# Register routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(generation.router, prefix="/api/generate", tags=["Generation"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhook"])
app.include_router(works.router, prefix="/api/works", tags=["Works"])
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
app.include_router(overseas_parser.router, prefix="/api/overseas", tags=["Overseas Parser"])

app.include_router(admin_auth.router, prefix="/api/admin/auth", tags=["Admin Auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_seo.router, prefix="/api/admin", tags=["Admin SEO"])
app.include_router(admin_category_pages.router, prefix="/api/admin", tags=["Admin Category Pages"])
app.include_router(admin_effects_pages.router, prefix="/api/admin", tags=["Admin Effects Pages"])
app.include_router(admin_generate_pages.router, prefix="/api/admin", tags=["Admin Generate Pages"])
app.include_router(admin_works.router, prefix="/api/admin", tags=["Admin Works Management"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["Admin Users Management"])
app.include_router(admin_comments.router, prefix="/api/admin", tags=["Admin Comments Management"])
app.include_router(admin_finance.router, prefix="/api/admin", tags=["Admin Finance Management"])
app.include_router(admin_recharge_discount.router, prefix="/api/admin", tags=["Admin Recharge Discount"])
app.include_router(admin_system.router, prefix="/api/admin", tags=["Admin System Management"])
app.include_router(admin_sockpuppets.router, prefix="/api/admin", tags=["Admin Sockpuppets"])
app.include_router(admin_moderation.router, prefix="/api/admin", tags=["Admin Moderation"])
app.include_router(admin_workflows.router, prefix="/api/admin", tags=["Admin Workflows"])
app.include_router(media.router, prefix="/api/admin/media", tags=["Admin Media"])
app.include_router(comments.router, prefix="/api", tags=["Comments"])
app.include_router(blog.router, prefix="/api/blog", tags=["Blog"])
app.include_router(topic.router, prefix="/api/topic", tags=["Topic"])
app.include_router(topic.router, prefix="/api/admin/topics", tags=["Admin Topics"])
app.include_router(follows.router, prefix="/api/follows", tags=["Follows"])
app.include_router(seo.router, tags=["SEO"])
app.include_router(recharge.router, prefix="/api/recharge", tags=["Recharge"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(checkin.router, prefix="/api", tags=["CheckIn"])
app.include_router(invitation.router, prefix="/api", tags=["Invitation"])
app.include_router(admin_promotions.router, prefix="/api/admin", tags=["Admin Promotions"])
app.include_router(promotions.router, prefix="/api", tags=["Promotions"])
app.include_router(admin_carousel.router, prefix="/api/admin", tags=["Admin Carousel"])
app.include_router(carousel.router, prefix="/api", tags=["Carousel"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
