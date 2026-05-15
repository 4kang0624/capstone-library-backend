from fastapi import APIRouter, HTTPException

from app.core.database import test_oracle_connection

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/db-connection-test")
def db_connection_test():
	try:
		return test_oracle_connection()
	except Exception as exc:
		error_message = str(exc)
		if "DPI-1050" in error_message:
			raise HTTPException(
				status_code=500,
				detail=(
					"Oracle client initialization failed. "
					"For Oracle 11g, install Oracle Instant Client 19c+ and set ORACLE_CLIENT_LIB_DIR to that path. "
					f"Original error: {error_message}"
				),
			) from exc
		if "DPY-3010" in error_message:
			raise HTTPException(
				status_code=500,
				detail=(
					"Oracle 11g requires python-oracledb thick mode. "
					"Set ORACLE_CLIENT_LIB_DIR in .env to your Oracle Client/DB BIN path and retry. "
					f"Original error: {error_message}"
				),
			) from exc
		raise HTTPException(status_code=500, detail=f"Oracle DB connection test failed: {exc}") from exc
