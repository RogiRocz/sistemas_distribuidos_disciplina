from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.rotas import loja, carrinho, usuarios

app = FastAPI(
    title="Sebo Virtual API - Trabalho 3 SD",
    description="Substituição da camada de RMI binária manual por uma API RESTful poliglota.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite qualquer origem (para teste local)
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loja.router)
app.include_router(carrinho.router)
app.include_router(usuarios.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Sebo Virtual API",
        "version": "1.0.0"
    }


@app.get("/api/info")
def api_info():
    return {
        "titulo": app.title,
        "versao": app.version,
        "docs": "/docs",
        "endpoints_principais": [
            "/loja",
            "/carrinho",
            "/usuarios",
            "/health"
        ]
    }


@app.get("/")
def raiz():
    return {
        "mensagem": "Servidor do Sebo Virtual Ativo!",
        "documentacao_interativa": "/docs",
        "healthcheck": "/health",
        "api_info": "/api/info"
    }