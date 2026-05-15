from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, VARCHAR

from app.core.database import Base
from app.enums.book_copy import BookCopyConditionStatus, BookCopyCurrentStatus


class BookCopy(Base):
	"""사용자 보유 도서 복본 모델"""

	__tablename__ = "book_copies"
	__table_args__ = (
		CheckConstraint(
			"condition_status IN ('GOOD', 'FAIR', 'POOR')",
			name="chk_book_copies_condition",
		),
		CheckConstraint(
			"is_available_for_rent IN (0, 1)",
			name="chk_book_copies_available",
		),
		CheckConstraint(
			"current_status IN ('AVAILABLE', 'REQUESTED', 'RENTED', 'UNAVAILABLE')",
			name="chk_book_copies_status",
		),
		Index("idx_bc_owner_user_id", "owner_user_id"),
		Index("idx_bc_book_id", "book_id"),
		Index("idx_bc_status", "current_status"),
	)

	id = Column(Integer, primary_key=True, index=True)
	owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
	condition_status = Column(VARCHAR(20), default=BookCopyConditionStatus.GOOD.value, nullable=False)
	is_available_for_rent = Column(Integer, default=0, nullable=False)
	current_status = Column(VARCHAR(30), default=BookCopyCurrentStatus.AVAILABLE.value, nullable=False)
	memo = Column(String(500), nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(
		DateTime,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	def __repr__(self) -> str:
		return f"<BookCopy(id={self.id}, owner_user_id={self.owner_user_id}, book_id={self.book_id})>"
