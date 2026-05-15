from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException


def _format_validation_errors(exc: RequestValidationError) -> list[dict]:
	formatted: list[dict] = []
	for err in exc.errors():
		formatted.append(
			{
				"field": ".".join(str(part) for part in err.get("loc", [])),
				"message": err.get("msg", "Invalid value"),
				"type": err.get("type", "validation_error"),
				"input": err.get("input"),
			}
		)
	return formatted


def add_exception_handlers(app: FastAPI) -> None:
	"""애플리케이션 전역 예외 핸들러 등록"""

	@app.exception_handler(AppException)
	async def app_exception_handler(
		request: Request,
		exc: AppException,
	) -> JSONResponse:
		return JSONResponse(
			status_code=exc.status_code,
			content={
				"code": exc.code,
				"message": exc.message,
			},
		)

	@app.exception_handler(RequestValidationError)
	async def request_validation_exception_handler(
		request: Request,
		exc: RequestValidationError,
	) -> JSONResponse:
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			content={
				"code": "VALIDATION_ERROR",
				"message": "요청 데이터 검증에 실패했습니다.",
				"errors": _format_validation_errors(exc),
				"path": request.url.path,
			},
		)

	@app.exception_handler(Exception)
	async def generic_exception_handler(
		request: Request,
		exc: Exception,
	) -> JSONResponse:
		return JSONResponse(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			content={
				"code": "INTERNAL_SERVER_ERROR",
				"message": "서버 오류가 발생했습니다.",
			},
		)
