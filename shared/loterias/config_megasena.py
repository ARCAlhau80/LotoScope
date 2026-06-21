from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_MEGASENA = LotteryConfig(
    id="megasena",
    nome_jogo="Mega-Sena",
    total_numeros=60,
    numeros_por_jogo=6,
    numero_minimo=1,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_MegaSenaFechado",
    tabela_combinacoes="COMBIN_MEGASENA",
    faixas={
        "baixa": FaixaConfig("Baixa (1-20)", 1, 20),
        "media": FaixaConfig("Média (21-40)", 21, 40),
        "alta": FaixaConfig("Alta (41-60)", 41, 60),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme por faixas", 0.4, 0.2, 0.4),
        "quentes": EstrategiaConfig("Numeros Quentes", "Prioriza numeros mais frequentes", 0.7, 0.1, 0.2),
        "frios": EstrategiaConfig("Numeros Frios", "Prioriza numeros menos frequentes", 0.1, 0.7, 0.2),
        "contrarian": EstrategiaConfig("Contraria", "Mix de quentes e frios", 0.3, 0.3, 0.4),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59},
    fibonacci={1, 2, 3, 5, 8, 13, 21, 34, 55},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 21,
        "soma_maxima": 345,
        "soma_media_esperada": 183,
        "pares_mais_comum": 3,
        "impares_mais_comum": 3,
    },
)

LotteryRegistry.registrar(CONFIG_MEGASENA)
