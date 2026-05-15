from sqlalchemy.orm import Session

from app.core.exceptions import (
	WishlistDuplicateException,
	WishlistForbiddenException,
	WishlistNotFoundException,
)
from app.models.book import Book
from app.models.wishlist import Wishlist
from app.repositories.book_repository import BookRepository
from app.repositories.wishlist_repository import WishlistRepository


class WishlistService:
	"""위시리스트 서비스"""

	@staticmethod
	def _with_book(db: Session, item: Wishlist) -> dict:
		book: Book | None = BookRepository.get_by_id(db, item.book_id)
		return {
			**item.__dict__,
			"title": book.title if book else None,
			"author": book.author if book else None,
			"cover_image_url": book.cover_image_url if book else None,
			"description": book.description if book else None,
		}

	@staticmethod
	def add_to_wishlist(
		db: Session,
		user_id: int,
		book_id: int,
		memo: str | None = None,
	) -> dict:
		if WishlistRepository.get_by_user_and_book(db, user_id, book_id):
			raise WishlistDuplicateException()
		item = WishlistRepository.create(db, user_id=user_id, book_id=book_id, memo=memo)
		return WishlistService._with_book(db, item)

	@staticmethod
	def get_my_wishlist(db: Session, user_id: int) -> list[dict]:
		items = WishlistRepository.get_by_user(db, user_id)
		return [WishlistService._with_book(db, item) for item in items]

	@staticmethod
	def delete_wishlist(db: Session, wishlist_id: int, user_id: int) -> None:
		item = WishlistRepository.get_by_id(db, wishlist_id)
		if not item:
			raise WishlistNotFoundException()
		if item.user_id != user_id:
			raise WishlistForbiddenException()
		WishlistRepository.delete(db, item)
