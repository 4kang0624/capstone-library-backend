from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["Wallet"])

class WalletNonceRequest(BaseModel):
	wallet_address: str

class WalletVerifyRequest(BaseModel):
	wallet_address: str
	signature: str

class WalletResponse(BaseModel):
	wallet_address: str

@router.post("/nonce")
def issue_wallet_nonce(
	request: WalletNonceRequest,
	db: Session = Depends(get_db),
):
	"""
	지갑 검증용 nonce 발급
	"""
	nonce = WalletService.issue_nonce(db, request.wallet_address)
	return {"nonce": nonce}

@router.post("/verify")
def verify_wallet_signature(
	request: WalletVerifyRequest,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	"""
	MetaMask 서명 검증 및 사용자 지갑 주소 저장
	"""
	result = WalletService.verify_signature_and_save(db, current_user.id, request.wallet_address, request.signature)
	if not result:
		raise HTTPException(status_code=400, detail="서명 검증에 실패했습니다.")
	return {"message": "지갑이 성공적으로 연결되었습니다."}

@router.get("/me", response_model=WalletResponse)
def get_my_wallet(
	current_user: User = Depends(get_current_user),
):
	"""
	연결된 지갑 조회
	"""
	if not current_user.wallet_address:
		raise HTTPException(status_code=404, detail="연결된 지갑이 없습니다.")
	return {"wallet_address": current_user.wallet_address}

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_my_wallet(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	"""
	지갑 연결 해제
	"""
	WalletService.disconnect_wallet(db, current_user.id)
	return
