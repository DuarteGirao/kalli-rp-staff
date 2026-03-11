# backend/routers/reports.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Inbox
from auth import get_current_user
 
router = APIRouter(prefix='/inbox', tags=['inbox'])
 
# Ver todas as mensagens do utilizador atual
@router.get('/')
def get_inbox(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    mensagens = db.query(Inbox).filter(
        Inbox.destinatario_id == current_user.id
    ).order_by(Inbox.created_at.desc()).all()
 
    return [{'id': m.id, 'tipo': m.tipo, 'titulo': m.titulo,
             'conteudo': m.conteudo, 'lida': m.lida,
             'data': m.created_at} for m in mensagens]
 
# Verificar se há mensagens não lidas (para o pop-up do login)
@router.get('/nao-lidas/count')
def count_nao_lidas(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    count = db.query(Inbox).filter(
        Inbox.destinatario_id == current_user.id,
        Inbox.lida == False
    ).count()
    return {'count': count}
 
# Marcar mensagem como lida
@router.patch('/{msg_id}/lida')
def marcar_lida(msg_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    msg = db.query(Inbox).filter(
        Inbox.id == msg_id,
        Inbox.destinatario_id == current_user.id
    ).first()
    if msg:
        setattr(msg, 'lida', True)
        db.commit()
    return {'ok': True}
