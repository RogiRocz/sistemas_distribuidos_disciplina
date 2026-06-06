from .produto import Produto

@dataclass
class Carrinho:
	itens: Dict[Produto, int] = field(default_factory=dict)