from __future__ import annotations

import io
import socket
import struct
import sys
import threading
from pathlib import Path

try:
    from .servidor.modelos.livro import Livro
    from .livro_input_stream import LivroInputStream
    from .livro_output_stream import LivroOutputStream
except ImportError:
    try:
        from servidor.modelos.livro import Livro
        from livro_input_stream import LivroInputStream
        from livro_output_stream import LivroOutputStream
    except ImportError:
        from Sebo_Virtual.servidor.modelos.livro import Livro
        from Sebo_Virtual.livro_input_stream import LivroInputStream
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


def exibir_livros(livros: list[Livro], titulo: str) -> None:
    print(f"\n=== {titulo} ===")
    print(f"Total de objetos lidos: {len(livros)}")
    
    for i, livro in enumerate(livros, 1):
        print(f"Objeto {i}:")
        print(f"  codigo: '{livro.codigo}'")
        print(f"  titulo: '{livro.titulo}'")
        print(f"  autor: '{livro.autor}'")
        print(f"  preco: '{livro.preco:.2f}'")


def teste_stdin(livros: list[Livro]) -> None:
    """Teste com entrada padrão: gera dados, escreve em bytes, lê de volta."""
    print("\n" + "="*80)
    print("Teste i) Entrada padrão (System.in)")
    print("="*80)
    
    # Gerar payload
    stream_out = LivroOutputStream(livros, quantidade_objetos=2, destino=io.BytesIO())
    payload = stream_out._serializar_livros(livros[:2])
    
    # Simular stdin com BytesIO
    entrada = io.BytesIO(payload)
    stream_in = LivroInputStream(entrada)
    
    # Ler livros
    livros_lidos = stream_in.ler_livros()
    exibir_livros(livros_lidos, "Lidos da entrada padrão (stdin)")
    print(f"Total de bytes lidos: {len(payload)}")


def teste_arquivo(livros: list[Livro]) -> None:
    """Teste com arquivo: escreve em arquivo, lê de volta."""
    print("\n" + "="*80)
    print("Teste ii) Arquivo (FileInputStream)")
    print("="*80)
    
    caminho_saida = Path(__file__).resolve().parent / "livros_teste.bin"
    
    # Escrever arquivo
    with caminho_saida.open("wb") as arquivo:
        stream_out = LivroOutputStream(livros, quantidade_objetos=2, destino=arquivo)
        bytes_enviados = stream_out.enviar()
    
    print(f"Arquivo '{caminho_saida.name}' gravado com {bytes_enviados} bytes")
    
    # Ler arquivo
    with caminho_saida.open("rb") as arquivo:
        stream_in = LivroInputStream(arquivo)
        livros_lidos = stream_in.ler_livros()
    
    exibir_livros(livros_lidos, f"Lidos do arquivo (FileInputStream)")
    
    # Limpar
    caminho_saida.unlink()
    print(f"Arquivo '{caminho_saida.name}' removido")


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
    """Teste com servidor remoto TCP: envia dados via socket, lê de volta."""
    print("\n" + "="*80)
    print("Teste iii) Servidor remoto (TCP)")
    print("="*80)
    
    # Iniciar servidor capturador
    servidor = _TCPServerCaptura()
    servidor.start()
    servidor.aguardar_pronto()
    
    # Conectar como cliente e enviar
    with socket.create_connection((servidor.host, servidor.port), timeout=5) as cliente:
        destino = cliente.makefile("wb")
        stream_out = LivroOutputStream(livros, quantidade_objetos=2, destino=destino)
        bytes_enviados = stream_out.enviar()
        destino.close()
    
    servidor.join(timeout=5)
    print(f"Servidor TCP em {servidor.host}:{servidor.port}")
    print(f"Total de bytes enviados: {bytes_enviados}")
    
    # Ler do payload capturado
    entrada = io.BytesIO(servidor.payload)
    stream_in = LivroInputStream(entrada)
    livros_lidos = stream_in.ler_livros()
    
    exibir_livros(livros_lidos, "Lidos do servidor remoto (TCP)")


def main() -> None:
    livros = criar_livros_exemplo()

    teste_stdin(livros)
    teste_arquivo(livros)
    teste_tcp(livros)

    print("\n" + "="*80)
    print("✓ Todos os testes de LivroInputStream foram executados com sucesso!")
    print("="*80)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
