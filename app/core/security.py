import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from jwt import PyJWTError
from jwt import decode as jwt_decode
from jwt import encode as jwt_encode


# 비밀번호 해싱 관련 함수
def hash_password(password: str) -> str:
	"""비밀번호를 SHA-256으로 해싱"""
	return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""비밀번호 검증"""
	return hash_password(plain_password) == hashed_password


# Token 해싱 관련 함수
def hash_token(token: str) -> str:
	"""토큰을 SHA-256으로 해싱"""
	return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
	"""토큰 해시 검증"""
	return hash_token(token) == token_hash


# JWT 토큰 관련 함수
SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	"""Access token 생성"""
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now(timezone.utc) + expires_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


def create_refresh_token() -> str:
	"""Refresh token 생성 (무작위 문자열)"""
	import secrets

	return secrets.token_urlsafe(32)


def verify_access_token(token: str) -> dict[str, Any] | None:
	"""Access token 검증 및 payload 반환"""
	try:
		payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		return payload
	except PyJWTError:
		return None


def get_refresh_token_expiry() -> datetime:
	"""Refresh token 만료 시각 반환"""
	return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
