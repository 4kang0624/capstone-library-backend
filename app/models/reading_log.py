from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, Numeric, Text, VARCHAR

from app.core.database import Base
from app.enums.reading import ReadingStatus


class ReadingLog(Base):
	"""독서 기록 모델"""

	__tablename__ = "reading_logs"
	__table_args__ = (
		CheckConstraint(
			"reading_status IN ('READING', 'COMPLETED', 'PAUSED')",
			name="chk_reading_logs_status",
		),
		CheckConstraint(
			"rating IS NULL OR (rating >= 0 AND rating <= 5)",
			name="chk_reading_logs_rating",
		),
		Index("idx_rl_user_id", "user_id"),
		Index("idx_rl_book_id", "book_id"),
		Index("idx_rl_book_copy_id", "book_copy_id"),
	)

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
	book_copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=True)
	reading_status = Column(VARCHAR(30), default=ReadingStatus.READING.value, nullable=False)
	started_at = Column(DateTime, nullable=True)
	finished_at = Column(DateTime, nullable=True)
	rating = Column(Numeric(2, 1), nullable=True)
	memo = Column(Text, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(
		DateTime,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	def __repr__(self) -> str:
		return f"<ReadingLog(id={self.id}, user_id={self.user_id}, book_id={self.book_id})>"
