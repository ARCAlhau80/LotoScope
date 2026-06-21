from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_DUPLASENA = LotteryConfig(
    id="duplasena",
    nome_jogo="Dupla Sena",
    total_numeros=50,
    numeros_por_jogo=6,
    numero_minimo=1,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_DuplaSena",
    tabela_combinacoes="COMBIN_DUPLASENA",
    faixas={
        "baixa": FaixaConfig("Baixa (1-17)", 1, 17),
        "media": FaixaConfig("Média (18-34)", 18, 34),
        "alta": FaixaConfig("Alta (35-50)", 35, 50),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme por faixas", 0.4, 0.2, 0.4),
        "quentes": EstrategiaConfig("Numeros Quentes", "Prioriza numeros mais frequentes", 0.7, 0.1, 0.2),
        "frios": EstrategiaConfig("Numeros Frios", "Prioriza numeros menos frequentes", 0.1, 0.7, 0.2),
        "contrarian": EstrategiaConfig("Contraria", "Mix de quentes e frios", 0.3, 0.3, 0.4),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47},
    fibonacci={1, 2, 3, 5, 8, 13, 21, 34},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 21,
        "soma_maxima": 285,
        "soma_media_esperada": 153,
        "pares_mais_comum": 3,
        "impares_mais_comum": 3,
    },
)

LotteryRegistry.registrar(CONFIG_DUPLASENA)
