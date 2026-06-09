from Trabalho_4.evento_broker import EventoBroker, TOPICOS
import requests
import json
import time
from datetime import datetime

class ClientePubSub:
    def __init__(self, nome: str = "Cliente Python"):
        self.nome = nome
        self.broker = EventoBroker()
        self.api_url = "http://127.0.0.1:8000"
    
    def conectar_api(self):
        try:
            resp = requests.get(f"{self.api_url}/health")
            if resp.status_code == 200:
                print(f" Conectado à API em {self.api_url}")
                return True
        except:
            print(f" Erro ao conectar à API")
            return False
    
    def callback_evento(self, topico: str, dados: dict):
        print(f"\n{'='*60}")
        print(f" EVENTO RECEBIDO!")
        print(f"{'='*60}")
        print(f"Tópico: {topico}")
        print(f"Tipo:   {dados.get('tipo', 'desconhecido')}")
        print(f"Dados:  {json.dumps(dados, indent=2, ensure_ascii=False)}")
        print(f"Hora:   {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")
    
    def executar(self):
        print(f"\n{'='*60}")
        print(f"  CLIENTE PUB/SUB - {self.nome}")
        print(f"{'='*60}\n")
        
        if not self.conectar_api():
            return
        
        print("\n Tópicos disponíveis:")
        for chave, topico in TOPICOS.items():
            print(f"  • {chave:30s} → {topico}")
        
        print(f"\n Escutando TODOS os eventos do Sebo Virtual...")
        print(f"   (Padrão: sebo:*)\n")
        
        self.broker.subscrever(
            topicos=["sebo:*"],
            callback=self.callback_evento,
            run_async=False  
        )


class ClientePubSubInteligente:
    
    def __init__(self):
        self.broker = EventoBroker()
        self.stats = {
            "produtos_novos": 0,
            "carrinhos_finalizados": 0,
            "usuarios_ativos": set(),
            "total_eventos": 0
        }
    
    def processar_evento(self, topico: str, dados: dict):
        self.stats["total_eventos"] += 1
        tipo = dados.get("tipo", "")
        
        
        if "produto:novo" in topico:
            self.stats["produtos_novos"] += 1
            produto = dados.get("produto", {})
            print(f"\n NOVO PRODUTO: {produto.get('titulo', 'Desconhecido')}")
            print(f"   Código: {produto.get('codigo')}")
            print(f"   Preço: R$ {produto.get('preco')}")
        
        
        elif "carrinho:finalizado" in topico:
            self.stats["carrinhos_finalizados"] += 1
            usuario = dados.get("usuario", "Desconhecido")
            total = dados.get("total", 0)
            print(f"\n COMPRA REALIZADA por {usuario}")
            print(f"   Total: R$ {total:.2f}")
            print(f"   Itens: {dados.get('quantidade_itens', 0)}")
        
        
        elif "usuario:logado" in topico:
            usuario = dados.get("usuario")
            self.stats["usuarios_ativos"].add(usuario)
            print(f"\n USUÁRIO LOGADO: {usuario}")
            print(f"   Usuários online: {len(self.stats['usuarios_ativos'])}")
        
        elif "usuario:deslogado" in topico:
            usuario = dados.get("usuario")
            self.stats["usuarios_ativos"].discard(usuario)
            print(f"\n USUÁRIO DESLOGADO: {usuario}")
            print(f"   Usuários online: {len(self.stats['usuarios_ativos'])}")
        
        
        elif "estoque:alterado" in topico:
            print(f"\n ESTOQUE ALTERADO: {dados.get('codigo_produto')}")
            print(f"   Antes: {dados.get('quantidade_anterior')}")
            print(f"   Agora: {dados.get('quantidade_nova')}")
        
        else:
            print(f"\n EVENTO: {tipo}")
    
    def exibir_stats(self):
        print(f"\n{'='*60}")
        print(f"  ESTATÍSTICAS DE MONITORAMENTO")
        print(f"{'='*60}")
        print(f"Total de eventos:        {self.stats['total_eventos']}")
        print(f"Produtos novos:          {self.stats['produtos_novos']}")
        print(f"Carrinhos finalizados:   {self.stats['carrinhos_finalizados']}")
        print(f"Usuários ativos agora:   {len(self.stats['usuarios_ativos'])}")
        if self.stats['usuarios_ativos']:
            print(f"  → {', '.join(self.stats['usuarios_ativos'])}")
        print(f"{'='*60}\n")
    
    def executar(self):
        print(f"\n{'='*60}")
        print(f"  CLIENTE PUB/SUB INTELIGENTE - MONITOR")
        print(f"{'='*60}\n")
        
        print(" Monitorando eventos em tempo real...")
        print("(Digite Ctrl+C para sair e ver estatísticas)\n")
        
        try:
            self.broker.subscrever(
                topicos=["sebo:*"],
                callback=self.processar_evento,
                run_async=False
            )
        except KeyboardInterrupt:
            print("\n\n  Monitoramento interrompido.")
            self.exibir_stats()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cliente Pub/Sub do Sebo Virtual")
    parser.add_argument("--modo", choices=["basico", "inteligente"], default="inteligente",
                       help="Modo de operação")
    parser.add_argument("--nome", default="Cliente Python", help="Nome do cliente")
    
    args = parser.parse_args()
    
    if args.modo == "basico":
        cliente = ClientePubSub(args.nome)
        cliente.executar()
    else:
        cliente = ClientePubSubInteligente()
        cliente.executar()