from fastapi import APIRouter

from app.routers.user.auth import router as auth_router
from app.routers.user.users import router as users_router
from app.routers.user.admin import router as admin_router
from app.routers.user.wallet import router as wallet_router
from app.routers.library.books import router as books_router
from app.routers.library.book_copies import router as book_copies_router
from app.routers.library.reading_logs import router as reading_logs_router
from app.routers.library.wishlists import router as wishlists_router
from app.routers.library.bookmarks import router as bookmarks_router
from app.routers.search.search import router as search_router
from app.routers.rental.rentals import router as rentals_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
api_router.include_router(wallet_router)
api_router.include_router(books_router)
api_router.include_router(book_copies_router)
api_router.include_router(reading_logs_router)
api_router.include_router(wishlists_router)
api_router.include_router(bookmarks_router)
api_router.include_router(search_router)
api_router.include_router(rentals_router)

