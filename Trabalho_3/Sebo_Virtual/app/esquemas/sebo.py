from pydantic import BaseModel, Field

class ProdutoBase(BaseModel):
    codigo: str
    titulo: str
    preco: float

class LivroCreate(ProdutoBase):
    autor: str
    editora: str
    ano_publicacao: int

class CDCreate(ProdutoBase):
    artista: str
    genero: str

class EbookCreate(ProdutoBase):
    formato: str
    tamanho_mb: float

class ApostilaCreate(ProdutoBase):
    disciplina: str
    instituicao: str

class AtualizarPreco(BaseModel):
    novo_preco: float = Field(..., gte=0, description="O preço não pode ser negativo")

class Login(BaseModel):
    username: str
    senha: str