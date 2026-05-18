"""
SERVIDOR RMI DE LOJA - VERSÃO SIMPLIFICADA E COMENTADA
========================================================

Este arquivo implementa o SERVIDOR que disponibiliza os métodos da Loja
como serviços remotos via RMI.

ESTRUTURA:
1. Criar uma Loja com catálogo
2. Criar um LojaDispatcher que mapeia requisições → métodos
3. Criar um RemoteServer e registrar o LojaDispatcher
4. Iniciar o servidor (fica aguardando requisições)
"""

import sys
from pathlib import Path

# ============================================================================
# IMPORTS - Trazer classes necessárias
# ============================================================================

try:
    # Tentar import relativo (quando executado como módulo)
    from .rmi_comentado import RemoteServer, RemoteDispatcher, Serializer
    from .servidor.modelos.loja import Loja
    from .servidor.modelos.livro import Livro
    from .servidor.modelos.cd import CD
    from .servidor.modelos.ebook import Ebook
    from .servidor.modelos.apostila import Apostila
except ImportError:
    # Fallback para imports diretos (quando executado diretamente)
    from rmi_comentado import RemoteServer, RemoteDispatcher, Serializer
    from servidor.modelos.loja import Loja
    from servidor.modelos.livro import Livro
    from servidor.modelos.cd import CD
    from servidor.modelos.ebook import Ebook
    from servidor.modelos.apostila import Apostila

import json


# ============================================================================
# CONFIGURAÇÃ0
# ============================================================================

HOST = "127.0.0.1"  # Escuta apenas local
PORTA = 5000        # Porta do servidor


# ============================================================================
# DESPACHANTE DE REQUISIÇÕES DA LOJA
# ============================================================================

