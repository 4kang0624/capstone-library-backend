from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, SignUpRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
	request: SignUpRequest,
	db: Session = Depends(get_db),
) -> dict:
	"""회원가입"""
	user = AuthService.signup(
		db=db,
		email=request.email,
		password=request.password,
		nickname=request.nickname,
	)
	access_token, refresh_token = AuthService.login(
		db=db,
		email=user.email,
		password=request.password,
	)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
	}


@router.post("/login", response_model=TokenResponse)
def login(
	request: LoginRequest,
	db: Session = Depends(get_db),
) -> dict:
	"""로그인"""
	access_token, refresh_token = AuthService.login(
		db=db,
		email=request.email,
		password=request.password,
	)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
	}


@router.post("/refresh", response_model=TokenResponse)
def refresh(
	request: RefreshTokenRequest,
	db: Session = Depends(get_db),
) -> dict:
	"""Access token 재발급"""
	access_token = AuthService.refresh_access_token(
		db=db,
		refresh_token=request.refresh_token,
	)
	return {
		"access_token": access_token,
		"refresh_token": request.refresh_token,
	}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	"""로그아웃"""
	AuthService.logout(db=db, user_id=current_user.id)

