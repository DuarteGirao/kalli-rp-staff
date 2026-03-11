from pydantic import BaseModel


class LoginRequest(BaseModel):
	username: str
	password: str


class AuthUser(BaseModel):
	id: int
	username: str
	role: str
	nivel: int


class TokenResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str
	user: AuthUser


class MeResponse(BaseModel):
	id: int
	username: str
	role: str
	nivel: int
