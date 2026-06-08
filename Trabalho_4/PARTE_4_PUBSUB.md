# 🚀 Parte 4: Pub/Sub (Publicar-Assinar)

## 📋 Visão Geral

Implementamos um **sistema de eventos centralizado** usando Redis Pub/Sub que desacopla completamente os componentes do Sebo Virtual.

### ✨ Características

✅ **Desacoplamento Espacial**: Clientes não precisam conhecer uns aos outros  
✅ **Desacoplamento Temporal**: Eventos são publicados mesmo que ninguém esteja escutando  
✅ **Escalabilidade**: Novos subscribers podem ser adicionados sem mudar o broker  
✅ **Tempo Real**: WebSocket para notificações instantâneas  
✅ **Resiliência**: Se um cliente cai, o sistema continua funcionando  

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│         Servidor FastAPI                    │
│  (produtor de eventos)                      │
│                                             │
│  • /loja        → publica "sebo:produto:*"│
│  • /carrinho    → publica "sebo:carrinho:*"│
│  • /usuarios    → publica "sebo:usuario:*" │
└────────────────┬────────────────────────────┘
                 │
                 ↓ publica eventos (JSON)
        ┌────────────────────┐
        │   Redis Pub/Sub    │
        │   (localhost:6379) │
        └────────────────────┘
         ↑     ↑     ↑       ↑
         │     │     │       │ (subscribers desacoplados)
    ┌────┴─┬──┴──┬──┴──┬───┴─────┐
    │      │     │     │         │
  Python  Java  HTML  Monitor  NovoCliente
  Client  Client Client         (pode ser adicionado!)
```

---

## 📦 Arquivos Criados

### Servidor
```
servidor/
├── app/
│   ├── evento_broker.py    ← Nova: Sistema Pub/Sub com Redis
│   └── rotas/
│       └── eventos.py      ← Nova: WebSocket para eventos
└── app/main.py             (será atualizado)
```

### Cliente Python
```
cliente_python/
└── app_pubsub.py           ← Nova: Client que escuta eventos
```

---

## 🚀 Como Usar

### 1️⃣ Instale Dependências

```bash
# No servidor
pip install redis

# No cliente
pip install redis requests websocket-client
```

### 2️⃣ Inicie Redis

**Opção A: Windows com Chocolatey**
```powershell
choco install redis
redis-server
```

**Opção B: Docker**
```bash
docker run -d -p 6379:6379 redis:latest
```

**Opção C: Linux ou WSL**
```bash
wsl
sudo apt-get install redis-server
redis-server
```


### 3️⃣ Inicie o Servidor

```bash
cd servidor
uvicorn app.main:app --reload
```

### 4️⃣ Inicie o Cliente Pub/Sub

**Modo Monitor (recomendado)**:
```bash
cd cliente_python
python app_pubsub.py --modo inteligente
```

**Modo Básico**:
```bash
python app_pubsub.py --modo basico
```

---

## 🎯 Tópicos de Eventos

| Tópico | Evento | Dados |
|--------|--------|-------|
| `sebo:produto:novo` | Novo produto adicionado | `{produto}` |
| `sebo:produto:atualizado` | Produto modificado | `{produto}` |
| `sebo:estoque:alterado` | Estoque mudou | `{codigo, antes, depois}` |
| `sebo:carrinho:alterado` | Carrinho atualizado | `{usuario, itens}` |
| `sebo:carrinho:finalizado` | Pedido realizado | `{usuario, total}` |
| `sebo:usuario:logado` | Login realizado | `{usuario}` |
| `sebo:usuario:deslogado` | Logout realizado | `{usuario}` |

---

## 💡 Exemplos de Uso

### Publicar um Evento

```python
from app.evento_broker import broker, TOPICOS

# Publica um novo produto
broker.publicar(TOPICOS["PRODUTO_NOVO"], {
    "tipo": "novo_produto",
    "produto": {
        "codigo": "L001",
        "titulo": "Clean Code",
        "preco": 179.80
    }
})
```

### Subscrever a Eventos

```python
from app.evento_broker import broker

def meu_callback(topico, dados):
    print(f"Evento em {topico}: {dados}")

# Escuta todos os eventos do sebo
broker.subscrever(["sebo:*"], callback=meu_callback)
```

### Usar WebSocket no Cliente JavaScript

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/eventos");

ws.onmessage = (event) => {
    const evento = JSON.parse(event.data);
    console.log("Evento recebido:", evento);
};

ws.send(JSON.stringify({tipo: "subscribe", topicos: ["sebo:*"]}));
```

