# backend/models.py
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy import Enum, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func

try:
    from .database import Base
except ImportError:
    from database import Base

class User(Base):
    __tablename__ = 'users'
    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String(50), unique=True, nullable=False)
    password_hash    = Column(String(255), nullable=False)
    display_name     = Column(String(100))
    role             = Column(Enum('staff','chefe','admin'), default='staff')
    hierarquia_nivel = Column(Integer, default=1)
    ativo            = Column(Boolean, default=True)
    created_at       = Column(DateTime, server_default=func.now())
    last_login       = Column(DateTime, nullable=True)
 
class Gestao(Base):
    __tablename__ = 'gestoes'
    id   = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
 
class GestaoMembro(Base):
    __tablename__ = 'gestao_membros'
    id        = Column(Integer, primary_key=True)
    user_id   = Column(Integer, ForeignKey('users.id'), nullable=False)
    gestao_id = Column(Integer, ForeignKey('gestoes.id'), nullable=False)
    is_chefe  = Column(Boolean, default=False)
    joined_at = Column(DateTime, server_default=func.now())
 
class Avaliacao(Base):
    __tablename__ = 'avaliacoes'
    id           = Column(Integer, primary_key=True)
    avaliador_id = Column(Integer, ForeignKey('users.id'))
    avaliado_id  = Column(Integer, ForeignKey('users.id'))
    gestao_id    = Column(Integer, ForeignKey('gestoes.id'))
    nota_final   = Column(Numeric(4,2), nullable=False)
    comentario   = Column(Text)
    created_at   = Column(DateTime, server_default=func.now())
 
class Inbox(Base):
    __tablename__ = 'inbox'
    id              = Column(Integer, primary_key=True)
    destinatario_id = Column(Integer, ForeignKey('users.id'))
    remetente_id    = Column(Integer, ForeignKey('users.id'), nullable=True)
    tipo            = Column(Enum('avaliacao','hierarquia','sistema'))
    titulo          = Column(String(200))
    conteudo        = Column(Text)
    avaliacao_id    = Column(Integer, ForeignKey('avaliacoes.id'), nullable=True)
    lida            = Column(Boolean, default=False)
    created_at      = Column(DateTime, server_default=func.now())
 
class ReportTicket(Base):
    __tablename__ = 'reports_tickets'
    id           = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey('users.id'))
    tipo         = Column(Enum('report','ticket'))
    quantidade   = Column(Integer, default=0)
    periodo      = Column(Date)
    importado_em = Column(DateTime, server_default=func.now())
 
class HistoricoHierarquia(Base):
    __tablename__ = 'historico_hierarquia'
    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey('users.id'))
    autor_id      = Column(Integer, ForeignKey('users.id'))
    nivel_antes   = Column(Integer)
    nivel_depois  = Column(Integer)
    justificacao  = Column(Text, nullable=False)
    created_at    = Column(DateTime, server_default=func.now())
