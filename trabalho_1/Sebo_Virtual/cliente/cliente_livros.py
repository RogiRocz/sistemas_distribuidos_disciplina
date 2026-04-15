"""
Cliente Remoto de Livros

Se conecta ao servidor e permite:
- listar: recebe todos os livros disponíveis
- buscar <codigo>: recebe um livro específico

Uso:
    Terminal 1: python3 servidor_livros.py
    Terminal 2: python3 cliente_livros.py
"""

import socket
import struct
import sys

try:
    from ..livro_input_stream import LivroInputStream
except ImportError:
    try:
        from livro_input_stream import LivroInputStream
    except ImportError:
        from Sebo_Virtual.livro_input_stream import LivroInputStream


HOST = "127.0.0.1"
PORTA = 5000


def enviar_comando(socket_cliente: socket.socket, comando: str) -> None:
    """Envia um comando para o servidor."""
    arquivo = socket_cliente.makefile('rwb')
    comando_bytes = comando.encode("utf-8")
    tamanho = struct.pack("!I", len(comando_bytes))
    
    arquivo.write(tamanho)
    arquivo.write(comando_bytes)
    arquivo.flush()
    
    print(f"[cliente] Comando enviado: '{comando}'", file=sys.stderr)


def receber_resposta(socket_cliente: socket.socket) -> None:
    """Recebe e desserializa a resposta do servidor."""
    
    arquivo = socket_cliente.makefile('rwb')
    stream_resposta = LivroInputStream(arquivo)
    livros = stream_resposta.ler_livros()
    
    print(f"[cliente] Resposta recebida: {len(livros)} livro(s)", file=sys.stderr)
    print("-" * 80)
    
    if not livros:
        print("Nenhum livro encontrado")
    else:
        for i, livro in enumerate(livros, 1):
            print(f"{i}. {livro.titulo}")
            print(f"   Código: {livro.codigo}")
            print(f"   Autor: {livro.autor}")
            print(f"   Preço: R$ {livro.preco:.2f}\n")


def conectar_servidor() -> None:
    """Conecta ao servidor e interage com o usuário."""
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
        try:
            socket_cliente.connect((HOST, PORTA))
            print(f"✓ Conectado ao servidor em {HOST}:{PORTA}", file=sys.stderr)
            
            print("\n" + "="*80)
            print("CLIENTE DE BIBLIOTECA REMOTA")
            print("="*80)
            print("\nComandos disponíveis:")
            print("  listar          - lista todos os livros")
            print("  buscar <codigo> - busca um livro específico")
            print("  sair            - desconecta do servidor\n")
            
            while True:
                try:
                    comando = input("> ").strip()
                    
                    if not comando:
                        continue
                    
                    if comando.lower() == "sair":
                        print("✓ Desconectando...", file=sys.stderr)
                        break
                    
                    # Enviar comando
                    enviar_comando(socket_cliente, comando)
                    
                    # Receber resposta
                    receber_resposta(socket_cliente)
                    
                except EOFError:
                    # Ctrl+D
                    break
        
        except ConnectionRefusedError:
            print(f"✗ Erro: não foi possível conectar ao servidor em {HOST}:{PORTA}", file=sys.stderr)
            print("  Inicie o servidor: python3 servidor_livros.py", file=sys.stderr)
            sys.exit(1)
        
        except Exception as e:
            print(f"✗ Erro: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    conectar_servidor()
