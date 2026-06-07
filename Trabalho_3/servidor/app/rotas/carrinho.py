from fastapi import APIRouter, HTTPException, Query, status
from app.dependencies import carrinho_instance, loja_instance

router = APIRouter(prefix="/carrinho", tags=["Objeto 2: Carrinho de Compras"])

@router.get("/")
def ver_carrinho():
    itens = carrinho_instance.listar_itens()
    detalhes = []
    total = 0.0
    total_itens = 0
    
    # Varre os códigos salvos no seu dataclass e monta o retorno em JSON
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
    # 1. Busca o objeto Produto real dentro do Catálogo da Loja
    prod = loja_instance.buscar_por_codigo(codigo)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto inexistente no catálogo")
    
    # 2. Passa o objeto Produto encontrado para a sua função do dataclass
    carrinho_instance.adicionar_produtos(prod, quantidade)
    return {
        "mensagem": f"Adicionado {quantidade}x do item '{prod.titulo}' ao carrinho",
        "produto": prod.to_dict(),
        "quantidade": quantidade
    }

@router.delete("/remover/{codigo}")
def remover_do_carrinho(codigo: str):
    itens_atuais = carrinho_instance.listar_itens()
    if codigo not in itens_atuais:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não está no carrinho")

    carrinho_instance.remover_produto(codigo)
    return {"mensagem": f"Produto {codigo} removido do carrinho"}

@router.post("/limpar")
def limpar_carrinho():
    carrinho_instance.limpar()
    return {"mensagem": "Carrinho esvaziado", "itens": 0}


@router.get("/resumo")
def resumo_carrinho():
    carrinho = ver_carrinho()
    return {
        "quantidade_itens_distintos": len(carrinho["itens"]),
        "quantidade_total": carrinho["quantidade_total"],
        "valor_total": carrinho["valor_total"]
    }