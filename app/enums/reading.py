from enum import Enum


class ReadingStatus(str, Enum):
	"""독서 상태"""

	READING = "READING"
	COMPLETED = "COMPLETED"
	PAUSED = "PAUSED"
