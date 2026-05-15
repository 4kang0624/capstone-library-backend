from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookmarkUpsertRequest(BaseModel):
	book_id: int
	book_copy_id: Optional[int] = None
	current_page: int
	note: Optional[str] = None


class BookmarkResponse(BaseModel):
	id: int
	user_id: int
	book_id: int
	book_copy_id: Optional[int] = None
	current_page: int
	note: Optional[str] = None
	created_at: datetime
	updated_at: datetime
	# Joined from books
	title: Optional[str] = None
	author: Optional[str] = None
	cover_image_url: Optional[str] = None

	class Config:
		from_attributes = True
