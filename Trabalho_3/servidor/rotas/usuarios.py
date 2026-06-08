from fastapi import APIRouter, HTTPException
from dependencies import usuarios_instance
from esquemas.sebo import Login
import sys
import os

sys.path.insert(0, os.path.abspath('../../Trabalho_4'))
from evento_broker import publicar_usuario_logado, publicar_usuario_deslogado  # ✨ ADICIONE ISTO

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