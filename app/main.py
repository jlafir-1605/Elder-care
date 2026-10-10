from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.api.auth import router as auth_router
from app.api.booking import router as booking_router
from app.api.charges import router as charges_router
from app.api.dashboard import router as dashboard_router
from app.api.reviews import router as reviews_router
from app.api.verification import router as verification_router
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(dashboard_router, prefix=settings.api_prefix)
    app.include_router(booking_router, prefix=settings.api_prefix)
    app.include_router(charges_router, prefix=settings.api_prefix)
    app.include_router(reviews_router, prefix=settings.api_prefix)
    app.include_router(verification_router, prefix=settings.api_prefix)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
