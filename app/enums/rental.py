from enum import Enum


class RentalStatus(str, Enum):
	"""대여 상태"""

	REQUESTED = "REQUESTED"
	APPROVED = "APPROVED"
	REJECTED = "REJECTED"
	CANCELLED = "CANCELLED"
	BORROWING = "BORROWING"
	RETURNED = "RETURNED"
	COMPLETED = "COMPLETED"
	DISPUTED = "DISPUTED"


class RentalSyncStatus(str, Enum):
	"""온체인 동기화 상태"""

	NOT_REQUIRED = "NOT_REQUIRED"
	PREPARED = "PREPARED"
	TX_SUBMITTED = "TX_SUBMITTED"
	SYNCED = "SYNCED"
	FAILED = "FAILED"


class DeliveryMethod(str, Enum):
	"""전달 방식"""

	PARCEL = "PARCEL"
	IN_PERSON = "IN_PERSON"
