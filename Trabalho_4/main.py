import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
TRABALHO3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Trabalho_3", "servidor"))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if TRABALHO3_DIR not in sys.path:
    sys.path.insert(0, TRABALHO3_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rotas import usuarios, carrinho, loja

try:
    from evento_broker import (
        publicar_usuario_logado, 
        publicar_carrinho_finalizado, 
        publicar_carrinho_alterado
    )
    import eventos as eventos
    eventos_router = eventos.router
    pubsub_disponivel = True
except ImportError as e:
    print(f" Aviso: Módulo de eventos/broker não disponível: {e}")
    pubsub_disponivel = False

app = FastAPI(
    title="Sebo Virtual API - Trabalho 3 SD",
    description="Substituição da camada de RMI binária manual por uma API RESTful poliglota com Pub/Sub.",
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

if pubsub_disponivel:
    app.include_router(eventos_router)
    print(" Pub/Sub (Trabalho 4) integrado com sucesso")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Sebo Virtual API",
        "version": "1.0.0",
        "pubsub": "ativo" if pubsub_disponivel else "inativo"
    }


@app.get("/api/info")
def api_info():
    endpoints = [
        "/loja",
        "/carrinho",
        "/usuarios",
        "/health",
        "/carrinho"
    ]
    
    if pubsub_disponivel:
        endpoints.extend([
            "/ws/eventos (WebSocket)",
            "/ws/eventos/status"
        ])
    
    return {
        "titulo": app.title,
        "versao": app.version,
        "docs": "/docs",
        "pubsub_ativo": pubsub_disponivel,
        "endpoints_principais": endpoints
    }


@app.get("/")
def raiz():
    status_pubsub = " Ativo" if pubsub_disponivel else "✗ Inativo"
    
    return {
        "mensagem": "Servidor do Sebo Virtual Ativo!",
        "documentacao_interativa": "/docs",
        "healthcheck": "/health",
        "api_info": "/api/info",
        "pubsub_status": status_pubsub
    }

if __name__ == "__main__":    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )