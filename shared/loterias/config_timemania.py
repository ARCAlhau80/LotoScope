from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_TIMEMANIA = LotteryConfig(
    id="timemania",
    nome_jogo="Timemania",
    total_numeros=80,
    numeros_por_jogo=7,
    numero_minimo=1,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_Timemania",
    faixas={
        "baixa": FaixaConfig("Baixa (1-27)", 1, 27),
        "media": FaixaConfig("Média (28-54)", 28, 54),
        "alta": FaixaConfig("Alta (55-80)", 55, 80),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme"),
        "torcida": EstrategiaConfig("Torcida", "Foco em baixos"),
        "visitante": EstrategiaConfig("Visitante", "Foco em altos"),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79},
    fibonacci={1, 2, 3, 5, 8, 13, 21, 34, 55},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 28,
        "soma_maxima": 532,
        "soma_media_esperada": 280,
    },
)

LotteryRegistry.registrar(CONFIG_TIMEMANIA)
