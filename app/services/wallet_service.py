import secrets
from datetime import datetime, timedelta, timezone

from eth_account import Account
from eth_account.messages import encode_defunct
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.wallet_nonce_repository import WalletNonceRepository

_NONCE_TTL_MINUTES = 10


class WalletService:
	@staticmethod
	def issue_nonce(db: Session, user_id: int, wallet_address: str) -> tuple[str, str]:
		"""지갑 검증용 nonce 발급 및 DB 저장"""
		nonce = secrets.token_urlsafe(16)
		message = f"Verify wallet ownership.\nNonce: {nonce}"
		expires_at = datetime.now(timezone.utc) + timedelta(minutes=_NONCE_TTL_MINUTES)
		WalletNonceRepository.create_nonce(
			db=db,
			user_id=user_id,
			wallet_address=wallet_address,
			nonce=nonce,
			message=message,
			expires_at=expires_at,
		)
		return nonce, message

	@staticmethod
	def verify_signature_and_save(
		db: Session,
		user_id: int,
		wallet_address: str,
		nonce: str,
		signature: str,
	) -> bool:
		"""서명 검증 및 사용자 지갑 주소 저장"""
		wallet_nonce = WalletNonceRepository.get_active_by_wallet_and_nonce(
			db=db,
			wallet_address=wallet_address,
			nonce=nonce,
		)
		if not wallet_nonce:
			return False

		msg = encode_defunct(text=wallet_nonce.message)
		try:
			recovered = Account.recover_message(msg, signature=signature)
		except Exception:
			return False
		if recovered.lower() != wallet_address.lower():
			return False

		WalletNonceRepository.mark_as_used(db, wallet_nonce)

		user = UserRepository.get_user_by_id(db, user_id)
		if not user:
			return False
		user.wallet_address = wallet_address
		db.commit()
		db.refresh(user)
		return True

	@staticmethod
	def disconnect_wallet(db: Session, user_id: int) -> None:
		"""지갑 연결 해제"""
		user = UserRepository.get_user_by_id(db, user_id)
		if user:
			user.wallet_address = None
			db.commit()
