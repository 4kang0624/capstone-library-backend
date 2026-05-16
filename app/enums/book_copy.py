from enum import Enum


class BookCopyConditionStatus(str, Enum):
	"""도서 상태"""

	GOOD = "GOOD"
	FAIR = "FAIR"
	POOR = "POOR"


class BookCopyCurrentStatus(str, Enum):
	"""책 상태"""

	AVAILABLE = "AVAILABLE"
	REQUESTED = "REQUESTED"
	RENTED = "RENTED"
	UNAVAILABLE = "UNAVAILABLE"
