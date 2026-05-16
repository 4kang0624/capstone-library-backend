from fastapi import APIRouter, HTTPException, Query

from app.integrations.naver_book_client import NaverBookRequestError, NaverBookTimeoutError
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


def _raise_search_http_exception(exc: Exception) -> None:
	if isinstance(exc, NaverBookTimeoutError):
		raise HTTPException(status_code=504, detail=str(exc)) from exc
	if isinstance(exc, NaverBookRequestError):
		raise HTTPException(status_code=502, detail=str(exc)) from exc
	if isinstance(exc, ValueError):
		raise HTTPException(status_code=500, detail=str(exc)) from exc
	raise exc


@router.get("/books")
def search_books(keyword: str = Query(..., min_length=1)) -> dict:
	try:
		return SearchService.search_by_keyword(keyword)
	except Exception as exc:
		_raise_search_http_exception(exc)


@router.get("/books/isbn/{isbn}")
def search_books_by_isbn(isbn: str) -> dict:
	try:
		return SearchService.search_by_isbn(isbn)
	except Exception as exc:
		_raise_search_http_exception(exc)
