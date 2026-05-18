"""
CLIENTE RMI DE LOJA - VERSÃO SIMPLIFICADA E COMENTADA
=========================================================

Este arquivo implementa o CLIENTE que invoca métodos remotos da Loja.

ESTRUTURA:
1. Criar um RemoteInvoker (faz as requisições)
2. Chamar do_operation() passando:
   - RemoteObjectRef (qual objeto remoto chamar)
   - Nome do método
   - Argumentos em JSON
3. Receber resultado
"""

import sys
import json
from pathlib import Path


try:
    # Tentar import relativo (quando executado como módulo)
    from .rmi_comentado import RemoteInvoker, RemoteObjectRef
except ImportError:
    # Fallback para import direto (quando executado diretamente)
    from rmi_comentado import RemoteInvoker, RemoteObjectRef


#Configuração da porta e host do servidor (deve coincidir com o servidor)
HOST = "127.0.0.1"  # IP do servidor
PORTA = 5000        # Porta do servidor



class ClienteLoja:
    """
    Este cliente facilita chamar os métodos remotos da Loja.
    Cada método aqui é um wrapper que:
    1. Prepara os argumentos em JSON
    2. Chama RemoteInvoker.do_operation()
    3. Desserializa e retorna o resultado
    """
    
    def __init__(self, host: str = HOST, port: int = PORTA):
        """
        Inicializa o cliente
        
        Args:
            host: IP do servidor (padrão: 127.0.0.1)
            port: Porta do servidor (padrão: 5000)
        """
        # Criar invocador remoto
        self.invoker = RemoteInvoker(host, port, timeout=5.0)
        
        # Criar referência para o objeto remoto "loja"
        self.loja_ref = RemoteObjectRef(
            object_name="loja",  # Nome do objeto no servidor
            host=host,           # IP do servidor
            port=port            # Porta do servidor
        )
    
    def _chamar_remoto(self, metodo: str, argumentos: dict = None) -> any:
        """
        MÉTODO AUXILIAR: Chama um método remoto e retorna resultado
        
        Args:
            metodo: Nome do método remoto (ex: "listar_produtos")
            argumentos: Dicionário de argumentos (padrão: vazio)
        
        Returns:
            Resultado desserializado
        """
        try:
            # Serializar argumentos para JSON
            if argumentos is None:
                argumentos = {}
            args_bytes = json.dumps(argumentos).encode('utf-8')
            
            # Chamar método remoto
            resultado_bytes = self.invoker.do_operation(
                self.loja_ref,
                metodo,
                args_bytes
            )
            
            # Desserializar resultado
            return json.loads(resultado_bytes.decode('utf-8'))
        
        except Exception as e:
            print(f"[!] Erro ao chamar '{metodo}': {e}")
            return None
    
    # ========== MÉTODOS REMOTOS DA LOJA ==========
    
    def listar_produtos(self) -> list:
        """
        Lista todos os produtos disponíveis
        
        Requisição:
            método: "listar_produtos"
            argumentos: {}
        
        Retorna:
            Lista de dicionários dos produtos
        """
        return self._chamar_remoto("listar_produtos", {}) or []
    
    def buscar_por_codigo(self, codigo: str) -> dict:
        """
        Busca um produto pelo código
        
        Requisição:
            método: "buscar_por_codigo"
            argumentos: {"codigo": "L001"}
        
        Retorna:
            Dicionário do produto ou None
        """
        return self._chamar_remoto("buscar_por_codigo", {"codigo": codigo})
    
    def buscar_por_titulo(self, titulo: str) -> list:
        """
        Busca produtos pelo título
        
        Requisição:
            método: "buscar_por_titulo"
            argumentos: {"titulo": "Clean"}
        
        Retorna:
            Lista de produtos encontrados
        """
        return self._chamar_remoto("buscar_por_titulo", {"titulo": titulo}) or []
    
    def adicionar_produto(self, tipo: str, **kwargs) -> dict:
        """
        Adiciona um novo produto à loja
        
        Args:
            tipo: Tipo de produto ("Livro", "CD", "Ebook", "Apostila")
            **kwargs: Atributos do produto
        
        Requisição:
            método: "adicionar_produto"
            argumentos: {"tipo": "Livro", "codigo": "L100", ...}
        
        Retorna:
            Dicionário do produto adicionado
        """
        args = {"tipo": tipo, **kwargs}
        return self._chamar_remoto("adicionar_produto", args)
    
    def remover_produto(self, codigo: str) -> dict:
        """
        Remove um produto da loja
        
        Requisição:
            método: "remover_produto"
            argumentos: {"codigo": "L100"}
        
        Retorna:
            Dicionário do produto removido
        """
        return self._chamar_remoto("remover_produto", {"codigo": codigo})
    
    def produtos_trocaveis(self) -> list:
        """
        Lista produtos que podem ser trocados
        
        Retorna:
            Lista de produtos trocáveis
        """
        return self._chamar_remoto("produtos_trocaveis", {}) or []
    
    def obter_nome_loja(self) -> str:
        """
        Obtém o nome da loja
        
        Retorna:
            String com o nome da loja
        """
        return self._chamar_remoto("obter_nome_loja", {}) or "Desconhecido"
    
    def atualizar_preco(self, codigo: str, novo_preco: float) -> dict:
        """
        Atualiza o preço de um produto
        
        Requisição:
            método: "atualizar_preco"
            argumentos: {"codigo": "L001", "novo_preco": 150.00}
        
        Retorna:
            Dicionário do produto atualizado
        """
        return self._chamar_remoto("atualizar_preco", {
            "codigo": codigo,
            "novo_preco": novo_preco
        })


