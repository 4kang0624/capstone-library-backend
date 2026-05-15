from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, VARCHAR

from app.core.database import Base
from app.enums.user import UserRole, UserStatus


class User(Base):
	"""사용자 모델"""

	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String(255), unique=True, index=True, nullable=False)
	password_hash = Column(String(255), nullable=False)
	nickname = Column(String(100), nullable=False)
	role = Column(
		VARCHAR(20),
		default=UserRole.USER.value,
		nullable=False,
	)
	status = Column(
		VARCHAR(20),
		default=UserStatus.ACTIVE.value,
		nullable=False,
	)
	wallet_address = Column(String(100), unique=True, nullable=True, index=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(
		DateTime,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)
	deleted_at = Column(DateTime, nullable=True)

	def __repr__(self) -> str:
		return f"<User(id={self.id}, email={self.email}, nickname={self.nickname})>"
