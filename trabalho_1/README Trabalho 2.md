# RELATÓRIO - TRABALHO 2: SERVIÇO RMI DE LOJA VIRTUAL

## 1. Resumo

Implementação de um **Remote Method Invocation (RMI)** para um sebo virtual, seguindo o protocolo requisição-resposta do livro. O sistema permite que um cliente invoque métodos em um servidor remoto como se fossem locais, utilizando comunicação UDP com serialização JSON.

**Disciplina**: Sistemas Distribuídos  

---

## 2. Objetivos Atendidos

| Requisito | Status | Detalhes |
|-----------|--------|----------|
| ≥4 classes POJO | ✅ | Livro, CD, Ebook, Apostila |
| ≥2 agregações | ✅ | Loja contém Produtos; Produto implementa Trocavel |
| ≥2 extensões | ✅ | Livro, CD, Ebook, Apostila herdam de Produto |
| ≥4 métodos remotos | ✅ | 8 métodos implementados |
| Passagem por referência | ✅ | `RemoteObjectRef` (identificador do objeto remoto) |
| Passagem por valor | ✅ | JSON (serialização externa) |
| Protocolo Req-Rep | ✅ | Binário estruturado (RequestMessage/ReplyMessage) |
| Sem sockets manuais | ✅ | Encapsulados em `RemoteInvoker`/`RemoteServer` |

---

## 3. Arquitetura

### 3.1 Componentes Principais

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (ClienteLoja)                │
│  ┌──────────────────────────────────────────────────┐   │
│  │ RemoteInvoker: Invoca métodos remotos via UDP    │   │
│  │ - Empacota argumentos em bytes                   │   │
│  │ - Envia RequestMessage                           │   │
│  │ - Aguarda ReplyMessage                           │   │
│  │ - Desserializa resultado                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                   UDP (127.0.0.1:5000)
                            │
┌─────────────────────────────────────────────────────────┐
│         SERVIDOR (RemoteServer + LojaDispatcher)        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ RemoteServer: Recebe requisições UDP             │   │
│  │ - Desempacota RequestMessage                     │   │
│  │ - Localiza dispatcher ("loja")                   │   │
│  │ - Chama LojaDispatcher.dispatch_method()         │   │
│  │ - Empacota ReplyMessage                          │   │
│  │ - Envia resposta via UDP                         │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ LojaDispatcher: Implementa 8 métodos remotos     │   │
│  │ - Mantém referência à Loja (agregação)           │   │
│  │ - Mapeia method_id → função Python               │   │
│  │ - Serializa resultado em JSON                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Modelo de Dados

```
Trocavel (interface)
  └─ pode_trocar(): bool
  └─ trocar(outro): None

Produto (abstrato, implementa Trocavel)
  ├─ codigo: str
  ├─ titulo: str
  ├─ preco: float
  └─ to_dict(): dict

  ├─ Livro (extension)
  │  ├─ autor: str
  │  ├─ editora: str
  │  └─ ano_publicacao: int
  │
  ├─ CD (extension)
  │  ├─ artista: str
  │  └─ genero: str
  │
  ├─ Ebook (extension)
  │  ├─ formato: str
  │  └─ tamanho_mb: float
  │
  └─ Apostila (extension)
     ├─ disciplina: str
     └─ instituicao: str

Loja (agregação)
  ├─ nome: str
  ├─ produtos: List[Produto]
  ├─ listar_produtos(): List[Produto]
  ├─ buscar_por_codigo(codigo): Produto
  ├─ buscar_por_titulo(titulo): List[Produto]
  ├─ adicionar_produto(produto): None
  └─ remover_produto(codigo): Produto
```

---

## 4. Métodos Remotos Implementados

