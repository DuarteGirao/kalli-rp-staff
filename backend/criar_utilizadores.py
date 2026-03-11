# backend/criar_utilizadores.py
# USAR APENAS UMA VEZ para criar os utilizadores iniciais
 
from sqlalchemy.orm import Session

from auth import hash_password
from database import SessionLocal
from models import Gestao, GestaoMembro, User
 
db: Session = SessionLocal()
 
utilizadores = [
    {'username': 'm1saki',  'password': '123456789', 'role': 'chefe'},
    {'username': 'quim',    'password': '123456789', 'role': 'chefe'},
    {'username': 'welel',   'password': '123456789', 'role': 'chefe'},
    {'username': 'larah',   'password': '123456789', 'role': 'chefe'},
    {'username': 'costa',   'password': '123456789', 'role': 'chefe'},
    {'username': 'tokito',   'password': '123456789', 'role': 'chefe'},
    {'username': 'dark',   'password': '123456789', 'role': 'chefe'},
]
 
for u in utilizadores:
    user = User(
        username=u['username'],
        password_hash=hash_password(u['password']),
        role=u['role']
    )
    db.add(user)
 
db.commit()
print('Utilizadores criados com sucesso!')
 
# Depois de criar os users, associa-os às gestões:
# gestao_ids: 1=Orgs, 2=Handlings, 3=Dev, 4=POVs, 5=Conteúdos, 6=Staff
associacoes = [
    ('m1saki', 1, True),   # M1saki é chefe de Orgs
    ('m1saki', 6, True),   # M1saki é chefe de Staff
    ('quim',   1, True),   # Quim é chefe de Orgs
    ('welel',  2, True),
    ('larah',  3, True),
    ('larah',  6, True),
    ('costa',  4, True),
    ('costa',  5, True),
    ('tokito', 6, True),
    ('dark', 6, True),
]
 
for username, gestao_id, is_chefe in associacoes:
    user: User | None = db.query(User).filter(User.username == username).first()
    gestao: Gestao | None = db.query(Gestao).filter(Gestao.id == gestao_id).first()

    if user is None or gestao is None:
        continue

    membro = GestaoMembro(user_id=user.id, gestao_id=gestao.id, is_chefe=is_chefe)
    db.add(membro)
 
db.commit()
print('Associações feitas!')
db.close()
