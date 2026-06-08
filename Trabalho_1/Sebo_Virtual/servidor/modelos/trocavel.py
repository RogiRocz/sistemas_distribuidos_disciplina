from __future__ import annotations

from abc import ABC, abstractmethod


class Trocavel(ABC):
    """Contrato para produtos que podem ser trocados."""

    @abstractmethod
    def pode_trocar(self) -> bool:
        """Indica se o produto aceita troca."""

    @abstractmethod
    def trocar(self, novo_produto: object) -> bool:
        """Realiza a troca com outro produto."""
