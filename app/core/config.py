from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


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


def _to_float(value: str | None, default: float) -> float:
	if value is None or value.strip() == "":
		return default
	try:
		return float(value)
	except ValueError as exc:
		raise ValueError(f"Invalid float value: {value}") from exc


@dataclass(frozen=True)
class Settings:
	# Naver book search API
	naver_client_id: str | None
	naver_client_secret: str | None
	naver_book_api_timeout: float

	@classmethod
	def from_env(cls) -> "Settings":
		return cls(
			naver_client_id=os.getenv("NAVER_CLIENT_ID"),
			naver_client_secret=os.getenv("NAVER_CLIENT_SECRET"),
			naver_book_api_timeout=_to_float(os.getenv("NAVER_BOOK_API_TIMEOUT"), 5.0),
		)

	def validate_naver(self) -> None:
		if not self.naver_client_id:
			raise ValueError("NAVER_CLIENT_ID is required")
		if not self.naver_client_secret:
			raise ValueError("NAVER_CLIENT_SECRET is required")


_load_env_file()
settings = Settings.from_env()
