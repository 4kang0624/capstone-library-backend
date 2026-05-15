from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WishlistCreateRequest(BaseModel):
	book_id: int
	memo: Optional[str] = None


class WishlistResponse(BaseModel):
	id: int
	user_id: int
	book_id: int
	memo: Optional[str] = None
	created_at: datetime
	# Joined from books
	title: Optional[str] = None
	author: Optional[str] = None
	cover_image_url: Optional[str] = None
	description: Optional[str] = None

	class Config:
		from_attributes = True
