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
    
    def to_dict(self) -> dict[str, object]:
        data = super().to_dict()
        data.update({
            "disciplina": self.disciplina,
            "instituicao": self.instituicao
        })
        return data
