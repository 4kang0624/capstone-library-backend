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
		return db.query(BookCopy).filter(BookCopy.owner_user_id == owner_user_id).all()

	@staticmethod
	def get_rentable(db: Session) -> list[BookCopy]:
		return (
			db.query(BookCopy)
			.filter(
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
	def delete(db: Session, copy: BookCopy) -> None:
		db.delete(copy)
		db.commit()
