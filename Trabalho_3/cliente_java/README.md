# 🚀 Cliente Java - Sebo Virtual

## Visão Geral

Cliente Java interativo para o **Trabalho 3 de Sistemas Distribuídos**. Replicas todas as funcionalidades do cliente HTML/JavaScript em uma aplicação de terminal elegante e responsiva.

---

## 📋 Funcionalidades

### 🔐 Autenticação (Objeto 3)
- Login com usuário e senha
- Validação de credenciais
- Rastreamento de sessão

### 📚 Catálogo (Objeto 1)
- Listar todos os produtos
- Buscar produtos por título
- Visualizar detalhes (código, tipo, preço)
- Suporta múltiplos tipos: Livros, CDs, Ebooks, Apostilas

### 🛒 Carrinho (Objeto 2)
- Adicionar produtos ao carrinho
- Visualizar itens com quantidades e valores
- Calcular subtotais automaticamente
- Limpar carrinho

### 👥 Usuários Ativos
- Visualizar lista de usuários conectados
- Atualização em tempo real

---

## 🛠️ Requisitos

- **Java 11+** (com módulo java.net.http)
- **Maven ou javac** para compilação
- **GSON 2.10.1** (baixado automaticamente)
- **Servidor rodando em http://127.0.0.1:8000**

---

## 📦 Como Compilar

### Opção 1: Usando o Script (Recomendado - Linux/Mac)

```bash
chmod +x run.sh
./run.sh
```

Esto script:
- ✅ Verifica se Java está instalado
- ✅ Baixa GSON automaticamente
- ✅ Compila o código
- ✅ Executa o cliente

### Opção 2: Compilação Manual

```bash
# Criar diretórios
mkdir -p bin lib

# Baixar GSON
wget https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar -O lib/gson-2.10.1.jar

# Compilar
javac -cp "lib/*" -d bin src/*.java

# Executar
java -cp "bin:lib/*" Main
```

### Opção 3: Windows (PowerShell)

```powershell
# Compilar
javac -cp "lib/*" -d bin src/*.java

# Executar
java -cp "bin;lib/*" Main
```

---

## 🎯 Como Usar

1. **Inicie o servidor FastAPI** (em outro terminal):
   ```bash
   cd ../servidor
   uvicorn app.main:app --reload
   ```

2. **Execute o cliente Java**:
   ```bash
   ./run.sh  # Linux/Mac
   # ou
   javac -cp "lib/*" -d bin src/*.java && java -cp "bin:lib/*" Main
   ```

3. **Escolha as opções no menu**:
   - `1` - Login (teste com admin/admin123)
   - `2` - Listar catálogo completo
   - `3` - Buscar produto por título
   - `4` - Gerenciar carrinho
   - `5` - Ver usuários ativos
   - `0` - Sair

---

## 📁 Estrutura do Projeto

```
cliente_java/
├── src/
│   ├── Main.java           # Menu principal e lógica
│   └── ApiClient.java      # Cliente HTTP + GSON
├── bin/                    # Arquivos compilados
├── lib/                    # Dependências (GSON)
├── run.sh                  # Script de execução
└── README.md              # Este arquivo
```

---

## 🔍 Detalhes das Classes

### ApiClient.java
- **HttpClient** (nativa Java 11+) para requisições HTTP
- **GSON** para parsing/serialização JSON
- Métodos:
  - `get(endpoint)` - Requisição GET
  - `post(endpoint, body)` - Requisição POST
  - `imprimirJson(json)` - Formatação bonita JSON

### Main.java
- **Menu interativo** com cores ANSI
- **Validação de entrada** do usuário
- **Formatação de tabelas** em terminal
- **Rastreamento de sessão** (usuário logado)
- Métodos para cada funcionalidade:
  - `menuLogin()` - Autenticação
  - `listarProdutos()` - Catálogo
  - `buscarProduto()` - Busca
  - `menuCarrinho()` - Carrinho
  - `exibirAtivos()` - Usuários

---

## 🎨 Interface

```
╔════════════════════════════════════════════════════╗
║   CLIENTE SEBO VIRTUAL - TRABALHO 3 (Java)        ║
║   Sistemas Distribuídos                           ║
╚════════════════════════════════════════════════════╝

┌─ MENU PRINCIPAL ─────────────────────────────────┐
│ 1. Login / Autenticação
│ 2. Listar Catálogo Completo
│ 3. Buscar Produto por Título
│ 4. Carrinho de Compras
│ 5. Ver Usuários Ativos
│ 0. Sair
└──────────────────────────────────────────────────┘
```

---

## ✨ Endpoints Utilizados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/loja/nome` | Nome da loja |
| GET | `/loja/produtos` | Lista de produtos |
| GET | `/loja/produtos/buscar/{titulo}` | Busca por título |
| POST | `/usuarios/login` | Autenticação |
| GET | `/carrinho` | Ver carrinho |
| GET | `/carrinho/adicionar/{cod}` | Adicionar produto |
| POST | `/carrinho/limpar` | Limpar carrinho |
| GET | `/usuarios/ativos` | Usuários conectados |

---

## 🐛 Troubleshooting

### "javac: command not found"
```bash
# Instalar Java Development Kit
sudo apt-get install default-jdk  # Linux
brew install openjdk              # macOS
```

### "Cannot find symbol: class GSON"
O script `run.sh` baixará GSON automaticamente. Se não funcionar:
```bash
wget https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar -O lib/gson-2.10.1.jar
```

### "Connection refused"
Certifique-se de que o servidor FastAPI está rodando em `http://127.0.0.1:8000`

---

## 📝 Notas de Desenvolvimento

- ✅ Usa **HttpClient nativa** (Java 11+) - sem dependências extras
- ✅ **GSON** para JSON parsing - download automático
- ✅ **Cores ANSI** para terminal colorido
- ✅ **Menu interativo** com validação de entrada
- ✅ **Logging de requisições** estilo API real
- ✅ **Tratamento de erros** robusto

---

## 👨‍💼 Autor

Criado para Trabalho 3 - Sistemas Distribuídos

**Principais tecnologias:**
- Java 11+
- HttpClient
- GSON
- Terminal com cores ANSI

---

**Divirta-se! 🎉**
