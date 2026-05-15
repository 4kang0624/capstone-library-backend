from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookCopyCreateRequest(BaseModel):
	book_id: int
	condition_status: str
	is_available_for_rent: bool
	memo: Optional[str] = None


class BookCopyUpdateRequest(BaseModel):
	condition_status: Optional[str] = None
	is_available_for_rent: Optional[bool] = None
	memo: Optional[str] = None


class BookCopyResponse(BaseModel):
	id: int
	owner_user_id: int
	book_id: int
	condition_status: str
	is_available_for_rent: int
	current_status: str
	memo: Optional[str] = None
	created_at: datetime
	updated_at: datetime
	# Joined from books
	title: Optional[str] = None
	author: Optional[str] = None
	cover_image_url: Optional[str] = None

	class Config:
		from_attributes = True
