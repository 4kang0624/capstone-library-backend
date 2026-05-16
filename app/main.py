from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exception_handlers import add_exception_handlers


def create_app() -> FastAPI:
	app = FastAPI(title=settings.app_name)
	add_exception_handlers(app)
	app.include_router(api_router, prefix=settings.api_prefix)
	return app


app = create_app()
