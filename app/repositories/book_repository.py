from sqlalchemy.orm import Session

from app.models.book import Book


class BookRepository:
	"""도서 저장소"""

	@staticmethod
	def get_by_id(db: Session, book_id: int) -> Book | None:
		return db.query(Book).filter(Book.id == book_id).first()

	@staticmethod
	def get_by_isbn13(db: Session, isbn13: str) -> Book | None:
		return db.query(Book).filter(Book.isbn13 == isbn13).first()

	@staticmethod
	def create(db: Session, **kwargs) -> Book:
		book = Book(**kwargs)
		db.add(book)
		db.commit()
		db.refresh(book)
		return book

	@staticmethod
	def increment_view_count(db: Session, book_id: int) -> None:
		db.query(Book).filter(Book.id == book_id).update(
			{Book.view_count: Book.view_count + 1}
		)
		db.commit()
