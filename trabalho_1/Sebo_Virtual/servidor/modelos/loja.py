from __future__ import annotations

from dataclasses import dataclass, field

from .produto import Produto


@dataclass
class Loja:
    nome: str
    estoque: list[Produto] = field(default_factory=list)

    def adicionar_produto(self, produto: Produto) -> None:
        self.estoque.append(produto)

    def listar_produtos(self) -> list[Produto]:
        return list(self.estoque)

    def buscar_por_codigo(self, codigo: str) -> Produto | None:
        for produto in self.estoque:
            if produto.codigo == codigo:
                return produto
        return None

    def buscar_por_titulo(self, titulo: str) -> list[Produto]:
        termo = titulo.lower().strip()
        return [produto for produto in self.estoque if termo in produto.titulo.lower()]

    def remover_produto(self, codigo: str) -> Produto | None:
        produto = self.buscar_por_codigo(codigo)
        if produto is None:
            return None
        self.estoque.remove(produto)
        return produto

    def produtos_trocaveis(self) -> list[Produto]:
        return [produto for produto in self.estoque if produto.pode_trocar()]