# ============================================================================
# FUNÇÕES DE EXIBIÇÃO
# ============================================================================

def imprimir_produto(produto: dict) -> None:
    """
    Imprime um produto de forma formatada
    
    Args:
        produto: Dicionário com dados do produto
    """
    if not produto:
        print("  [Produto não encontrado]")
        return
    
    print(f"\n  ┌─────────────────────────────┐")
    print(f"  │ ID:       {produto.get('codigo', 'N/A'):<18}│")
    print(f"  │ Título:   {produto.get('titulo', 'N/A'):<18}│")
    print(f"  │ Tipo:     {produto.get('tipo', 'N/A'):<18}│")
    print(f"  │ Preço:    R$ {produto.get('preco', 0):<14.2f}│")
    
    # Imprimir atributos específicos por tipo
    tipo = produto.get('tipo', '')
    if tipo == 'Livro':
        print(f"  │ Autor:    {produto.get('autor', 'N/A'):<18}│")
    elif tipo == 'CD':
        print(f"  │ Artista:  {produto.get('artista', 'N/A'):<18}│")
    elif tipo == 'Ebook':
        print(f"  │ Formato:  {produto.get('formato', 'N/A'):<18}│")
    elif tipo == 'Apostila':
        print(f"  │ Discipl.: {produto.get('disciplina', 'N/A'):<18}│")
    
    print(f"  └─────────────────────────────┘")


# ============================================================================
# MENU INTERATIVO
# ============================================================================

