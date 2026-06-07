from __future__ import annotations

from dataclasses import dataclass, field

from .produto import Produto


@dataclass
class Loja:
    nome: str
    estoque: dict = field(default_factory=dict)

    def adicionar_produto(self, produto: Produto) -> None:
        self.estoque[produto.codigo] = produto

    def listar_produtos(self):
        return self.estoque

    def buscar_por_codigo(self, codigo: str) -> Produto | None:
        return self.estoque.get(codigom, None)

    def buscar_por_titulo(self, titulo: str):
       return [p for p in self.produtos.values() if titulo.lower() in p.titulo.lower()]

    def remover_produto(self, codigo: str) -> Produto | None:
        return self.produtos.pop(codigo, None)

    def produtos_trocaveis(self):
		return [p for p in self.produtos.values() if p.pode_trocar()]