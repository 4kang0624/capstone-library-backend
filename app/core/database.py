from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

try:
	import oracledb as oracle_dbapi
	_ORACLE_DBAPI_NAME = "oracledb"
except ImportError:
	oracle_dbapi = None
	_ORACLE_DBAPI_NAME = None


_ORACLE_CLIENT_INITIALIZED = False


def _validate_oracle_settings() -> None:
	if not settings.oracle_db_host:
		raise RuntimeError("ORACLE_DB_HOST is required")
	if not settings.oracle_db_service_name:
		raise RuntimeError("ORACLE_DB_SERVICE_NAME is required")
	if not settings.oracle_db_user:
		raise RuntimeError("ORACLE_DB_USER is required")
	if not settings.oracle_db_password:
		raise RuntimeError("ORACLE_DB_PASSWORD is required")


def _init_oracle_client_if_needed() -> None:
	global _ORACLE_CLIENT_INITIALIZED

	if oracle_dbapi is None or _ORACLE_DBAPI_NAME is None:
		raise RuntimeError(
			"No Oracle Python driver is installed. Install 'cx_Oracle' (recommended for 11.2 client) "
			"or 'oracledb'."
		)

	if _ORACLE_CLIENT_INITIALIZED:
		return

	if _ORACLE_DBAPI_NAME == "oracledb" and not settings.oracle_client_lib_dir:
		raise RuntimeError(
			"ORACLE_CLIENT_LIB_DIR is required for Oracle 11g because python-oracledb thin mode is not supported."
		)

	init_kwargs = {}
	if settings.oracle_client_lib_dir:
		init_kwargs["lib_dir"] = settings.oracle_client_lib_dir

	init_oracle_client = getattr(oracle_dbapi, "init_oracle_client", None)
	if init_oracle_client is None:
		_ORACLE_CLIENT_INITIALIZED = True
		return

	try:
		init_oracle_client(**init_kwargs)
	except Exception as exc:
		if "already initialized" in str(exc).lower():
			_ORACLE_CLIENT_INITIALIZED = True
			return
		raise

	_ORACLE_CLIENT_INITIALIZED = True


_validate_oracle_settings()

DATABASE_URL = URL.create(
	"oracle+cx_oracle" if _ORACLE_DBAPI_NAME == "cx_Oracle" else "oracle+oracledb",
	username=settings.oracle_db_user,
	password=settings.oracle_db_password,
	host=settings.oracle_db_host,
	port=settings.oracle_db_port,
	query={"service_name": settings.oracle_db_service_name or ""},
)

# 반드시 엔진 생성 전에 thick client 초기화
_init_oracle_client_if_needed()

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
)

Base = declarative_base()


def get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def initialize_oracle_client() -> None:
	"""Initialize Oracle client in thick mode for direct python-oracledb usage."""
	_init_oracle_client_if_needed()


def test_oracle_connection() -> dict:
	"""Run a lightweight Oracle connectivity test query."""
	_validate_oracle_settings()
	initialize_oracle_client()

	dsn = oracle_dbapi.makedsn(
		host=settings.oracle_db_host,
		port=settings.oracle_db_port,
		service_name=settings.oracle_db_service_name,
	)

	with oracle_dbapi.connect(
		user=settings.oracle_db_user,
		password=settings.oracle_db_password,
		dsn=dsn,
	) as connection:
		with connection.cursor() as cursor:
			cursor.execute("SELECT 1 FROM DUAL")
			result = cursor.fetchone()

	if not result or result[0] != 1:
		raise RuntimeError("Oracle DB test query returned unexpected result")

	return {
		"success": True,
		"message": "Oracle DB connection test succeeded",
		"driver": _ORACLE_DBAPI_NAME,
		"host": settings.oracle_db_host,
		"port": settings.oracle_db_port,
		"service_name": settings.oracle_db_service_name,
	}
