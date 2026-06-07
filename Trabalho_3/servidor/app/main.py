from fastapi import FastAPI
from app.rotas import loja_rotas, carrinho_rotas, usuarios_rotas

app = FastAPI(
    title="Sebo Virtual API - Trabalho 3 SD",
    description="Substituição da camada de RMI binária manual por uma API RESTful poliglota.",
    version="1.0.0"
)

# Acoplamento das rotas que manipulam os 3 objetos distribuídos distintos
app.include_router(loja_rotas.router)
app.include_router(carrinho_rotas.router)
app.include_router(usuarios_rotas.router)

@app.get("/")
def raiz():
    return {
        "mensagem": "Servidor do Sebo Virtual Ativo!",
        "documentacao_interativa": "/docs"
    }