import com.google.gson.*;
import java.util.*;

public class Main {
    private static ApiClient api;
    private static Scanner scanner;
    private static String usuarioLogado = null;
    private static final String RESET = "\033[0m";
    private static final String BLUE = "\033[34m";
    private static final String GREEN = "\033[32m";
    private static final String YELLOW = "\033[33m";
    private static final String RED = "\033[31m";

    public static void main(String[] args) {
        api = new ApiClient();
        scanner = new Scanner(System.in);

        exibirBemVindo();
        carregarNomeLoja();
        menuPrincipal();
    }

    private static void exibirBemVindo() {
        System.out.println(BLUE + "\n╔════════════════════════════════════════════════════╗");
        System.out.println("║   CLIENTE SEBO VIRTUAL - TRABALHO 3 (Java)        ║");
        System.out.println("║   Sistemas Distribuídos                           ║");
        System.out.println("╚════════════════════════════════════════════════════╝" + RESET);
    }

    private static void carregarNomeLoja() {
        System.out.println("\n⏳ Conectando ao servidor...");
        JsonElement res = api.get("/loja/nome");
        if (res != null && res.isJsonObject()) {
            String nomeLoja = res.getAsJsonObject().get("nome").getAsString();
            System.out.println(GREEN + "✓ Conectado a: " + nomeLoja + RESET);
        } else {
            System.out.println(RED + "✗ Erro ao conectar ao servidor!" + RESET);
        }
    }

    private static void menuPrincipal() {
        boolean ativo = true;
        
        while (ativo) {
            System.out.println(BLUE + "\n┌─ MENU PRINCIPAL ─────────────────────────────────┐");
            System.out.println("│ 1. Login / Autenticação");
            System.out.println("│ 2. Listar Catálogo Completo");
            System.out.println("│ 3. Buscar Produto por Título");
            System.out.println("│ 4. Carrinho de Compras");
            System.out.println("│ 5. Ver Usuários Ativos");
            System.out.println("│ 0. Sair");
            System.out.println("└──────────────────────────────────────────────────┘" + RESET);

            System.out.print("\nEscolha uma opção: ");
            int opcao = lerInteiro();

            switch (opcao) {
                case 1:
                    menuLogin();
                    break;
                case 2:
                    listarProdutos();
                    break;
                case 3:
                    buscarProduto();
                    break;
                case 4:
                    menuCarrinho();
                    break;
                case 5:
                    exibirAtivos();
                    break;
                case 0:
                    System.out.println(GREEN + "\n👋 Até logo!" + RESET);
                    ativo = false;
                    break;
                default:
                    System.out.println(RED + "Opção inválida!" + RESET);
            }
            
            if (ativo) {
                System.out.print("\n[Pressione ENTER para continuar...]");
                scanner.nextLine();
            }
        }
        scanner.close();
    }

    // ═══════════════════════════════════════════════════════════════
    // AUTENTICAÇÃO (OBJETO 3)
    // ═══════════════════════════════════════════════════════════════
    private static void menuLogin() {
        if (usuarioLogado != null) {
            System.out.println(GREEN + "✓ Você já está logado como: " + usuarioLogado + RESET);
            return;
        }

        System.out.println(YELLOW + "\n━━ LOGIN ━━" + RESET);
        System.out.print("Usuário: ");
        String usuario = scanner.nextLine();
        System.out.print("Senha: ");
        String senha = scanner.nextLine();

        JsonObject loginData = new JsonObject();
        loginData.addProperty("username", usuario);
        loginData.addProperty("senha", senha);

        JsonElement res = api.post("/usuarios/login", loginData);

        if (res != null && res.isJsonObject()) {
            String status = res.getAsJsonObject().get("status").getAsString();
            if (status.equals("Autenticado")) {
                usuarioLogado = usuario;
                System.out.println(GREEN + "✓ Login bem-sucedido! Bem-vindo, " + usuario + RESET);
                System.out.println(api.getUltimaResposta());
                return;
            }
        }

        System.out.println(RED + "✗ Usuário ou senha incorretos!" + RESET);
        System.out.println(api.getUltimaResposta());
    }

    // ═══════════════════════════════════════════════════════════════
    // CATÁLOGO (OBJETO 1)
    // ═══════════════════════════════════════════════════════════════
    private static void listarProdutos() {
        System.out.println(YELLOW + "\n━━ CATÁLOGO COMPLETO ━━" + RESET);
        
        JsonElement res = api.get("/loja/produtos");
        System.out.println(api.getUltimaResposta());

        if (res != null && res.isJsonArray()) {
            JsonArray produtos = res.getAsJsonArray();
            
            if (produtos.size() == 0) {
                System.out.println(RED + "Nenhum produto encontrado." + RESET);
                return;
            }

            System.out.println(BLUE + String.format("\n%-8s %-30s %-12s %-10s", 
                    "CÓDIGO", "TÍTULO", "TIPO", "PREÇO") + RESET);
            System.out.println("─".repeat(70));

            for (JsonElement p : produtos) {
                JsonObject prod = p.getAsJsonObject();
                String codigo = prod.get("codigo").getAsString();
                String titulo = prod.get("titulo").getAsString();
                String tipo = prod.get("tipo").getAsString();
                double preco = prod.get("preco").getAsDouble();

                System.out.printf("%-8s %-30s %-12s R$ %.2f\n", 
                        codigo, titulo, tipo, preco);
            }
        } else {
            System.out.println(RED + "✗ Erro ao carregar catálogo!" + RESET);
        }
    }

