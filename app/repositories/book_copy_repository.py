from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.book_copy import BookCopy
from app.enums.book_copy import BookCopyCurrentStatus


class BookCopyRepository:
	"""도서 복본 저장소"""

	@staticmethod
	def get_by_id(db: Session, copy_id: int) -> BookCopy | None:
		return db.query(BookCopy).filter(BookCopy.id == copy_id).first()

	@staticmethod
	def get_by_owner(db: Session, owner_user_id: int) -> list[BookCopy]:
		return (
			db.query(BookCopy)
			.filter(BookCopy.owner_user_id == owner_user_id, BookCopy.deleted_at == None)
			.all()
		)

	@staticmethod
	def get_by_book(db: Session, book_id: int) -> list[BookCopy]:
		return (
			db.query(BookCopy)
			.filter(BookCopy.book_id == book_id, BookCopy.deleted_at == None)
			.all()
		)

	@staticmethod
	def get_rentable(db: Session) -> list[BookCopy]:
		return (
			db.query(BookCopy)
			.filter(
				BookCopy.deleted_at == None,
				BookCopy.is_available_for_rent == 1,
				BookCopy.current_status == BookCopyCurrentStatus.AVAILABLE.value,
			)
			.all()
		)

	@staticmethod
	def create(db: Session, **kwargs) -> BookCopy:
		copy = BookCopy(**kwargs)
		db.add(copy)
		db.commit()
		db.refresh(copy)
		return copy

	@staticmethod
	def update(db: Session, copy_id: int, **kwargs) -> BookCopy | None:
		copy = BookCopyRepository.get_by_id(db, copy_id)
		if not copy:
			return None
		for key, value in kwargs.items():
			if hasattr(copy, key):
				setattr(copy, key, value)
		db.commit()
		db.refresh(copy)
		return copy

	@staticmethod
	def has_rental_history(db: Session, copy_id: int) -> bool:
		result = db.execute(
			text("SELECT COUNT(*) FROM rentals WHERE book_copy_id = :copy_id"),
			{"copy_id": copy_id},
		).scalar()
		return (result or 0) > 0

	@staticmethod
	def soft_delete(db: Session, copy_id: int) -> None:
		db.execute(
			text(
				"UPDATE book_copies SET deleted_at = :now, is_available_for_rent = 0,"
				" current_status = 'UNAVAILABLE' WHERE id = :copy_id"
			),
			{"now": datetime.now(timezone.utc), "copy_id": copy_id},
		)
		db.commit()

	@staticmethod
	def delete(db: Session, copy: BookCopy) -> None:
		try:
			db.delete(copy)
			db.commit()
		except IntegrityError:
			db.rollback()
			BookCopyRepository.soft_delete(db, copy.id)
