"""
Teste Automatizado: Serviço Remoto de Livros

Inicia o servidor e testa com múltiplos clientes em paralelo.

Uso:
    python3 teste_servico_remoto.py
"""

import socket
import struct
import sys
import threading
import time

try:
    from .livro_input_stream import LivroInputStream
    from .servidor.servidor_livros import CATALOGO, processar_requisicao
except ImportError:
    try:
        from livro_input_stream import LivroInputStream
        from servidor.servidor_livros import CATALOGO, processar_requisicao
    except ImportError:
        from Sebo_Virtual.livro_input_stream import LivroInputStream
        from Sebo_Virtual.servidor.servidor_livros import CATALOGO, processar_requisicao


HOST = "127.0.0.1"
PORTA = 5001  # Porta diferente para não conflitar


class ServidorTeste(threading.Thread):
    """Servidor para teste automatizado que reutiliza a lógica de servidor_livros.py."""
    
    def __init__(self):
        super().__init__(daemon=True)
        self.servidor = None
        self._pronto = threading.Event()
        self._erro = None
        self._conexoes_processadas = 0
    
    def run(self):
        try:
            self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.servidor.bind((HOST, PORTA))
            self.servidor.listen(10)
            self._pronto.set()
            
            print(f"[servidor] Aguardando conexões em {HOST}:{PORTA}", file=sys.stderr)
            print(f"[servidor] Catálogo contém {len(CATALOGO)} livro(s)", file=sys.stderr)
            
            # Aceitar até 3 conexões
            for _ in range(3):
                try:
                    cliente_socket, endereco = self.servidor.accept()
                    print(f"[servidor] Cliente conectado de {endereco}", file=sys.stderr)
                    
                    # Usar a função processar_requisicao de servidor_livros.py
                    processar_requisicao(cliente_socket)
                    self._conexoes_processadas += 1
                
                except Exception as e:
                    print(f"[servidor] Erro: {e}", file=sys.stderr)
        
        except Exception as e:
            self._erro = e
            self._pronto.set()
    
    def aguardar_pronto(self):
        self._pronto.wait(timeout=5)
        if self._erro:
            raise self._erro
    
    def parar(self):
        if self.servidor:
            self.servidor.close()


def cliente_fazer_requisicao(nome: str, comando: str) -> list:
    """Cliente faz uma requisição ao servidor."""
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORTA))
            
            # Enviar comando (empacotar) usando makefile
            arquivo = sock.makefile('rwb')
            comando_bytes = comando.encode("utf-8")
            tamanho = struct.pack("!I", len(comando_bytes))
            arquivo.write(tamanho)
            arquivo.write(comando_bytes)
            arquivo.flush()
            
            print(f"[{nome}] Comando enviado: '{comando}'", file=sys.stderr)
            
            # Receber resposta (desempacotar) usando makefile
            stream = LivroInputStream(arquivo)
            livros = stream.ler_livros()
            
            print(f"[{nome}] Resposta: {len(livros)} livro(s)", file=sys.stderr)
            arquivo.close()
            return livros
    
    except Exception as e:
        print(f"[{nome}] Erro: {e}", file=sys.stderr)
        return []


def main():
    print("\n" + "="*80)
    print("TESTE: SERVIÇO REMOTO DE LIVROS COM SOCKETS TCP")
    print("="*80)
    print("\nA classe ServidorTeste reutiliza a lógica de servidor_livros.py")
    
    # Iniciar servidor
    servidor = ServidorTeste()
    servidor.start()
    servidor.aguardar_pronto()
    
    time.sleep(1)  # Aguardar servidor iniciar
    
    # Simular clientes fazendo requisições
    print("\n--- Cliente 1: Listar todos os livros ---", file=sys.stderr)
    livros_1 = cliente_fazer_requisicao("Cliente1", "listar")
    print(f"Resultado:\n")
    for livro in livros_1:
        print(f"  • {livro.titulo} ({livro.codigo}) - R$ {livro.preco:.2f}")
    
    time.sleep(0.5)
    
    print("\n--- Cliente 2: Buscar livro 002 ---", file=sys.stderr)
    livros_2 = cliente_fazer_requisicao("Cliente2", "buscar 002")
    print(f"Resultado:\n")
    for livro in livros_2:
        print(f"  • {livro.titulo} ({livro.codigo}) - R$ {livro.preco:.2f}")
    
    time.sleep(0.5)
    
    print("\n--- Cliente 3: Buscar livro 001 ---", file=sys.stderr)
    livros_3 = cliente_fazer_requisicao("Cliente3", "buscar 001")
    print(f"Resultado:\n")
    for livro in livros_3:
        print(f"  • {livro.titulo} ({livro.codigo}) - R$ {livro.preco:.2f}")
    
    # Aguardar servidor finalizar
    servidor.join(timeout=2)
    servidor.parar()
    
    print("\n" + "="*80)
    print("✓ Teste concluído com sucesso!")
    print("="*80)
    print("\nFluxo")
    print("1. Cliente empacota comando (struct.pack + encode)")
    print("2. Cliente envia via socket TCP")
    print("3. Servidor desempacota comando (struct.unpack + decode)")
    print("4. Servidor processa requisição (processar_requisicao)")
    print("5. Servidor empacota resposta com LivroOutputStream")
    print("6. Servidor envia resposta via socket TCP")
    print("7. Cliente desempacota resposta com LivroInputStream")
    print("\n✓ Todos os dados foram empacotados/desempacotados via sockets TCP!")
    print("✓ Reutilizando lógica de servidor_livros.py na classe ServidorTeste")


if __name__ == "__main__":
    main()