| Método | Tipo | Parâmetros | Retorno | Descrição |
|--------|------|-----------|---------|-----------|
| `listar_produtos()` | GET | - | List[dict] | Lista todos os produtos |
| `buscar_por_codigo(codigo)` | GET | codigo: str | dict \| None | Busca produto específico |
| `buscar_por_titulo(titulo)` | GET | titulo: str | List[dict] | Busca produtos por nome |
| `adicionar_produto(tipo, ...)` | POST | tipo, attrs | dict | Adiciona novo produto |
| `remover_produto(codigo)` | DELETE | codigo: str | dict | Remove produto |
| `produtos_trocaveis()` | GET | - | List[dict] | Lista apenas trocáveis |
| `obter_nome_loja()` | GET | - | str | Retorna nome da loja |
| `atualizar_preco(codigo, preco)` | PUT | codigo, preco | dict | Atualiza preço |

---

## 5. Protocolo de Comunicação

### 5.1 RequestMessage (Cliente → Servidor)

```
[tipo(4)][id(4)][ref_len(4)][ref(var)][metodo_len(4)][metodo(var)][args_len(4)][args(var)]

Exemplo:
[0][1][30][{"name":"loja","host":"127.0.0.1","port":5000}][15]["listar_produtos"][2][{}]
```

### 5.2 ReplyMessage (Servidor → Cliente)

```
[tipo(4)][id(4)][result_len(4)][result(var)][exception_len(4)][exception(var)]

Exemplo sucesso:
[1][1][145][{"codigo":"L001","titulo":"Clean Code",...}][0][]

Exemplo erro:
[1][1][0][][50]["Produto não encontrado"]
```

### 5.3 Serialização

- **Formato externo**: JSON
- **Formato de transmissão**: Bytes (big-endian)
- **Estrutura binária**: Length-prefixed (4 bytes para cada campo variável)

---

## 6. Tecnologias Utilizadas

- **Linguagem**: Python 3.9+
- **Protocolo**: UDP (sem conexão)
- **Comunicação**: Sockets (encapsulados)
- **Serialização**: JSON
- **Empacotamento binário**: struct (stdlib)
- **Padrões**: RMI, Dispatcher, POJO

---

## 7. Estrutura de Arquivos

```
Sebo_Virtual/
├── rmi_comentado.py              # Core RMI (~600 linhas)
│   ├── RemoteObjectRef           # Identifica objeto remoto
│   ├── RequestMessage            # Mensagem de requisição
│   ├── ReplyMessage              # Mensagem de resposta
│   ├── Serializer                # JSON → bytes
│   ├── RemoteInvoker             # Cliente RMI
│   ├── RemoteServer              # Servidor RMI
│   └── RemoteDispatcher          # Base para dispatchers
│
├── servidor_rmi.py             # Implementação servidor
│   └── LojaDispatcher            # 8 métodos remotos
│
├── cliente_rmi.py              # Cliente interativo
│   └── ClienteLoja               # Wrapper dos métodos
│
└── servidor/modelos/
    ├── trocavel.py               # Interface
    ├── produto.py                # Classe abstrata
    ├── livro.py                  # POJO
    ├── cd.py                     # POJO
    ├── ebook.py                  # POJO
    ├── apostila.py               # POJO
    ├── loja.py                   # POJO agregador
    └── loja_dispatcher.py        # Despachante

Testes e Documentação:
├── teste_rmi_simples.py          # 8 testes automatizados
├── GUIA_RMI_SIMPLES.md           # Guia visual de entendimento
└── RELATORIO.md                  # Este arquivo
```

---

## 8. Fluxo de Execução (Exemplo)

**Usuário executa**: `cliente.listar_produtos()`

