from fastapi import APIRouter, HTTPException, Query, status
from app.dependencies import loja_instance
from app.esquemas.sebo import LivroCreate, CDCreate, EbookCreate, ApostilaCreate, AtualizarPreco
from app.modelos.livro import Livro
from app.modelos.cd import CD
from app.modelos.ebook import Ebook
from app.modelos.apostila import Apostila

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
    return {"status": "sucesso", "produto": livro.to_dict()}

@router.post("/produtos/cd", status_code=status.HTTP_201_CREATED)
def adicionar_cd(schema: CDCreate):
    cd = CD(**schema.model_dump())
    loja_instance.adicionar_produto(cd)
    return {"status": "sucesso", "produto": cd.to_dict()}

@router.post("/produtos/ebook", status_code=status.HTTP_201_CREATED)
def adicionar_ebook(schema: EbookCreate):
    ebook = Ebook(**schema.model_dump())
    loja_instance.adicionar_produto(ebook)
    return {"status": "sucesso", "produto": ebook.to_dict()}

@router.post("/produtos/apostila", status_code=status.HTTP_201_CREATED)
def adicionar_apostila(schema: ApostilaCreate):
    apostila = Apostila(**schema.model_dump())
    loja_instance.adicionar_produto(apostila)
    return {"status": "sucesso", "produto": apostila.to_dict()}

@router.patch("/produtos/{codigo}/preco")
def atualizar_preco(codigo: str, schema: AtualizarPreco):
    produto = loja_instance.buscar_por_codigo(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não encontrado")
    produto.preco = schema.novo_preco
    return {"status": "Preço atualizado", "produto": produto.to_dict()}

@router.delete("/produtos/{codigo}")
def remover_produto(codigo: str):
    produto = loja_instance.remover_produto(codigo)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto {codigo} não encontrado")
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