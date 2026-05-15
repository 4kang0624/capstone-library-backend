import secrets
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository

class WalletService:
	@staticmethod
	def issue_nonce(db: Session, wallet_address: str) -> str:
		"""지갑 검증용 nonce 발급 (랜덤 문자열)"""
		# 실제로는 wallet_nonce 테이블에 저장 필요 (여기선 단순 발급)
		return secrets.token_urlsafe(16)

	@staticmethod
	def verify_signature_and_save(db: Session, user_id: int, wallet_address: str, signature: str) -> bool:
		"""서명 검증 및 사용자 지갑 주소 저장 (서명 검증은 더미)"""
		# 실제로는 nonce, signature, wallet_address 검증 필요
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
