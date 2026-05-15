from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.bookmark import BookmarkResponse, BookmarkUpsertRequest
from app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.put("", response_model=BookmarkResponse)
def upsert_bookmark(
	request: BookmarkUpsertRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""책갈피 upsert — 없으면 INSERT, 있으면 current_page / note UPDATE"""
	return BookmarkService.upsert_bookmark(
		db=db,
		user_id=current_user.id,
		book_id=request.book_id,
		book_copy_id=request.book_copy_id,
		current_page=request.current_page,
		note=request.note,
	)


@router.get("/me", response_model=list[BookmarkResponse])
def get_my_bookmarks(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[dict]:
	"""내 책갈피 목록"""
	return BookmarkService.get_my_bookmarks(db=db, user_id=current_user.id)


@router.get("/books/{book_id}", response_model=BookmarkResponse)
def get_bookmark_by_book(
	book_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""특정 책에 대한 사용자의 책갈피 조회"""
	return BookmarkService.get_bookmark_by_book(db=db, user_id=current_user.id, book_id=book_id)


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
	bookmark_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	"""책갈피 삭제 (본인 확인)"""
	BookmarkService.delete_bookmark(db=db, bookmark_id=bookmark_id, user_id=current_user.id)
