from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint

from app.core.database import Base


class Bookmark(Base):
	"""책갈피 모델"""

	__tablename__ = "bookmarks"
	__table_args__ = (
		UniqueConstraint("user_id", "book_id", name="uk_bookmarks_user_book"),
		CheckConstraint("current_page >= 0", name="chk_bookmarks_current_page"),
		Index("idx_bm_user_id", "user_id"),
		Index("idx_bm_book_id", "book_id"),
		Index("idx_bm_book_copy_id", "book_copy_id"),
	)

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
	book_copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=True)
	current_page = Column(Integer, default=0, nullable=False)
	note = Column(String(500), nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(
		DateTime,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	def __repr__(self) -> str:
		return f"<Bookmark(id={self.id}, user_id={self.user_id}, book_id={self.book_id})>"
