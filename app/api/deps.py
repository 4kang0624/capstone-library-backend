from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import (
	AdminRequiredException,
	TokenInvalidException,
	UserNotActiveException,
)
from app.core.security import verify_access_token
from app.enums.user import UserRole, UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	db: Session = Depends(get_db),
) -> User:
	"""
	현재 인증된 사용자 조회
	
	Bearer token에서 사용자 정보를 추출하고 검증합니다.
	"""
	token = credentials.credentials

	# Access token 검증
	payload = verify_access_token(token)
	if payload is None:
		raise TokenInvalidException()

	user_id = payload.get("sub")
	if user_id is None:
		raise TokenInvalidException()

	try:
		user_id = int(user_id)
	except (ValueError, TypeError):
		raise TokenInvalidException()

	# 사용자 조회
	user = UserRepository.get_user_by_id(db, user_id)
	if user is None:
		raise TokenInvalidException()

	return user


def get_active_user(
	current_user: User = Depends(get_current_user),
) -> User:
	"""
	활성 사용자 조회
	
	현재 사용자가 ACTIVE 상태인지 확인합니다.
	탈퇴하거나 정지된 사용자는 접근할 수 없습니다.
	"""
	if current_user.status != UserStatus.ACTIVE.value:
		raise UserNotActiveException()

	return current_user


def require_admin(
	current_user: User = Depends(get_active_user),
) -> User:
	"""
	관리자 권한 확인
	
	현재 사용자가 ADMIN 역할을 가지고 있는지 확인합니다.
	"""
	if current_user.role != UserRole.ADMIN.value:
		raise AdminRequiredException()

	return current_user


__all__ = ["get_db", "get_current_user", "get_active_user", "require_admin"]
