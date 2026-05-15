from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.admin_service import AdminService
from app.enums.user import UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])

def admin_required(current_user: User = Depends(get_current_user)) -> User:
    """ADMIN 권한 체크 의존성"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")
    return current_user

@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    회원 목록 조회 (ADMIN 전용)
    """
    users = AdminService.list_users(db)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    회원 상세 조회 (ADMIN 전용)
    """
    user = AdminService.get_user_detail(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user

from pydantic import BaseModel
from app.enums.user import UserStatus

class ChangeUserStatusRequest(BaseModel):
    status: UserStatus

@router.patch("/users/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: int,
    request: ChangeUserStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    """
    회원 상태 변경 (ADMIN 전용)
    """
    user = AdminService.change_user_status(db, user_id, request.status)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user