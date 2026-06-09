# 🌐 Parte 3: Web Services e API RESTful

## 📋 Visão Geral

Nesta etapa, substituímos a camada de comunicação **RMI binária manual** (implementada no Trabalho 2) por uma **API RESTful** utilizando o framework **FastAPI**. O sistema agora utiliza o protocolo **HTTP** e serialização **JSON**, permitindo que diferentes clientes (em linguagens distintas) interajam com o Sebo Virtual de forma padronizada.

### ✨ Características da Evolução

✅ **Interoperabilidade**: O servidor agora aceita requisições de qualquer linguagem (Python, JS, Java, etc).
✅ **Passagem por Valor (JSON)**: Objetos são transmitidos em formato textual padronizado.
✅ **URIs como Referências**: Em vez de `RemoteObjectRef`, usamos rotas como `/loja` e `/carrinho` para identificar recursos.
✅ **Documentação Automática**: Swagger UI disponível nativamente em `/docs`.
✅ **Arquitetura Poliglota**: Implementação de clientes em Python e JavaScript/HTML.

---

## 🏗️ Arquitetura do Sistema

O sistema foi organizado seguindo o padrão de **3 Camadas (Controller-Service-Model)** para garantir o desacoplamento exigido:

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTES (Poliglota)                 │
│  ┌──────────────────┐    ┌──────────────────────────┐   │
│  │ Cliente Python   │    │  Cliente HTML/JS         │   │
│  │ (requests)       │    │  (Fetch API / Browser)   │   │
│  └─────────┬────────┘    └─────────────┬────────────┘   │
└────────────┼───────────────────────────┼────────────────┘
             │                           │
             ↓ Requisições HTTP/JSON     ↓
┌─────────────────────────────────────────────────────────┐
│              SERVIDOR (FastAPI / Uvicorn)               │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Rotas (API Endpoints) - Camada de Controle       │   │
│  │ • /loja      • /carrinho     • /usuarios         │   │
│  └────────────────────────┬─────────────────────────┘   │
│                           │                             │
│  ┌────────────────────────▼─────────────────────────┐   │
│  │ Objetos Distribuídos (Instâncias em Memória)     │   │
│  │ 1. Loja (Catálogo)                               │   │
│  │ 2. CarrinhoCompras (Sessão)                      │   │
│  │ 3. GerenciadorUsuarios (Autenticação)            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Objetos Distribuídos

Conforme exigido, o servidor gerencia **3 instâncias principais** que representam os estados do sistema:

1. **Objeto 1: Catálogo (Loja)**
   * Gerencia o estoque de produtos (Livro, CD, Ebook, Apostila).
   * Métodos: Adicionar, Listar, Buscar por Título/Código e Estatísticas.
2. **Objeto 2: Carrinho de Compras**
   * Mantém o estado dos itens selecionados para "compra".
   * Métodos: Adicionar item (com validação na Loja), Remover, Listar e Limpar.
3. **Objeto 3: Gerenciador de Usuários**
   * Controla autenticação e monitora usuários ativos.
   * Métodos: Login, Logout e Listagem de Conectados.

---

## 📁 Estrutura do Projeto

```text
Trabalho_3/
├── servidor/               # Processo do Servidor (Independente)
│   ├── main.py             # Ponto de entrada e config. CORS
│   ├── dependencies.py     # Inicialização dos 3 Objetos Distribuídos
│   ├── esquemas/           # Validação de dados (Pydantic)
│   ├── modelos/            # POJOs e Lógica de Negócio (Entidades)
│   └── rotas/              # Controladores REST por Recurso
├── cliente_python/         # Cliente 1 (Python + Requests)
│   └── app.py
└── cliente_js/             # Cliente 2 (Poliglota: HTML + Fetch API)
    └── app.html            # Dashboard Visual
```

---

## 🚀 Como Executar

### 1️⃣ Inicie o Servidor

Certifique-se de estar com o ambiente virtual ativo e as dependências instaladas (`pip install fastapi uvicorn requests`).

```bash
cd Trabalho_3/servidor
uvicorn main:app --reload
```

*O servidor estará ativo em `http://127.0.0.1:8000`*

### 2️⃣ Execute o Cliente Python

Em um novo terminal:

```bash
cd Trabalho_3/cliente_python
python app.py
```

### 3️⃣ Execute o Cliente JavaScript (Navegador)

Para evitar bloqueios de segurança do navegador, utilize o servidor HTTP do Python:

```bash
cd Trabalho_3/cliente_js
python -m http.server 8080
```

*Acesse no navegador: `http://localhost:8080/app.html`*

---

## 🎯 Requisitos Atendidos

| Requisito               | Status | Implementação                                             |
| ----------------------- | ------ | ----------------------------------------------------------- |
| Sem Sockets/RMI manuais | ✅     | Utilizado protocolo HTTP nativo do FastAPI.                 |
| 3 Objetos Distribuídos | ✅     | Loja, Carrinho e Gerenciador de Usuários.                  |
| Projeto Separado        | ✅     | Pastas distintas para Servidor e Clientes.                  |
| Clientes Poliglotas     | ✅     | Implementações em**Python** e **JavaScript**. |
| Passagem por Valor      | ✅     | Dados transmitidos via payloads JSON.                       |
| 4+ Classes POJO         | ✅     | Livro, CD, Ebook, Apostila (herança de Produto).           |
| Tratamento de Erros     | ✅     | Feedback visual para login inválido e 404 para produtos.   |

---

## 🧪 Demonstração de Funcionalidades

### 1. Documentação Interativa

O sistema gera automaticamente uma interface para testes de todos os endpoints em:
`http://127.0.0.1:8000/docs`

### 2. Dashboard JS

O cliente JavaScript oferece uma interface visual onde é possível acompanhar em tempo real:

* O estado do carrinho (com cálculo automático de subtotais).
* A lista de usuários logados no servidor.
* Busca dinâmica no catálogo.

---

## 💡 Conclusão

A migração para **Web Services** resolveu os problemas de acoplamento do RMI. No Trabalho 2, o cliente precisava ter as classes Python (`Livro`, `CD`) para desserializar os dados. No Trabalho 3, o cliente só precisa entender **JSON**, tornando o sistema verdadeiramente distribuído e independente de plataforma.

---

**Autor:** Ygor Cruz e Cauã Victor
**Disciplina:** Sistemas Distribuídos
**Data:** Junho de 2026
