import os
import sys

# 1. CONFIGURAÇÃO DE CAMINHOS REAIS (Baseado em Trabalho_4 dentro de Trabalho_3)
# BASE_DIR será: .../Trabalho_3/servidor
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# TRABALHO4_DIR aponta para: .../Trabalho_3/Trabalho_4
TRABALHO4_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Trabalho_4"))

# injeta a pasta atual (servidor) e a do Trabalho_4 no path do interpretador
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if TRABALHO4_DIR not in sys.path:
    sys.path.insert(0, TRABALHO4_DIR)

# 2. IMPORTS DO FRAMEWORK
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 3. IMPORTS DO PROJETO (Trabalho 3 e Trabalho 4)
from rotas import usuarios, carrinho, loja

# O import direto agora funciona porque TRABALHO4_DIR está no sys.path
try:
    from evento_broker import publicar_usuario_logado, publicar_carrinho_finalizado
    import eventos
    eventos_router = eventos.router
    pubsub_disponivel = True
except ImportError as e:
    print(f"⚠️ Aviso: Módulo de eventos/broker não disponível: {e}")
    pubsub_disponivel = False

# 4. INICIALIZAÇÃO DA API
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

# Rotas principais (Trabalho 3)
app.include_router(loja.router)
app.include_router(carrinho.router)
app.include_router(usuarios.router)

# Rotas de Pub/Sub (Trabalho 4)
if pubsub_disponivel:
    app.include_router(eventos_router)
    print("✓ Pub/Sub (Trabalho 4) integrado com sucesso")


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
        "/health"
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
    status_pubsub = "✓ Ativo" if pubsub_disponivel else "✗ Inativo"
    
    return {
        "mensagem": "Servidor do Sebo Virtual Ativo!",
        "documentacao_interativa": "/docs",
        "healthcheck": "/health",
        "api_info": "/api/info",
        "pubsub_status": status_pubsub
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )