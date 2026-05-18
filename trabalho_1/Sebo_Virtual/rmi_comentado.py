"""
SISTEMA RMI (Remote Method Invocation) 

FLUXO:
1. Cliente cria uma REQUISIÇÃO com:
   - Nome do objeto remoto
   - Nome do método a chamar
   - Argumentos (em JSON)

2. REQUISIÇÃO é empacotada em BYTES (estrutura binária):
   [tipo][id][ref_len][referência][método_len][método][args_len][argumentos]

3. Envia via UDP para o SERVIDOR

4. SERVIDOR recebe, desempacota e executa o método

5. SERVIDOR cria uma RESPOSTA com o resultado

6. RESPOSTA é empacotada em BYTES e enviada ao cliente

7. Cliente desempacota e retorna o resultado

ESTRUTURA DAS MENSAGENS:
=======================

REQUISIÇÃO (tipo = 0):
  messageType (4 bytes):     0 = Request
  requestId (4 bytes):       ID único da requisição
  objectRefLen (4 bytes):    Tamanho da referência do objeto
  objectRef (variável):      Referência em JSON: {object_name, host, port}
  methodLen (4 bytes):       Tamanho do nome do método
  methodId (variável):       Nome do método (ex: "listar_produtos")
  argsLen (4 bytes):         Tamanho dos argumentos
  arguments (variável):      Argumentos em JSON

RESPOSTA (tipo = 1):
  messageType (4 bytes):     1 = Reply
  requestId (4 bytes):       ID da requisição original
  resultLen (4 bytes):       Tamanho do resultado
  result (variável):         Resultado em JSON
  exceptionLen (4 bytes):    Tamanho da mensagem de erro
  exception (variável):      Mensagem de erro (vazio se sucesso)
"""

import json
import socket
import struct
from dataclasses import dataclass, asdict
from typing import Any, Optional, Callable, Dict
from abc import ABC, abstractmethod


# CLASSES DE REFERÊNCIA E MENSAGENS
@dataclass
class RemoteObjectRef:
    """
    REFERÊNCIA PARA OBJETO REMOTO
    
    Identifica um objeto que está em execução no servidor.
    É passada como REFERÊNCIA (não por valor) nas requisições.
    
    Atributos:
        object_name: Nome único do objeto (ex: "loja", "carrinho")
        host: Endereço IP onde o objeto está (ex: "127.0.0.1")
        port: Porta onde o servidor escuta (ex: 5000)
    """
    object_name: str  # Nome do objeto remoto
    host: str         # IP do servidor
    port: int         # Porta do servidor

    def to_dict(self) -> dict:
        """Converte para dicionário (para JSON)"""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'RemoteObjectRef':
        """Reconstrói a partir de um dicionário"""
        return RemoteObjectRef(**data)


