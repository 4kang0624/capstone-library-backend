from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
	ReadingLogForbiddenException,
	ReadingLogNotFoundException,
)
from app.models.book import Book
from app.models.reading_log import ReadingLog
from app.repositories.book_repository import BookRepository
from app.repositories.reading_log_repository import ReadingLogRepository


class ReadingLogService:
	"""독서 기록 서비스"""

	@staticmethod
	def _with_book(db: Session, log: ReadingLog) -> dict:
		book: Book | None = BookRepository.get_by_id(db, log.book_id)
		return {
			**log.__dict__,
			"title": book.title if book else None,
			"author": book.author if book else None,
			"cover_image_url": book.cover_image_url if book else None,
		}

	@staticmethod
	def create_log(
		db: Session,
		user_id: int,
		book_id: int,
		reading_status: str,
		book_copy_id: Optional[int] = None,
		started_at: Optional[datetime] = None,
		finished_at: Optional[datetime] = None,
		rating: Optional[float] = None,
		memo: Optional[str] = None,
	) -> dict:
		log = ReadingLogRepository.create(
			db,
			user_id=user_id,
			book_id=book_id,
			book_copy_id=book_copy_id,
			reading_status=reading_status,
			started_at=started_at,
			finished_at=finished_at,
			rating=rating,
			memo=memo,
		)
		return ReadingLogService._with_book(db, log)

	@staticmethod
	def get_my_logs(db: Session, user_id: int) -> list[dict]:
		logs = ReadingLogRepository.get_by_user(db, user_id)
		return [ReadingLogService._with_book(db, log) for log in logs]

	@staticmethod
	def update_log(
		db: Session,
		log_id: int,
		user_id: int,
		reading_status: Optional[str] = None,
		finished_at: Optional[datetime] = None,
		rating: Optional[float] = None,
		memo: Optional[str] = None,
	) -> dict:
		log = ReadingLogRepository.get_by_id(db, log_id)
		if not log:
			raise ReadingLogNotFoundException()
		if log.user_id != user_id:
			raise ReadingLogForbiddenException()

		update_data: dict = {}
		if reading_status is not None:
			update_data["reading_status"] = reading_status
		if finished_at is not None:
			update_data["finished_at"] = finished_at
		if rating is not None:
			update_data["rating"] = rating
		if memo is not None:
			update_data["memo"] = memo

		log = ReadingLogRepository.update(db, log_id, **update_data)
		return ReadingLogService._with_book(db, log)

	@staticmethod
	def delete_log(db: Session, log_id: int, user_id: int) -> None:
		log = ReadingLogRepository.get_by_id(db, log_id)
		if not log:
			raise ReadingLogNotFoundException()
		if log.user_id != user_id:
			raise ReadingLogForbiddenException()
		ReadingLogRepository.delete(db, log)
