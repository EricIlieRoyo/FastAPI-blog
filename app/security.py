import hashlib
import secrets
from typing import Optional
from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.entity.user import User


def hash_password(password: str) -> str:
    """Genera un hash seguro PBKDF2 con sal criptográfica."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash almacenado."""
    try:
        salt, key_hex = hashed_password.split("$", 1)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Obtiene el usuario actual de la sesión si está autenticado."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    from app.repository.user_repository import UserRepository
    user_repo = UserRepository(db)
    return user_repo.get_by_id(user_id)


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """Valida que el usuario actual haya iniciado sesión y tenga rol de administrador."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login?next=" + request.url.path}
        )
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido: Solo administradores pueden ingresar a este panel."
        )
    return user
