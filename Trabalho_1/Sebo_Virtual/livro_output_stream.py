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


class LivroOutputStream(io.RawIOBase):
    """Stream de saida para enviar um conjunto de livros em formato binario.

    Protocolo utilizado:
    - 4 bytes: quantidade de objetos enviados (unsigned int, big-endian)
    - Para cada livro:
      - Para cada atributo serializado:
        - 4 bytes: tamanho do atributo em bytes
        - N bytes: valor do atributo em UTF-8
    """

    _ATRIBUTOS = ("codigo", "titulo", "autor", "preco")

    def __init__(
        self,
        livros: Sequence[Livro],
        quantidade_objetos: int,
        destino: BinaryIO,
    ) -> None:
        super().__init__()
        if quantidade_objetos < 0:
            raise ValueError("quantidade_objetos nao pode ser negativa")
        if quantidade_objetos > len(livros):
            raise ValueError("quantidade_objetos nao pode ser maior que a quantidade de livros")
        if destino is None:
            raise ValueError("destino nao pode ser nulo")

        self._livros = list(livros)
        self._quantidade_objetos = quantidade_objetos
        self._destino = destino
        self._fechado = False

    def writable(self) -> bool:
        return True

    def write(self, b: bytes | bytearray) -> int:
        if self._fechado:
            raise ValueError("stream fechada")

        dados = bytes(b)
        self._destino.write(dados)
        return len(dados)

    def close(self) -> None:
        self._fechado = True
        super().close()

    def enviar(self) -> int:
        """Serializa e envia os objetos configurados para o destino.

        Retorna o total de bytes enviados.
        """
        payload = self._serializar_livros(self._livros[: self._quantidade_objetos])
        bytes_enviados = self.write(payload)
        if hasattr(self._destino, "flush"):
            self._destino.flush()
        return bytes_enviados

    @classmethod
    def _serializar_livros(cls, livros: Sequence[Livro]) -> bytes:
        buffer = bytearray()
        buffer.extend(struct.pack("!I", len(livros)))

        for livro in livros:
            for atributo in cls._ATRIBUTOS:
                valor = cls._valor_atributo(livro, atributo)
                dados_atributo = valor.encode("utf-8")
                buffer.extend(struct.pack("!I", len(dados_atributo)))
                buffer.extend(dados_atributo)

        return bytes(buffer)

    @staticmethod
    def _valor_atributo(livro: Livro, atributo: str) -> str:
        valor = getattr(livro, atributo)
        if valor is None:
            return ""
        if atributo == "preco":
            return f"{float(valor):.2f}"
        return str(valor)
