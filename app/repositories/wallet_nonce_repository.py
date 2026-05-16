from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.wallet_nonce import WalletNonce


class WalletNonceRepository:
	"""WalletNonce 저장소"""

	@staticmethod
	def create_nonce(
		db: Session,
		user_id: int,
		wallet_address: str,
		nonce: str,
		message: str,
		expires_at: datetime,
	) -> WalletNonce:
		"""nonce 생성 및 저장"""
		wallet_nonce = WalletNonce(
			user_id=user_id,
			wallet_address=wallet_address,
			nonce=nonce,
			message=message,
			expires_at=expires_at,
		)
		db.add(wallet_nonce)
		db.commit()
		db.refresh(wallet_nonce)
		return wallet_nonce

	@staticmethod
	def get_active_by_wallet_and_nonce(
		db: Session,
		wallet_address: str,
		nonce: str,
	) -> WalletNonce | None:
		"""유효한 nonce 조회 (미사용 + 만료 전)"""
		now = datetime.now(timezone.utc)
		return (
			db.query(WalletNonce)
			.filter(
				WalletNonce.wallet_address == wallet_address,
				WalletNonce.nonce == nonce,
				WalletNonce.used_at == None,  # noqa: E711
				WalletNonce.expires_at > now,
			)
			.first()
		)

	@staticmethod
	def mark_as_used(db: Session, wallet_nonce: WalletNonce) -> WalletNonce:
		"""nonce를 사용 완료 처리"""
		wallet_nonce.used_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(wallet_nonce)
		return wallet_nonce
