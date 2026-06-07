from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from .trocavel import Trocavel


@dataclass
class Produto(Trocavel, ABC):
    codigo: str
    titulo: str
    preco: float

    def __post_init__(self) -> None:
        if not self.codigo.strip():
            raise ValueError("codigo nao pode ser vazio")
        if not self.titulo.strip():
            raise ValueError("titulo nao pode ser vazio")
        if self.preco < 0:
            raise ValueError("preco nao pode ser negativo")

    def pode_trocar(self) -> bool:
        return True

    def trocar(self, novo_produto: object) -> bool:
        return isinstance(novo_produto, Produto)

    @property
    def tipo(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> dict[str, object]:
        return {
            "codigo": self.codigo,
            "titulo": self.titulo,
            "preco": self.preco,
            "tipo": self.tipo,
        }

    def __str__(self) -> str:
        return f"{self.tipo}({self.codigo} - {self.titulo} - R$ {self.preco:.2f})"