class LojaDispatcher(RemoteDispatcher):
    """
    DESPACHANTE DE REQUISIÇÕES DA LOJA
    
    Este objeto implementa os métodos remotos da Loja.
    Quando o cliente faz uma requisição, o servidor chama dispatch_method()
    que localiza o método e o executa.
    
    MÉTODOS REMOTOS DISPONÍVEIS:
    1. listar_produtos() - Retorna todos os produtos
    2. buscar_por_codigo(codigo) - Encontra produto específico
    3. buscar_por_titulo(titulo) - Busca por nome
    4. adicionar_produto(tipo, **kwargs) - Cria novo produto
    5. remover_produto(codigo) - Deleta produto
    6. obter_nome_loja() - Retorna nome da loja
    """
    
    def __init__(self, loja: Loja):
        """
        Inicializa o despachante
        
        Args:
            loja: Instância da Loja cuja qual implementará os métodos
        """
        self.loja = loja
        
        # Dicionário que mapeia NOMES DE MÉTODOS → funções Python
        # Quando requisição chega com method_id="listar_produtos",
        # ele procura aqui e encontra self.listar_produtos
        self.methods = {
            "listar_produtos": self.listar_produtos,
            "buscar_por_codigo": self.buscar_por_codigo,
            "buscar_por_titulo": self.buscar_por_titulo,
            "adicionar_produto": self.adicionar_produto,
            "remover_produto": self.remover_produto,
            "obter_nome_loja": self.obter_nome_loja,
            "atualizar_preco": self.atualizar_preco,
            "produtos_trocaveis": self.produtos_trocaveis,
        }
    
    def dispatch_method(self, method_id: str, arguments: bytes) -> bytes:
        """
        PROCESSA UMA REQUISIÇÃO DE MÉTODO REMOTO
        
        Este é o método chamado pelo RemoteServer quando uma requisição chega.
        
        Args:
            method_id: Nome do método (ex: "listar_produtos")
            arguments: Argumentos em bytes JSON (ex: b'{"codigo": "L001"}')
        
        Returns:
            Resultado serializado em bytes JSON
        
        Levanta:
            Exception: Se método não existe ou houve erro na execução
        """
        # PASSO 1: Verificar se método existe
        if method_id not in self.methods:
            raise Exception(f"Método '{method_id}' não existe")
        
        # PASSO 2: Obter a função que implementa o método
        method_function = self.methods[method_id]
        
        try:
            # PASSO 3: Desserializar argumentos (bytes JSON → dict Python)
            args = {}
            if arguments:
                args = json.loads(arguments.decode('utf-8'))
            
            # PASSO 4: Chamar a função com os argumentos
            result = method_function(**args)
            
            # PASSO 5: Serializar resultado (Python → bytes JSON)
            return Serializer.serialize(result)
        
        except Exception as e:
            raise Exception(f"Erro ao executar '{method_id}': {str(e)}")
    
    # ========== IMPLEMENTAÇÃO DOS MÉTODOS REMOTOS ==========
    
    def listar_produtos(self) -> list:
        """
        MÉTODO REMOTO: Listar todos os produtos
        
        REQUISIÇÃO:
            método: "listar_produtos"
            argumentos: {} (nenhum)
        
        RESPOSTA:
            [
              {"codigo": "L001", "titulo": "Clean Code", "tipo": "Livro", ...},
              {"codigo": "C001", "titulo": "Thriller", "tipo": "CD", ...},
              ...
            ]
        """
        produtos = self.loja.listar_produtos()
        return [p.to_dict() for p in produtos]
    
    def buscar_por_codigo(self, codigo: str) -> dict:
        """
        MÉTODO REMOTO: Buscar produto por código
        
        REQUISIÇÃO:
            método: "buscar_por_codigo"
            argumentos: {"codigo": "L001"}
        
        RESPOSTA:
            {"codigo": "L001", "titulo": "Clean Code", "tipo": "Livro", ...}
            ou null se não encontrado
        """
        produto = self.loja.buscar_por_codigo(codigo)
        return produto.to_dict() if produto else None
    
    def buscar_por_titulo(self, titulo: str) -> list:
        """
        MÉTODO REMOTO: Buscar produtos por título
        
        REQUISIÇÃO:
            método: "buscar_por_titulo"
            argumentos: {"titulo": "Clean"}
        
        RESPOSTA:
            [{"codigo": "L001", "titulo": "Clean Code", ...}]
        """
        produtos = self.loja.buscar_por_titulo(titulo)
        return [p.to_dict() for p in produtos]
    
    def adicionar_produto(self, tipo: str, **kwargs) -> dict:
        """
        MÉTODO REMOTO: Adicionar novo produto
        
        REQUISIÇÃO:
            método: "adicionar_produto"
            argumentos: {
              "tipo": "Livro",
              "codigo": "L100",
              "titulo": "Meu Livro",
              "autor": "Fulano",
              "preco": 50.00
            }
        
        RESPOSTA:
            {"codigo": "L100", "titulo": "Meu Livro", ...}
        """
        # Criar instância do tipo correto de produto
        if tipo == "Livro":
            produto = Livro(**kwargs)
        elif tipo == "CD":
            produto = CD(**kwargs)
        elif tipo == "Ebook":
            produto = Ebook(**kwargs)
        elif tipo == "Apostila":
            produto = Apostila(**kwargs)
        else:
            raise ValueError(f"Tipo de produto desconhecido: {tipo}")
        
        # Adicionar à loja
        self.loja.adicionar_produto(produto)
        return produto.to_dict()
    
    def remover_produto(self, codigo: str) -> dict:
        """
        MÉTODO REMOTO: Remover produto
        
        REQUISIÇÃO:
            método: "remover_produto"
            argumentos: {"codigo": "L100"}
        
        RESPOSTA:
            {"codigo": "L100", "titulo": "Meu Livro", ...}
            ou null se não encontrado
        """
        produto = self.loja.remover_produto(codigo)
        return produto.to_dict() if produto else None
    
    def obter_nome_loja(self) -> str:
        """
        MÉTODO REMOTO: Obter nome da loja
        
        REQUISIÇÃO:
            método: "obter_nome_loja"
            argumentos: {}
        
        RESPOSTA:
            "Sebo Virtual"
        """
        return self.loja.nome
    
    def atualizar_preco(self, codigo: str, novo_preco: float) -> dict:
        """
        MÉTODO REMOTO: Atualizar preço
        
        REQUISIÇÃO:
            método: "atualizar_preco"
            argumentos: {"codigo": "L001", "novo_preco": 120.00}
        
        RESPOSTA:
            {"codigo": "L001", "preco": 120.00, ...}
        """
        if novo_preco < 0:
            raise ValueError("Preço não pode ser negativo")
        
        produto = self.loja.buscar_por_codigo(codigo)
        if produto is None:
            raise ValueError(f"Produto {codigo} não encontrado")
        
        produto.preco = novo_preco
        return produto.to_dict()
    
    def produtos_trocaveis(self) -> list:
        """
        MÉTODO REMOTO: Listar produtos trocáveis
        
        REQUISIÇÃO:
            método: "produtos_trocaveis"
            argumentos: {}
        
        RESPOSTA:
            [{"codigo": "L001", ...}, {"codigo": "C001", ...}]
        """
        produtos = self.loja.produtos_trocaveis()
        return [p.to_dict() for p in produtos]


