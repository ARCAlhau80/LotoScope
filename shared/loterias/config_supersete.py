from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_SUPERSETE = LotteryConfig(
    id="supersete",
    nome_jogo="Super Sete",
    total_numeros=10,
    numeros_por_jogo=7,
    numero_minimo=0,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_SuperSete",
    faixas={
        "baixa": FaixaConfig("Baixa (0-3)", 0, 3),
        "media": FaixaConfig("Média (4-6)", 4, 6),
        "alta": FaixaConfig("Alta (7-9)", 7, 9),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme"),
        "baixos": EstrategiaConfig("Baixos", "Prioriza digitos baixos"),
        "altos": EstrategiaConfig("Altos", "Prioriza digitos altos"),
    },
    primos={2, 3, 5, 7},
    fibonacci={0, 1, 2, 3, 5, 8},
    params_estatisticos={
        "consecutivos_max_comum": 0,
        "soma_minima": 0,
        "soma_maxima": 63,
        "soma_media_esperada": 31,
    },
    is_positional=True,
)

LotteryRegistry.registrar(CONFIG_SUPERSETE)
