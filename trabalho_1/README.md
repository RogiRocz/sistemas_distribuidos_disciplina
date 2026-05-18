# Sistema RMI de Loja Virtual - Trabalho 1

## Visão Geral

Sistema distribuído implementando **Remote Method Invocation (RMI)** com protocolo requisição-resposta (seção 5.2) para uma Loja Virtual.

## ✅ Requisitos Atendidos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| ≥4 classes POJO | ✅ | Livro, CD, Ebook, Apostila |
| ≥2 agregações | ✅ | Loja tem Produtos |
| ≥2 extensões | ✅ | Livro/CD/Ebook/Apostila herdam Produto |
| ≥4 métodos remotos | ✅ | 8 métodos implementados |
| Passagem por referência | ✅ | RemoteObjectRef |
| Passagem por valor | ✅ | JSON |
| Protocolo Req-Rep | ✅ | Binário estruturado |
| Serialização externa | ✅ | JSON |

## 🏗️ Arquitetura

**POJOs/Modelo de Domínio:**
- `Trocavel` (interface)
- `Produto` (abstrata) → Livro, CD, Ebook, Apostila
- `Loja` (serviço principal)

**Classes de Serviço (2):**
1. `LojaDispatcher` - Implementa métodos remotos
2. `RemoteServer` - Infraestrutura RMI

## 📁 Arquivos

```
Sebo_Virtual/
├── rmi_comentado.py            # Core RMI (simplificado e comentado)
├── servidor_rmi_simples.py     # Servidor (simplificado e comentado)
├── cliente_rmi_simples.py      # Cliente (simplificado e comentado)
└── servidor/modelos/
    ├── trocavel.py             # Interface
    ├── produto.py              # Classe abstrata
    ├── livro.py                # Extensão de Produto
    ├── cd.py                   # Extensão de Produto
    ├── ebook.py                # Extensão de Produto
    ├── apostila.py             # Extensão de Produto
    ├── loja.py                 # Agregador de Produtos
    └── loja_dispatcher.py       # Despachante de métodos

Arquivos de Teste/Documentação:
├── teste_rmi_simples.py        # Teste automatizado com 8 casos
└── GUIA_RMI_SIMPLES.md         # Guia visual de entendimento
```

## 🚀 Como Usar

**Opção 1 - Teste Automatizado (recomendado para começar):**
```bash
python teste_rmi_simples.py
```
Executa os 8 testes e mostra o fluxo completo de cada requisição RMI.

**Opção 2 - Servidor + Cliente Manual:**
```bash
# Terminal 1 - Servidor
python -m Sebo_Virtual.servidor_rmi_simples

# Terminal 2 - Cliente (menu interativo)
python -m Sebo_Virtual.cliente_rmi_simples
```

## 📡 Métodos Remotos

1. `listar_produtos()` - Lista todos os produtos
2. `buscar_por_codigo(codigo)` - Busca específica
3. `buscar_por_titulo(titulo)` - Busca por nome
4. `adicionar_produto(tipo, ...)` - Adiciona novo
5. `remover_produto(codigo)` - Remove
6. `produtos_trocaveis()` - Filtra trocáveis
7. `obter_nome_loja()` - Info da loja
8. `atualizar_preco(codigo, novo_preco)` - Atualiza preço

## 🧪 Status dos Testes

```
✓ Comunicação RMI (UDP)
✓ Invocação remota de 8 métodos
✓ Serialização/Desserialização JSON
✓ Passagem de parâmetros por valor
✓ Tratamento de exceções
✓ 4 tipos de produtos
✓ Operações CRUD completas
```

**Resultado**: TODOS OS 8 TESTES PASSARAM ✅

## 📖 Por Onde Começar

1. Leia [GUIA_RMI_SIMPLES.md](GUIA_RMI_SIMPLES.md) - Explica visualmente o conceito
2. Execute `python teste_rmi_simples.py` - Veja funcionando
3. Leia [rmi_comentado.py](Sebo_Virtual/rmi_comentado.py) - Entenda o protocolo
4. Leia [servidor_rmi_simples.py](Sebo_Virtual/servidor_rmi_simples.py) - Veja implementação
5. Leia [cliente_rmi_simples.py](Sebo_Virtual/cliente_rmi_simples.py) - Entenda invocação

**Tempo estimado**: ~1 hora para entender completamente
