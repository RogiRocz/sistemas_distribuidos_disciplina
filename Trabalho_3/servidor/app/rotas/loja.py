from fastapi import APIRouter, HTTPException, Query, status
from app.dependencies import loja_instance
from app.esquemas.sebo import LivroCreate, CDCreate, EbookCreate, ApostilaCreate, AtualizarPreco
from app.modelos.livro import Livro
from app.modelos.cd import CD
from app.modelos.ebook import Ebook
from app.modelos.apostila import Apostila
import sys
import os


sys.path.insert(0, os.path.abspath('../../Trabalho_4'))
from evento_broker import (
    publicar_produto_novo, 
    TOPICOS,
    broker
)

router = APIRouter(prefix="/loja", tags=["Objeto 1: Catálogo da Loja"])

@router.get("/nome")
def obter_nome_loja():
    return {"nome": loja_instance.nome}

@router.get("/produtos")
def listar_produtos():
    return [p.to_dict() for p in loja_instance.listar_produtos()]

@router.get("/produtos/trocaveis")
def listar_produtos_trocaveis():
    return [p.to_dict() for p in loja_instance.produtos_trocaveis()]

@router.get("/produtos/{codigo}")
def buscar_por_codigo(codigo: str):
    produto = loja_instance.buscar_por_codigo(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não encontrado")
    return produto.to_dict()

@router.get("/produtos/buscar/{titulo}")
def buscar_por_titulo(titulo: str):
    return [p.to_dict() for p in loja_instance.buscar_por_titulo(titulo)]


@router.get("/produtos/buscar")
def buscar_por_titulo_query(titulo: str = Query(..., min_length=1)):
    return [p.to_dict() for p in loja_instance.buscar_por_titulo(titulo)]

@router.post("/produtos/livro", status_code=status.HTTP_201_CREATED)
def adicionar_livro(schema: LivroCreate):
    livro = Livro(**schema.model_dump())
    loja_instance.adicionar_produto(livro)
    
    # Publica evento de novo produto
    publicar_produto_novo(livro.to_dict())
    
    return {"status": "sucesso", "produto": livro.to_dict()}

@router.post("/produtos/cd", status_code=status.HTTP_201_CREATED)
def adicionar_cd(schema: CDCreate):
    cd = CD(**schema.model_dump())
    loja_instance.adicionar_produto(cd)
    
    # Publica evento de novo produto
    publicar_produto_novo(cd.to_dict())
    
    return {"status": "sucesso", "produto": cd.to_dict()}

@router.post("/produtos/ebook", status_code=status.HTTP_201_CREATED)
def adicionar_ebook(schema: EbookCreate):
    ebook = Ebook(**schema.model_dump())
    loja_instance.adicionar_produto(ebook)
    
    # Publica evento de novo produto
    publicar_produto_novo(ebook.to_dict())
    
    return {"status": "sucesso", "produto": ebook.to_dict()}

@router.post("/produtos/apostila", status_code=status.HTTP_201_CREATED)
def adicionar_apostila(schema: ApostilaCreate):
    apostila = Apostila(**schema.model_dump())
    loja_instance.adicionar_produto(apostila)
    
    # Publica evento de novo produto
    publicar_produto_novo(apostila.to_dict())
    
    return {"status": "sucesso", "produto": apostila.to_dict()}

@router.patch("/produtos/{codigo}/preco")
def atualizar_preco(codigo: str, schema: AtualizarPreco):
    produto = loja_instance.buscar_por_codigo(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não encontrado")
    
    # Publica evento de atualização de preço
    preco_anterior = produto.preco
    produto.preco = schema.novo_preco
    
    broker.publicar("sebo:produto:atualizado", {
        "tipo": "preco_alterado",
        "codigo": codigo,
        "preco_anterior": preco_anterior,
        "preco_novo": schema.novo_preco,
        "produto": produto.to_dict()
    })
    
    return {"status": "Preço atualizado", "produto": produto.to_dict()}

@router.delete("/produtos/{codigo}")
def remover_produto(codigo: str):
    produto = loja_instance.remover_produto(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não encontrado")
    
    # Publica evento de produto deletado
    broker.publicar("sebo:produto:deletado", {
        "tipo": "produto_deletado",
        "codigo": codigo,
        "produto_removido": produto.to_dict()
    })
    
    return {"status": "Removido", "produto": produto.to_dict()}


@router.get("/estatisticas")
def estatisticas_catalogo():
    produtos = loja_instance.listar_produtos()
    por_tipo = {}

    for produto in produtos:
        por_tipo[produto.tipo] = por_tipo.get(produto.tipo, 0) + 1

    return {
        "total_produtos": len(produtos),
        "por_tipo": por_tipo,
        "nomes_disponiveis": [produto.titulo for produto in produtos]
    }