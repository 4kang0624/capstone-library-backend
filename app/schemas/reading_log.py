from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadingLogCreateRequest(BaseModel):
	book_id: int
	book_copy_id: Optional[int] = None
	reading_status: str
	started_at: Optional[datetime] = None
	finished_at: Optional[datetime] = None
	rating: Optional[float] = None
	memo: Optional[str] = None


class ReadingLogUpdateRequest(BaseModel):
	reading_status: Optional[str] = None
	finished_at: Optional[datetime] = None
	rating: Optional[float] = None
	memo: Optional[str] = None


class ReadingLogResponse(BaseModel):
	id: int
	user_id: int
	book_id: int
	book_copy_id: Optional[int] = None
	reading_status: str
	started_at: Optional[datetime] = None
	finished_at: Optional[datetime] = None
	rating: Optional[float] = None
	memo: Optional[str] = None
	created_at: datetime
	updated_at: datetime
	# Joined from books
	title: Optional[str] = None
	author: Optional[str] = None
	cover_image_url: Optional[str] = None

	class Config:
		from_attributes = True
