from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
	BookmarkForbiddenException,
	BookmarkNotFoundException,
)
from app.models.book import Book
from app.models.bookmark import Bookmark
from app.repositories.book_repository import BookRepository
from app.repositories.bookmark_repository import BookmarkRepository


class BookmarkService:
	"""책갈피 서비스"""

	@staticmethod
	def _with_book(db: Session, bookmark: Bookmark) -> dict:
		book: Book | None = BookRepository.get_by_id(db, bookmark.book_id)
		return {
			**bookmark.__dict__,
			"title": book.title if book else None,
			"author": book.author if book else None,
			"cover_image_url": book.cover_image_url if book else None,
		}

	@staticmethod
	def upsert_bookmark(
		db: Session,
		user_id: int,
		book_id: int,
		current_page: int,
		book_copy_id: Optional[int] = None,
		note: Optional[str] = None,
	) -> dict:
		"""책갈피 upsert — 없으면 INSERT, 있으면 current_page / note UPDATE."""
		existing = BookmarkRepository.get_by_user_and_book(db, user_id, book_id)
		if existing:
			bookmark = BookmarkRepository.update(
				db,
				existing.id,
				current_page=current_page,
				note=note,
				book_copy_id=book_copy_id,
			)
		else:
			bookmark = BookmarkRepository.create(
				db,
				user_id=user_id,
				book_id=book_id,
				book_copy_id=book_copy_id,
				current_page=current_page,
				note=note,
			)
		return BookmarkService._with_book(db, bookmark)

	@staticmethod
	def get_my_bookmarks(db: Session, user_id: int) -> list[dict]:
		bookmarks = BookmarkRepository.get_by_user(db, user_id)
		return [BookmarkService._with_book(db, bm) for bm in bookmarks]

	@staticmethod
	def get_bookmark_by_book(db: Session, user_id: int, book_id: int) -> dict:
		bookmark = BookmarkRepository.get_by_user_and_book(db, user_id, book_id)
		if not bookmark:
			raise BookmarkNotFoundException()
		return BookmarkService._with_book(db, bookmark)

	@staticmethod
	def delete_bookmark(db: Session, bookmark_id: int, user_id: int) -> None:
		bookmark = BookmarkRepository.get_by_id(db, bookmark_id)
		if not bookmark:
			raise BookmarkNotFoundException()
		if bookmark.user_id != user_id:
			raise BookmarkForbiddenException()
		BookmarkRepository.delete(db, bookmark)
