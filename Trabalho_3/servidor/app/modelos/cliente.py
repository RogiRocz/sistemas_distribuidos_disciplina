"""Cliente - Modelo que representa um cliente da loja."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Cliente:
    """Cliente da loja (agregação: tem um carrinho).
    
    Attributes:
        id: Identificador único do cliente
        nome: Nome do cliente
        email: Email do cliente
        carrinho: Carrinho de compras (agregação)
    """
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
    """Carrinho de compras de um cliente (agregação de produtos).
    
    Attributes:
        itens: Dicionário {codigo_produto: quantidade}
        valor_total: Valor total do carrinho
    """
    itens: dict[str, int] = field(default_factory=dict)
    valor_total: float = 0.0

    def adicionar_item(self, codigo_produto: str, quantidade: int = 1) -> None:
        """Adiciona um item ao carrinho."""
        if codigo_produto in self.itens:
            self.itens[codigo_produto] += quantidade
        else:
            self.itens[codigo_produto] = quantidade

    def remover_item(self, codigo_produto: str) -> bool:
        """Remove um item do carrinho."""
        if codigo_produto in self.itens:
            del self.itens[codigo_produto]
            return True
        return False

    def limpar(self) -> None:
        """Limpa o carrinho."""
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
