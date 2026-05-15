from fastapi import FastAPI

from app.api.router import api_router
from app.core.exception_handlers import add_exception_handlers


def create_app() -> FastAPI:
	app = FastAPI(title="Capstone Library Backend")
	add_exception_handlers(app)
	app.include_router(api_router, prefix="/api")
	return app


app = create_app()
