from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from typing import Set
from Trabalho_4.evento_broker import broker, TOPICOS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["eventos"])

conexoes_ativas: Set[WebSocket] = set()


@router.websocket("/eventos")
async def websocket_eventos(websocket: WebSocket):
    await websocket.accept()
    conexoes_ativas.add(websocket)
    
    logger.info(f" Cliente conectado ao WebSocket. Total: {len(conexoes_ativas)}")
    
    try:
    
        await broadcast_para_todos({
            "tipo": "cliente_conectado",
            "mensagem": f"Nova conexão estabelecida. Total: {len(conexoes_ativas)}"
        })
        
    
        while True:
            dados = await websocket.receive_text()
            
            try:
                msg = json.loads(dados)
                tipo = msg.get("tipo")
                
                if tipo == "ping":
                    await websocket.send_json({"tipo": "pong"})
                
                elif tipo == "subscribe":
                    topicos = msg.get("topicos", [])
                    await websocket.send_json({
                        "tipo": "subscrito",
                        "topicos": topicos,
                        "mensagem": f"Inscrito em: {', '.join(topicos)}"
                    })
                    logger.info(f"👂 Cliente inscrito em: {topicos}")
                
            except json.JSONDecodeError:
                logger.warning(f"Mensagem inválida recebida: {dados}")
    
    except WebSocketDisconnect:
        conexoes_ativas.discard(websocket)
        logger.info(f" Cliente desconectado. Total: {len(conexoes_ativas)}")
        
    
        await broadcast_para_todos({
            "tipo": "cliente_desconectado",
            "mensagem": f"Um cliente desconectou. Total: {len(conexoes_ativas)}"
        })
    
    except Exception as e:
        logger.error(f"Erro WebSocket: {e}")
        conexoes_ativas.discard(websocket)


async def broadcast_para_todos(evento: dict):
    if not conexoes_ativas:
        return
    
    desconectadas = set()
    
    for websocket in conexoes_ativas:
        try:
            await websocket.send_json(evento)
        except Exception as e:
            logger.warning(f"Erro ao enviar evento: {e}")
            desconectadas.add(websocket)
    
    conexoes_ativas.difference_update(desconectadas)


@router.get("/eventos/status")
async def status_eventos():
    return {
        "broker_redis": broker.redis_client is not None,
        "clientes_conectados": len(conexoes_ativas),
        "topicos_disponiveis": list(TOPICOS.keys()),
        "status": "ativo" if broker.redis_client else "desconectado"
    }
