# backend/routers/reports.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any
from database import get_db
from models import User, ReportTicket
from auth import get_current_user, require_role
import pandas as pd
import io
 
router = APIRouter(prefix='/reports', tags=['reports'])
 
# Estatísticas do utilizador atual (para o dashboard)
@router.get('/stats/me')
def my_stats(db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    from datetime import date
    hoje  = date.today()
    mes_atual = hoje.replace(day=1)
 
    # Reports e tickets do mês atual
    stats = db.query(
        ReportTicket.tipo,
        func.sum(ReportTicket.quantidade).label('total')
    ).filter(
        ReportTicket.user_id == current_user.id,
        ReportTicket.periodo >= mes_atual
    ).group_by(ReportTicket.tipo).all()
 
    result: dict[str, Any] = {'reports': 0, 'tickets': 0}
    for tipo, total in stats:
        result[tipo + 's'] = int(total)
 
    # Histórico dos últimos 6 meses (para gráfico de linha)
    historico = db.query(
        ReportTicket.periodo,
        ReportTicket.tipo,
        func.sum(ReportTicket.quantidade).label('total')
    ).filter(
        ReportTicket.user_id == current_user.id
    ).group_by(ReportTicket.periodo, ReportTicket.tipo
    ).order_by(ReportTicket.periodo).all()
 
    result['historico'] = [{'periodo': str(h.periodo),
                            'tipo': h.tipo, 'total': int(h.total)}
                           for h in historico]
    return result
 
# Import CSV — só Gestão da Staff
@router.post('/import')
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role('chefe', 'admin'))
):
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(400, 'Apenas ficheiros .csv são aceites')
 
    conteudo = await file.read()
    try:
        df = pd.read_csv(io.StringIO(conteudo.decode('utf-8')))
    except Exception:
        raise HTTPException(400, 'Erro ao ler CSV. Verifica o formato.')
 
    # Colunas esperadas: username, tipo, quantidade, periodo
    colunas = {'username', 'tipo', 'quantidade', 'periodo'}
    if not colunas.issubset(df.columns):
        raise HTTPException(400, f'CSV precisa das colunas: {colunas}')
 
    erros, inseridos = [], 0
    for _, row in df.iterrows():
        user = db.query(User).filter(User.username == row['username']).first()
        if not user:
            erros.append(f'Utilizador não encontrado: {row["username"]}')
            continue
        rt = ReportTicket(
            user_id    = user.id,
            tipo       = row['tipo'],
            quantidade = int(row['quantidade']),
            periodo    = row['periodo']
        )
        db.add(rt)
        inseridos += 1
 
    db.commit()
    return {'inseridos': inseridos, 'erros': erros}
