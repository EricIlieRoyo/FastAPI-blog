from app.controller.home_controller import router as home_router
from app.controller.post_controller import router as post_router
from app.controller.auth_controller import router as auth_router
from app.controller.admin_controller import router as admin_router

__all__ = ["home_router", "post_router", "auth_router", "admin_router"]
