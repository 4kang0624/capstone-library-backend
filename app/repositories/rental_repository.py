from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.rental import Rental


class RentalRepository:
	"""대여 저장소"""

	@staticmethod
	def get_by_id(db: Session, rental_id: int) -> Rental | None:
		return db.query(Rental).filter(Rental.id == rental_id).first()

	@staticmethod
	def get_by_user(db: Session, user_id: int) -> list[Rental]:
		"""사용자가 대여자 또는 빌린 사람인 모든 대여 조회 (최신순)"""
		return (
			db.query(Rental)
			.filter(
				(Rental.lender_user_id == user_id) | (Rental.borrower_user_id == user_id)
			)
			.order_by(Rental.created_at.desc())
			.all()
		)

	@staticmethod
	def create(db: Session, **kwargs) -> Rental:
		rental = Rental(**kwargs)
		db.add(rental)
		db.commit()
		db.refresh(rental)
		return rental

	@staticmethod
	def update(db: Session, rental_id: int, **kwargs) -> Rental | None:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			return None
		for key, value in kwargs.items():
			if hasattr(rental, key):
				setattr(rental, key, value)
		db.commit()
		db.refresh(rental)
		return rental
