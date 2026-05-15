from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundException
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
	"""사용자 서비스"""

	@staticmethod
	def get_user(db: Session, user_id: int) -> User | None:
		"""사용자 조회"""
		return UserRepository.get_user_by_id(db, user_id)

	@staticmethod
	def update_user(
		db: Session,
		user_id: int,
		nickname: str | None = None,
	) -> User | None:
		"""사용자 정보 수정"""
		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			raise UserNotFoundException()

		update_data = {}
		if nickname is not None:
			update_data["nickname"] = nickname

		user = UserRepository.update_user(db, user_id, **update_data)
		return user

	@staticmethod
	def delete_user(db: Session, user_id: int) -> User | None:
		"""사용자 탈퇴 (소프트 삭제)"""
		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			raise UserNotFoundException()

		return UserRepository.soft_delete_user(db, user_id)
