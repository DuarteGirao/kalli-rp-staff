# backend/routers/avaliacoes.py
from decimal import Decimal
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, GestaoMembro, Avaliacao, Inbox
from auth import get_current_user
from schemas import AvaliacaoCreate
 
router = APIRouter(prefix='/avaliacoes', tags=['avaliacoes'])
 
@router.post('/')
def criar_avaliacao(body: AvaliacaoCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    # Verificar se é chefe da gestão em questão
    is_chefe = db.query(GestaoMembro).filter(
        GestaoMembro.user_id   == current_user.id,
        GestaoMembro.gestao_id == body.gestao_id,
        GestaoMembro.is_chefe  == True
    ).first()
    if not is_chefe:
        raise HTTPException(403, 'Apenas chefes podem avaliar')
 
    # Validar nota
    if not (0 <= body.nota_final <= 20):
        raise HTTPException(400, 'Nota deve estar entre 0 e 20')
 
    # Criar avaliação
    av = Avaliacao(
        avaliador_id = current_user.id,
        avaliado_id  = body.avaliado_id,
        gestao_id    = body.gestao_id,
        nota_final   = body.nota_final,
        comentario   = body.comentario
    )
    db.add(av)
    db.flush()  # obter o id antes do commit
 
    # Enviar mensagem para inbox do avaliado
    avaliado: User | None = db.query(User).filter(User.id == body.avaliado_id).first()
    if avaliado is None:
        raise HTTPException(status_code=404, detail='Utilizador avaliado não encontrado')

    msg = Inbox(
        destinatario_id = body.avaliado_id,
        remetente_id    = current_user.id,
        tipo            = 'avaliacao',
        titulo          = f'Nova avaliação — {body.nota_final:.1f}/20',
        conteudo        = body.comentario or 'Sem comentário adicional.',
        avaliacao_id    = av.id
    )
    db.add(msg)
    db.commit()
 
    return {'mensagem': f'Avaliação enviada para {avaliado.username}', 'id': av.id}
 
@router.get('/membro/{user_id}')
def get_avaliacoes_membro(user_id: int, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    # Só o próprio ou chefes podem ver
    if cast(int, current_user.id) != user_id and current_user.role not in ('chefe', 'admin'):
        raise HTTPException(403, 'Sem permissão')
 
    avaliacoes = db.query(Avaliacao).filter(
        Avaliacao.avaliado_id == user_id
    ).order_by(Avaliacao.created_at.desc()).all()
 
    return [{'id': a.id, 'nota': float(cast(Decimal, a.nota_final)),
             'comentario': a.comentario, 'data': a.created_at}
            for a in avaliacoes]