@dataclass
class RequestMessage:
    """
    Representa um pedido do cliente para executar um método remoto.
    
    Fluxo:
    1. Cliente cria RequestMessage com os dados da requisição
    2. Converte para bytes com to_bytes()
    3. Envia via UDP
    4. Servidor recebe bytes e reconstrói com from_bytes()
    """
    message_type: int = 0                    # 0 = Request, 1 = Reply
    request_id: int = 0                      # ID único para correlacionar request com response
    object_reference: RemoteObjectRef = None # Qual objeto remoto chamar
    method_id: str = ""                      # Qual método chamar
    arguments: bytes = b""                   # Argumentos do método (em JSON)

    def to_bytes(self) -> bytes:
        """
        Converte a mensagem em BYTES para enviar pela rede
        
        Estrutura binária:
        [tipo:4][id:4][ref_len:4][referência][método_len:4][método][args_len:4][argumentos]
        """
        # Passo 1: Converter object_reference em JSON
        ref_json = json.dumps(self.object_reference.to_dict()).encode('utf-8')
        
        # Passo 2: Converter method_id em bytes
        method_bytes = self.method_id.encode('utf-8')
        
        # Passo 3: Montar a mensagem binária
        buffer = b""
        
        # Campo 1: messageType (4 bytes, big-endian)
        buffer += struct.pack("!I", self.message_type)
        
        # Campo 2: requestId (4 bytes)
        buffer += struct.pack("!I", self.request_id)
        
        # Campo 3: Tamanho da referência (4 bytes) + a referência
        buffer += struct.pack("!I", len(ref_json))
        buffer += ref_json
        
        # Campo 4: Tamanho do método (4 bytes) + o método
        buffer += struct.pack("!I", len(method_bytes))
        buffer += method_bytes
        
        # Campo 5: Tamanho dos argumentos (4 bytes) + argumentos
        buffer += struct.pack("!I", len(self.arguments))
        buffer += self.arguments
        
        return buffer

    @staticmethod
    def from_bytes(data: bytes) -> 'RequestMessage':
        """
        Reconstrói a mensagem a partir de BYTES recebidos pela rede
        """
        offset = 0
        
        # Ler messageType (4 bytes)
        message_type = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        
        # Ler requestId (4 bytes)
        request_id = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        
        # Ler referência (tamanho + dados)
        ref_len = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        ref_json = data[offset:offset+ref_len].decode('utf-8')
        object_ref = RemoteObjectRef.from_dict(json.loads(ref_json))
        offset += ref_len
        
        # Ler método (tamanho + dados)
        method_len = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        method_id = data[offset:offset+method_len].decode('utf-8')
        offset += method_len
        
        # Ler argumentos (tamanho + dados)
        args_len = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        arguments = data[offset:offset+args_len]
        
        return RequestMessage(
            message_type=message_type,
            request_id=request_id,
            object_reference=object_ref,
            method_id=method_id,
            arguments=arguments
        )


@dataclass
class ReplyMessage:
    """
    MENSAGEM DE RESPOSTA
    
    Representa a resposta do servidor após executar um método.
    
    Pode conter:
    - result: Resultado da execução (sucesso)
    - exception: Mensagem de erro (falha)
    """
    message_type: int = 1     # Sempre 1 = Reply
    request_id: int = 0       # Mesmo ID da requisição
    result: bytes = b""       # Resultado em JSON (se sucesso)
    exception: bytes = b""    # Mensagem de erro (se falha)

    def to_bytes(self) -> bytes:
        """Converte a resposta em BYTES para enviar"""
        buffer = b""
        buffer += struct.pack("!I", self.message_type)
        buffer += struct.pack("!I", self.request_id)
        buffer += struct.pack("!I", len(self.result))
        buffer += self.result
        buffer += struct.pack("!I", len(self.exception))
        buffer += self.exception
        return buffer

    @staticmethod
    def from_bytes(data: bytes) -> 'ReplyMessage':
        """Reconstrói a resposta a partir de BYTES"""
        offset = 0
        message_type = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        request_id = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        
        result_len = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        result = data[offset:offset+result_len]
        offset += result_len
        
        exception_len = struct.unpack("!I", data[offset:offset+4])[0]
        offset += 4
        exception = data[offset:offset+exception_len]
        
        return ReplyMessage(
            message_type=message_type,
            request_id=request_id,
            result=result,
            exception=exception
        )


# UTILITÁRIOS DE SERIALIZAÇÃO
class Serializer:
    """
    UTILITÁRIO DE SERIALIZAÇÃO
    
    Converte objetos Python ↔ JSON (bytes)
    Usado para serializar argumentos e resultados
    """
    
    @staticmethod
    def serialize(obj: Any) -> bytes:
        """Converte um objeto em bytes JSON"""
        if isinstance(obj, bytes):
            return obj
        
        # Se tem método to_dict, usar
        if hasattr(obj, 'to_dict'):
            return json.dumps(obj.to_dict()).encode('utf-8')
        
        # Senão, converter __dict__
        if hasattr(obj, '__dict__'):
            return json.dumps(obj.__dict__, default=str).encode('utf-8')
        
        # Último recurso
        return json.dumps(obj, default=str).encode('utf-8')
    
    @staticmethod
    def serialize_list(objects: list) -> bytes:
        """Serializa uma lista de objetos reutilizando serialize()"""
        data = []
        for obj in objects:
            serialized = Serializer.serialize(obj)
            data.append(json.loads(serialized.decode('utf-8')))
        return json.dumps(data, default=str).encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes, target_class=None) -> Any:
        """Desserializa bytes JSON em um objeto"""
        if not data:
            return None
        
        parsed = json.loads(data.decode('utf-8'))
        
        if target_class is None:
            return parsed
        
        # Tentar instantiar a classe
        if hasattr(target_class, 'from_dict'):
            return target_class.from_dict(parsed)
        else:
            try:
                return target_class(**parsed)
            except TypeError:
                return parsed

