from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FaixaConfig:
    nome: str
    inicio: int
    fim: int


@dataclass
class EstrategiaConfig:
    nome: str
    descricao: str
    peso_quentes: float = 0.4
    peso_frios: float = 0.2
    peso_aleatorio: float = 0.4


@dataclass
class LotteryConfig:
    id: str
    nome_jogo: str
    total_numeros: int
    numeros_por_jogo: int
    numero_minimo: int = 1
    colunas_resultado: List[str] = field(default_factory=list)
    tabela_resultados: str = ""
    tabela_combinacoes: str = ""
    db_name: str = "LOTOFACIL"

    faixas: Dict[str, FaixaConfig] = field(default_factory=dict)
    estrategias: Dict[str, EstrategiaConfig] = field(default_factory=dict)
    primos: set = field(default_factory=set)
    fibonacci: set = field(default_factory=set)

    params_estatisticos: Dict = field(default_factory=lambda: {
        "consecutivos_max_comum": 2,
    })

    def __post_init__(self):
        if not self.colunas_resultado:
            self.colunas_resultado = [f"N{i}" for i in range(1, self.numeros_por_jogo + 1)]
        if not self.tabela_resultados:
            self.tabela_resultados = f"Resultados_{self.id}"
        if not self.tabela_combinacoes:
            self.tabela_combinacoes = f"COMBIN_{self.id}"

    @property
    def numeros(self):
        return list(range(self.numero_minimo, self.numero_maximo + 1))

    @property
    def numero_maximo(self):
        return self.numero_minimo + self.total_numeros - 1

    def validar_numero(self, numero: int) -> bool:
        return self.numero_minimo <= numero <= self.numero_maximo

    def validar_combinacao(self, combinacao):
        if len(combinacao) != self.numeros_por_jogo:
            return False, f"Deve ter exatamente {self.numeros_por_jogo} numeros"
        if len(set(combinacao)) != len(combinacao):
            return False, "Nao pode ter numeros repetidos"
        for num in combinacao:
            if not self.validar_numero(num):
                return False, f"Numero {num} fora da faixa valida"
        return True, "Combinacao valida"

    def get_faixa(self, numero: int) -> Optional[str]:
        for nome, faixa in self.faixas.items():
            if faixa.inicio <= numero <= faixa.fim:
                return nome
        return None

    def sql_select_resultados(self) -> str:
        cols = ", ".join(["Concurso"] + self.colunas_resultado)
        return f"SELECT {cols} FROM {self.tabela_resultados} ORDER BY Concurso"


class LotteryRegistry:
    _loterias: Dict[str, LotteryConfig] = {}

    @classmethod
    def registrar(cls, config: LotteryConfig):
        cls._loterias[config.id] = config

    @classmethod
    def get(cls, lottery_id: str) -> Optional[LotteryConfig]:
        return cls._loterias.get(lottery_id)

    @classmethod
    def listar(cls) -> List[LotteryConfig]:
        return list(cls._loterias.values())

    @classmethod
    def ids_disponiveis(cls) -> List[str]:
        return list(cls._loterias.keys())
