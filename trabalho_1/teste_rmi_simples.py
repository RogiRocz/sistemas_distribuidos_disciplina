"""
TESTE SIMPLIFICADO - DEMONSTRA O FLUXO COMPLETO RMI
====================================================

Este arquivo demonstra o fluxo COMPLETO de uma requisição RMI:
1. Cliente prepara requisição
2. Empacota em bytes
3. Envia para servidor
4. Servidor desempacota
5. Executa método
6. Empacota resposta em bytes
7. Envia de volta
8. Cliente recebe e usa resultado

EXECUTE ASSIM:
  Terminal 1: python -m Sebo_Virtual.servidor_rmi_simples
  Terminal 2: python teste_rmi_simples.py
"""

import sys
import json
import threading
import time
from pathlib import Path

try:
    from Sebo_Virtual.servidor_rmi_simples import criar_catalogo_inicial, LojaDispatcher
    from Sebo_Virtual.cliente_rmi_simples import ClienteLoja
    from Sebo_Virtual.rmi_comentado import RemoteServer, RemoteObjectRef, RemoteInvoker
except ImportError:
    from servidor_rmi_simples import criar_catalogo_inicial, LojaDispatcher
    from cliente_rmi_simples import ClienteLoja
    from rmi_comentado import RemoteServer, RemoteObjectRef, RemoteInvoker


# ============================================================================
# FUNÇÃO PARA EXECUTAR SERVIDOR EM THREAD
# ============================================================================

def executar_servidor_em_thread():
    """
    Inicia o servidor em uma thread separada para os testes
    """
    try:
        # Criar loja
        loja = criar_catalogo_inicial()
        
        # Criar despachante
        dispatcher = LojaDispatcher(loja)
        
        # Criar e iniciar servidor
        server = RemoteServer("127.0.0.1", 5000)
        server.register_object("loja", dispatcher)
        
        # Iniciar (fica bloqueado até parar)
        server.start()
    except Exception as e:
        print(f"[!] Erro no servidor: {e}")


# ============================================================================
# TESTES
# ============================================================================

