from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

_WEI_RE = re.compile(r"^[0-9]+$")


class RentalCreateRequest(BaseModel):
	book_copy_id: int
	deposit_wei: str = "0"
	shipping_fee_wei: str = "0"
	delivery_method: str = "PARCEL"
	shipping_address: Optional[str] = None
	due_date: Optional[datetime] = None
	request_message: Optional[str] = None

	@field_validator("deposit_wei", "shipping_fee_wei")
	@classmethod
	def validate_wei(cls, v: str) -> str:
		if not _WEI_RE.match(v):
			raise ValueError("wei 값은 숫자 문자열이어야 합니다.")
		return v


class RentalRejectRequest(BaseModel):
	reject_reason: Optional[str] = None


class RentalDeliveryUpdateRequest(BaseModel):
	tracking_number: Optional[str] = None
	courier_company: Optional[str] = None
	shipping_address: Optional[str] = None


class RentalSyncOnchainRequest(BaseModel):
	tx_hash: str
	onchain_rental_id: int
	onchain_status: Optional[str] = None


class RentalSyncReturnOnchainRequest(BaseModel):
	return_tx_hash: str


class RentalDisputeRequest(BaseModel):
	dispute_reason: str


class RentalResponse(BaseModel):
	id: int
	book_id: int
	book_copy_id: int
	lender_user_id: int
	borrower_user_id: int
	rental_status: str
	sync_status: str
	deposit_wei: str
	shipping_fee_wei: str
	delivery_method: str
	shipping_address: Optional[str] = None
	tracking_number: Optional[str] = None
	courier_company: Optional[str] = None
	due_date: Optional[datetime] = None
	request_message: Optional[str] = None
	reject_reason: Optional[str] = None
	dispute_reason: Optional[str] = None
	requested_at: datetime
	approved_at: Optional[datetime] = None
	rejected_at: Optional[datetime] = None
	cancelled_at: Optional[datetime] = None
	borrowed_at: Optional[datetime] = None
	returned_at: Optional[datetime] = None
	contract_address: Optional[str] = None
	chain_id: Optional[int] = None
	tx_hash: Optional[str] = None
	return_tx_hash: Optional[str] = None
	onchain_rental_id: Optional[int] = None
	lender_wallet_address: Optional[str] = None
	borrower_wallet_address: Optional[str] = None
	onchain_status: Optional[str] = None
	last_synced_at: Optional[datetime] = None
	created_at: datetime
	updated_at: datetime

	class Config:
		from_attributes = True


class PrepareOnchainResponse(BaseModel):
	rental_id: int
	contract_address: str
	chain_id: int
	book_copy_id: int
	due_date_unix: Optional[int] = None
	deposit_wei: str
	shipping_fee_wei: str
	lender_wallet_address: Optional[str] = None
	borrower_wallet_address: Optional[str] = None
