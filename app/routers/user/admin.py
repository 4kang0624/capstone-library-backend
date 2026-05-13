from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/")
def admin_test():
    return {"message": "Admin router is working!"}