from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class FileService:
	"""파일 저장 서비스"""

	@staticmethod
	def save_rental_image(
		file: UploadFile,
		phase: str,
		rental_id: int,
	) -> tuple[str, str, int]:
		"""
		대여 이미지를 로컬 디스크에 저장합니다.

		Args:
			file: 업로드된 파일
			phase: 이미지 촬영 시점 ('BEFORE' 또는 'AFTER')
			rental_id: 대여 ID (파일명 접두어로 사용)

		Returns:
			(file_path, content_type, file_size) 튜플
		"""
		phase_dir = phase.lower()  # "before" or "after"
		upload_dir = Path(settings.upload_dir) / "rental_images" / phase_dir
		upload_dir.mkdir(parents=True, exist_ok=True)

		original_name = file.filename or "upload"
		ext = Path(original_name).suffix or ".jpg"
		unique_name = f"{rental_id}_{uuid.uuid4().hex}{ext}"
		dest_path = upload_dir / unique_name

		content = file.file.read()
		dest_path.write_bytes(content)

		return (
			str(dest_path),
			file.content_type or "application/octet-stream",
			len(content),
		)