def menu_principal(cliente: ClienteLoja) -> None:
    """
    Menu interativo do cliente
    
    Permite ao usuário invocar os métodos remotos de forma interativa
    """
    while True:
        print("\n" + "="*70)
        print("CLIENTE RMI - LOJA VIRTUAL")
        print("="*70)
        
        # Obter nome da loja (remoto)
        nome_loja = cliente.obter_nome_loja()
        print(f"\nLoja: {nome_loja}")
        
        print("\n[1] Listar todos os produtos")
        print("[2] Buscar produto por código")
        print("[3] Buscar produtos por título")
        print("[4] Adicionar novo produto")
        print("[5] Remover produto")
        print("[6] Listar produtos trocáveis")
        print("[7] Atualizar preço de produto")
        print("[0] Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            # LISTAR PRODUTOS
            print("\n[*] Listando produtos...")
            produtos = cliente.listar_produtos()
            if produtos:
                print(f"\n[✓] {len(produtos)} produtos encontrados:\n")
                for p in produtos:
                    imprimir_produto(p)
            else:
                print("[!] Nenhum produto disponível")
        
        elif opcao == "2":
            # BUSCAR POR CÓDIGO
            codigo = input("\nDigite o código do produto: ").strip()
            print("[*] Buscando...")
            produto = cliente.buscar_por_codigo(codigo)
            if produto:
                print("\n[✓] Produto encontrado:")
                imprimir_produto(produto)
            else:
                print("[!] Produto não encontrado")
        
        elif opcao == "3":
            # BUSCAR POR TÍTULO
            titulo = input("\nDigite o título (ou parte dele): ").strip()
            print("[*] Buscando...")
            produtos = cliente.buscar_por_titulo(titulo)
            if produtos:
                print(f"\n[✓] {len(produtos)} produtos encontrados:\n")
                for p in produtos:
                    imprimir_produto(p)
            else:
                print("[!] Nenhum produto encontrado")
        
        elif opcao == "4":
            # ADICIONAR PRODUTO
            print("\n[*] Adicionar novo produto")
            print("    Tipos: Livro, CD, Ebook, Apostila")
            tipo = input("    Tipo: ").strip()
            codigo = input("    Código: ").strip()
            titulo = input("    Título: ").strip()
            preco_str = input("    Preço: ").strip()
            
            try:
                preco = float(preco_str)
                kwargs = {
                    "codigo": codigo,
                    "titulo": titulo,
                    "preco": preco
                }
                
                # Adicionar atributos específicos
                if tipo == "Livro":
                    kwargs["autor"] = input("    Autor: ").strip()
                elif tipo == "CD":
                    kwargs["artista"] = input("    Artista: ").strip()
                elif tipo == "Apostila":
                    kwargs["disciplina"] = input("    Disciplina: ").strip()
                
                print("\n[*] Adicionando...")
                produto = cliente.adicionar_produto(tipo, **kwargs)
                if produto:
                    print("[✓] Produto adicionado:")
                    imprimir_produto(produto)
            except ValueError:
                print("[!] Preço inválido")
        
        elif opcao == "5":
            # REMOVER PRODUTO
            codigo = input("\nDigite o código do produto a remover: ").strip()
            print("[*] Removendo...")
            produto = cliente.remover_produto(codigo)
            if produto:
                print("[✓] Produto removido:")
                imprimir_produto(produto)
            else:
                print("[!] Produto não encontrado")
        
        elif opcao == "6":
            # LISTAR TROCÁVEIS
            print("\n[*] Listando produtos trocáveis...")
            produtos = cliente.produtos_trocaveis()
            if produtos:
                print(f"\n[✓] {len(produtos)} produtos trocáveis:\n")
                for p in produtos:
                    imprimir_produto(p)
            else:
                print("[!] Nenhum produto trocável")
        
        elif opcao == "7":
            # ATUALIZAR PREÇO
            codigo = input("\nDigite o código do produto: ").strip()
            novo_preco_str = input("Digite o novo preço: ").strip()
            try:
                novo_preco = float(novo_preco_str)
                print("[*] Atualizando...")
                produto = cliente.atualizar_preco(codigo, novo_preco)
                if produto:
                    print("[✓] Preço atualizado:")
                    imprimir_produto(produto)
            except ValueError:
                print("[!] Preço inválido")
        
        elif opcao == "0":
            print("\n[*] Encerrando cliente...")
            break
        
        else:
            print("[!] Opção inválida")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    FUNÇÃO PRINCIPAL - CONECTA AO SERVIDOR E INICIA MENU
    """
    print("\n" + "="*70)
    print("CLIENTE RMI DE LOJA VIRTUAL - VERSÃO COMENTADA")
    print("="*70)
    
    try:
        # Conectar ao servidor
        print(f"\n[*] Conectando ao servidor em {HOST}:{PORTA}...")
        cliente = ClienteLoja(HOST, PORTA)
        
        # Testar conexão
        print("[*] Testando conexão...")
        nome_loja = cliente.obter_nome_loja()
        print(f"[✓] Conectado! Loja: '{nome_loja}'")
        
        # Menu interativo
        menu_principal(cliente)
        
    except Exception as e:
        print(f"[!] Erro: {e}")
        print("[!] Certifique-se de que o servidor está rodando")


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    main()
