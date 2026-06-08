from dataclasses import dataclass

@dataclass
class GerenciadorUsuarios:
    def __init__(self):
        # Usuários e senhas mockados na infraestrutura
        self.credenciais = {
            "admin": "admin123",
            "aluno": "ufc2026"
        }
        self.usuarios_ativos = set()

    def autenticar(self, username: str, senha: str) -> bool:
        if self.credenciais.get(username) == senha:
            self.usuarios_ativos.add(username)
            return True
        return False

    def deslogar(self, username: str):
        self.usuarios_ativos.discard(username)

    def listar_conectados(self) -> list:
        return list(self.usuarios_ativos)