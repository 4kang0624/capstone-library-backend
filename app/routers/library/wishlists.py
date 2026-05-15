from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.wishlist import WishlistCreateRequest, WishlistResponse
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/wishlists", tags=["Wishlists"])


@router.post("", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
	request: WishlistCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""위시리스트 등록"""
	return WishlistService.add_to_wishlist(
		db=db,
		user_id=current_user.id,
		book_id=request.book_id,
		memo=request.memo,
	)


@router.get("/me", response_model=list[WishlistResponse])
def get_my_wishlist(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[dict]:
	"""내 위시리스트 목록"""
	return WishlistService.get_my_wishlist(db=db, user_id=current_user.id)


@router.delete("/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wishlist(
	wishlist_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	"""위시리스트 항목 삭제 (본인 확인)"""
	WishlistService.delete_wishlist(db=db, wishlist_id=wishlist_id, user_id=current_user.id)
