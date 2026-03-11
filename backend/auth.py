# backend/auth.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

try:
    from .database import get_db
    from .models import User
except ImportError:
    from database import get_db
    from models import User

ph = PasswordHasher()  # usa Argon2id por defeito
 
_secret_key = os.getenv('SECRET_KEY')
ALGORITHM  = os.getenv('ALGORITHM', 'HS256')
ACCESS_EXPIRE  = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
REFRESH_EXPIRE = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

if not _secret_key:
    raise RuntimeError('SECRET_KEY não definida no ambiente (.env)')

SECRET_KEY: str = _secret_key
 
bearer_scheme = HTTPBearer()
 
# ── Funções de hash ──────────────────────────────────────────
def hash_password(password: str) -> str:
    return ph.hash(password)
 
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
 
# ── Funções JWT ───────────────────────────────────────────────
def create_access_token(data: dict[str, Any]) -> str:
    to_encode: dict[str, Any] = data.copy()
    to_encode['exp'] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRE)
    to_encode['type'] = 'access'
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 
def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode: dict[str, Any] = data.copy()
    to_encode['exp'] = datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE)
    to_encode['type'] = 'refresh'
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 
# ── Dependência para proteger endpoints ───────────────────────
# Usa assim num endpoint: current_user = Depends(get_current_user)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'access':
            raise HTTPException(status_code=401, detail='Token inválido')

        raw_user_id = payload.get('sub')
        if raw_user_id is None:
            raise HTTPException(status_code=401, detail='Token inválido')

        user_id = int(raw_user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail='Token expirado ou inválido')
    except ValueError:
        raise HTTPException(status_code=401, detail='Token inválido')
 
    user = db.query(User).filter(User.id == user_id, User.ativo == True).first()
    if not user:
        raise HTTPException(status_code=401, detail='Utilizador não encontrado')
    return user
 
# ── Dependência: requer role específica ───────────────────────
# Uso: current_user = Depends(require_role('admin'))
def require_role(*roles: str) -> Callable[..., User]:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail='Sem permissão')
        return current_user
    return checker
