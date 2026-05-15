from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.reading_log import ReadingLogCreateRequest, ReadingLogResponse, ReadingLogUpdateRequest
from app.services.reading_log_service import ReadingLogService

router = APIRouter(prefix="/reading-logs", tags=["ReadingLogs"])


@router.post("", response_model=ReadingLogResponse, status_code=status.HTTP_201_CREATED)
def create_reading_log(
	request: ReadingLogCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""독서 기록 등록"""
	return ReadingLogService.create_log(
		db=db,
		user_id=current_user.id,
		book_id=request.book_id,
		book_copy_id=request.book_copy_id,
		reading_status=request.reading_status,
		started_at=request.started_at,
		finished_at=request.finished_at,
		rating=request.rating,
		memo=request.memo,
	)


@router.get("/me", response_model=list[ReadingLogResponse])
def get_my_reading_logs(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[dict]:
	"""내 독서 기록 목록"""
	return ReadingLogService.get_my_logs(db=db, user_id=current_user.id)


@router.patch("/{log_id}", response_model=ReadingLogResponse)
def update_reading_log(
	log_id: int,
	request: ReadingLogUpdateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""독서 기록 수정 (본인 확인)"""
	return ReadingLogService.update_log(
		db=db,
		log_id=log_id,
		user_id=current_user.id,
		reading_status=request.reading_status,
		finished_at=request.finished_at,
		rating=request.rating,
		memo=request.memo,
	)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading_log(
	log_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	"""독서 기록 삭제 (본인 확인)"""
	ReadingLogService.delete_log(db=db, log_id=log_id, user_id=current_user.id)
