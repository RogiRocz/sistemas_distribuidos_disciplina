from __future__ import annotations

import io
import struct
from typing import BinaryIO, Sequence

try:
    from .servidor.modelos.livro import Livro
except ImportError:
    try:
        from servidor.modelos.livro import Livro
    except ImportError:
        from Sebo_Virtual.servidor.modelos.livro import Livro


class LivroInputStream(io.RawIOBase):
    
    """Stream de entrada para ler um conjunto de livros em formato binario.

    Protocolo utilizado:
    - 4 bytes: quantidade de objetos enviados (unsigned int, big-endian)
    - Para cada livro:
      - Para cada atributo serializado:
        - 4 bytes: tamanho do atributo em bytes
        - N bytes: valor do atributo em UTF-8
    """

    _ATRIBUTOS = ("codigo", "titulo", "autor", "preco")

    def __init__(self, origem: BinaryIO) -> None:
        super().__init__()
        if origem is None:
            raise ValueError("origem nao pode ser nula")

        self._origem = origem
        self._fechado = False

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        if self._fechado:
            raise ValueError("stream fechada")

        return self._origem.read(size)

    def close(self) -> None:
        self._fechado = True
        super().close()

    def ler_livros(self) -> list[Livro]:
        """Lê os livros do stream e retorna uma lista de objetos Livro."""
        quantidade_bytes = self.read(4)
        if len(quantidade_bytes) < 4:
            raise ValueError("dados insuficientes para ler a quantidade de objetos")

        quantidade_objetos = struct.unpack("!I", quantidade_bytes)[0]
        livros = []

        for _ in range(quantidade_objetos):
            atributos = {}
            for atributo in self._ATRIBUTOS:
                tamanho_bytes = self.read(4)
                if len(tamanho_bytes) < 4:
                    raise ValueError(f"dados insuficientes para ler o tamanho do atributo '{atributo}'")

                tamanho_atributo = struct.unpack("!I", tamanho_bytes)[0]
                valor_bytes = self.read(tamanho_atributo)
                if len(valor_bytes) < tamanho_atributo:
                    raise ValueError(f"dados insuficientes para ler o valor do atributo '{atributo}'")

                atributos[atributo] = valor_bytes.decode("utf-8")

            atributos["preco"] = float(atributos["preco"])
            livro = Livro(**atributos)
            livros.append(livro)

        return livros
