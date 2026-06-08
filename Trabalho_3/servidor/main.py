import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rotas import loja, carrinho, usuarios
from evento_broker import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
TRABALHO4_DIR = os.path.abspath(os.path.join(BASE_DIR, "../Trabalho_4"))

if TRABALHO4_DIR not in sys.path:
    sys.path.insert(0, TRABALHO4_DIR)

app = FastAPI(
    title="Sebo Virtual API - Trabalho 3 SD",
    description="API REST com Pub/Sub em Redis",
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
        "service": "Sebo Virtual API",
        "version": "1.0.0"
    }

@app.get("/")
def raiz():
    return {
        "mensagem": "Servidor do Sebo Virtual Ativo!",
        "docs": "/docs",
        "health": "/health"
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