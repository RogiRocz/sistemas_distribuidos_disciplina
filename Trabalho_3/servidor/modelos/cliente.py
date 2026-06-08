from __future__ import annotations
from dataclasses import dataclass, field
@dataclass
class Cliente:
    id: str
    nome: str
    email: str
    carrinho: Carrinho = field(default_factory=lambda: Carrinho())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "carrinho": self.carrinho.to_dict()
        }

    @staticmethod
    def from_dict(data: dict) -> Cliente:
        carrinho_data = data.get("carrinho", {})
        carrinho = Carrinho.from_dict(carrinho_data) if carrinho_data else Carrinho()
        return Cliente(
            id=data["id"],
            nome=data["nome"],
            email=data["email"],
            carrinho=carrinho
        )

    def __str__(self) -> str:
        return f"Cliente({self.id} - {self.nome} - {self.email})"


@dataclass
class Carrinho:
    itens: dict[str, int] = field(default_factory=dict)
    valor_total: float = 0.0

    def adicionar_item(self, codigo_produto: str, quantidade: int = 1) -> None:
        if codigo_produto in self.itens:
            self.itens[codigo_produto] += quantidade
        else:
            self.itens[codigo_produto] = quantidade

    def remover_item(self, codigo_produto: str) -> bool:
        if codigo_produto in self.itens:
            del self.itens[codigo_produto]
            return True
        return False

    def limpar(self) -> None:
        self.itens.clear()
        self.valor_total = 0.0

    def to_dict(self) -> dict:
        return {
            "itens": self.itens,
            "valor_total": self.valor_total
        }

    @staticmethod
    def from_dict(data: dict) -> Carrinho:
        return Carrinho(
            itens=data.get("itens", {}),
            valor_total=data.get("valor_total", 0.0)
        )

    def __str__(self) -> str:
        return f"Carrinho(itens={len(self.itens)}, total=R${self.valor_total:.2f})"
