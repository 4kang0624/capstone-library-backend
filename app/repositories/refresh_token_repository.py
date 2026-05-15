from datetime import datetime
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
	"""Refresh Token 저장소"""

	@staticmethod
	def create_refresh_token(
		db: Session,
		user_id: int,
		token_hash: str,
		expires_at: datetime,
		user_agent: str | None = None,
		ip_address: str | None = None,
	) -> RefreshToken:
		"""Refresh token 생성"""
		refresh_token = RefreshToken(
			user_id=user_id,
			token_hash=token_hash,
			expires_at=expires_at,
			user_agent=user_agent,
			ip_address=ip_address,
		)
		db.add(refresh_token)
		db.commit()
		db.refresh(refresh_token)
		return refresh_token

	@staticmethod
	def get_refresh_token_by_id(db: Session, token_id: int) -> RefreshToken | None:
		"""ID로 refresh token 조회"""
		return db.query(RefreshToken).filter(RefreshToken.id == token_id).first()

	@staticmethod
	def get_refresh_token_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
		"""토큰 해시로 refresh token 조회"""
		return (
			db.query(RefreshToken)
			.filter(RefreshToken.token_hash == token_hash)
			.first()
		)

	@staticmethod
	def get_user_refresh_tokens(db: Session, user_id: int) -> list[RefreshToken]:
		"""사용자의 refresh token 조회"""
		return db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()

	@staticmethod
	def get_active_refresh_tokens(db: Session, user_id: int) -> list[RefreshToken]:
		"""사용자의 활성 refresh token 조회"""
		from datetime import datetime, timezone

		return (
			db.query(RefreshToken)
			.filter(
				RefreshToken.user_id == user_id,
				RefreshToken.revoked_at == None,
				RefreshToken.expires_at > datetime.now(timezone.utc),
			)
			.all()
		)

	@staticmethod
	def revoke_refresh_token(db: Session, token_id: int) -> RefreshToken | None:
		"""Refresh token 폐기"""
		from datetime import datetime, timezone

		refresh_token = RefreshTokenRepository.get_refresh_token_by_id(db, token_id)
		if not refresh_token:
			return None

		refresh_token.revoked_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(refresh_token)
		return refresh_token

	@staticmethod
	def revoke_all_user_tokens(db: Session, user_id: int) -> None:
		"""사용자의 모든 refresh token 폐기"""
		from datetime import datetime, timezone

		tokens = RefreshTokenRepository.get_user_refresh_tokens(db, user_id)
		for token in tokens:
			token.revoked_at = datetime.now(timezone.utc)

		db.commit()

	@staticmethod
	def update_last_used(db: Session, token_id: int) -> RefreshToken | None:
		"""Refresh token의 마지막 사용 시각 업데이트"""
		from datetime import datetime, timezone

		refresh_token = RefreshTokenRepository.get_refresh_token_by_id(db, token_id)
		if not refresh_token:
			return None

		refresh_token.last_used_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(refresh_token)
		return refresh_token
