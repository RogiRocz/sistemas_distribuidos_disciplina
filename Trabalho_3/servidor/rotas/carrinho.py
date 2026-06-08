import os
import sys
from fastapi import APIRouter, HTTPException, Query, status
from dependencies import carrinho_instance, loja_instance

# Partindo de Trabalho_3/servidor/rotas/ para Trabalho_3/Trabalho_4/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRABALHO4_PATH = os.path.abspath(os.path.join(BASE_DIR, "../../Trabalho_4"))

if TRABALHO4_PATH not in sys.path:
    sys.path.insert(0, TRABALHO4_PATH)

# CORRIGIDO: Adicionado o import da função 'publicar_carrinho_alterado'
from evento_broker import (
    broker, 
    TOPICOS, 
    publicar_produto_novo, 
    publicar_carrinho_finalizado,
    publicar_carrinho_alterado
)

router = APIRouter(prefix="/carrinho", tags=["Objeto 2: Carrinho de Compras"])

@router.get("/")
def ver_carrinho():
    itens = carrinho_instance.listar_itens()
    detalhes = []
    total = 0.0
    total_itens = 0
    
    for codigo, qtd in itens.items():
        prod = loja_instance.buscar_por_codigo(codigo)
        if prod:
            subtotal = prod.preco * qtd
            total += subtotal
            total_itens += qtd
            detalhes.append({**prod.to_dict(), "quantidade": qtd, "subtotal": subtotal})
            
    return {"itens": detalhes, "quantidade_total": total_itens, "valor_total": total}

@router.post("/adicionar/{codigo}", status_code=status.HTTP_201_CREATED)
def adicionar_ao_carrinho(codigo: str, quantidade: int = Query(1, ge=1)):
    prod = loja_instance.buscar_por_codigo(codigo)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto inexistente no catálogo")
    
    carrinho_instance.adicionar_produtos(prod, quantidade)
    
    carrinho_atual = ver_carrinho()
    
    # CORRIGIDO: Substituído pelo método centralizado do broker
    publicar_carrinho_alterado(
        usuario="anonimo",
        acao="item_adicionado",
        detalhes={
            "codigo_produto": codigo,
            "produto": prod.to_dict(),
            "quantidade_adicionada": quantidade,
            "carrinho": carrinho_atual
        }
    )
    
    return {
        "mensagem": f"Adicionado {quantidade}x do item '{prod.titulo}' ao carrinho",
        "produto": prod.to_dict(),
        "quantidade": quantity # Nota: ajustado se houver dependência, mantendo o padrão
    }

@router.delete("/remover/{codigo}")
def remover_do_carrinho(codigo: str):
    itens_atuais = carrinho_instance.listar_itens()
    if codigo not in itens_atuais:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não está no carrinho")

    carrinho_instance.remover_produto(codigo)
    
    carrinho_atual = ver_carrinho()
    
    # CORRIGIDO: Substituído pelo método centralizado do broker
    publicar_carrinho_alterado(
        usuario="anonimo",
        acao="item_removido",
        detalhes={
            "codigo_produto": codigo,
            "carrinho": carrinho_atual
        }
    )
    
    return {"mensagem": f"Produto {codigo} removido do carrinho"}

@router.post("/limpar")
def limpar_carrinho():
    carrinho_antes = ver_carrinho()
    total = carrinho_antes["valor_total"]
    quantidade = carrinho_antes["quantidade_total"]
    
    carrinho_instance.limpar()
    
    if quantidade > 0:
        # CORRIGIDO: Agora dispara o evento correto de alteração/limpeza do carrinho no Pub/Sub
        publicar_carrinho_alterado(
            usuario="anonimo",
            acao="limpar",
            detalhes={
                "carrinho_anterior": carrinho_antes
            }
        )
        
        # Mantido caso seu fluxo de negócios exija tratar uma limpeza como finalização de pedido
        publicar_carrinho_finalizado(
            usuario="anonimo",
            total=total,
            itens=len(carrinho_antes["itens"])
        )
    
    return {"mensagem": "Carrinho esvaziado", "itens": 0}

@router.get("/resumo")
def resumo_carrinho():
    carrinho = ver_carrinho()
    return {
        "quantidade_itens_distintos": len(carrinho["itens"]),
        "quantidade_total": carrinho["quantidade_total"],
        "valor_total": carrinho["valor_total"]
    }