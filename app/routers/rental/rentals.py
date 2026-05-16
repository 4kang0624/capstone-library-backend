from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_user, get_db
from app.enums.file import RentalImagePhase
from app.integrations.blockchain_mapper import PrepareOnchainData
from app.models.user import User
from app.schemas.rental import (
	PrepareOnchainResponse,
	RentalCreateRequest,
	RentalDeliveryUpdateRequest,
	RentalDisputeRequest,
	RentalRejectRequest,
	RentalResponse,
	RentalSyncOnchainRequest,
	RentalSyncReturnOnchainRequest,
)
from app.schemas.rental_image import RentalImageResponse
from app.services.rental_service import RentalService

router = APIRouter(prefix="/rentals", tags=["Rentals"])


# ── 대여 요청 / 조회 ────────────────────────────────────────────────────────────

@router.post("", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def create_rental(
	request: RentalCreateRequest,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""대여 요청 생성"""
	return RentalService.create_rental(
		db=db,
		borrower_user_id=current_user.id,
		book_copy_id=request.book_copy_id,
		deposit_wei=request.deposit_wei,
		shipping_fee_wei=request.shipping_fee_wei,
		delivery_method=request.delivery_method,
		shipping_address=request.shipping_address,
		due_date=request.due_date,
		request_message=request.request_message,
	)


@router.get("/me", response_model=list[RentalResponse])
def get_my_rentals(
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> list[RentalResponse]:
	"""내 대여 목록 (대여자 + 빌린 사람 모두 포함)"""
	return RentalService.get_my_rentals(db=db, user_id=current_user.id)


@router.get("/{rental_id}", response_model=RentalResponse)
def get_rental(
	rental_id: int,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""대여 단건 조회"""
	return RentalService.get_rental(db=db, rental_id=rental_id, user_id=current_user.id)


# ── 상태 전환 ───────────────────────────────────────────────────────────────────

@router.post("/{rental_id}/approve", response_model=RentalResponse)
def approve_rental(
	rental_id: int,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""대여 승인 (대여자 전용)"""
	return RentalService.approve_rental(db=db, rental_id=rental_id, user_id=current_user.id)


@router.post("/{rental_id}/reject", response_model=RentalResponse)
def reject_rental(
	rental_id: int,
	request: RentalRejectRequest,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""대여 거절 (대여자 전용)"""
	return RentalService.reject_rental(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		reject_reason=request.reject_reason,
	)


@router.post("/{rental_id}/cancel", response_model=RentalResponse)
def cancel_rental(
	rental_id: int,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""대여 취소 (빌린 사람 전용)"""
	return RentalService.cancel_rental(db=db, rental_id=rental_id, user_id=current_user.id)


# ── 배송 정보 ───────────────────────────────────────────────────────────────────

@router.patch("/{rental_id}/delivery", response_model=RentalResponse)
def update_delivery(
	rental_id: int,
	request: RentalDeliveryUpdateRequest,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""배송 정보 수정 (대여자 전용)"""
	return RentalService.update_delivery(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		tracking_number=request.tracking_number,
		courier_company=request.courier_company,
		shipping_address=request.shipping_address,
	)


# ── 온체인 ──────────────────────────────────────────────────────────────────────

@router.post("/{rental_id}/prepare-onchain", response_model=PrepareOnchainResponse)
def prepare_onchain(
	rental_id: int,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> PrepareOnchainData:
	"""MetaMask 컨트랙트 호출에 필요한 파라미터 반환"""
	return RentalService.prepare_onchain(db=db, rental_id=rental_id, user_id=current_user.id)


@router.post("/{rental_id}/sync-onchain", response_model=RentalResponse)
def sync_onchain(
	rental_id: int,
	request: RentalSyncOnchainRequest,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""tx hash / onchain rental ID 동기화 → 상태 BORROWING 전환"""
	return RentalService.sync_onchain(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		tx_hash=request.tx_hash,
		onchain_rental_id=request.onchain_rental_id,
		onchain_status=request.onchain_status,
	)


@router.post("/{rental_id}/sync-return-onchain", response_model=RentalResponse)
def sync_return_onchain(
	rental_id: int,
	request: RentalSyncReturnOnchainRequest,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""반납 tx hash 동기화 → 상태 COMPLETED 전환"""
	return RentalService.sync_return_onchain(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		return_tx_hash=request.return_tx_hash,
	)


# ── 이미지 조회 / 업로드 ──────────────────────────────────────────────────────────

@router.get("/{rental_id}/images", response_model=list[RentalImageResponse])
def get_rental_images(
	rental_id: int,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> list[RentalImageResponse]:
	"""대여 이미지 전체 조회 (before + after)"""
	return RentalService.get_images(db=db, rental_id=rental_id, user_id=current_user.id)


@router.post(
	"/{rental_id}/images/before",
	response_model=RentalImageResponse,
	status_code=status.HTTP_201_CREATED,
)
def upload_before_image(
	rental_id: int,
	file: UploadFile = File(...),
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalImageResponse:
	"""대여 전 사진 업로드"""
	return RentalService.upload_image(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		file=file,
		phase=RentalImagePhase.BEFORE.value,
	)


@router.post(
	"/{rental_id}/images/after",
	response_model=RentalImageResponse,
	status_code=status.HTTP_201_CREATED,
)
def upload_after_image(
	rental_id: int,
	file: UploadFile = File(...),
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalImageResponse:
	"""반납 후 사진 업로드"""
	return RentalService.upload_image(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		file=file,
		phase=RentalImagePhase.AFTER.value,
	)


# ── 반납 / 분쟁 ─────────────────────────────────────────────────────────────────

@router.post("/{rental_id}/return", response_model=RentalResponse)
def return_rental(
	rental_id: int,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""반납 처리 (대여자 전용)"""
	return RentalService.return_rental(db=db, rental_id=rental_id, user_id=current_user.id)


@router.post("/{rental_id}/dispute", response_model=RentalResponse)
def dispute_rental(
	rental_id: int,
	request: RentalDisputeRequest,
	current_user: User = Depends(get_active_user),
	db: Session = Depends(get_db),
) -> RentalResponse:
	"""분쟁 제기"""
	return RentalService.dispute_rental(
		db=db,
		rental_id=rental_id,
		user_id=current_user.id,
		dispute_reason=request.dispute_reason,
	)
