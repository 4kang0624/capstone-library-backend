from enum import Enum


class UserRole(str, Enum):
	"""사용자 역할"""
	USER = "USER"
	ADMIN = "ADMIN"


class UserStatus(str, Enum):
	"""사용자 상태"""
	ACTIVE = "ACTIVE"
	SUSPENDED = "SUSPENDED"
	DELETED = "DELETED"
