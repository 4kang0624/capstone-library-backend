from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, VARCHAR

from app.core.database import Base
from app.enums.rental import DeliveryMethod, RentalStatus, RentalSyncStatus


class Rental(Base):
	"""P2P 대여 트랜잭션 모델"""

	__tablename__ = "rentals"
	__table_args__ = (
		CheckConstraint(
			"rental_status IN ('REQUESTED', 'APPROVED', 'REJECTED', 'CANCELLED', 'BORROWING', 'RETURNED', 'COMPLETED', 'DISPUTED')",
			name="chk_rentals_status",
		),
		CheckConstraint(
			"sync_status IN ('NOT_REQUIRED', 'PREPARED', 'TX_SUBMITTED', 'SYNCED', 'FAILED')",
			name="chk_rentals_sync_status",
		),
		CheckConstraint(
			"delivery_method IN ('PARCEL', 'IN_PERSON')",
			name="chk_rentals_delivery_method",
		),
		CheckConstraint("REGEXP_LIKE(deposit_wei, '^[0-9]+$')", name="chk_rentals_deposit_num"),
		CheckConstraint("REGEXP_LIKE(shipping_fee_wei, '^[0-9]+$')", name="chk_rentals_ship_fee_num"),
		CheckConstraint("lender_user_id <> borrower_user_id", name="chk_rentals_not_self_rental"),
		Index("idx_rentals_book_id", "book_id"),
		Index("idx_rentals_book_copy_id", "book_copy_id"),
		Index("idx_rentals_lender_id", "lender_user_id"),
		Index("idx_rentals_borrower_id", "borrower_user_id"),
		Index("idx_rentals_status", "rental_status"),
		Index("idx_rentals_sync_status", "sync_status"),
		Index("idx_rentals_tx_hash", "tx_hash"),
		Index("idx_rentals_onchain_id", "onchain_rental_id"),
	)

	id = Column(Integer, primary_key=True, index=True)
	book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
	book_copy_id = Column(Integer, ForeignKey("book_copies.id"), nullable=False)
	lender_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	borrower_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	rental_status = Column(VARCHAR(30), default=RentalStatus.REQUESTED.value, nullable=False)
	sync_status = Column(VARCHAR(30), default=RentalSyncStatus.NOT_REQUIRED.value, nullable=False)
	deposit_wei = Column(String(78), default="0", nullable=False)
	shipping_fee_wei = Column(String(78), default="0", nullable=False)
	delivery_method = Column(VARCHAR(20), default=DeliveryMethod.PARCEL.value, nullable=False)
	shipping_address = Column(String(500), nullable=True)
	tracking_number = Column(String(100), nullable=True)
	courier_company = Column(String(100), nullable=True)
	due_date = Column(DateTime, nullable=True)
	request_message = Column(String(500), nullable=True)
	reject_reason = Column(String(500), nullable=True)
	dispute_reason = Column(String(1000), nullable=True)
	requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	approved_at = Column(DateTime, nullable=True)
	rejected_at = Column(DateTime, nullable=True)
	cancelled_at = Column(DateTime, nullable=True)
	borrowed_at = Column(DateTime, nullable=True)
	returned_at = Column(DateTime, nullable=True)
	contract_address = Column(String(100), nullable=True)
	chain_id = Column(Integer, nullable=True)
	tx_hash = Column(String(100), nullable=True)
	return_tx_hash = Column(String(100), nullable=True)
	onchain_rental_id = Column(Integer, nullable=True)
	lender_wallet_address = Column(String(100), nullable=True)
	borrower_wallet_address = Column(String(100), nullable=True)
	onchain_status = Column(VARCHAR(30), nullable=True)
	last_synced_at = Column(DateTime, nullable=True)
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at = Column(
		DateTime,
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False,
	)

	def __repr__(self) -> str:
		return f"<Rental(id={self.id}, book_copy_id={self.book_copy_id}, status={self.rental_status})>"