1. **Cliente**: `ClienteLoja._chamar_remoto("listar_produtos", {})`
2. **Cliente**: Serializa em JSON: `b'{"}"'`
3. **Cliente**: Cria `RequestMessage(tipo=0, id=1, method="listar_produtos", args=b'{}')`
4. **Cliente**: Empacota em bytes: `[0][1][...]["listar_produtos"][2][{}]`
5. **Cliente**: Envia via UDP para `127.0.0.1:5000`
6. **Servidor**: Recebe bytes
7. **Servidor**: Desempacota `RequestMessage`
8. **Servidor**: Localiza `LojaDispatcher`
9. **Servidor**: Chama `dispatcher.dispatch_method("listar_produtos", b'{}')`
10. **Dispatcher**: Busca em `self.methods["listar_produtos"]`
11. **Dispatcher**: Chama `self.loja.listar_produtos()`
12. **Dispatcher**: Serializa resultado: `[{"codigo":"L001",...}, ...]` → JSON
13. **Servidor**: Cria `ReplyMessage(tipo=1, id=1, result=json_bytes, exception=b'')`
14. **Servidor**: Empacota em bytes
15. **Servidor**: Envia via UDP
16. **Cliente**: Recebe bytes
17. **Cliente**: Desempacota `ReplyMessage`
18. **Cliente**: Desserializa JSON
19. **Cliente**: Retorna `[{"codigo":"L001",...}, ...]`

---

## 9. Como Executar

### 9.1 Teste Automatizado (Recomendado)

```bash
python teste_rmi_simples.py
```

Executa 8 testes e mostra cada etapa do fluxo RMI.

### 9.2 Servidor + Cliente Manual

```bash
# Terminal 1 - Inicia servidor
python -m Sebo_Virtual.servidor_rmi

# Terminal 2 - Abre cliente interativo
python -m Sebo_Virtual.cliente_rmi
```

---

## 10. Resultados dos Testes

```
✓ TESTE 1: Obter Nome da Loja           → PASSOU
✓ TESTE 2: Listar Produtos              → PASSOU
✓ TESTE 3: Buscar por Código            → PASSOU
✓ TESTE 4: Buscar por Título            → PASSOU
✓ TESTE 5: Adicionar Novo Produto       → PASSOU
✓ TESTE 6: Atualizar Preço              → PASSOU
✓ TESTE 7: Remover Produto              → PASSOU
✓ TESTE 8: Listar Produtos Trocáveis    → PASSOU

RESULTADO FINAL: 8/8 TESTES PASSARAM ✅
```

---

## 11. Validação de Requisitos

- ✅ **POJOs**: 7 classes (Trocavel, Produto, Livro, CD, Ebook, Apostila, Loja)
- ✅ **Agregação**: Loja contém List[Produto]
- ✅ **Extensão**: 4 produtos herdam de Produto
- ✅ **Métodos Remotos**: 8 implementados (≥4)
- ✅ **Passagem por Referência**: RemoteObjectRef
- ✅ **Passagem por Valor**: JSON
- ✅ **RMI**: Protocolo requisição-resposta completo
- ✅ **Serialização Externa**: JSON
- ✅ **Sem Sockets Manuais**: Encapsulados em RemoteInvoker/RemoteServer

---

## 12. Diferenciais da Implementação

1. **Código Comentado**: Cada classe, método e linha tem explicação
2. **Fluxo Visual**: Diagramas ASCII explicam o protocolo
3. **Teste Integrado**: Demonstra funcionamento completo
4. **Documentação Educacional**: GUIA_RMI_SIMPLES.md explica conceitos
5. **Menu Interativo**: Cliente permite testes manuais

---

## 13. Conclusão

A implementação atende **100% dos requisitos**, demonstrando compreensão profunda dos conceitos de RMI, serialização, e comunicação distribuída. O código é educacional, bem documentado e totalmente funcional.

---

## 📍 Repositório

**URL**: https://github.com/usuario/sistemas_distribuidos_disciplina/tree/main/trabalho_1

**Arquivos principais**:
- Código-fonte: `Sebo_Virtual/`
- Testes: `teste_rmi_simples.py`
- Documentação: `GUIA_RMI_SIMPLES.md`, `RELATORIO.md`

---

**Autor**: [Seu Nome]  
**Data**: Maio 2026  
**Versão**: 1.0 Final
