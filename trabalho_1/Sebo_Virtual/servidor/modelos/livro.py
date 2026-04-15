from __future__ import annotations

from dataclasses import dataclass

from .produto import Produto


@dataclass
class Livro(Produto):
    autor: str = ""
    editora: str = ""
    ano_publicacao: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.autor.strip():
            raise ValueError("autor nao pode ser vazio")
