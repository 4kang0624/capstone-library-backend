from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.enums.user import UserStatus
from app.models.user import User

class AdminService:
	@staticmethod
	def list_users(db: Session) -> list[User]:
		"""전체 회원 목록 조회"""
		return db.query(User).all()

	@staticmethod
	def get_user_detail(db: Session, user_id: int) -> User | None:
		"""회원 상세 조회"""
		return UserRepository.get_user_by_id(db, user_id)

	@staticmethod
	def change_user_status(db: Session, user_id: int, status: UserStatus) -> User | None:
		"""회원 상태 변경"""
		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			return None
		user.status = status
		db.commit()
		db.refresh(user)
		return user
