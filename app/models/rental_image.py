from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, VARCHAR

from app.core.database import Base
class RentalImage(Base):
	"""대여 상태 이미지 모델"""

	__tablename__ = "rental_images"
	__table_args__ = (
		CheckConstraint("image_phase IN ('BEFORE', 'AFTER')", name="chk_rental_images_phase"),
		CheckConstraint("file_size IS NULL OR file_size >= 0", name="chk_rental_images_file_size"),
		Index("idx_ri_rental_id", "rental_id"),
		Index("idx_ri_uploader_id", "uploader_user_id"),
	)

	id = Column(Integer, primary_key=True, index=True)
	rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
	uploader_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	image_phase = Column(VARCHAR(30), nullable=False)
	file_path = Column(String(500), nullable=False)
	original_name = Column(String(255), nullable=True)
	content_type = Column(String(100), nullable=True)
	file_size = Column(Integer, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

	def __repr__(self) -> str:
		return f"<RentalImage(id={self.id}, rental_id={self.rental_id}, phase={self.image_phase})>"
