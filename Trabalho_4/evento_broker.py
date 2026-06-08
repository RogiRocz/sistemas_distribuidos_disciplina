"""
Módulo de Pub/Sub para o Sebo Virtual
Permite que eventos sejam publicados e consumidos de forma desacoplada
"""

import redis
import json
from typing import Callable, List
from threading import Thread
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventoBroker:
    """
    Broker de eventos centralizado usando Redis Pub/Sub
    Permite publicar eventos e subscrever a tópicos
    """
    
    def __init__(self, host='localhost', port=6381, db=0):
        """Inicializa conexão com Redis"""
        try:
            self.redis_client = redis.Redis(
                host=host, 
                port=port, 
                db=db, 
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Testa conexão
            self.redis_client.ping()
            logger.info(f"✓ Conectado ao Redis em {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"✗ Erro ao conectar Redis: {e}")
            self.redis_client = None

    def publicar(self, topico: str, dados: dict) -> bool:
        """
        Publica um evento em um tópico
        
        Args:
            topico: Nome do tópico (ex: 'sebo:produto:novo')
            dados: Dicionário com os dados do evento
        
        Returns:
            True se publicado com sucesso
        """
        if not self.redis_client:
            logger.warning(f"Redis não disponível. Evento não publicado: {topico}")
            return False
        
        try:
            mensagem = json.dumps(dados, default=str)
            self.redis_client.publish(topico, mensagem)
            logger.info(f"📢 Evento publicado em '{topico}'")
            return True
        except Exception as e:
            logger.error(f"Erro ao publicar evento: {e}")
            return False

    def subscrever(self, topicos: List[str], callback: Callable, run_async=True):
        """
        Se subscreve a um ou mais tópicos e escuta eventos
        
        Args:
            topicos: Lista de tópicos (suporta padrões com *)
            callback: Função chamada quando evento é recebido
            run_async: Se True, executa em thread separada
        """
        if not self.redis_client:
            logger.error("Redis não disponível. Não foi possível subscrever")
            return
        
        def _listener():
            pubsub = self.redis_client.pubsub()
            pubsub.psubscribe(topicos)
            logger.info(f"👂 Escutando tópicos: {topicos}")
            
            for mensagem in pubsub.listen():
                if mensagem['type'] == 'pmessage':
                    try:
                        dados = json.loads(mensagem['data'])
                        topico = mensagem['pattern']
                        callback(topico, dados)
                    except json.JSONDecodeError:
                        logger.error(f"Erro ao decodificar evento: {mensagem['data']}")
        
        if run_async:
            thread = Thread(target=_listener, daemon=True)
            thread.start()
            return thread
        else:
            _listener()


# ═══════════════════════════════════════════════════════════════
# TÓPICOS PADRÃO DO SEBO VIRTUAL
# ═══════════════════════════════════════════════════════════════

TOPICOS = {
    # Produtos
    "PRODUTO_NOVO": "sebo:produto:novo",
    "PRODUTO_ATUALIZADO": "sebo:produto:atualizado",
    "PRODUTO_DELETADO": "sebo:produto:deletado",
    "ESTOQUE_ALTERADO": "sebo:estoque:alterado",
    
    # Carrinho
    "CARRINHO_ALTERADO": "sebo:carrinho:alterado",
    "CARRINHO_FINALIZADO": "sebo:carrinho:finalizado",
    
    # Usuários
    "USUARIO_LOGADO": "sebo:usuario:logado",
    "USUARIO_DESLOGADO": "sebo:usuario:deslogado",
    
    # Pedidos
    "PEDIDO_CRIADO": "sebo:pedido:criado",
    "PEDIDO_ATUALIZADO": "sebo:pedido:atualizado",
    
    # Sistema
    "SISTEMA_NOTIFICACAO": "sebo:sistema:notificacao",
}


# Instância global
broker = EventoBroker()


# ═══════════════════════════════════════════════════════════════
# FUNÇÕES DE CONVENIÊNCIA
# ═══════════════════════════════════════════════════════════════

def publicar_produto_novo(produto: dict):
    """Publica quando um novo produto é adicionado"""
    broker.publicar(TOPICOS["PRODUTO_NOVO"], {
        "tipo": "novo_produto",
        "produto": produto,
        "timestamp": str(datetime.now())
    })


def publicar_estoque_alterado(codigo: str, quantidade_anterior: int, quantidade_nova: int):
    """Publica quando o estoque de um produto muda"""
    broker.publicar(TOPICOS["ESTOQUE_ALTERADO"], {
        "tipo": "estoque_alterado",
        "codigo_produto": codigo,
        "quantidade_anterior": quantidade_anterior,
        "quantidade_nova": quantidade_nova,
        "timestamp": str(datetime.now())
    })


def publicar_carrinho_finalizado(usuario: str, total: float, itens: int):
    """Publica quando um carrinho é finalizado"""
    broker.publicar(TOPICOS["CARRINHO_FINALIZADO"], {
        "tipo": "carrinho_finalizado",
        "usuario": usuario,
        "total": total,
        "quantidade_itens": itens,
        "timestamp": str(datetime.now())
    })


def publicar_usuario_logado(usuario: str):
    """Publica quando um usuário faz login"""
    broker.publicar(TOPICOS["USUARIO_LOGADO"], {
        "tipo": "usuario_logado",
        "usuario": usuario,
        "timestamp": str(datetime.now())
    })


def publicar_usuario_deslogado(usuario: str):
    """Publica quando um usuário faz logout"""
    broker.publicar(TOPICOS["USUARIO_DESLOGADO"], {
        "tipo": "usuario_deslogado",
        "usuario": usuario,
        "timestamp": str(datetime.now())
    })