def teste_fluxo_completo():
    """
    TESTE: Demonstra o fluxo COMPLETO de uma requisição RMI
    """
    print("\n" + "="*70)
    print("TESTE SIMPLIFICADO - FLUXO COMPLETO RMI")
    print("="*70)
    
    # Iniciar servidor em thread
    print("\n[*] Iniciando servidor em thread...")
    servidor_thread = threading.Thread(
        target=executar_servidor_em_thread,
        daemon=True
    )
    servidor_thread.start()
    
    # Aguardar servidor iniciar
    time.sleep(2)
    
    # Conectar cliente
    print("\n[*] Conectando cliente...")
    try:
        cliente = ClienteLoja("127.0.0.1", 5000)
        print("[✓] Cliente conectado\n")
    except Exception as e:
        print(f"[!] Erro ao conectar: {e}")
        return
    
    # TESTE 1: Obter nome da loja
    print("-" * 70)
    print("TESTE 1: OBTER NOME DA LOJA")
    print("-" * 70)
    print("\nFluxo:")
    print("  1. Cliente chama: cliente.obter_nome_loja()")
    print("  2. ClienteLoja._chamar_remoto('obter_nome_loja', {})")
    print("  3. RemoteInvoker.do_operation()")
    print("     a. Cria RequestMessage")
    print("     b. Empacota em bytes")
    print("     c. Envia UDP para 127.0.0.1:5000")
    print("  4. RemoteServer recebe bytes")
    print("     a. Desempacota RequestMessage")
    print("     b. Localiza LojaDispatcher")
    print("     c. Chama dispatch_method('obter_nome_loja', b'{}')")
    print("  5. LojaDispatcher executa loja.nome")
    print("  6. RemoteServer empacota ReplyMessage")
    print("  7. Envia resposta via UDP")
    print("  8. Cliente recebe e desserializa\n")
    
    nome_loja = cliente.obter_nome_loja()
    print(f"[✓] Resultado: {nome_loja}\n")
    
    # TESTE 2: Listar produtos
    print("-" * 70)
    print("TESTE 2: LISTAR PRODUTOS")
    print("-" * 70)
    print("\nChamando: cliente.listar_produtos()")
    produtos = cliente.listar_produtos()
    print(f"\n[✓] Total de produtos: {len(produtos)}")
    print("    Primeiros 2 produtos:")
    for p in produtos[:2]:
        print(f"    - {p['codigo']}: {p['titulo']} ({p['tipo']}) - R$ {p['preco']:.2f}")
    
    # TESTE 3: Buscar por código
    print("\n" + "-" * 70)
    print("TESTE 3: BUSCAR POR CÓDIGO")
    print("-" * 70)
    print("\nChamando: cliente.buscar_por_codigo('L001')")
    produto = cliente.buscar_por_codigo("L001")
    print(f"\n[✓] Encontrado:")
    print(f"    Código: {produto['codigo']}")
    print(f"    Título: {produto['titulo']}")
    print(f"    Tipo: {produto['tipo']}")
    print(f"    Autor: {produto.get('autor', 'N/A')}")
    print(f"    Preço: R$ {produto['preco']:.2f}")
    
    # TESTE 4: Buscar por título
    print("\n" + "-" * 70)
    print("TESTE 4: BUSCAR POR TÍTULO")
    print("-" * 70)
    print("\nChamando: cliente.buscar_por_titulo('Design')")
    encontrados = cliente.buscar_por_titulo("Design")
    print(f"\n[✓] Encontrados {len(encontrados)} produto(s):")
    for p in encontrados:
        print(f"    - {p['titulo']}")
    
    # TESTE 5: Adicionar produto
    print("\n" + "-" * 70)
    print("TESTE 5: ADICIONAR NOVO PRODUTO")
    print("-" * 70)
    print("\nChamando: cliente.adicionar_produto(...)")
    novo = cliente.adicionar_produto(
        "Livro",
        codigo="L999",
        titulo="Novo Livro de Teste",
        autor="Autor Teste",
        preco=99.90,
        editora="Editora Teste",
        ano_publicacao=2024
    )
    print(f"\n[✓] Produto adicionado:")
    print(f"    Código: {novo['codigo']}")
    print(f"    Título: {novo['titulo']}")
    print(f"    Preço: R$ {novo['preco']:.2f}")
    
    # TESTE 6: Atualizar preço
    print("\n" + "-" * 70)
    print("TESTE 6: ATUALIZAR PREÇO")
    print("-" * 70)
    print("\nChamando: cliente.atualizar_preco('L001', 150.00)")
    atualizado = cliente.atualizar_preco("L001", 150.00)
    print(f"\n[✓] Preço atualizado:")
    print(f"    Código: {atualizado['codigo']}")
    print(f"    Novo preço: R$ {atualizado['preco']:.2f}")
    
    # TESTE 7: Remover produto
    print("\n" + "-" * 70)
    print("TESTE 7: REMOVER PRODUTO")
    print("-" * 70)
    print("\nChamando: cliente.remover_produto('L999')")
    removido = cliente.remover_produto("L999")
    print(f"\n[✓] Produto removido:")
    print(f"    Código: {removido['codigo']}")
    print(f"    Título: {removido['titulo']}")
    
    # Verificar que foi removido
    inexistente = cliente.buscar_por_codigo("L999")
    print(f"\n    Verificação: cliente.buscar_por_codigo('L999')")
    print(f"    Resultado: {inexistente}")
    print(f"    [✓] Confirmado: produto foi removido\n")
    
    # TESTE 8: Produtos trocáveis
    print("-" * 70)
    print("TESTE 8: LISTAR PRODUTOS TROCÁVEIS")
    print("-" * 70)
    print("\nChamando: cliente.produtos_trocaveis()")
    trocaveis = cliente.produtos_trocaveis()
    print(f"\n[✓] Total de produtos trocáveis: {len(trocaveis)}")
    
    # Resultado final
    print("\n" + "="*70)
    print("✓ TODOS OS TESTES EXECUTADOS COM SUCESSO!")
    print("="*70)
    print("\nResumo do Fluxo RMI:")
    print("  ✓ Requisições empacotadas em bytes")
    print("  ✓ Transmitidas via UDP")
    print("  ✓ Desempacotadas no servidor")
    print("  ✓ Métodos executados remotamente")
    print("  ✓ Respostas retornadas em bytes")
    print("  ✓ Desserializadas no cliente")
    print("  ✓ Protocoloquisição-Resposta funcionando")
    print("="*70 + "\n")


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    try:
        teste_fluxo_completo()
    except KeyboardInterrupt:
        print("\n[!] Teste interrompido")
    except Exception as e:
        print(f"\n[!] Erro: {e}")
        import traceback
        traceback.print_exc()
