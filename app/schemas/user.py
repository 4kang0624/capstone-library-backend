from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.enums.user import UserRole, UserStatus


class UserResponse(BaseModel):
	"""사용자 응답"""

	id: int
	email: EmailStr
	nickname: str
	role: UserRole
	status: UserStatus
	wallet_address: str | None = None
	created_at: datetime
	updated_at: datetime

	class Config:
		from_attributes = True


class UpdateUserRequest(BaseModel):
	"""사용자 정보 수정 요청"""

	nickname: str = Field(..., min_length=1, max_length=100)


class ChangePasswordRequest(BaseModel):
	"""비밀번호 변경 요청"""

	current_password: str
	new_password: str = Field(..., min_length=8)
