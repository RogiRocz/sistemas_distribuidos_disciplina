import os
import sys

# Garante a raiz do projeto e o servidor do Trabalho 3 no PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.abspath(os.path.join(BASE_DIR, ".."))
TRABALHO3_DIR = os.path.join(RAIZ_PROJETO, "Trabalho_3", "servidor")
TRABALHO4_DIR = os.path.join(RAIZ_PROJETO, "Trabalho_4")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if TRABALHO3_DIR not in sys.path:
    sys.path.insert(0, TRABALHO3_DIR)
if TRABALHO4_DIR not in sys.path:
    sys.path.insert(0, TRABALHO4_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rotas import usuarios, carrinho, loja 
from evento_broker import publicar_usuario_logado, publicar_carrinho_finalizado

app = FastAPI(
    title="Sebo Virtual API - Trabalho 4 SD",
    description="Barramento de Eventos com Redis Pub/Sub.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "service": "Sebo Virtual API - Eventos",
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
        "mensagem": "Servidor do Sebo Virtual (Trabalho 4) Ativo!",
        "documentacao_interativa": "/docs",
        "healthcheck": "/health",
        "api_info": "/api/info"
    }