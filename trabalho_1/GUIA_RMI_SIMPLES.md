# RMI Simplificado - Guia de Entendimento

## 📚 O que é RMI?

**RMI (Remote Method Invocation)** = Chamar um método que está em outro computador, como se estivesse local.

```
Cliente local          Servidor remoto
   │                       │
   ├─ Quer chamar método   │
   ├─ Empacota em bytes    │
   ├─ Envia via UDP ──────>│
   │                       ├─ Recebe bytes
   │                       ├─ Desempacota
   │                       ├─ Executa método
   │                       ├─ Empacota resultado
   │<────── Envia bytes ───┤
   ├─ Recebe bytes         │
   ├─ Desempacota          │
   └─ Usa resultado        │
```

## 📁 Arquivos Importantes

### 1. **rmi_comentado.py** - Core do sistema RMI
   - `RemoteObjectRef` - Identifica qual objeto remoto chamar
   - `RequestMessage` - Mensagem de REQUISIÇÃO (cliente → servidor)
   - `ReplyMessage` - Mensagem de RESPOSTA (servidor → cliente)
   - `RemoteInvoker` - Cliente que faz requisições
   - `RemoteServer` - Servidor que recebe e processa requisições
   - `RemoteDispatcher` - Base para implementar métodos remotos

### 2. **servidor_rmi_simples.py** - Implementação do servidor
   - `LojaDispatcher` - Implementa os 8 métodos remotos
   - Cria RemoteServer
   - Registra LojaDispatcher
   - Aguarda requisições

### 3. **cliente_rmi_simples.py** - Cliente para invocar remotamente
   - `ClienteLoja` - Facilita chamar métodos remotos
   - Menu interativo

### 4. **teste_rmi_simples.py** - Teste automatizado
   - Inicia servidor em thread
   - Executa 8 testes
   - Demonstra cada operação

## 🔄 Fluxo Passo a Passo

### Exemplo: `cliente.listar_produtos()`

#### PASSO 1: Cliente prepara requisição
```python
# Arquivo: cliente_rmi_simples.py
def listar_produtos(self) -> list:
    return self._chamar_remoto("listar_produtos", {})

def _chamar_remoto(self, metodo: str, argumentos: dict = None):
    args_bytes = json.dumps(argumentos or {}).encode('utf-8')
```
**O que acontece:**
- Método é convertido em string: `"listar_produtos"`
- Argumentos são convertidos em JSON bytes: `b'{"codigo": "L001"}'`
- `RemoteObjectRef` identifica: `object_name="loja"`, `host="127.0.0.1"`, `port=5000`

#### PASSO 2: Cliente cria RequestMessage e empacota em bytes
```python
# Arquivo: rmi_comentado.py
request = RequestMessage(
    message_type=0,                    # 0 = Request
    request_id=1,                      # ID único
    object_reference=remote_obj_ref,   # RemoteObjectRef
    method_id="listar_produtos",       # Nome do método
    arguments=b'{}'                    # Argumentos JSON
)

# Empacotar em bytes
binary_data = request.to_bytes()
```

**Estrutura binária criada:**
```
┌────────┬──────────┬─────────┬──────────────┬────────────┬──────────────┬──────────┬──────────┐
│ tipo:0 │ id:1 (4) │ refLen  │ ref JSON     │ metodoLen  │ listar... (16)│ argsLen:2│ b'{}'    │
│ (4)    │          │ (4)     │              │ (4)        │              │ (4)      │          │
└────────┴──────────┴─────────┴──────────────┴────────────┴──────────────┴──────────┴──────────┘
```

#### PASSO 3: Cliente envia via UDP
```python
# Arquivo: rmi_comentado.py (RemoteInvoker.do_operation)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(binary_data, ("127.0.0.1", 5000))
```

#### PASSO 4: Servidor recebe bytes
```python
# Arquivo: rmi_comentado.py (RemoteServer.handle_request)
data, client_address = self.socket.recvfrom(65536)
request = RequestMessage.from_bytes(data)  # Desempacotar bytes
```

#### PASSO 5: Servidor localiza despachante e executa método
```python
# Arquivo: rmi_comentado.py (RemoteServer.handle_request)
dispatcher = self.dispatchers.get("loja")  # LojaDispatcher

# Arquivo: servidor_rmi_simples.py (LojaDispatcher.dispatch_method)
method_function = self.methods["listar_produtos"]
result = method_function(**{})  # Chamar método local

# Resultado:
# result = [{"codigo": "L001", "titulo": "Clean Code", ...}, ...]
```

