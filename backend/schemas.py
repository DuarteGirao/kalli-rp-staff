from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    id: int
    username: str
    role: str
    nivel: int


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str
    user:          AuthUser


class MeResponse(BaseModel):
    id: int
    username: str
    role: str
    nivel: int


class RefreshRequest(BaseModel):
    refresh_token: str


class AvaliacaoCreate(BaseModel):
    avaliado_id: int
    gestao_id:   int
    nota_final:  float
    comentario:  str | None = None

    @field_validator('nota_final')
    @classmethod
    def nota_valida(cls, v: float) -> float:
        if not (0 <= v <= 20):
            raise ValueError('Nota deve estar entre 0 e 20')
        return round(v, 2)


class HierarquiaUpdate(BaseModel):
    user_id:      int
    novo_nivel:   int
    justificacao: str

    @field_validator('justificacao')
    @classmethod
    def just_minimo(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError('Justificação precisa de pelo menos 10 caracteres')
        return v