# LADO DO CLIENTE: INVOCADOR REMOTO
class RemoteInvoker:
    """
    INVOCADOR REMOTO (LADO CLIENTE)
    
    Responsável por fazer requisições ao servidor remoto.
    
    Fluxo:
    1. Cliente chama do_operation(ref, metodo, argumentos)
    2. Cria RequestMessage
    3. Converte em bytes
    4. Envia via UDP
    5. Aguarda resposta
    6. Desempacota ReplyMessage
    7. Retorna resultado ou lança exceção
    """
    
    def __init__(self, server_host: str, server_port: int, timeout: float = 5.0):
        """
        Inicializa o invocador remoto
        
        Args:
            server_host: IP do servidor (ex: "127.0.0.1")
            server_port: Porta do servidor (ex: 5000)
            timeout: Tempo máximo de espera por resposta (segundos)
        """
        self.server_host = server_host
        self.server_port = server_port
        self.timeout = timeout
        self.request_counter = 0  # Contador para gerar IDs únicos
    
    def do_operation(self, object_ref: RemoteObjectRef, method_id: str, 
                     arguments: bytes = b"") -> bytes:
        """
        EXECUTA UMA OPERAÇÃO REMOTA
        
        Este é o método principal. Você o chama para invocar um método remoto.
        
        Args:
            object_ref: Referência ao objeto remoto (RemoteObjectRef)
            method_id: Nome do método a chamar (string)
            arguments: Argumentos em bytes JSON (padrão: vazio)
        
        Returns:
            Resultado do método em bytes JSON
        
        Raises:
            Exception: Se houve erro remoto ou timeout
        """
        # ID
        self.request_counter += 1
        
        # Criar a requisição
        request = RequestMessage(
            message_type=0,                    # 0 = Request
            request_id=self.request_counter,   # ID único
            object_reference=object_ref,       # Qual objeto chamar
            method_id=method_id,               # Qual método chamar
            arguments=arguments                # Argumentos
        )
        
        try:
            # Abrir socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Converter requisição em bytes
            request_bytes = request.to_bytes()
            
            # Enviar para o servidor
            sock.sendto(request_bytes, (object_ref.host, object_ref.port))
            
            # Aguardar resposta
            response_bytes, _ = sock.recvfrom(65536)
            sock.close()
            
            # Desempacotar resposta
            reply = ReplyMessage.from_bytes(response_bytes)
            
            # Verificar se houve erro
            if reply.exception:
                raise Exception(f"Erro no servidor: {reply.exception.decode('utf-8')}")
            
            # Retornar resultado
            return reply.result
            
        except socket.timeout:
            raise Exception(f"Timeout: servidor {object_ref.host}:{object_ref.port} não respondeu")
        except Exception as e:
            raise Exception(f"Erro na requisição remota: {str(e)}")


# LADO DO SERVIDOR: DISPATCHER E SERVIDOR RMI
class RemoteDispatcher(ABC):
    """
    
    Um despachante é um objeto que implementa os métodos remotos.
    Subclasses devem implementar dispatch_method para processar requisições.
    """
    
    @abstractmethod
    def dispatch_method(self, method_id: str, arguments: bytes) -> bytes:
        """
        PROCESSA UMA REQUISIÇÃO DE MÉTODO REMOTO
        
        Deve ser implementado pelas subclasses.
        
        Args:
            method_id: Nome do método a executar
            arguments: Argumentos em bytes JSON
        
        Returns:
            Resultado em bytes JSON
        
        Raises:
            Exception: Se o método não existe ou houve erro
        """
        pass


