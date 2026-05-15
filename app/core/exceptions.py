from fastapi import status


class AppException(Exception):
	"""베이스 애플리케이션 예외"""

	def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
		self.code = code
		self.message = message
		self.status_code = status_code
		super().__init__(message)


# ── Auth ─────────────────────────────────────────────────────────────────────

class DuplicateEmailException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_SIGNUP_DUPLICATE_EMAIL",
			message="이미 사용 중인 이메일입니다.",
			status_code=status.HTTP_409_CONFLICT,
		)


class LoginUserNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_LOGIN_USER_NOT_FOUND",
			message="이메일 또는 비밀번호가 올바르지 않습니다.",
			status_code=status.HTTP_401_UNAUTHORIZED,
		)


class LoginInvalidPasswordException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_LOGIN_INVALID_PASSWORD",
			message="이메일 또는 비밀번호가 올바르지 않습니다.",
			status_code=status.HTTP_401_UNAUTHORIZED,
		)


class TokenInvalidException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_TOKEN_INVALID",
			message="유효하지 않은 토큰입니다.",
			status_code=status.HTTP_401_UNAUTHORIZED,
		)


class TokenExpiredException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_TOKEN_EXPIRED",
			message="만료된 토큰입니다.",
			status_code=status.HTTP_401_UNAUTHORIZED,
		)


class TokenRevokedException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_TOKEN_REVOKED",
			message="폐기된 토큰입니다.",
			status_code=status.HTTP_401_UNAUTHORIZED,
		)


# ── User ─────────────────────────────────────────────────────────────────────

class UserNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="USER_NOT_FOUND",
			message="사용자를 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


class UserNotActiveException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="USER_NOT_ACTIVE",
			message="해당 사용자는 더 이상 활성 상태가 아닙니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)


class PasswordMismatchException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="USER_PASSWORD_MISMATCH",
			message="현재 비밀번호가 올바르지 않습니다.",
			status_code=status.HTTP_400_BAD_REQUEST,
		)


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminRequiredException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="AUTH_ADMIN_REQUIRED",
			message="관리자 권한이 필요합니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)
