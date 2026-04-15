from __future__ import annotations

from dataclasses import dataclass

from .produto import Produto


@dataclass
class Apostila(Produto):
    disciplina: str = ""
    instituicao: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.disciplina.strip():
            raise ValueError("disciplina nao pode ser vazia")
