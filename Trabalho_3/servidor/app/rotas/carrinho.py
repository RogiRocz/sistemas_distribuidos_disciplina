from fastapi import APIRouter, HTTPException
from app.dependencies import carrinho_instance, loja_instance

router = APIRouter(prefix="/carrinho", tags=["Objeto 2: Carrinho de Compras"])

@router.get("")
def ver_carrinho():
    itens = carrinho_instance.listar_itens()
    detalhes = []
    total = 0.0
    
    # Varre os códigos salvos no seu dataclass e monta o retorno em JSON
    for codigo, qtd in itens.items():
        prod = loja_instance.buscar_por_codigo(codigo)
        if prod:
            d = prod.to_dict()
            d["quantidade"] = qtd
            d["subtotal"] = prod.preco * qtd
            total += d["subtotal"]
            detalhes.append(d)
            
    return {"itens": detalhes, "valor_total": total}

@router.post("/adicionar/{codigo}")
def adicionar_ao_carrinho(codigo: str, quantidade: int = 1):
    # 1. Busca o objeto Produto real dentro do Catálogo da Loja
    prod = loja_instance.buscar_por_codigo(codigo)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto inexistente no catálogo")
    
    # 2. Passa o objeto Produto encontrado para a sua função do dataclass
    carrinho_instance.adicionar_produtos(prod, quantidade)
    return {"mensagem": f"Adicionado {quantidade}x do item '{prod.titulo}' ao carrinho"}

@router.delete("/remover/{codigo}")
def remover_do_carrinho(codigo: str):
    carrinho_instance.remover_produto(codigo)
    return {"mensagem": f"Produto {codigo} removido do carrinho"}

@router.post("/limpar")
def limpar_carrinho():
    carrinho_instance.limpar()
    return {"mensagem": "Carrinho esvaziado"}	