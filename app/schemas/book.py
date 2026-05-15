from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookImportRequest(BaseModel):
	isbn13: str
	isbn10: Optional[str] = None
	title: str
	author: str
	publisher: str
	published_date: Optional[str] = None
	description: Optional[str] = None
	cover_image_url: Optional[str] = None
	source: str
	external_book_id: Optional[str] = None
	external_url: Optional[str] = None


class BookImportResponse(BaseModel):
	id: int
	isbn13: str
	title: str
	author: str
	publisher: str
	published_date: Optional[str] = None
	description: Optional[str] = None
	cover_image_url: Optional[str] = None
	source: str
	created: bool

	class Config:
		from_attributes = True


class BookDetailResponse(BaseModel):
	id: int
	isbn13: str
	isbn10: Optional[str] = None
	title: str
	author: str
	publisher: str
	published_date: Optional[str] = None
	description: Optional[str] = None
	cover_image_url: Optional[str] = None
	source: str
	view_count: int
	created_at: datetime

	class Config:
		from_attributes = True
