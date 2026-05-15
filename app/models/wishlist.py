from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint

from app.core.database import Base


class Wishlist(Base):
	"""찜 목록 모델"""

	__tablename__ = "wishlists"
	__table_args__ = (
		UniqueConstraint("user_id", "book_id", name="uk_wishlists_user_book"),
		Index("idx_wl_user_id", "user_id"),
		Index("idx_wl_book_id", "book_id"),
	)

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
	memo = Column(String(500), nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

	def __repr__(self) -> str:
		return f"<Wishlist(id={self.id}, user_id={self.user_id}, book_id={self.book_id})>"
