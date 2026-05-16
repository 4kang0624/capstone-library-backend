from pydantic import BaseModel


class WalletNonceRequest(BaseModel):
	"""nonce 발급 요청"""

	wallet_address: str


class WalletNonceResponse(BaseModel):
	"""nonce 발급 응답"""

	nonce: str
	message: str


class WalletVerifyRequest(BaseModel):
	"""서명 검증 요청"""

	wallet_address: str
	nonce: str
	signature: str


class WalletResponse(BaseModel):
	"""지갑 정보 응답"""

	wallet_address: str
