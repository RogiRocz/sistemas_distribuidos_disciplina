from dataclasses import dataclass, field
from .produto import Produto

@dataclass
class Loja:
    nome: str
    estoque: dict = field(default_factory=dict)

    def adicionar_produto(self, produto: Produto):
        self.estoque[produto.codigo] = produto

    def listar_produtos(self):
        return list(self.estoque.values())

    def buscar_por_codigo(self, codigo: str):
        return self.estoque.get(codigo)

    def buscar_por_titulo(self, titulo: str):
        return [p for p in self.estoque.values() if titulo.lower() in p.titulo.lower()]

    def remover_produto(self, codigo: str):
        return self.estoque.pop(codigo, None)

    def produtos_trocaveis(self):
        return [p for p in self.estoque.values() if p.pode_trocar()]