    private static void buscarProduto() {
        System.out.println(YELLOW + "\n━━ BUSCAR PRODUTO ━━" + RESET);
        System.out.print("Digite o título a buscar: ");
        String titulo = scanner.nextLine();

        JsonElement res = api.get("/loja/produtos/buscar/" + titulo);
        System.out.println(api.getUltimaResposta());

        if (res != null && res.isJsonArray()) {
            JsonArray resultados = res.getAsJsonArray();
            
            if (resultados.size() == 0) {
                System.out.println(YELLOW + "Nenhum produto encontrado para: " + titulo + RESET);
                return;
            }

            System.out.println(GREEN + "\n✓ Encontrados " + resultados.size() + " resultado(s):\n" + RESET);
            api.imprimirJson(res);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // CARRINHO (OBJETO 2)
    // ═══════════════════════════════════════════════════════════════
    private static void menuCarrinho() {
        boolean carrinhoAtivo = true;

        while (carrinhoAtivo) {
            System.out.println(BLUE + "\n┌─ CARRINHO DE COMPRAS ────────────────────────────┐");
            System.out.println("│ 1. Ver Itens do Carrinho");
            System.out.println("│ 2. Adicionar Produto");
            System.out.println("│ 3. Limpar Carrinho");
            System.out.println("│ 0. Voltar");
            System.out.println("└──────────────────────────────────────────────────┘" + RESET);

            System.out.print("\nEscolha uma opção: ");
            int opcao = lerInteiro();

            switch (opcao) {
                case 1:
                    verCarrinho();
                    break;
                case 2:
                    adicionarAoCarrinho();
                    break;
                case 3:
                    limparCarrinho();
                    break;
                case 0:
                    carrinhoAtivo = false;
                    break;
                default:
                    System.out.println(RED + "Opção inválida!" + RESET);
            }
        }
    }

    private static void verCarrinho() {
        System.out.println(YELLOW + "\n━━ ITENS NO CARRINHO ━━" + RESET);
        
        JsonElement res = api.get("/carrinho");
        System.out.println(api.getUltimaResposta());

        if (res != null && res.isJsonObject()) {
            JsonObject carrinho = res.getAsJsonObject();
            JsonArray itens = carrinho.getAsJsonArray("itens");

            if (itens.size() == 0) {
                System.out.println(YELLOW + "Seu carrinho está vazio." + RESET);
                return;
            }

            System.out.println(BLUE + String.format("\n%-30s %5s %12s %12s", 
                    "PRODUTO", "QTD", "PREÇO UN.", "SUBTOTAL") + RESET);
            System.out.println("─".repeat(65));

            for (JsonElement item : itens) {
                JsonObject it = item.getAsJsonObject();
                String titulo = it.get("titulo").getAsString();
                int qtd = it.get("quantidade").getAsInt();
                double preco = it.get("preco").getAsDouble();
                double subtotal = it.get("subtotal").getAsDouble();

                System.out.printf("%-30s %5d R$%10.2f R$%10.2f\n", 
                        titulo, qtd, preco, subtotal);
            }

            System.out.println("─".repeat(65));
            double total = carrinho.get("valor_total").getAsDouble();
            System.out.printf(GREEN + "TOTAL: R$ %.2f" + RESET + "\n", total);
        }
    }

    private static void adicionarAoCarrinho() {
        System.out.println(YELLOW + "\n━━ ADICIONAR AO CARRINHO ━━" + RESET);
        System.out.print("Código do produto: ");
        String codigo = scanner.nextLine();
        System.out.print("Quantidade: ");
        int quantidade = lerInteiro();

        JsonElement res = api.get("/carrinho/adicionar/" + codigo + "?quantidade=" + quantidade);
        System.out.println(api.getUltimaResposta());

        if (res != null) {
            System.out.println(GREEN + "✓ Produto adicionado ao carrinho!" + RESET);
        } else {
            System.out.println(RED + "✗ Erro ao adicionar produto!" + RESET);
        }
    }

    private static void limparCarrinho() {
        System.out.print("\nTem certeza que deseja limpar o carrinho? (s/n): ");
        String confirmacao = scanner.nextLine();

        if (confirmacao.equalsIgnoreCase("s")) {
            JsonElement res = api.post("/carrinho/limpar", new JsonObject());
            System.out.println(api.getUltimaResposta());
            System.out.println(GREEN + "✓ Carrinho limpo!" + RESET);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // USUÁRIOS ATIVOS
    // ═══════════════════════════════════════════════════════════════
    private static void exibirAtivos() {
        System.out.println(YELLOW + "\n━━ USUÁRIOS ATIVOS ━━" + RESET);
        
        JsonElement res = api.get("/usuarios/ativos");
        System.out.println(api.getUltimaResposta());

        if (res != null && res.isJsonObject()) {
            JsonArray usuarios = res.getAsJsonObject().getAsJsonArray("usuarios_conectados");
            
            if (usuarios.size() == 0) {
                System.out.println(YELLOW + "Ninguém conectado no momento." + RESET);
                return;
            }

            System.out.println(GREEN + "\n✓ Usuários conectados:\n" + RESET);
            for (int i = 0; i < usuarios.size(); i++) {
                System.out.println("  " + (i + 1) + ". " + usuarios.get(i).getAsString());
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // UTILIDADES
    // ═══════════════════════════════════════════════════════════════
    private static int lerInteiro() {
        try {
            return Integer.parseInt(scanner.nextLine());
        } catch (NumberFormatException e) {
            return -1;
        }
    }
}
