from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class RefreshToken(Base):
	"""Refresh Token 모델"""

	__tablename__ = "refresh_tokens"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
	token_hash = Column(String(255), nullable=False, index=True)
	expires_at = Column(DateTime, nullable=False)
	revoked_at = Column(DateTime, nullable=True)
	last_used_at = Column(DateTime, nullable=True)
	user_agent = Column(String(500), nullable=True)
	ip_address = Column(String(45), nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

	def __repr__(self) -> str:
		return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
