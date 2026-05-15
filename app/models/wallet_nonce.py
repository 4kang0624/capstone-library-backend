from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String

from app.core.database import Base


class WalletNonce(Base):
	"""지갑 서명 nonce 모델"""

	__tablename__ = "wallet_nonces"
	__table_args__ = (
		Index("idx_wn_user_id", "user_id"),
		Index("idx_wn_wallet_addr", "wallet_address"),
		Index("idx_wn_nonce", "nonce"),
	)

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	wallet_address = Column(String(100), nullable=False)
	nonce = Column(String(100), nullable=False)
	message = Column(String(1000), nullable=False)
	expires_at = Column(DateTime, nullable=False)
	used_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

	def __repr__(self) -> str:
		return f"<WalletNonce(id={self.id}, user_id={self.user_id})>"
