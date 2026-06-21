from shared.loterias.config_base import LotteryConfig, FaixaConfig, EstrategiaConfig, LotteryRegistry

CONFIG_LOTOFACIL = LotteryConfig(
    id="lotofacil",
    nome_jogo="Lotofácil",
    total_numeros=25,
    numeros_por_jogo=15,
    numero_minimo=1,
    db_name="LOTOFACIL",
    tabela_resultados="Resultados_INT",
    tabela_combinacoes="COMBINACOES_LOTOFACIL",
    faixas={
        "baixa": FaixaConfig("Baixa (1-12)", 1, 12),
        "alta": FaixaConfig("Alta (13-25)", 13, 25),
    },
    estrategias={
        "equilibrada": EstrategiaConfig("Equilibrada", "Distribuicao uniforme", 0.4, 0.2, 0.4),
        "quentes": EstrategiaConfig("Numeros Quentes", "Prioriza mais frequentes", 0.7, 0.1, 0.2),
        "frios": EstrategiaConfig("Numeros Frios", "Prioriza menos frequentes", 0.1, 0.7, 0.2),
        "invertida": EstrategiaConfig("Invertida v3.0", "Exclui QUENTES (mean reversion)", 0.3, 0.3, 0.4),
    },
    primos={2, 3, 5, 7, 11, 13, 17, 19, 23},
    fibonacci={1, 2, 3, 5, 8, 13, 21},
    params_estatisticos={
        "consecutivos_max_comum": 2,
        "soma_minima": 120,
        "soma_maxima": 210,
        "soma_media_esperada": 195,
        "pares_mais_comum": 7,
        "impares_mais_comum": 8,
    },
)

LotteryRegistry.registrar(CONFIG_LOTOFACIL)
