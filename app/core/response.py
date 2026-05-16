from typing import Any


def success_response(
	data: Any = None,
	message: str = "요청이 성공적으로 처리되었습니다.",
	code: str = "OK",
) -> dict:
	"""공통 성공 응답 포맷"""
	return {
		"success": True,
		"code": code,
		"message": message,
		"data": data,
	}
