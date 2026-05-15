from sqlalchemy.orm import Session

from app.models.reading_log import ReadingLog


class ReadingLogRepository:
	"""독서 기록 저장소"""

	@staticmethod
	def get_by_id(db: Session, log_id: int) -> ReadingLog | None:
		return db.query(ReadingLog).filter(ReadingLog.id == log_id).first()

	@staticmethod
	def get_by_user(db: Session, user_id: int) -> list[ReadingLog]:
		return db.query(ReadingLog).filter(ReadingLog.user_id == user_id).all()

	@staticmethod
	def create(db: Session, **kwargs) -> ReadingLog:
		log = ReadingLog(**kwargs)
		db.add(log)
		db.commit()
		db.refresh(log)
		return log

	@staticmethod
	def update(db: Session, log_id: int, **kwargs) -> ReadingLog | None:
		log = ReadingLogRepository.get_by_id(db, log_id)
		if not log:
			return None
		for key, value in kwargs.items():
			if hasattr(log, key):
				setattr(log, key, value)
		db.commit()
		db.refresh(log)
		return log

	@staticmethod
	def delete(db: Session, log: ReadingLog) -> None:
		db.delete(log)
		db.commit()
