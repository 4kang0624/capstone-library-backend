from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# 환경 변수 파일 불러오기 (/.env)
def _load_env_file() -> None:
	env_path = Path(__file__).resolve().parents[2] / ".env"
	if not env_path.exists():
		return

	for raw_line in env_path.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, value = line.split("=", 1)
		os.environ.setdefault(key.strip(), value.strip())

# 환경 변수를 float 타입으로 변환하는 함수
def _to_float(value: str | None, default: float) -> float:
	if value is None or value.strip() == "":
		return default
	try:
		return float(value)
	except ValueError as exc:
		raise ValueError(f"Invalid float value: {value}") from exc

# 환경 변수를 int 타입으로 변환하는 함수
def _to_int(value: str | None, default: int) -> int:
	if value is None or value.strip() == "":
		return default
	try:
		return int(value)
	except ValueError as exc:
		raise ValueError(f"Invalid int value: {value}") from exc


@dataclass(frozen=True)
class Settings:
	# Naver book search API
	naver_client_id: str | None
	naver_client_secret: str | None
	naver_book_api_timeout: float
	oracle_db_host: str | None
	oracle_db_port: int
	oracle_db_service_name: str | None
	oracle_db_user: str | None
	oracle_db_password: str | None
	oracle_client_lib_dir: str | None
	# JWT
	secret_key: str
	jwt_access_token_expire_minutes: int
	jwt_refresh_token_expire_days: int
	# File uploads
	upload_dir: str
	# Blockchain
	contract_address: str | None
	chain_id: int

	@classmethod
	def from_env(cls) -> "Settings":
		return cls(
			naver_client_id=os.getenv("NAVER_CLIENT_ID"),
			naver_client_secret=os.getenv("NAVER_CLIENT_SECRET"),
			naver_book_api_timeout=_to_float(os.getenv("NAVER_BOOK_API_TIMEOUT"), 5.0),
			oracle_db_host=os.getenv("ORACLE_DB_HOST"),
			oracle_db_port=_to_int(os.getenv("ORACLE_DB_PORT"), 1521),
			oracle_db_service_name=os.getenv("ORACLE_DB_SERVICE_NAME"),
			oracle_db_user=os.getenv("ORACLE_DB_USER"),
			oracle_db_password=os.getenv("ORACLE_DB_PASSWORD"),
			oracle_client_lib_dir=os.getenv("ORACLE_CLIENT_LIB_DIR"),
			secret_key=os.getenv("SECRET_KEY", "secret-key"),
			jwt_access_token_expire_minutes=_to_int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"), 30),
			jwt_refresh_token_expire_days=_to_int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS"), 7),
			upload_dir=os.getenv("UPLOAD_DIR", "app/uploads"),
			contract_address=os.getenv("CONTRACT_ADDRESS"),
			chain_id=_to_int(os.getenv("CHAIN_ID"), 1),
		)

	def validate_naver(self) -> None:
		if not self.naver_client_id:
			raise ValueError("NAVER_CLIENT_ID is required")
		if not self.naver_client_secret:
			raise ValueError("NAVER_CLIENT_SECRET is required")

	def validate_blockchain(self) -> None:
		if not self.contract_address:
			raise ValueError("CONTRACT_ADDRESS is required")


_load_env_file()
settings = Settings.from_env()
