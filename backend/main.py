# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import users, gestoes, avaliacoes, inbox, hierarquia, reports
from starlette.responses import Response
 
app = FastAPI(title='Kalli RP Staff API', version='1.0')
 
# Rate limiting global
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


def _rate_limit_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    raise exc


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
 
# CORS — permite o frontend falar com o backend
app.add_middleware(CORSMiddleware,
    allow_origins=['http://localhost:5500', 'https://o-teu-dominio.com'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
 
# Registar todos os routers
app.include_router(users.router)
app.include_router(gestoes.router)
app.include_router(avaliacoes.router)
app.include_router(inbox.router)
app.include_router(hierarquia.router)
app.include_router(reports.router)
 
@app.get('/')
def root():
    return {'status': 'Kalli RP Staff API online'}
