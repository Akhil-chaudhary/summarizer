from fastapi import FastAPI

from app.routers.documents_router import router as documents_router


def create_app() -> FastAPI:
    """Author: Akhil Chaudhary

    Create and configure the FastAPI application instance.
    """
    app = FastAPI(title="Summarizer API", version="0.1.0")
    app.include_router(documents_router)
    return app


app = create_app()
