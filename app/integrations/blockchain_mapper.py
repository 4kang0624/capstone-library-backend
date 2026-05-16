from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timezone

from app.core.config import settings
from app.models.rental import Rental

_WEI_RE = re.compile(r"^[0-9]+$")


def _validated_wei(value: str | None) -> str:
	"""wei 값이 숫자 문자열인지 검증하고 반환. 유효하지 않으면 '0' 반환."""
	if value and _WEI_RE.match(value):
		return value
	return "0"


@dataclass(frozen=True)
class PrepareOnchainData:
	"""프론트엔드가 MetaMask로 스마트 컨트랙트를 호출하기 위한 파라미터 DTO"""

	rental_id: int
	contract_address: str
	chain_id: int
	book_copy_id: int
	due_date_unix: int | None
	deposit_wei: str
	shipping_fee_wei: str
	lender_wallet_address: str | None
	borrower_wallet_address: str | None


class BlockchainMapper:
	"""
	Rental 모델 → 스마트 컨트랙트 호출용 DTO 변환 유틸리티.

	백엔드는 컨트랙트를 직접 호출하지 않습니다.
	프론트가 이 데이터를 이용해 MetaMask로 직접 호출하며,
	백엔드는 prepare / sync 역할만 담당합니다.
	"""

	@staticmethod
	def to_prepare_onchain(rental: Rental) -> PrepareOnchainData:
		"""Rental 인스턴스를 PrepareOnchainData로 변환합니다."""
		due_date_unix: int | None = None
		if rental.due_date is not None:
			dt = rental.due_date
			if dt.tzinfo is None:
				dt = dt.replace(tzinfo=timezone.utc)
			due_date_unix = int(dt.timestamp())

		return PrepareOnchainData(
			rental_id=rental.id,
			contract_address=settings.contract_address or "",
			chain_id=settings.chain_id,
			book_copy_id=rental.book_copy_id,
			due_date_unix=due_date_unix,
			deposit_wei=_validated_wei(rental.deposit_wei),
			shipping_fee_wei=_validated_wei(rental.shipping_fee_wei),
			lender_wallet_address=rental.lender_wallet_address,
			borrower_wallet_address=rental.borrower_wallet_address,
		)
