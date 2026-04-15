from __future__ import annotations

from dataclasses import dataclass

from .produto import Produto


@dataclass
class CD(Produto):
    artista: str = ""
    genero: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.artista.strip():
            raise ValueError("artista nao pode ser vazio")
