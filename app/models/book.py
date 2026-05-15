from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Integer, String, Text, UniqueConstraint, VARCHAR

from app.core.database import Base


class Book(Base):
	"""도서 마스터 모델"""

	__tablename__ = "books"
	__table_args__ = (
		UniqueConstraint("isbn13", name="uk_books_isbn13"),
		CheckConstraint("source IN ('NAVER', 'MANUAL')", name="chk_books_source"),
		CheckConstraint("view_count >= 0", name="chk_books_view_count"),
		Index("idx_books_title", "title"),
		Index("idx_books_author", "author"),
		Index("idx_books_isbn10", "isbn10"),
	)

	id = Column(Integer, primary_key=True, index=True)
	isbn13 = Column(String(20), nullable=True)
	isbn10 = Column(String(20), nullable=True)
	title = Column(String(300), nullable=False)
	author = Column(String(300), nullable=True)
	publisher = Column(String(200), nullable=True)
	published_date = Column(String(30), nullable=True)
	description = Column(Text, nullable=True)
	cover_image_url = Column(String(500), nullable=True)
	source = Column(VARCHAR(50), default="NAVER", nullable=False)
	external_book_id = Column(String(100), nullable=True)
	external_url = Column(String(500), nullable=True)
	view_count = Column(Integer, default=0, nullable=False)
	last_fetched_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(
		DateTime,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	def __repr__(self) -> str:
		return f"<Book(id={self.id}, title={self.title})>"
