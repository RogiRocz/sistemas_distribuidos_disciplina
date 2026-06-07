from app.modelos.loja import Loja
from app.modelos.carrinho import CarrinhoCompras
from app.modelos.usuarios import GerenciadorUsuarios
from app.modelos.livro import Livro
from app.modelos.cd import CD
from app.modelos.ebook import Ebook
from app.modelos.apostila import Apostila

# Inicialização centralizada em memória simulando os objetos remotos compartilhados
loja_instance = Loja(nome="Sebo Virtual UFC")
carrinho_instance = CarrinhoCompras()
usuarios_instance = GerenciadorUsuarios()

# Carga do catálogo inicial (idêntica à do Trabalho anterior)
loja_instance.adicionar_produto(Livro("L001", "Clean Code", 89.90, "Robert C. Martin", "Prentice Hall", 2008))
loja_instance.adicionar_produto(Livro("L002", "Design Patterns", 120.00, "Gang of Four", "Addison-Wesley", 1994))
loja_instance.adicionar_produto(CD("C001", "Thriller", 35.00, "Michael Jackson", "Pop"))
loja_instance.adicionar_produto(Ebook("E001", "Python for Developers", 29.90, "PDF", 15.5))
loja_instance.adicionar_produto(Apostila("A001", "Sistemas Distribuídos", 50.00, "Engenharia de Software", "UFC Quixadá"))