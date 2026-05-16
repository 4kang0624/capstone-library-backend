from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.rental_image import RentalImage


class RentalImageRepository:
	"""대여 이미지 저장소"""

	@staticmethod
	def get_by_rental(db: Session, rental_id: int) -> list[RentalImage]:
		return db.query(RentalImage).filter(RentalImage.rental_id == rental_id).all()

	@staticmethod
	def get_by_rental_and_phase(db: Session, rental_id: int, phase: str) -> list[RentalImage]:
		return (
			db.query(RentalImage)
			.filter(
				RentalImage.rental_id == rental_id,
				RentalImage.image_phase == phase,
			)
			.all()
		)

	@staticmethod
	def create(db: Session, **kwargs) -> RentalImage:
		image = RentalImage(**kwargs)
		db.add(image)
		db.commit()
		db.refresh(image)
		return image
