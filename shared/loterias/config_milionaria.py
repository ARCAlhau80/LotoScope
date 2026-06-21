from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_MILIONARIA = LotteryConfig(
    id="maismilionaria",
    nome_jogo="Mais Milionária",
    total_numeros=50,
    numeros_por_jogo=6,
    numero_minimo=1,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_MaisMilionaria",
    faixas={
        "baixa": FaixaConfig("Baixa (1-17)", 1, 17),
        "media": FaixaConfig("Média (18-34)", 18, 34),
        "alta": FaixaConfig("Alta (35-50)", 35, 50),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme"),
        "baixos": EstrategiaConfig("Baixos", "Foco em baixos"),
        "altos": EstrategiaConfig("Altos", "Foco em altos"),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47},
    fibonacci={1, 2, 3, 5, 8, 13, 21, 34},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 21,
        "soma_maxima": 279,
        "soma_media_esperada": 153,
    },
)

LotteryRegistry.registrar(CONFIG_MILIONARIA)
