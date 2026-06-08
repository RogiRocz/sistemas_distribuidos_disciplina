from fastapi import APIRouter, HTTPException
from dependencies import usuarios_instance
from esquemas.sebo import Login
import sys
import os

# Partindo de Trabalho_3/servidor/rotas/ para Trabalho_3/Trabalho_4/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRABALHO4_PATH = os.path.abspath(os.path.join(BASE_DIR, "../Trabalho_4"))

if TRABALHO4_PATH not in sys.path:
    sys.path.insert(0, TRABALHO4_PATH)

from evento_broker import broker, TOPICOS, publicar_produto_novo

router = APIRouter(prefix="/usuarios", tags=["Objeto 3: Gerenciador de Usuários"])

@router.post("/login")
def login(schema: Login):
    if not usuarios_instance.autenticar(schema.username, schema.senha):
        raise HTTPException(status_code=401, detail="Falha na autenticação. Credenciais inválidas.")
    publicar_usuario_logado(schema.username)
    return {"status": "Autenticado", "usuario": schema.username}

@router.post("/logout/{username}")
def logout(username: str):
    usuarios_instance.deslogar(username)
    publicar_usuario_deslogado(username)  # ✨ MUDE ISTO (era logado, agora é deslogado)
    return {"status": "Desconectado"}

@router.get("/ativos")
def listar_ativos():
    return {"usuarios_conectados": usuarios_instance.listar_conectados()}