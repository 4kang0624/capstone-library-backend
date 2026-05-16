from typing import Any

from app.integrations.naver_book_client import create_naver_book_client_from_settings


class SearchService:
	"""네이버 책 검색 서비스"""

	@staticmethod
	def search_by_keyword(keyword: str) -> dict[str, Any]:
		"""키워드로 책 검색"""
		client = create_naver_book_client_from_settings()
		return client.search_by_keyword(keyword=keyword)

	@staticmethod
	def search_by_isbn(isbn: str) -> dict[str, Any]:
		"""ISBN으로 책 검색"""
		client = create_naver_book_client_from_settings()
		return client.search_by_isbn(isbn=isbn)
