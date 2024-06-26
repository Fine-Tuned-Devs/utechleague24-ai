from pydantic import BaseModel


class TokenRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class ProcessRequest(BaseModel):
    input_text: str
