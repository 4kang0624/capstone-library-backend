from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.book import BookDetailResponse, BookImportRequest, BookImportResponse
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/import", response_model=BookImportResponse, status_code=status.HTTP_200_OK)
def import_book(
	request: BookImportRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""외부 데이터 기반 도서 upsert (ISBN 기준 중복 확인)"""
	book, created = BookService.import_book(
		db=db,
		isbn13=request.isbn13,
		isbn10=request.isbn10,
		title=request.title,
		author=request.author,
		publisher=request.publisher,
		published_date=request.published_date,
		description=request.description,
		cover_image_url=request.cover_image_url,
		source=request.source,
		external_book_id=request.external_book_id,
		external_url=request.external_url,
	)
	return {
		"id": book.id,
		"isbn13": book.isbn13,
		"title": book.title,
		"author": book.author,
		"publisher": book.publisher,
		"published_date": book.published_date,
		"description": book.description,
		"cover_image_url": book.cover_image_url,
		"source": book.source,
		"created": created,
	}


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(
	book_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""도서 상세 조회 + view_count 증가"""
	return BookService.get_book_detail(db=db, book_id=book_id)
