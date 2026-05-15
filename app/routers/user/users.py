from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
	ChangePasswordRequest,
	UpdateUserRequest,
	UserResponse,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
	current_user: User = Depends(get_current_user),
) -> User:
	"""현재 사용자 정보 조회"""
	return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
	request: UpdateUserRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> User:
	"""현재 사용자 정보 수정"""
	return UserService.update_user(
		db=db,
		user_id=current_user.id,
		nickname=request.nickname,
	)


@router.patch("/me/password")
def change_current_user_password(
	request: ChangePasswordRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> dict:
	"""비밀번호 변경"""
	AuthService.change_password(
		db=db,
		user_id=current_user.id,
		current_password=request.current_password,
		new_password=request.new_password,
	)
	return {"message": "비밀번호가 변경되었습니다."}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	"""회원 탈퇴"""
	UserService.delete_user(
		db=db,
		user_id=current_user.id,
	)

