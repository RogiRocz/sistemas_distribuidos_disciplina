from fastapi import APIRouter, HTTPException
from app.dependencies import usuarios_instance
from app.esquemas.sebo import Login

router = APIRouter(prefix="/usuarios", tags=["Objeto 3: Gerenciador de Usuários"])

@router.post("/login")
def login(schema: Login):
    if not usuarios_instance.autenticar(schema.username, schema.senha):
        raise HTTPException(status_code=401, detail="Falha na autenticação. Credenciais inválidas.")
    return {"status": "Autenticado", "usuario": schema.username}

@router.post("/logout/{username}")
def logout(username: str):
    usuarios_instance.deslogar(username)
    return {"status": "Desconectado"}

@router.get("/ativos")
def listar_ativos():
    return {"usuarios_conectados": usuarios_instance.listar_conectados()}