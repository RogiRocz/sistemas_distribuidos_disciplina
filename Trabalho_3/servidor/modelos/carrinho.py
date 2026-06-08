from dataclasses import dataclass, field
from typing import Dict
from modelos.produto import Produto

@dataclass
class CarrinhoCompras:
    itens: Dict[str, int] = field(default_factory=dict)

    def adicionar_produtos(self, prod: Produto, qntd: int = 1):
        if prod.codigo in self.itens:
            self.itens[prod.codigo] += qntd
        else:
            self.itens[prod.codigo] = qntd

    def remover_produto(self, codigo_produto: str):
        if codigo_produto in self.itens:
            del self.itens[codigo_produto]

    def listar_itens(self) -> Dict[str, int]:
        return self.itens

    def limpar(self):
        self.itens.clear()