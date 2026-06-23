# deps package initialization
from app.database.session import get_db

__all__ = ["get_db"]
