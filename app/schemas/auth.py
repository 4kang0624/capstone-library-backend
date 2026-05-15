from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
	"""회원가입 요청"""

	email: EmailStr
	password: str = Field(..., min_length=8)
	nickname: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
	"""로그인 요청"""

	email: EmailStr
	password: str


class TokenResponse(BaseModel):
	"""토큰 응답"""

	access_token: str
	refresh_token: str
	token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
	"""Refresh token 요청"""

	refresh_token: str
