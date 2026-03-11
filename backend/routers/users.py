# backend/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, timezone
from typing import cast

from auth import create_access_token, create_refresh_token
from auth import get_current_user, verify_password
from database import get_db
from models import User
from schemas import AuthUser, LoginRequest, MeResponse, TokenResponse
 
router  = APIRouter(prefix='/auth', tags=['auth'])
limiter = Limiter(key_func=get_remote_address)
 
@router.post('/login', response_model=TokenResponse)
@limiter.limit('5/15minutes')   # pyright: ignore[reportUnknownMemberType, reportUntypedFunctionDecorator]
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # 1. Procurar utilizador
    user: User | None = db.query(User).filter(
        User.username == body.username,
        User.ativo == True
    ).first()
 
    # 2. Verificar password (mesmo se user não existe, para evitar timing attacks)
    if not user or not verify_password(body.password, cast(str, user.password_hash)):
        raise HTTPException(status_code=401, detail='Credenciais inválidas')
 
    # 3. Atualizar last_login
    setattr(user, 'last_login', datetime.now(timezone.utc))
    db.commit()
 
    # 4. Gerar tokens
    access  = create_access_token({'sub': str(user.id)})
    refresh = create_refresh_token({'sub': str(user.id)})

    user_id = cast(int, user.id)
    username = cast(str, user.username)
    role = cast(str, user.role)
    nivel = cast(int, user.hierarquia_nivel)
 
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type='bearer',
        user=AuthUser(id=user_id, username=username, role=role, nivel=nivel),
    )
 
@router.get('/me', response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> MeResponse:
    user_id = cast(int, current_user.id)
    username = cast(str, current_user.username)
    role = cast(str, current_user.role)
    nivel = cast(int, current_user.hierarquia_nivel)

    return MeResponse(
        id=user_id,
        username=username,
        role=role,
        nivel=nivel,
    )