---

## 🔍 Verificar Status

```bash
curl http://localhost:8000/ws/eventos/status
```

Resposta:
```json
{
    "broker_redis": true,
    "clientes_conectados": 3,
    "topicos_disponiveis": ["PRODUTO_NOVO", "CARRINHO_FINALIZADO", ...],
    "status": "ativo"
}
```

---

## 📊 Desacoplamento Demonstrado

### ❌ Antes (Acoplado)

```python
# Cliente precisa conhecer o servidor
cliente = Cliente(ip="192.168.1.100", porta=8000)
cliente.notificar_novo_produto(produto)

# Se mudar IP, quebra tudo!
```

### ✅ Depois (Desacoplado)

```python
# Servidor publica evento
broker.publicar("sebo:produto:novo", produto)

# Cliente subscreve sem conhecer origem
broker.subscrever(["sebo:*"], meu_callback)

# Funciona mesmo se servidor tiver outro IP!
```

---

## 🧪 Teste de Resiliência

### Teste 1: Temporal Decoupling

1. Inicie o servidor
2. Publique um evento manualmente (via curl)
3. **Inicie o cliente DEPOIS**
4. O cliente NÃO recebe eventos passados (Pub/Sub padrão)

**Solução**: Use Redis Streams para persistência

```python
# Com Redis Streams (futuro)
broker.publicar_persistente("sebo:produto:novo", dados, ttl=3600)
```

### Teste 2: Spatial Decoupling

1. Inicie Cliente Python, Java, HTML simultaneamente
2. Publique evento no servidor
3. **Todos recebem em tempo real**, sem acoplamento!

### Teste 3: Escalabilidade

1. Inicie múltiplos clientes
2. Publique evento
3. Todos recebem = sem problema de carga!

---

## 📈 Próximos Passos

### Melhorias Possíveis

1. **Redis Streams** para persistência
   ```python
   broker.xadd("sebo:eventos", {"tipo": "novo_produto"})
   ```

2. **Consumer Groups** para garantias
   ```python
   pubsub = redis.pubsub_manager()
   pubsub.add_consumer_group("sebo:*", "grupo1")
   ```

3. **Message Queues** para operações críticas
   ```python
   # Combinar Pub/Sub (notificações) + Queues (transações)
   queue.push("sebo:pagamentos", pedido)  # Garante entrega
   broker.publish("sebo:notificacoes", pedido)  # Notifica
   ```

4. **Dead Letter Queue** para erro
   ```python
   if evento_falhou:
       queue.push("sebo:dlq:erro", evento)
   ```

---

## 🎓 Conceitos Demonstrados

✅ **Pub/Sub Pattern**: Dissociação entre produtor e consumidor  
✅ **Observer Pattern**: Clientes reagem a eventos  
✅ **Broker Pattern**: Intermediário centralizado (Redis)  
✅ **Temporal Decoupling**: Remetente não espera resposta  
✅ **Spatial Decoupling**: Remetente não sabe quem recebe  
✅ **Event Sourcing**: Histórico de eventos (melhorias futuras)  

---

## 🐛 Troubleshooting

**"Redis connection refused"**
```bash
# Verifique se Redis está rodando
redis-cli ping
# Deve retornar: PONG
```

**"No module named 'redis'"**
```bash
pip install redis
```

**WebSocket não conecta**
```javascript
// Verifique URL
const ws = new WebSocket("ws://localhost:8000/ws/eventos");
// Não http, mas ws!
```

---

## 📝 Arquitetura Completa do Trabalho 3

```
TRABALHO 3 - SEBO VIRTUAL
├── Parte 1: API REST (FastAPI)
├── Parte 2: Autenticação/Objeto (3 Objetos + 3 Clientes)
├── Parte 3: Clientes Heterogêneos (Python, HTML, Java)
└── Parte 4: Pub/Sub (Comunicação Indireta) ← VOCÊ ESTÁ AQUI!
    ├── Redis Broker
    ├── Event Publishing
    ├── Event Subscription
    ├── WebSocket Broadcasting
    └── Monitor em Tempo Real
```

---

**Parabéns! Seu sistema agora é distribuído, desacoplado e escalável!** 🎉

Próximo: Parte 5 será sobre Tolerância a Falhas ou Consenso Distribuído? 🤔
