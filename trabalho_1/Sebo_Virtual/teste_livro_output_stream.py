from __future__ import annotations

import io
import socket
import struct
import sys
import threading
from pathlib import Path

try:
    from .servidor.modelos.livro import Livro
    from .livro_output_stream import LivroOutputStream
except ImportError:
    try:
        from servidor.modelos.livro import Livro
        from livro_output_stream import LivroOutputStream
    except ImportError:
        from Sebo_Virtual.servidor.modelos.livro import Livro
        from Sebo_Virtual.livro_output_stream import LivroOutputStream


ATRIBUTOS = ("codigo", "titulo", "autor", "preco")


def criar_livros_exemplo() -> list[Livro]:
    return [
        Livro(codigo="L001", titulo="Engenharia de Software", preco=89.9, autor="Sommerville"),
        Livro(codigo="L002", titulo="Redes de Computadores", preco=120.0, autor="Tanenbaum"),
    ]


def _ler_atributo(payload: bytes, deslocamento: int) -> tuple[str, int, int]:
    tamanho = struct.unpack_from("!I", payload, deslocamento)[0]
    deslocamento += 4
    dados = payload[deslocamento : deslocamento + tamanho]
    deslocamento += tamanho
    return dados.decode("utf-8"), tamanho, deslocamento


def exibir_resumo_payload(payload: bytes, titulo: str) -> None:
    deslocamento = 0
    quantidade = struct.unpack_from("!I", payload, deslocamento)[0]
    deslocamento += 4

    print(f"\n=== {titulo} ===")
    print(f"Total de objetos no payload: {quantidade}")

    for i in range(quantidade):
        print(f"Objeto {i + 1}:")
        for atributo in ATRIBUTOS:
            valor, tamanho, deslocamento = _ler_atributo(payload, deslocamento)
            print(f"  {atributo}: '{valor}' ({tamanho} bytes)")


def teste_stdout(livros: list[Livro]) -> None:
    stream = LivroOutputStream(livros, quantidade_objetos=2, destino=sys.stdout.buffer)
    payload = stream._serializar_livros(livros[:2])

    # Exibe resumo legivel e tambem envia os bytes para o stdout real.
    exibir_resumo_payload(payload, "Teste com destino System.out (resumo no stdout)")
    print("Payload binario enviado para System.out abaixo:")
    bytes_enviados = stream.enviar()
    print(f"\nBytes enviados para System.out: {bytes_enviados}")


def teste_arquivo(livros: list[Livro]) -> None:
    caminho_saida = Path(__file__).resolve().parent / "saida_livros.bin"
    with caminho_saida.open("wb") as arquivo:
        stream = LivroOutputStream(livros, quantidade_objetos=2, destino=arquivo)
        bytes_enviados = stream.enviar()

    conteudo = caminho_saida.read_bytes()
    exibir_resumo_payload(conteudo, f"Teste com FileOutputStream ({caminho_saida.name})")
    print(f"Bytes gravados no arquivo: {bytes_enviados}")


class _TCPServerCaptura(threading.Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.host = "127.0.0.1"
        self.port = 0
        self.payload = b""
        self._ready = threading.Event()
        self._erro: Exception | None = None

    def run(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
                servidor.bind((self.host, self.port))
                servidor.listen(1)
                self.port = servidor.getsockname()[1]
                self._ready.set()

                conn, _ = servidor.accept()
                with conn:
                    partes: list[bytes] = []
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        partes.append(chunk)
                    self.payload = b"".join(partes)
        except Exception as exc:
            self._erro = exc
            self._ready.set()

    def aguardar_pronto(self) -> None:
        self._ready.wait(timeout=5)
        if self._erro is not None:
            raise self._erro


def teste_tcp(livros: list[Livro]) -> None:
    servidor = _TCPServerCaptura()
    servidor.start()
    servidor.aguardar_pronto()

    with socket.create_connection((servidor.host, servidor.port), timeout=5) as cliente:
        destino = cliente.makefile("wb")
        stream = LivroOutputStream(livros, quantidade_objetos=2, destino=destino)
        bytes_enviados = stream.enviar()
        destino.close()

    servidor.join(timeout=5)
    exibir_resumo_payload(servidor.payload, "Teste com servidor remoto TCP")
    print(f"Bytes enviados via TCP: {bytes_enviados}")


def main() -> None:
    livros = criar_livros_exemplo()

    # O print comum em Python representa o papel de System.out em Java.
    print("Destino i) saida padrao (System.out)")
    teste_stdout(livros)

    print("\nDestino ii) arquivo (FileOutputStream)")
    teste_arquivo(livros)

    print("\nDestino iii) servidor remoto (TCP)")
    teste_tcp(livros)

    print("\nTodos os testes foram executados.")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
