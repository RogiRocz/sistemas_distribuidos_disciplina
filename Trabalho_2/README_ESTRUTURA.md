# Trabalho 2 - Sistema RMI de Loja Virtual

## Estrutura Organizada

```
Trabalho_2/
├── README Trabalho 2.md              # Especificação completa do trabalho
├── GUIA_RMI_SIMPLES.md              # Guia de uso do sistema RMI
├── teste_rmi_simples.py             # Testes de validação
│
└── Sebo_Virtual/
    ├── __init__.py
    ├── rmi_comentado.py             # Framework RMI (classes base)
    ├── cliente_rmi.py               # Cliente RMI genérico
    ├── servidor_rmi.py              # Servidor RMI genérico
    │
    ├── cliente/
    │   └── cliente_livros.py         # Cliente específico para loja de livros
    │
    └── servidor/
        ├── __init__.py
        ├── servidor_livros.py        # Servidor específico para loja de livros
        │
        └── modelos/                  # Classes de domínio (POJOs)
            ├── __init__.py
            ├── trocavel.py           # Interface Trocavel
            ├── produto.py            # Classe abstrata Produto
            ├── livro.py              # Classe concreta Livro
            ├── cd.py                 # Classe concreta CD
            ├── ebook.py              # Classe concreta Ebook
            ├── apostila.py           # Classe concreta Apostila
            ├── loja.py               # Serviço de Loja
            ├── loja_dispatcher.py    # Dispatcher para métodos remotos
            └── cliente.py            # Modelo de Cliente
```

## Como Usar

### Iniciar o Servidor
```bash
cd Trabalho_2/Sebo_Virtual/servidor
python servidor_livros.py
```

### Iniciar o Cliente (em outro terminal)
```bash
cd Trabalho_2/Sebo_Virtual/cliente
python cliente_livros.py
```

### Executar Testes
```bash
cd Trabalho_2
python teste_rmi_simples.py
```

## Componentes Principais

- **rmi_comentado.py**: Implementação do framework RMI com:
  - `RemoteObjectRef`: Referência remota de objetos
  - `RequestMessage/ReplyMessage`: Protocolo de comunicação
  - `RemoteInvoker`: Cliente que invoca métodos remotos
  - `RemoteDispatcher/RemoteServer`: Servidor que atende requisições

- **cliente_rmi.py/servidor_rmi.py**: Implementação genérica cliente-servidor

- **cliente_livros.py/servidor_livros.py**: Aplicação específica para loja virtual

- **modelos/**: Classes de entidades que são serializadas em JSON

## Requisitos Atendidos

- ✅ 4+ classes POJOs (Livro, CD, Ebook, Apostila)
- ✅ 2+ agregações (Loja contém Produtos; Produto implementa Trocavel)
- ✅ 2+ extensões (Livro, CD, Ebook, Apostila herdam de Produto)
- ✅ 4+ métodos remotos (8 implementados)
- ✅ Passagem por referência (RemoteObjectRef)
- ✅ Passagem por valor (JSON)
- ✅ Protocolo Requisição-Resposta
- ✅ Sem sockets manuais (encapsulados no framework)
