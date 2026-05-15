from sqlalchemy.orm import Session

from app.models.bookmark import Bookmark


class BookmarkRepository:
	"""책갈피 저장소"""

	@staticmethod
	def get_by_id(db: Session, bookmark_id: int) -> Bookmark | None:
		return db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()

	@staticmethod
	def get_by_user(db: Session, user_id: int) -> list[Bookmark]:
		return db.query(Bookmark).filter(Bookmark.user_id == user_id).all()

	@staticmethod
	def get_by_user_and_book(db: Session, user_id: int, book_id: int) -> Bookmark | None:
		return (
			db.query(Bookmark)
			.filter(Bookmark.user_id == user_id, Bookmark.book_id == book_id)
			.first()
		)

	@staticmethod
	def create(db: Session, **kwargs) -> Bookmark:
		bookmark = Bookmark(**kwargs)
		db.add(bookmark)
		db.commit()
		db.refresh(bookmark)
		return bookmark

	@staticmethod
	def update(db: Session, bookmark_id: int, **kwargs) -> Bookmark | None:
		bookmark = BookmarkRepository.get_by_id(db, bookmark_id)
		if not bookmark:
			return None
		for key, value in kwargs.items():
			if hasattr(bookmark, key):
				setattr(bookmark, key, value)
		db.commit()
		db.refresh(bookmark)
		return bookmark

	@staticmethod
	def delete(db: Session, bookmark: Bookmark) -> None:
		db.delete(bookmark)
		db.commit()
