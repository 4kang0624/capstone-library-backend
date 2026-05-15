from sqlalchemy.orm import Session

from app.models.wishlist import Wishlist


class WishlistRepository:
	"""위시리스트 저장소"""

	@staticmethod
	def get_by_id(db: Session, wishlist_id: int) -> Wishlist | None:
		return db.query(Wishlist).filter(Wishlist.id == wishlist_id).first()

	@staticmethod
	def get_by_user(db: Session, user_id: int) -> list[Wishlist]:
		return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()

	@staticmethod
	def get_by_user_and_book(db: Session, user_id: int, book_id: int) -> Wishlist | None:
		return (
			db.query(Wishlist)
			.filter(Wishlist.user_id == user_id, Wishlist.book_id == book_id)
			.first()
		)

	@staticmethod
	def create(db: Session, **kwargs) -> Wishlist:
		wishlist = Wishlist(**kwargs)
		db.add(wishlist)
		db.commit()
		db.refresh(wishlist)
		return wishlist

	@staticmethod
	def delete(db: Session, wishlist: Wishlist) -> None:
		db.delete(wishlist)
		db.commit()