class RemoteServer:
    """
    SERVIDOR RMI
    
    Escuta por requisições UDP e processa-as.
    
    Fluxo:
    1. Registrar objetos remotos com register_object()
    2. Iniciar servidor com start()
    3. Servidor aguarda requisições indefinidamente
    4. Para cada requisição:
       a. Desempacota RequestMessage
       b. Localiza o dispatcher
       c. Chama dispatch_method()
       d. Empacota ReplyMessage
       e. Envia resposta
    """
    
    def __init__(self, host: str, port: int):
        """
        Inicializa o servidor RMI
        
        Args:
            host: IP para escuta (ex: "127.0.0.1")
            port: Porta para escuta (ex: 5000)
        """
        self.host = host
        self.port = port
        self.socket = None
        
        # Dicionário que mapeia nomes de objetos → seus despachantes
        # Exemplo: {"loja": LojaDispatcher, "carrinho": CarrinhoDispatcher}
        self.dispatchers: Dict[str, RemoteDispatcher] = {}
    
    def register_object(self, object_name: str, dispatcher: RemoteDispatcher) -> None:
        """
        REGISTRA UM OBJETO REMOTO
        
        Mapeia um nome para um despachante (objeto que implementa os métodos).
        
        Args:
            object_name: Nome único do objeto (ex: "loja")
            dispatcher: Despachante que implementa os métodos
        """
        self.dispatchers[object_name] = dispatcher
        print(f"[✓] Objeto '{object_name}' registrado")
    
    def start(self) -> None:
        """
        INICIA O SERVIDOR
        
        Abre um socket UDP e fica aguardando requisições indefinidamente.
        Processa uma requisição por vez.
        """
        # Criar socket UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        
        print(f"[✓] Servidor RMI iniciado em {self.host}:{self.port}")
        print("[*] Aguardando requisições... (Ctrl+C para parar)\n")
        
        try:
            # Loop infinito processando requisições
            while True:
                self.handle_request()
        except KeyboardInterrupt:
            print("\n[*] Servidor parado")
        finally:
            self.socket.close()
    
    def handle_request(self) -> None:
        """
        PROCESSA UMA ÚNICA REQUISIÇÃO
        """
        try:
            # Receber dados UDP
            data, client_address = self.socket.recvfrom(65536)
            
            # Desempacotar requisição
            request = RequestMessage.from_bytes(data)
            
            print(f"\n[*] Requisição recebida:")
            print(f"    Objeto: {request.object_reference.object_name}")
            print(f"    Método: {request.method_id}")
            
            # Localizar despachante para o objeto
            dispatcher = self.dispatchers.get(request.object_reference.object_name)
            
            if dispatcher is None:
                # Objeto não encontrado
                error_msg = f"Objeto '{request.object_reference.object_name}' não encontrado"
                reply = ReplyMessage(
                    message_type=1,
                    request_id=request.request_id,
                    exception=error_msg.encode('utf-8')
                )
                print(f"    [!] {error_msg}")
            else:
                try:
                    # Executar o método
                    method_result = dispatcher.dispatch_method(
                        request.method_id,
                        request.arguments
                    )
                    
                    # Empacotar resultado em resposta
                    reply = ReplyMessage(
                        message_type=1,
                        request_id=request.request_id,
                        result=method_result
                    )
                    print(f"    [✓] Sucesso")
                    
                except Exception as e:
                    # Houve erro ao executar o método
                    error_msg = str(e)
                    reply = ReplyMessage(
                        message_type=1,
                        request_id=request.request_id,
                        exception=error_msg.encode('utf-8')
                    )
                    print(f"    [!] Erro: {error_msg}")
            
            # Enviar resposta de volta ao cliente
            self.socket.sendto(reply.to_bytes(), client_address)
            
        except Exception as e:
            print(f"[!] Erro ao processar requisição: {e}")
