from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RentalImageResponse(BaseModel):
	id: int
	rental_id: int
	uploader_user_id: int
	image_phase: str
	file_path: str
	original_name: Optional[str] = None
	content_type: Optional[str] = None
	file_size: Optional[int] = None
	created_at: datetime

	class Config:
		from_attributes = True
