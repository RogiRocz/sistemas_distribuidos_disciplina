"""Despachante de requisições remotas para a Loja - Implementação RMI."""

from __future__ import annotations

import json
from typing import Any

try:
    from ...rmi import RemoteDispatcher, Serializer
    from .loja import Loja
    from .livro import Livro
    from .cd import CD
    from .ebook import Ebook
    from .apostila import Apostila
except ImportError:
    import sys
    from pathlib import Path
    
    # Ajustar path
    raiz_modelo = Path(__file__).parent
    raiz_sebo = raiz_modelo.parents[2]
    if str(raiz_sebo) not in sys.path:
        sys.path.insert(0, str(raiz_sebo))
    
    from Sebo_Virtual.rmi import RemoteDispatcher, Serializer
    from Sebo_Virtual.servidor.modelos.loja import Loja
    from Sebo_Virtual.servidor.modelos.livro import Livro
    from Sebo_Virtual.servidor.modelos.cd import CD
    from Sebo_Virtual.servidor.modelos.ebook import Ebook
    from Sebo_Virtual.servidor.modelos.apostila import Apostila


class LojaDispatcher(RemoteDispatcher):
    """Despachante de requisições remotas para operações da loja.
    
    Métodos remotos disponíveis:
    1. listar_produtos() - Lista todos os produtos
    2. buscar_por_codigo(codigo: str) - Busca produto por código
    3. buscar_por_titulo(titulo: str) - Busca produtos por título
    4. adicionar_produto(produto_json: str) - Adiciona novo produto
    5. remover_produto(codigo: str) - Remove produto do estoque
    6. produtos_trocaveis() - Lista produtos que podem ser trocados
    """
    
    def __init__(self, loja: Loja):
        """Inicializa o despachante.
        
        Args:
            loja: Instância da Loja a ser acessada remotamente
        """
        self.loja = loja
        self.methods = {
            "listar_produtos": self.listar_produtos,
            "buscar_por_codigo": self.buscar_por_codigo,
            "buscar_por_titulo": self.buscar_por_titulo,
            "adicionar_produto": self.adicionar_produto,
            "remover_produto": self.remover_produto,
            "produtos_trocaveis": self.produtos_trocaveis,
            "obter_nome_loja": self.obter_nome_loja,
            "atualizar_preco": self.atualizar_preco,
        }
    
    def dispatch_method(self, method_id: str, arguments: bytes) -> bytes:
        """Processa uma requisição de método remoto.
        
        Args:
            method_id: Nome do método
            arguments: Argumentos em bytes (JSON)
            
        Returns:
            Resultado em bytes (JSON)
            
        Raises:
            Exception: Se o método não existe
        """
        if method_id not in self.methods:
            raise Exception(f"Método '{method_id}' não encontrado")
        
        method_handler = self.methods[method_id]
        
        try:
            # Desserializar argumentos se houver
            args = {}
            if arguments:
                args = json.loads(arguments.decode('utf-8'))
            
            # Chamar o método
            result = method_handler(**args)
            
            # Serializar resultado
            return Serializer.serialize(result)
        except Exception as e:
            raise Exception(f"Erro ao executar '{method_id}': {str(e)}")
    
    # ========== Métodos Remotos ==========
    
    def listar_produtos(self) -> list[dict]:
        """Lista todos os produtos da loja.
        
        Returns:
            Lista de dicionários representando os produtos
        """
        produtos = self.loja.listar_produtos()
        return [p.to_dict() for p in produtos]
    
    def buscar_por_codigo(self, codigo: str) -> dict | None:
        """Busca um produto pelo código.
        
        Args:
            codigo: Código do produto
            
        Returns:
            Dicionário do produto ou None
        """
        produto = self.loja.buscar_por_codigo(codigo)
        return produto.to_dict() if produto else None
    
    def buscar_por_titulo(self, titulo: str) -> list[dict]:
        """Busca produtos pelo título.
        
        Args:
            titulo: Título a buscar
            
        Returns:
            Lista de dicionários dos produtos encontrados
        """
        produtos = self.loja.buscar_por_titulo(titulo)
        return [p.to_dict() for p in produtos]
    
    def adicionar_produto(self, tipo: str, **kwargs) -> dict:
        """Adiciona um novo produto à loja.
        
        Args:
            tipo: Tipo do produto ("Livro", "CD", "Ebook", "Apostila")
            **kwargs: Atributos do produto
            
        Returns:
            Dicionário do produto adicionado
        """
        # Criar instância do produto correto
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
        
        self.loja.adicionar_produto(produto)
        return produto.to_dict()
    
    def remover_produto(self, codigo: str) -> dict | None:
        """Remove um produto da loja.
        
        Args:
            codigo: Código do produto
            
        Returns:
            Dicionário do produto removido ou None
        """
        produto = self.loja.remover_produto(codigo)
        return produto.to_dict() if produto else None
    
    def produtos_trocaveis(self) -> list[dict]:
        """Lista produtos que podem ser trocados.
        
        Returns:
            Lista de dicionários dos produtos trocáveis
        """
        produtos = self.loja.produtos_trocaveis()
        return [p.to_dict() for p in produtos]
    
    def obter_nome_loja(self) -> str:
        """Retorna o nome da loja.
        
        Returns:
            Nome da loja
        """
        return self.loja.nome
    
    def atualizar_preco(self, codigo: str, novo_preco: float) -> dict:
        """Atualiza o preço de um produto.
        
        Args:
            codigo: Código do produto
            novo_preco: Novo preço
            
        Returns:
            Dicionário do produto atualizado
        """
        if novo_preco < 0:
            raise ValueError("Preço não pode ser negativo")
        
        produto = self.loja.buscar_por_codigo(codigo)
        if produto is None:
            raise ValueError(f"Produto com código {codigo} não encontrado")
        
        produto.preco = novo_preco
        return produto.to_dict()