# ============================================================================
# FUNÇÃO PARA CRIAR CATÁLOGO INICIAL
# ============================================================================

def criar_catalogo_inicial() -> Loja:
    """
    CRIA UMA LOJA COM PRODUTOS DE EXEMPLO
    
    Retorna:
        Loja preenchida com 7 produtos de exemplo
    """
    loja = Loja(nome="Sebo Virtual")
    
    # Adicionar 3 Livros
    loja.adicionar_produto(Livro(
        codigo="L001",
        titulo="Clean Code",
        autor="Robert C. Martin",
        preco=89.90,
        editora="Prentice Hall",
        ano_publicacao=2008
    ))
    
    loja.adicionar_produto(Livro(
        codigo="L002",
        titulo="Design Patterns",
        autor="Gang of Four",
        preco=120.00,
        editora="Addison-Wesley",
        ano_publicacao=1994
    ))
    
    loja.adicionar_produto(Livro(
        codigo="L003",
        titulo="Refactoring",
        autor="Martin Fowler",
        preco=95.50,
        editora="Addison-Wesley",
        ano_publicacao=1999
    ))
    
    # Adicionar 2 CDs
    loja.adicionar_produto(CD(
        codigo="C001",
        titulo="Thriller",
        artista="Michael Jackson",
        preco=35.00,
        genero="Pop"
    ))
    
    loja.adicionar_produto(CD(
        codigo="C002",
        titulo="The Wall",
        artista="Pink Floyd",
        preco=45.00,
        genero="Rock"
    ))
    
    # Adicionar 1 Ebook
    loja.adicionar_produto(Ebook(
        codigo="E001",
        titulo="Python for Developers",
        preco=29.90,
        formato="PDF",
        tamanho_mb=15.5
    ))
    
    # Adicionar 1 Apostila
    loja.adicionar_produto(Apostila(
        codigo="A001",
        titulo="Sistemas Distribuídos",
        preco=50.00,
        disciplina="Engenharia de Software",
        instituicao="Universidade Federal"
    ))
    
    return loja


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    FUNÇÃO PRINCIPAL - INICIA O SERVIDOR
    """
    print("\n" + "="*70)
    print("SERVIDOR RMI DE LOJA VIRTUAL - VERSÃO COMENTADA")
    print("="*70)
    
    # PASSO 1: Criar loja com catálogo inicial
    print("\n[1] Carregando catálogo...")
    loja = criar_catalogo_inicial()
    print(f"    ✓ {len(loja.listar_produtos())} produtos carregados")
    
    # PASSO 2: Criar despachante que implementará os métodos remotos
    print("\n[2] Criando despachante de requisições...")
    dispatcher = LojaDispatcher(loja)
    print(f"    ✓ {len(dispatcher.methods)} métodos remotos disponíveis")
    
    # PASSO 3: Criar servidor RMI
    print(f"\n[3] Inicializando servidor RMI em {HOST}:{PORTA}...")
    server = RemoteServer(HOST, PORTA)
    
    # PASSO 4: Registrar objeto remoto
    print("\n[4] Registrando objeto remoto...")
    server.register_object("loja", dispatcher)
    
    # PASSO 5: Iniciar servidor (fica aguardando requisições)
    print("\n[5] Iniciando servidor (Ctrl+C para parar)...")
    print("\n" + "="*70)
    
    try:
        server.start()  # Fica aqui aguardando requisições
    except KeyboardInterrupt:
        print("\n[!] Servidor interrompido")


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    main()
