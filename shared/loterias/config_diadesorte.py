from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_DIADESORTE = LotteryConfig(
    id="diadesorte",
    nome_jogo="Dia de Sorte",
    total_numeros=31,
    numeros_por_jogo=7,
    numero_minimo=1,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_DiaDeSorte",
    faixas={
        "baixa": FaixaConfig("Baixa (1-10)", 1, 10),
        "media": FaixaConfig("Média (11-20)", 11, 20),
        "alta": FaixaConfig("Alta (21-31)", 21, 31),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme"),
        "concentrada": EstrategiaConfig("Concentrada", "Foco em numeros baixos"),
        "dispersa": EstrategiaConfig("Dispersa", "Foco em numeros altos"),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31},
    fibonacci={1, 2, 3, 5, 8, 13, 21},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 28,
        "soma_maxima": 196,
        "soma_media_esperada": 112,
    },
)

LotteryRegistry.registrar(CONFIG_DIADESORTE)
