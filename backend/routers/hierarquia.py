# backend/routers/hierarquia.py
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, HistoricoHierarquia, Inbox
from auth import require_role
from schemas import HierarquiaUpdate
 
router = APIRouter(prefix='/hierarquia', tags=['hierarquia'])
 
# Só a Gestão da Staff (chefes + admins) pode usar estes endpoints
@router.post('/alterar')
def alterar_hierarquia(
    body: HierarquiaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role('chefe', 'admin'))
):
    if not body.justificacao or len(body.justificacao.strip()) < 10:
        raise HTTPException(400, 'Justificação obrigatória (mínimo 10 caracteres)')
 
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(404, 'Utilizador não encontrado')
 
    nivel_antes  = cast(int, user.hierarquia_nivel)
    nivel_depois = body.novo_nivel

    if nivel_depois < 1:
        raise HTTPException(400, 'Nível mínimo é 1')

    # Atualizar o nível
    setattr(user, 'hierarquia_nivel', nivel_depois)
 
    # Guardar no histórico
    hist = HistoricoHierarquia(
        user_id      = body.user_id,
        autor_id     = current_user.id,
        nivel_antes  = nivel_antes,
        nivel_depois = nivel_depois,
        justificacao = body.justificacao
    )
    db.add(hist)
 
    # Notificar o staff afetado
    direcao = 'subiu' if nivel_depois > nivel_antes else 'desceu'
    msg = Inbox(
        destinatario_id = body.user_id,
        remetente_id    = current_user.id,
        tipo            = 'hierarquia',
        titulo          = f'Alteração de hierarquia — Nível {nivel_antes} → {nivel_depois}',
        conteudo        = f'A tua posição na hierarquia {direcao}.\n\nJustificação: {body.justificacao}'
    )
    db.add(msg)
    db.commit()
 
    return {'mensagem': f'{user.username} {direcao} de nível {nivel_antes} para {nivel_depois}'}
 
@router.get('/historico/{user_id}')
def get_historico(user_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role('chefe', 'admin'))):
    hist = db.query(HistoricoHierarquia).filter(
        HistoricoHierarquia.user_id == user_id
    ).order_by(HistoricoHierarquia.created_at.desc()).all()
    return hist
