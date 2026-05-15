from sqlalchemy.orm import Session

from app.core.exceptions import BookNotFoundException
from app.models.book import Book
from app.repositories.book_repository import BookRepository


class BookService:
	"""도서 서비스"""

	@staticmethod
	def import_book(
		db: Session,
		isbn13: str,
		title: str,
		author: str,
		publisher: str,
		source: str,
		isbn10: str | None = None,
		published_date: str | None = None,
		description: str | None = None,
		cover_image_url: str | None = None,
		external_book_id: str | None = None,
		external_url: str | None = None,
	) -> tuple[Book, bool]:
		"""
		외부 데이터를 books 테이블에 upsert.
		반환: (book, created) — created=True이면 신규 INSERT, False이면 기존 재사용.
		"""
		existing = BookRepository.get_by_isbn13(db, isbn13)
		if existing:
			return existing, False

		book = BookRepository.create(
			db,
			isbn13=isbn13,
			isbn10=isbn10,
			title=title,
			author=author,
			publisher=publisher,
			published_date=published_date,
			description=description,
			cover_image_url=cover_image_url,
			source=source,
			external_book_id=external_book_id,
			external_url=external_url,
		)
		return book, True

	@staticmethod
	def get_book_detail(db: Session, book_id: int) -> Book:
		"""books 테이블에서 해당 책 상세 조회 후 view_count +1."""
		book = BookRepository.get_by_id(db, book_id)
		if not book:
			raise BookNotFoundException()
		BookRepository.increment_view_count(db, book_id)
		db.refresh(book)
		return book
