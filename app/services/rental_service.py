from __future__ import annotations

from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
	BookCopyNotAvailableException,
	BookCopyNotFoundException,
	RentalForbiddenException,
	RentalNotFoundException,
	RentalStatusConflictException,
	WalletNotConnectedException,
)
from app.enums.book_copy import BookCopyCurrentStatus
from app.enums.file import RentalImagePhase
from app.enums.rental import DeliveryMethod, RentalStatus, RentalSyncStatus
from app.integrations.blockchain_mapper import BlockchainMapper, PrepareOnchainData
from app.models.rental import Rental
from app.models.rental_image import RentalImage
from app.models.user import User
from app.repositories.book_copy_repository import BookCopyRepository
from app.repositories.rental_image_repository import RentalImageRepository
from app.repositories.rental_repository import RentalRepository
from app.services.file_service import FileService


def _now() -> datetime:
	return datetime.now(timezone.utc)


class RentalService:
	"""대여 서비스"""

	# ── 조회 ──────────────────────────────────────────────────────────────────

	@staticmethod
	def get_rental(db: Session, rental_id: int, user_id: int) -> Rental:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		return rental

	@staticmethod
	def get_my_rentals(db: Session, user_id: int) -> list[Rental]:
		return RentalRepository.get_by_user(db, user_id)

	# ── 대여 요청 ──────────────────────────────────────────────────────────────

	@staticmethod
	def create_rental(
		db: Session,
		borrower_user_id: int,
		book_copy_id: int,
		deposit_wei: str,
		shipping_fee_wei: str,
		delivery_method: str,
		shipping_address: str | None,
		due_date: datetime | None,
		request_message: str | None,
	) -> Rental:
		copy = BookCopyRepository.get_by_id(db, book_copy_id)
		if not copy:
			raise BookCopyNotFoundException()
		if (
			not copy.is_available_for_rent
			or copy.current_status != BookCopyCurrentStatus.AVAILABLE.value
		):
			raise BookCopyNotAvailableException()
		if copy.owner_user_id == borrower_user_id:
			raise RentalStatusConflictException("본인 소유의 책은 대여할 수 없습니다.")

		rental = RentalRepository.create(
			db,
			book_id=copy.book_id,
			book_copy_id=book_copy_id,
			lender_user_id=copy.owner_user_id,
			borrower_user_id=borrower_user_id,
			deposit_wei=deposit_wei,
			shipping_fee_wei=shipping_fee_wei,
			delivery_method=delivery_method,
			shipping_address=shipping_address,
			due_date=due_date,
			request_message=request_message,
			rental_status=RentalStatus.REQUESTED.value,
			sync_status=RentalSyncStatus.NOT_REQUIRED.value,
			requested_at=_now(),
		)
		BookCopyRepository.update(db, book_copy_id, current_status=BookCopyCurrentStatus.REQUESTED.value)
		return rental

	# ── 대여 승인 / 거절 / 취소 ────────────────────────────────────────────────

	@staticmethod
	def approve_rental(db: Session, rental_id: int, user_id: int) -> Rental:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status != RentalStatus.REQUESTED.value:
			raise RentalStatusConflictException("REQUESTED 상태에서만 승인할 수 있습니다.")

		return RentalRepository.update(
			db,
			rental_id,
			rental_status=RentalStatus.APPROVED.value,
			approved_at=_now(),
		)

	@staticmethod
	def reject_rental(db: Session, rental_id: int, user_id: int, reject_reason: str | None) -> Rental:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status != RentalStatus.REQUESTED.value:
			raise RentalStatusConflictException("REQUESTED 상태에서만 거절할 수 있습니다.")

		BookCopyRepository.update(
			db, rental.book_copy_id, current_status=BookCopyCurrentStatus.AVAILABLE.value
		)
		return RentalRepository.update(
			db,
			rental_id,
			rental_status=RentalStatus.REJECTED.value,
			reject_reason=reject_reason,
			rejected_at=_now(),
		)

	@staticmethod
	def cancel_rental(db: Session, rental_id: int, user_id: int) -> Rental:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status not in (
			RentalStatus.REQUESTED.value,
			RentalStatus.APPROVED.value,
		):
			raise RentalStatusConflictException("REQUESTED 또는 APPROVED 상태에서만 취소할 수 있습니다.")

		BookCopyRepository.update(
			db, rental.book_copy_id, current_status=BookCopyCurrentStatus.AVAILABLE.value
		)
		return RentalRepository.update(
			db,
			rental_id,
			rental_status=RentalStatus.CANCELLED.value,
			cancelled_at=_now(),
		)

	# ── 배송 정보 수정 ─────────────────────────────────────────────────────────

	@staticmethod
	def update_delivery(
		db: Session,
		rental_id: int,
		user_id: int,
		tracking_number: str | None,
		courier_company: str | None,
		shipping_address: str | None,
	) -> Rental:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status not in (
			RentalStatus.APPROVED.value,
			RentalStatus.BORROWING.value,
			RentalStatus.RETURNED.value,
		):
			raise RentalStatusConflictException("배송 정보는 APPROVED / BORROWING / RETURNED 상태에서만 수정할 수 있습니다.")

		update_data: dict = {}
		if tracking_number is not None:
			update_data["tracking_number"] = tracking_number
		if courier_company is not None:
			update_data["courier_company"] = courier_company
		if shipping_address is not None:
			update_data["shipping_address"] = shipping_address

		return RentalRepository.update(db, rental_id, **update_data)

	# ── 온체인 ─────────────────────────────────────────────────────────────────

	@staticmethod
	def prepare_onchain(db: Session, rental_id: int, user_id: int) -> PrepareOnchainData:
		"""
		프론트엔드가 MetaMask 호출에 사용할 컨트랙트 파라미터를 반환합니다.
		sync_status를 PREPARED로 설정하고 지갑 주소를 스냅샷합니다.
		"""
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status != RentalStatus.APPROVED.value:
			raise RentalStatusConflictException("APPROVED 상태에서만 온체인 준비를 할 수 있습니다.")

		# 지갑 주소 조회
		from app.repositories.user_repository import UserRepository

		lender = UserRepository.get_user_by_id(db, rental.lender_user_id)
		borrower = UserRepository.get_user_by_id(db, rental.borrower_user_id)

		if not lender or not lender.wallet_address:
			raise WalletNotConnectedException()
		if not borrower or not borrower.wallet_address:
			raise WalletNotConnectedException()

		RentalRepository.update(
			db,
			rental_id,
			sync_status=RentalSyncStatus.PREPARED.value,
			contract_address=settings.contract_address,
			chain_id=settings.chain_id,
			lender_wallet_address=lender.wallet_address,
			borrower_wallet_address=borrower.wallet_address,
		)

		# 업데이트된 rental을 다시 조회해서 매핑
		updated = RentalRepository.get_by_id(db, rental_id)
		return BlockchainMapper.to_prepare_onchain(updated)

	@staticmethod
	def sync_onchain(
		db: Session,
		rental_id: int,
		user_id: int,
		tx_hash: str,
		onchain_rental_id: int,
		onchain_status: str | None = None,
	) -> Rental:
		"""tx_hash와 onchain_rental_id를 저장하고 대여 상태를 BORROWING으로 전환합니다."""
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		is_approved = rental.rental_status == RentalStatus.APPROVED.value
		is_sync_ready = rental.sync_status in (
			RentalSyncStatus.PREPARED.value,
			RentalSyncStatus.TX_SUBMITTED.value,
		)
		if not is_approved and not is_sync_ready:
			raise RentalStatusConflictException(
				"rental_status가 APPROVED 이거나 sync_status가 PREPARED / TX_SUBMITTED 상태여야 합니다."
			)

		update_fields: dict = {
			"tx_hash": tx_hash,
			"onchain_rental_id": onchain_rental_id,
			"sync_status": RentalSyncStatus.SYNCED.value,
			"rental_status": RentalStatus.BORROWING.value,
			"borrowed_at": _now(),
			"last_synced_at": _now(),
		}
		if onchain_status is not None:
			update_fields["onchain_status"] = onchain_status

		BookCopyRepository.update(
			db, rental.book_copy_id, current_status=BookCopyCurrentStatus.RENTED.value
		)
		return RentalRepository.update(db, rental_id, **update_fields)

	@staticmethod
	def sync_return_onchain(
		db: Session,
		rental_id: int,
		user_id: int,
		return_tx_hash: str,
	) -> Rental:
		"""반납 tx hash를 저장하고 대여 상태를 COMPLETED로 전환합니다."""
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status != RentalStatus.RETURNED.value:
			raise RentalStatusConflictException("RETURNED 상태에서만 반납 온체인 동기화를 할 수 있습니다.")

		return RentalRepository.update(
			db,
			rental_id,
			return_tx_hash=return_tx_hash,
			sync_status=RentalSyncStatus.SYNCED.value,
			rental_status=RentalStatus.COMPLETED.value,
			last_synced_at=_now(),
		)
	# ── 이미지 조회 ──────────────────────────────────────────────────────────────

	@staticmethod
	def get_images(db: Session, rental_id: int, user_id: int) -> list[RentalImage]:
		"""대여 이미지 전체 조회 (before + after)"""
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		return RentalImageRepository.get_by_rental(db, rental_id)
	# ── 이미지 업로드 ──────────────────────────────────────────────────────────

	@staticmethod
	def upload_image(
		db: Session,
		rental_id: int,
		user_id: int,
		file: UploadFile,
		phase: str,
	) -> RentalImage:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()

		if phase == RentalImagePhase.BEFORE.value:
			if rental.rental_status not in (
				RentalStatus.REQUESTED.value,
				RentalStatus.APPROVED.value,
			):
				raise RentalStatusConflictException(
					"대여 전 사진은 REQUESTED 또는 APPROVED 상태에서만 업로드할 수 있습니다."
				)
		elif phase == RentalImagePhase.AFTER.value:
			if rental.rental_status not in (
				RentalStatus.BORROWING.value,
				RentalStatus.RETURNED.value,
			):
				raise RentalStatusConflictException(
					"반납 후 사진은 BORROWING 또는 RETURNED 상태에서만 업로드할 수 있습니다."
				)

		file_path, content_type, file_size = FileService.save_rental_image(file, phase, rental_id)

		return RentalImageRepository.create(
			db,
			rental_id=rental_id,
			uploader_user_id=user_id,
			image_phase=phase,
			file_path=file_path,
			original_name=file.filename,
			content_type=content_type,
			file_size=file_size,
		)

	# ── 반납 / 분쟁 ────────────────────────────────────────────────────────────

	@staticmethod
	def return_rental(db: Session, rental_id: int, user_id: int) -> Rental:
		"""대여자(lender)가 반납을 확인합니다."""
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status != RentalStatus.BORROWING.value:
			raise RentalStatusConflictException("BORROWING 상태에서만 반납 처리를 할 수 있습니다.")

		BookCopyRepository.update(
			db, rental.book_copy_id, current_status=BookCopyCurrentStatus.AVAILABLE.value
		)
		return RentalRepository.update(
			db,
			rental_id,
			rental_status=RentalStatus.RETURNED.value,
			returned_at=_now(),
		)

	@staticmethod
	def dispute_rental(db: Session, rental_id: int, user_id: int, dispute_reason: str) -> Rental:
		rental = RentalRepository.get_by_id(db, rental_id)
		if not rental:
			raise RentalNotFoundException()
		if rental.lender_user_id != user_id and rental.borrower_user_id != user_id:
			raise RentalForbiddenException()
		if rental.rental_status not in (
			RentalStatus.BORROWING.value,
			RentalStatus.RETURNED.value,
		):
			raise RentalStatusConflictException("BORROWING 또는 RETURNED 상태에서만 분쟁을 제기할 수 있습니다.")

		return RentalRepository.update(
			db,
			rental_id,
			rental_status=RentalStatus.DISPUTED.value,
			dispute_reason=dispute_reason,
		)
