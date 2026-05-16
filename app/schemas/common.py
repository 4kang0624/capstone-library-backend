from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
	"""공통 성공 응답 스키마"""

	success: bool = True
	code: str = "OK"
	message: str = "요청이 성공적으로 처리되었습니다."
	data: T | None = None
