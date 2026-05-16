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


# ── Book ─────────────────────────────────────────────────────────────────────

class BookNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOK_NOT_FOUND",
			message="책을 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


# ── BookCopy ──────────────────────────────────────────────────────────────────

class BookCopyNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOK_COPY_NOT_FOUND",
			message="책 복본을 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


class BookCopyForbiddenException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOK_COPY_FORBIDDEN",
			message="본인 소유의 책 복본이 아닙니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)


class BookCopyDeleteConflictException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOK_COPY_DELETE_CONFLICT",
			message="대여 중이거나 대여 요청된 책은 삭제할 수 없습니다.",
			status_code=status.HTTP_409_CONFLICT,
		)


# ── ReadingLog ────────────────────────────────────────────────────────────────

class ReadingLogNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="READING_LOG_NOT_FOUND",
			message="독서 기록을 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


class ReadingLogForbiddenException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="READING_LOG_FORBIDDEN",
			message="본인의 독서 기록이 아닙니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)


# ── Wishlist ──────────────────────────────────────────────────────────────────

class WishlistNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="WISHLIST_NOT_FOUND",
			message="위시리스트 항목을 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


class WishlistForbiddenException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="WISHLIST_FORBIDDEN",
			message="본인의 위시리스트 항목이 아닙니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)


class WishlistDuplicateException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="WISHLIST_DUPLICATE",
			message="이미 위시리스트에 추가된 책입니다.",
			status_code=status.HTTP_409_CONFLICT,
		)


# ── Bookmark ──────────────────────────────────────────────────────────────────

class BookmarkNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOKMARK_NOT_FOUND",
			message="책갈피를 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


class BookmarkForbiddenException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOKMARK_FORBIDDEN",
			message="본인의 책갈피가 아닙니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)


# ── Rental ────────────────────────────────────────────────────────────────────

class RentalNotFoundException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="RENTAL_NOT_FOUND",
			message="대여 정보를 찾을 수 없습니다.",
			status_code=status.HTTP_404_NOT_FOUND,
		)


class RentalForbiddenException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="RENTAL_FORBIDDEN",
			message="해당 대여에 접근 권한이 없습니다.",
			status_code=status.HTTP_403_FORBIDDEN,
		)


class RentalStatusConflictException(AppException):
	def __init__(self, message: str = "현재 대여 상태에서는 해당 작업을 수행할 수 없습니다.") -> None:
		super().__init__(
			code="RENTAL_STATUS_CONFLICT",
			message=message,
			status_code=status.HTTP_409_CONFLICT,
		)


class BookCopyNotAvailableException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="BOOK_COPY_NOT_AVAILABLE",
			message="해당 책 복본은 현재 대여할 수 없습니다.",
			status_code=status.HTTP_409_CONFLICT,
		)


class WalletNotConnectedException(AppException):
	def __init__(self) -> None:
		super().__init__(
			code="WALLET_NOT_CONNECTED",
			message="지갑이 연결되어 있지 않습니다.",
			status_code=status.HTTP_400_BAD_REQUEST,
		)