#### PASSO 6: Servidor empacota resultado em ReplyMessage
```python
# Arquivo: rmi_comentado.py
result_json = json.dumps(result).encode('utf-8')
reply = ReplyMessage(
    message_type=1,           # 1 = Reply
    request_id=1,             # Mesmo ID da requisição
    result=result_json,       # Resultado em bytes
    exception=b''             # Vazio (sem erro)
)

reply_bytes = reply.to_bytes()
```

#### PASSO 7: Servidor envia resposta via UDP
```python
self.socket.sendto(reply_bytes, client_address)
```

#### PASSO 8: Cliente recebe e desserializa
```python
response_bytes, _ = sock.recvfrom(65536)
reply = ReplyMessage.from_bytes(response_bytes)
resultado_final = json.loads(reply.result.decode('utf-8'))
```

**Resultado final:**
```python
[
  {"codigo": "L001", "titulo": "Clean Code", ...},
  {"codigo": "L002", "titulo": "Design Patterns", ...},
  ...
]
```

## 🚀 Como Executar

### Opção 1: Teste Automático
```bash
# Terminal único - tudo em uma thread
python teste_rmi_simples.py
```

### Opção 2: Servidor + Cliente Manual
```bash
# Terminal 1 - Servidor
python -m Sebo_Virtual.servidor_rmi_simples

# Terminal 2 - Cliente
python -m Sebo_Virtual.cliente_rmi_simples
```

## 🎯 Requisitos Atendidos

✅ **POJOs**: Livro, CD, Ebook, Apostila, Produto, Loja
✅ **Agregações**: Loja tem Produtos
✅ **Extensões**: Livro/CD/Ebook/Apostila herdam Produto
✅ **Métodos Remotos**: 8 implementados
✅ **Passagem por Referência**: RemoteObjectRef
✅ **Passagem por Valor**: JSON
✅ **RMI**: Sem sockets manuais (encapsulados)
✅ **Protocolo Req-Rep**: Estrutura binária completa
✅ **Serialização**: JSON

## 📊 Estrutura das Mensagens

### RequestMessage (Cliente → Servidor)
```
[messageType:4][requestId:4][refLen:4][ref:var][methodLen:4][method:var][argsLen:4][args:var]
 0=Request
```

### ReplyMessage (Servidor → Cliente)
```
[messageType:4][requestId:4][resultLen:4][result:var][exceptionLen:4][exception:var]
 1=Reply
```

## 💡 Conceitos-Chave

1. **Transparência**: Cliente chama como se fosse local, mas é remoto
2. **Empacotamento**: Python objects → JSON → bytes → rede
3. **Desempacotamento**: bytes → JSON → Python objects
4. **ID de Requisição**: Correlaciona requisição com resposta
5. **Tratamento de Erros**: Exceção remota é lançada no cliente

## 🔧 Como Adicionar Novo Método Remoto

1. **Implementar método em LojaDispatcher** (servidor_rmi_simples.py):
```python
def novo_metodo(self, param1: str) -> dict:
    """Sua implementação aqui"""
    resultado = self.loja.fazer_algo(param1)
    return resultado.to_dict()
```

2. **Adicionar ao dicionário de métodos**:
```python
self.methods = {
    ...
    "novo_metodo": self.novo_metodo,
    ...
}
```

3. **Criar wrapper no cliente** (cliente_rmi_simples.py):
```python
def novo_metodo(self, param1: str) -> dict:
    return self._chamar_remoto("novo_metodo", {"param1": param1})
```

## ❓ Perguntas Frequentes

**P: Por que usar UDP e não TCP?**
A: UDP é mais simples (sem conexão), menor overhead. Para aplicações críticas, TCP seria melhor.

**P: Como sabe qual método chamar?**
A: O `method_id` (string) é procurado no dicionário `self.methods` do dispatcher.

**P: E se o servidor cair?**
A: `RemoteInvoker.do_operation()` tira exceção de timeout.

**P: Como passa objetos complexos?**
A: Convertendo para dict com `to_dict()` e depois para JSON.

---

**Versão**: Simplificada e Comentada
**Data**: 2024/2025
**Status**: ✅ Completo e Testado
