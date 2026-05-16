from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.book_copy import BookCopyCreateRequest, BookCopyResponse, BookCopyUpdateRequest
from app.services.book_copy_service import BookCopyService

router = APIRouter(prefix="/book-copies", tags=["BookCopies"])


@router.post("", response_model=BookCopyResponse, status_code=status.HTTP_201_CREATED)
def create_book_copy(
	request: BookCopyCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""독서 복본 등록"""
	return BookCopyService.create_copy(
		db=db,
		owner_user_id=current_user.id,
		book_id=request.book_id,
		condition_status=request.condition_status,
		is_available_for_rent=request.is_available_for_rent,
		memo=request.memo,
	)


@router.get("", response_model=list[BookCopyResponse])
def get_book_copies_by_book(
	book_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[dict]:
	"""사용자 복본 목록 (book_id 필터 필수)"""
	return BookCopyService.get_copies_by_book(db=db, book_id=book_id)


@router.get("/me", response_model=list[BookCopyResponse])
def get_my_book_copies(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[dict]:
	"""내 독서 복본 목록"""
	return BookCopyService.get_my_copies(db=db, user_id=current_user.id)


@router.get("/rentable", response_model=list[BookCopyResponse])
def get_rentable_book_copies(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[dict]:
	"""대여 가능한 독서 복본 목록"""
	return BookCopyService.get_rentable_copies(db=db)


@router.get("/{copy_id}", response_model=BookCopyResponse)
def get_book_copy(
	copy_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""독서 복본 단건 조회"""
	return BookCopyService.get_copy(db=db, copy_id=copy_id)


@router.patch("/{copy_id}", response_model=BookCopyResponse)
def update_book_copy(
	copy_id: int,
	request: BookCopyUpdateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""독서 복본 수정 (본인 소유 확인)"""
	return BookCopyService.update_copy(
		db=db,
		copy_id=copy_id,
		user_id=current_user.id,
		condition_status=request.condition_status,
		is_available_for_rent=request.is_available_for_rent,
		memo=request.memo,
	)


@router.delete("/{copy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_copy(
	copy_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	"""독서 복본 삭제 (본인 소유 + 대여 상태 확인)"""
	BookCopyService.delete_copy(db=db, copy_id=copy_id, user_id=current_user.id)
