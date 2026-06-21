from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_LOTOMANIA = LotteryConfig(
    id="lotomania",
    nome_jogo="Lotomania",
    total_numeros=100,
    numeros_por_jogo=20,
    numero_minimo=0,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_Lotomania",
    faixas={
        "baixa": FaixaConfig("Baixa (0-33)", 0, 33),
        "media": FaixaConfig("Média (34-66)", 34, 66),
        "alta": FaixaConfig("Alta (67-99)", 67, 99),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme por faixas"),
        "concentrada": EstrategiaConfig("Concentrada", "Prioriza faixa media"),
        "dispersa": EstrategiaConfig("Dispersa", "Prioriza extremos"),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97},
    fibonacci={0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 0,
        "soma_maxima": 1990,
        "soma_media_esperada": 990,
        "pares_mais_comum": 10,
        "impares_mais_comum": 10,
    },
)

LotteryRegistry.registrar(CONFIG_LOTOMANIA)
