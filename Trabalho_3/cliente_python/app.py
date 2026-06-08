import requests
import json

BASE_URL = "http://172.18.104.6:8000"

def format_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False)

def testar_sistema():
    print("=== CLIENTE SEBO VIRTUAL (TRABALHO 3) ===")

    print("\n0. Verificando status da API...")
    health = requests.get(f"{BASE_URL}/health").json()
    print(format_json(health))

    # --- OBJETO 1: LOJA (Catálogo) ---
    print("\n1. Consultando nome da loja...")
    res = requests.get(f"{BASE_URL}/loja/nome")
    print(f"Nome: {res.json()['nome']}")

    print("\n2. Listando produtos disponíveis...")
    produtos = requests.get(f"{BASE_URL}/loja/produtos").json()
    for p in produtos:
        print(f"[{p['codigo']}] {p['titulo']} - R$ {p['preco']}")

    # --- OBJETO 3: USUÁRIOS (Autenticação) ---
    print("\n3. Tentando login (Objeto Gerenciador de Usuários)...")
    login_data = {"username": "admin", "senha": "admin123"}
    res_login = requests.post(f"{BASE_URL}/usuarios/login", json=login_data)
    if res_login.status_code == 200:
        print(f"Sucesso: Usuário '{res_login.json()['usuario']}' autenticado.")
    
    # --- OBJETO 2: CARRINHO ---
    print("\n4. Adicionando itens ao carrinho...")
    # Adicionando Clean Code (L001)
    requests.post(f"{BASE_URL}/carrinho/adicionar/L001?quantidade=2")
    # Adicionando Thriller (C001)
    requests.post(f"{BASE_URL}/carrinho/adicionar/C001?quantidade=1")

    print("\n5. Visualizando Carrinho de Compras...")
    res_carrinho = requests.get(f"{BASE_URL}/carrinho")
    carrinho = res_carrinho.json()
    
    for item in carrinho['itens']:
        print(f"- {item['quantidade']}x {item['titulo']} (Subtotal: R$ {item['subtotal']})")
    print(f"VALOR TOTAL: R$ {carrinho['valor_total']}")

    print("\n5.1. Consultando resumo do carrinho...")
    resumo = requests.get(f"{BASE_URL}/carrinho/resumo").json()
    print(format_json(resumo))

    # --- OPERAÇÃO DE BUSCA ---
    print("\n6. Buscando produto por título 'Pattern'...")
    res_busca = requests.get(f"{BASE_URL}/loja/produtos/buscar/Pattern")
    print(format_json(res_busca.json()))

    print("\n7. Consultando estatísticas do catálogo...")
    stats = requests.get(f"{BASE_URL}/loja/estatisticas")
    print(format_json(stats.json()))

if __name__ == "__main__":
    try:
        testar_sistema()
    except requests.exceptions.ConnectionError:
        print("ERRO: O servidor não está rodando! Execute 'uvicorn app.main:app --reload' primeiro.")