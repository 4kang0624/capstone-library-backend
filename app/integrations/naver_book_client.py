from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import settings


class NaverBookClientError(Exception):
	"""Base exception for Naver book client errors."""


class NaverBookTimeoutError(NaverBookClientError):
	"""Raised when the request to Naver API times out."""


class NaverBookRequestError(NaverBookClientError):
	"""Raised when Naver API request fails or returns invalid response."""

	def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None) -> None:
		super().__init__(message)
		self.status_code = status_code
		self.response_body = response_body


@dataclass(frozen=True)
class NaverBookClient:
	"""Simple Naver Book Search API client.

	Returns raw Naver response JSON before any normalization.
	"""

	client_id: str
	client_secret: str
	request_timeout: float = 5.0
	base_url: str = "https://openapi.naver.com/v1/search"

	def __post_init__(self) -> None:
		if not self.client_id:
			raise ValueError("Naver client_id is required")
		if not self.client_secret:
			raise ValueError("Naver client_secret is required")

	def search_by_keyword(
		self,
		keyword: str,
		display: int = 10,
		start: int = 1,
		sort: str = "sim",
	) -> dict[str, Any]:
		"""Search books by keyword.

		Naver endpoint: /book.json
		"""

		if not keyword or not keyword.strip():
			raise ValueError("keyword is required")

		params = {
			"query": keyword.strip(),
			"display": display,
			"start": start,
			"sort": sort,
		}
		return self._request("book.json", params)

	def search_by_isbn(
		self,
		isbn: str,
		display: int = 10,
		start: int = 1,
		sort: str = "sim",
	) -> dict[str, Any]:
		"""Search books by ISBN using advanced search endpoint.

		Naver endpoint: /book_adv.json with d_isbn
		"""

		if not isbn or not isbn.strip():
			raise ValueError("isbn is required")

		params = {
			"d_isbn": isbn.strip(),
			"display": display,
			"start": start,
			"sort": sort,
		}
		return self._request("book_adv.json", params)

	def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
		query = urlencode(params)
		url = f"{self.base_url}/{endpoint}?{query}"

		req = Request(
			url=url,
			headers={
				"X-Naver-Client-Id": self.client_id,
				"X-Naver-Client-Secret": self.client_secret,
			},
			method="GET",
		)

		try:
			with urlopen(req, timeout=self.request_timeout) as res:
				status_code = getattr(res, "status", None)
				raw_body = res.read().decode("utf-8")
		except HTTPError as exc:
			body = ""
			try:
				body = exc.read().decode("utf-8")
			except Exception:
				body = ""
			raise NaverBookRequestError(
				message=f"Naver API request failed with status {exc.code}",
				status_code=exc.code,
				response_body=body,
			) from exc
		except (socket.timeout, TimeoutError) as exc:
			raise NaverBookTimeoutError(
				f"Naver API request timed out after {self.request_timeout} seconds"
			) from exc
		except URLError as exc:
			if isinstance(exc.reason, socket.timeout):
				raise NaverBookTimeoutError(
					f"Naver API request timed out after {self.request_timeout} seconds"
				) from exc
			raise NaverBookRequestError(f"Failed to call Naver API: {exc.reason}") from exc

		try:
			payload = json.loads(raw_body)
		except json.JSONDecodeError as exc:
			raise NaverBookRequestError(
				message="Naver API returned invalid JSON",
				status_code=status_code,
				response_body=raw_body,
			) from exc

		if isinstance(payload, dict) and payload.get("errorCode"):
			raise NaverBookRequestError(
				message=f"Naver API error: {payload.get('errorMessage', 'unknown error')}",
				status_code=status_code,
				response_body=raw_body,
			)

		return payload


def create_naver_book_client_from_settings() -> NaverBookClient:
	"""Build a NaverBookClient from environment-backed app settings."""

	settings.validate_naver()
	return NaverBookClient(
		client_id=settings.naver_client_id or "",
		client_secret=settings.naver_client_secret or "",
		request_timeout=settings.naver_book_api_timeout,
	)
