from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
	DuplicateEmailException,
	LoginInvalidPasswordException,
	LoginUserNotFoundException,
	PasswordMismatchException,
	TokenExpiredException,
	TokenInvalidException,
	TokenRevokedException,
	UserNotFoundException,
)
from app.core.security import (
	create_access_token,
	create_refresh_token,
	get_refresh_token_expiry,
	hash_password,
	hash_token,
	verify_password,
)
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:
	"""인증 서비스"""

	@staticmethod
	def signup(
		db: Session,
		email: str,
		password: str,
		nickname: str,
	) -> User:
		"""회원가입"""
		# 이메일 중복 확인
		existing_user = UserRepository.get_user_by_email(db, email)
		if existing_user:
			raise DuplicateEmailException()

		# 비밀번호 해싱
		password_hash = hash_password(password)

		# 사용자 생성
		user = UserRepository.create_user(
			db=db,
			email=email,
			password_hash=password_hash,
			nickname=nickname,
		)

		return user

	@staticmethod
	def login(
		db: Session,
		email: str,
		password: str,
		user_agent: str | None = None,
		ip_address: str | None = None,
	) -> tuple[str, str]:
		"""로그인"""
		# 사용자 조회
		user = UserRepository.get_user_by_email(db, email)
		if not user:
			raise LoginUserNotFoundException()

		# 비밀번호 검증
		if not verify_password(password, user.password_hash):
			raise LoginInvalidPasswordException()

		# Access token 생성
		access_token = create_access_token(
			data={"sub": str(user.id), "email": user.email}
		)

		# Refresh token 생성 및 저장
		refresh_token = create_refresh_token()
		token_hash = hash_token(refresh_token)
		expires_at = get_refresh_token_expiry()

		RefreshTokenRepository.create_refresh_token(
			db=db,
			user_id=user.id,
			token_hash=token_hash,
			expires_at=expires_at,
			user_agent=user_agent,
			ip_address=ip_address,
		)

		return access_token, refresh_token

	@staticmethod
	def refresh_access_token(
		db: Session,
		refresh_token: str,
	) -> str:
		"""Access token 재발급"""
		# Refresh token 해시
		token_hash = hash_token(refresh_token)

		# Refresh token 조회
		refresh_token_obj = RefreshTokenRepository.get_refresh_token_by_hash(
			db, token_hash
		)
		if not refresh_token_obj:
			raise TokenInvalidException()

		# Refresh token 만료 확인
		if refresh_token_obj.expires_at < datetime.now(timezone.utc):
			raise TokenExpiredException()

		# Refresh token 폐기 확인
		if refresh_token_obj.revoked_at is not None:
			raise TokenRevokedException()

		# 사용자 조회
		user = UserRepository.get_user_by_id(db, refresh_token_obj.user_id)
		if not user:
			raise UserNotFoundException()

		# 마지막 사용 시각 업데이트
		RefreshTokenRepository.update_last_used(db, refresh_token_obj.id)

		# 새 access token 생성
		access_token = create_access_token(
			data={"sub": str(user.id), "email": user.email}
		)

		return access_token

	@staticmethod
	def logout(
		db: Session,
		user_id: int,
	) -> None:
		"""로그아웃"""
		# 사용자의 모든 refresh token 폐기
		RefreshTokenRepository.revoke_all_user_tokens(db, user_id)

	@staticmethod
	def change_password(
		db: Session,
		user_id: int,
		current_password: str,
		new_password: str,
	) -> User:
		"""비밀번호 변경"""
		# 사용자 조회
		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			raise UserNotFoundException()

		# 현재 비밀번호 검증
		if not verify_password(current_password, user.password_hash):
			raise PasswordMismatchException()

		# 새 비밀번호 해싱
		new_password_hash = hash_password(new_password)

		# 비밀번호 업데이트
		user = UserRepository.update_user(
			db, user_id, password_hash=new_password_hash
		)

		# 모든 refresh token 폐기 (비밀번호 변경 시 전체 로그아웃)
		RefreshTokenRepository.revoke_all_user_tokens(db, user_id)

		return user
