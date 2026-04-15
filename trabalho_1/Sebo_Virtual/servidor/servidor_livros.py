"""
Servidor Remoto de Livros

Aguarda conexões de clientes e oferece operações remotas:
- listar: retorna todos os livros disponíveis
- buscar <codigo>: retorna um livro específico
"""

import socket
import struct
import sys
from typing import Optional

try:
    from ..livro_input_stream import LivroInputStream
    from ..livro_output_stream import LivroOutputStream
    from .modelos.livro import Livro
except ImportError:
    try:
        from livro_input_stream import LivroInputStream
        from livro_output_stream import LivroOutputStream
        from servidor.modelos.livro import Livro
    except ImportError:
        from Sebo_Virtual.livro_input_stream import LivroInputStream
        from Sebo_Virtual.livro_output_stream import LivroOutputStream
        from Sebo_Virtual.servidor.modelos.livro import Livro


HOST = "127.0.0.1"
PORTA = 5000

# Base de dados de livros
CATALOGO = {
    "001": Livro(codigo="001", titulo="Clean Code", autor="Robert C. Martin", preco=89.90),
    "002": Livro(codigo="002", titulo="Design Patterns", autor="Gang of Four", preco=120.00),
    "003": Livro(codigo="003", titulo="Refactoring", autor="Martin Fowler", preco=95.50),
    "004": Livro(codigo="004", titulo="The Pragmatic Programmer", autor="Hunt & Thomas", preco=75.00),
    "005": Livro(codigo="005", titulo="Code Complete", autor="Steve McConnell", preco=110.00),
}


def processar_requisicao(cliente_socket: socket.socket) -> None:
    """Processa uma requisição do cliente."""
    
    try:
        # Usar makefile para criar um file-like object
        arquivo = cliente_socket.makefile('rwb')
        
        # Ler comando do cliente (4 bytes: tamanho do comando em string)
        tamanho_bytes = arquivo.read(4)
        if not tamanho_bytes:
            print("[servidor] Cliente desconectou", file=sys.stderr)
            return
        
        tamanho_comando = struct.unpack("!I", tamanho_bytes)[0]
        comando_bytes = arquivo.read(tamanho_comando)
        comando = comando_bytes.decode("utf-8").strip()
        
        print(f"[servidor] Comando recebido: '{comando}'", file=sys.stderr)
        
        # Executar comando
        resposta_livros = []
        
        if comando.lower() == "listar":
            # Listar todos os livros
            resposta_livros = list(CATALOGO.values())
            print(f"[servidor] Retornando {len(resposta_livros)} livro(s)", file=sys.stderr)
        
        elif comando.lower().startswith("buscar"):
            # Buscar um livro específico
            partes = comando.split()
            if len(partes) >= 2:
                codigo = partes[1]
                if codigo in CATALOGO:
                    resposta_livros = [CATALOGO[codigo]]
                    print(f"[servidor] Livro '{codigo}' encontrado", file=sys.stderr)
                else:
                    print(f"[servidor] Livro '{codigo}' não encontrado", file=sys.stderr)
        
        else:
            print(f"[servidor] Comando desconhecido", file=sys.stderr)
        
        # Empacotar resposta (serializar livros)
        stream_resposta = LivroOutputStream(resposta_livros, len(resposta_livros), arquivo)
        bytes_enviados = stream_resposta.enviar()
        arquivo.flush()
        print(f"[servidor] Resposta enviada: {bytes_enviados} bytes", file=sys.stderr)
        
        arquivo.close()
        
    except Exception as e:
        print(f"[servidor] Erro ao processar requisição: {e}", file=sys.stderr)
    
    finally:
        cliente_socket.close()


def iniciar_servidor() -> None:
    """Inicia o servidor e aguarda conexões de clientes."""
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORTA))
        servidor.listen(5)
        
        print(f"✓ Servidor aguardando conexões em {HOST}:{PORTA}", file=sys.stderr)
        print(f"✓ Catálogo contém {len(CATALOGO)} livro(s)", file=sys.stderr)
        print("[servidor] Digite Ctrl+C para parar", file=sys.stderr)
        
        try:
            while True:
                cliente_socket, endereco = servidor.accept()
                print(f"[servidor] Cliente conectado de {endereco}", file=sys.stderr)
                processar_requisicao(cliente_socket)
        
        except KeyboardInterrupt:
            print("\n✓ Servidor finalizado pelo usuário", file=sys.stderr)


if __name__ == "__main__":
    iniciar_servidor()
