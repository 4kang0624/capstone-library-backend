from sqlalchemy.orm import Session

from app.core.exceptions import (
	BookCopyDeleteConflictException,
	BookCopyForbiddenException,
	BookCopyNotFoundException,
)
from app.enums.book_copy import BookCopyCurrentStatus
from app.models.book import Book
from app.models.book_copy import BookCopy
from app.repositories.book_copy_repository import BookCopyRepository
from app.repositories.book_repository import BookRepository


class BookCopyService:
	"""독서 복본 서비스"""

	@staticmethod
	def _with_book(db: Session, copy: BookCopy) -> dict:
		"""BookCopy 등록 정보에 books JOIN 데이터를 더한 dict 반환."""
		book: Book | None = BookRepository.get_by_id(db, copy.book_id)
		return {
			**copy.__dict__,
			"title": book.title if book else None,
			"author": book.author if book else None,
			"cover_image_url": book.cover_image_url if book else None,
		}

	@staticmethod
	def create_copy(
		db: Session,
		owner_user_id: int,
		book_id: int,
		condition_status: str,
		is_available_for_rent: bool,
		memo: str | None = None,
	) -> dict:
		copy = BookCopyRepository.create(
			db,
			owner_user_id=owner_user_id,
			book_id=book_id,
			condition_status=condition_status,
			is_available_for_rent=1 if is_available_for_rent else 0,
			memo=memo,
		)
		return BookCopyService._with_book(db, copy)

	@staticmethod
	def get_my_copies(db: Session, user_id: int) -> list[dict]:
		copies = BookCopyRepository.get_by_owner(db, user_id)
		return [BookCopyService._with_book(db, c) for c in copies]

	@staticmethod
	def get_rentable_copies(db: Session) -> list[dict]:
		copies = BookCopyRepository.get_rentable(db)
		return [BookCopyService._with_book(db, c) for c in copies]

	@staticmethod
	def get_copy(db: Session, copy_id: int) -> dict:
		copy = BookCopyRepository.get_by_id(db, copy_id)
		if not copy:
			raise BookCopyNotFoundException()
		return BookCopyService._with_book(db, copy)

	@staticmethod
	def update_copy(
		db: Session,
		copy_id: int,
		user_id: int,
		condition_status: str | None = None,
		is_available_for_rent: bool | None = None,
		memo: str | None = None,
	) -> dict:
		copy = BookCopyRepository.get_by_id(db, copy_id)
		if not copy:
			raise BookCopyNotFoundException()
		if copy.owner_user_id != user_id:
			raise BookCopyForbiddenException()

		update_data: dict = {}
		if condition_status is not None:
			update_data["condition_status"] = condition_status
		if is_available_for_rent is not None:
			update_data["is_available_for_rent"] = 1 if is_available_for_rent else 0
		if memo is not None:
			update_data["memo"] = memo

		copy = BookCopyRepository.update(db, copy_id, **update_data)
		return BookCopyService._with_book(db, copy)

	@staticmethod
	def delete_copy(db: Session, copy_id: int, user_id: int) -> None:
		copy = BookCopyRepository.get_by_id(db, copy_id)
		if not copy:
			raise BookCopyNotFoundException()
		if copy.owner_user_id != user_id:
			raise BookCopyForbiddenException()
		if copy.current_status in (
			BookCopyCurrentStatus.REQUESTED.value,
			BookCopyCurrentStatus.RENTED.value,
		):
			raise BookCopyDeleteConflictException()
		BookCopyRepository.delete(db, copy)
