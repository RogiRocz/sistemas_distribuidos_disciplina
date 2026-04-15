from __future__ import annotations

from dataclasses import dataclass

from .produto import Produto


@dataclass
class Ebook(Produto):
    formato: str = "PDF"
    tamanho_mb: float | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.formato.strip():
            raise ValueError("formato nao pode ser vazio")
