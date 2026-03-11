# backend/routers/gestoes.py
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, GestaoMembro
from auth import get_current_user
 
router = APIRouter(prefix='/gestoes', tags=['gestoes'])
 
# Ver membros da minha gestão (qualquer staff autenticado)
@router.get('/{gestao_id}/membros')
def get_membros(gestao_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    membros = db.query(GestaoMembro, User).join(
        User, GestaoMembro.user_id == User.id
    ).filter(GestaoMembro.gestao_id == gestao_id).all()
 
    return [{'id': u.id, 'username': u.username,
             'nivel': u.hierarquia_nivel, 'is_chefe': gm.is_chefe}
            for gm, u in membros]
 
# Adicionar membro à gestão (só chefes dessa gestão)
@router.post('/{gestao_id}/membros')
def add_membro(gestao_id: int, user_id: int,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    # Verificar se o utilizador atual é chefe desta gestão
    is_chefe = db.query(GestaoMembro).filter(
        GestaoMembro.user_id   == current_user.id,
        GestaoMembro.gestao_id == gestao_id,
        GestaoMembro.is_chefe  == True
    ).first()
 
    if is_chefe is None and cast(str, current_user.role) != 'admin':
        raise HTTPException(403, 'Apenas chefes desta gestão podem adicionar membros')
 
    # Verificar se já existe
    existe = db.query(GestaoMembro).filter(
        GestaoMembro.user_id   == user_id,
        GestaoMembro.gestao_id == gestao_id
    ).first()
    if existe:
        raise HTTPException(400, 'Utilizador já é membro desta gestão')
 
    novo = GestaoMembro(user_id=user_id, gestao_id=gestao_id)
    db.add(novo)
    db.commit()
    return {'mensagem': 'Membro adicionado com sucesso'}
 
# Remover membro (só chefes)
@router.delete('/{gestao_id}/membros/{user_id}')
def remove_membro(gestao_id: int, user_id: int,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    is_chefe = db.query(GestaoMembro).filter(
        GestaoMembro.user_id   == current_user.id,
        GestaoMembro.gestao_id == gestao_id,
        GestaoMembro.is_chefe  == True
    ).first()
    if is_chefe is None and cast(str, current_user.role) != 'admin':
        raise HTTPException(403, 'Sem permissão')
 
    membro = db.query(GestaoMembro).filter(
        GestaoMembro.user_id   == user_id,
        GestaoMembro.gestao_id == gestao_id
    ).first()
    if not membro:
        raise HTTPException(404, 'Membro não encontrado')
 
    db.delete(membro)
    db.commit()
    return {'mensagem': 'Membro removido'}
