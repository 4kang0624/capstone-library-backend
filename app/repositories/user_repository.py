from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User
from app.enums.user import UserStatus


class UserRepository:
	"""사용자 저장소"""

	@staticmethod
	def _build_deleted_email(email: str, user_id: int, deleted_at: datetime) -> str:
		"""삭제 보관용 이메일 생성 (UNIQUE 충돌 방지)"""
		suffix = f".deleted.{user_id}.{int(deleted_at.timestamp())}"
		local, separator, domain = email.partition("@")

		if separator:
			# Oracle VARCHAR2(255) 길이에 맞게 local part를 절단한다.
			max_local_len = 255 - len("@") - len(domain) - len(suffix)
			safe_local = local[:max(1, max_local_len)]
			return f"{safe_local}{suffix}@{domain}"

		max_email_len = 255 - len(suffix)
		safe_email = email[:max(1, max_email_len)]
		return f"{safe_email}{suffix}"

	@staticmethod
	def create_user(
		db: Session,
		email: str,
		password_hash: str,
		nickname: str,
	) -> User:
		"""사용자 생성"""
		user = User(
			email=email,
			password_hash=password_hash,
			nickname=nickname,
		)
		db.add(user)
		db.commit()
		db.refresh(user)
		return user

	@staticmethod
	def get_user_by_id(db: Session, user_id: int) -> User | None:
		"""ID로 사용자 조회"""
		return db.query(User).filter(User.id == user_id).first()

	@staticmethod
	def get_user_by_email(db: Session, email: str) -> User | None:
		"""이메일로 사용자 조회"""
		return db.query(User).filter(User.email == email).first()

	@staticmethod
	def get_user_by_wallet_address(db: Session, wallet_address: str) -> User | None:
		"""지갑 주소로 사용자 조회"""
		return db.query(User).filter(User.wallet_address == wallet_address).first()

	@staticmethod
	def get_active_users(db: Session) -> list[User]:
		"""활성 사용자 조회"""
		return db.query(User).filter(User.status == UserStatus.ACTIVE.value).all()

	@staticmethod
	def update_user(db: Session, user_id: int, **kwargs) -> User | None:
		"""사용자 정보 업데이트"""
		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			return None

		for key, value in kwargs.items():
			if hasattr(user, key):
				setattr(user, key, value)

		db.commit()
		db.refresh(user)
		return user

	@staticmethod
	def soft_delete_user(db: Session, user_id: int) -> User | None:
		"""사용자 소프트 삭제"""
		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			return None

		deleted_at = datetime.now(timezone.utc)
		archived_email = UserRepository._build_deleted_email(user.email, user.id, deleted_at)

		return UserRepository.update_user(
			db,
			user_id,
			email=archived_email,
			status=UserStatus.DELETED.value,
			deleted_at=deleted_at,
		)
