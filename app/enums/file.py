from enum import Enum


class RentalImagePhase(str, Enum):
	"""대여 이미지 업로드 시점"""

	BEFORE = "BEFORE"
	AFTER = "AFTER"
