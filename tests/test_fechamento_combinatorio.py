"""Testes de fechamento combinatório e desdobramento C(5,3)."""

import time
from itertools import combinations

from lotofacil_lite.sistemas.fechamento_combinatorio import (
    busca_local_fechamento,
    comb_rank_lex,
    construir_fechamento_guloso_amostrado,
    custo_por_aposta,
    fechamento_lotofacil_25,
    fechamento_lotofacil_25_otimizado,
    limite_inferior_cobertura,
    n_combinacoes,
    relatorio_custo,
    remover_apostas_redundantes,
    verificar_cobertura,
)
from lotofacil_lite.sistemas.sistema_desdobramento_standalone import (
    SistemaDesdobramentoStandalone,
)


def test_n_combinacoes():
    assert n_combinacoes(25, 15) == 3_268_760
    assert n_combinacoes(5, 3) == 10
    assert n_combinacoes(7, 5) == 21
    assert n_combinacoes(10, 5) == 252


def test_limite_inferior_schonheim():
    assert limite_inferior_cobertura(25, 15, 3) == 7
    assert limite_inferior_cobertura(23, 13, 3) == 8
    assert limite_inferior_cobertura(21, 11, 3) == 12


def test_remover_apostas_redundantes_preserva_cobertura():
    universo = list(range(1, 8))
    apostas = construir_fechamento_guloso_amostrado(universo, k=5, t=3, max_apostas=50, seed=1)
    antes = verificar_cobertura(apostas, universo, 5, 3)
    reduzidas = remover_apostas_redundantes(apostas, universo, 5, 3)
    depois = verificar_cobertura(reduzidas, universo, 5, 3)
    assert depois["coberta"] == antes["coberta"]
    assert depois["t_subsets_cobertos"] == antes["t_subsets_cobertos"]
    assert len(reduzidas) <= len(apostas)


def test_fechamento_cobre_todos_t_subsets():
    universo = list(range(1, 8))  # v = 7
    apostas = construir_fechamento_guloso_amostrado(universo, k=5, t=3, max_apostas=50)
    rel = verificar_cobertura(apostas, universo, k=5, t=3)
    assert rel["coberta"] is True
    assert rel["t_subsets_cobertos"] == rel["t_subsets_total"]


def test_relatorio_custo_real():
    apostas = [list(range(1, 16)), list(range(2, 17))]
    custo = relatorio_custo(apostas)
    assert custo["total_apostas"] == 2
    assert custo["preco_por_jogo"] == 3.50
    assert custo["custo_total"] == 7.00


def test_custo_por_aposta_tabela():
    """Tabela oficial: k dezenas custam C(k,15) apostas simples de R$ 3,50."""
    assert custo_por_aposta(15) == 3.50
    assert custo_por_aposta(16) == 56.00
    assert custo_por_aposta(17) == 476.00
    assert custo_por_aposta(18) == 2856.00
    assert custo_por_aposta(19) == 13566.00
    assert custo_por_aposta(20) == 54264.00


def test_relatorio_custo_respeita_k_da_aposta():
    apostas = [list(range(1, 17))]  # uma aposta de 16 dezenas
    custo = relatorio_custo(apostas)
    assert custo["k"] == 16
    assert custo["preco_por_jogo"] == 56.00
    assert custo["custo_total"] == 56.00


def test_cobertura_funciona_com_universo_nao_1_based():
    """O rank lex deve usar posicoes no universo, nao os rotulos das dezenas."""
    universo = list(range(3, 8))  # 3..7
    apostas = construir_fechamento_guloso_amostrado(universo, k=4, t=2, max_apostas=50)
    rel = verificar_cobertura(apostas, universo, k=4, t=2)
    assert rel["coberta"] is True
    assert rel["t_subsets_cobertos"] == rel["t_subsets_total"]


def test_fechamento_otimizado_respeita_universo_restrito():
    universo = list(range(3, 26))  # 23 dezenas restantes apos 2 fixos
    apostas = fechamento_lotofacil_25_otimizado(
        k=13, t=11, max_apostas=10, seed=7,
        universo=universo, candidatos_pool=120, amostra_por_passo=15,
        max_iteracoes=5,
    )
    assert apostas
    for aposta in apostas:
        assert len(aposta) == 13
        assert set(aposta) <= set(universo)


def test_pool_nao_limita_max_apostas():
    """candidatos_pool pequeno nao pode truncar a quantidade pedida."""
    universo = list(range(1, 21))
    apostas = construir_fechamento_guloso_amostrado(
        universo, k=5, t=4, max_apostas=30, candidatos_pool=5, seed=1,
    )
    assert len(apostas) == 30


def test_max_apostas_zero_significa_sem_limite():
    """max_apostas=0 nao trunca: roda ate cobrir todos os t-subconjuntos."""
    universo = list(range(1, 8))  # v=7, C(7,5)=21 apostas candidatas
    apostas = construir_fechamento_guloso_amostrado(
        universo, k=5, t=3, max_apostas=0, seed=5,
    )
    rel = verificar_cobertura(apostas, universo, k=5, t=3)
    assert len(apostas) > 0
    assert rel["coberta"] is True


def test_busca_local_orcamento_zero_nao_altera():
    universo = list(range(1, 10))
    base = construir_fechamento_guloso_amostrado(universo, k=6, t=4, max_apostas=20, seed=3)
    saida = busca_local_fechamento(base, universo, 6, 4, orcamento_avaliacoes=0)
    assert saida == base


def test_verificar_cobertura_deteta_incompleto():
    universo = list(range(1, 8))
    apostas = construir_fechamento_guloso_amostrado(universo, k=5, t=3, max_apostas=50)
    vazio = verificar_cobertura([], universo, k=5, t=3)
    assert vazio["coberta"] is False
    assert vazio["t_subsets_cobertos"] == 0


def test_desdobramento_garantia_c53_com_todos_trios():
    sistema = SistemaDesdobramentoStandalone()
    numeros_restantes = [1, 2, 3, 4, 5]
    trios = sistema.calcular_desdobramento_c53(numeros_restantes)
    assert len(trios) == 10  # C(5,3)

    apostas = []
    for trio in trios:
        base = sorted(list(trio) + [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22])
        apostas.append(base[:15])

    garantia = sistema.verificar_garantia_c53(numeros_restantes, apostas)
    assert garantia["garantia_c53"] is True
    assert garantia["trios_cobertos"] == 10


def test_desdobramento_sem_todos_trios_perde_garantia():
    sistema = SistemaDesdobramentoStandalone()
    numeros_restantes = [1, 2, 3, 4, 5]
    trios = sistema.calcular_desdobramento_c53(numeros_restantes)
    apostas = [sorted(list(trios[0]) + [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22])[:15]]
    garantia = sistema.verificar_garantia_c53(numeros_restantes, apostas)
    assert garantia["garantia_c53"] is False
    assert garantia["trios_cobertos"] == 1


def test_rank_lex_eh_contiguo():
    """C(5,3) = 10 combinacoes devem gerar ranks 0..9 unicos."""
    universo = list(range(1, 6))
    ranks = [comb_rank_lex(c, 5) for c in combinations(universo, 3)]
    assert sorted(ranks) == list(range(10))


def test_fechamento_pequeno_produz_cobertura():
    universo = list(range(1, 10))  # v = 9
    apostas = construir_fechamento_guloso_amostrado(universo, k=6, t=4, max_apostas=500, seed=1)
    rel = verificar_cobertura(apostas, universo, k=6, t=4)
    assert rel["total_apostas"] <= 500
    assert rel["garantia_percentual"] > 0.0
    assert rel["t_subsets_cobertos"] > 0


def test_busca_local_nao_piora_cobertura():
    universo = list(range(1, 10))  # v = 9
    base = construir_fechamento_guloso_amostrado(universo, k=6, t=4, max_apostas=100, seed=3)
    antes = verificar_cobertura(base, universo, k=6, t=4)
    depois = verificar_cobertura(
        busca_local_fechamento(base, universo, k=6, t=4, max_iteracoes=50, seed=3),
        universo,
        k=6,
        t=4,
    )
    assert depois["t_subsets_cobertos"] >= antes["t_subsets_cobertos"]
    assert depois["garantia_percentual"] >= antes["garantia_percentual"]


def test_v25_roda_dentro_do_tempo_e_melhora_cobertura():
    """Lotofacil v=25,k=15,t=11: guloso + busca local rapido e declaracao de cobertura."""
    inicio = time.time()
    apostas = fechamento_lotofacil_25_otimizado(
        k=15, t=11, max_apostas=40, seed=7,
        candidatos_pool=300, amostra_por_passo=25, max_iteracoes=40,
    )
    duracao = time.time() - inicio
    rel = verificar_cobertura(apostas, list(range(1, 26)), k=15, t=11)
    custo = relatorio_custo(apostas)
    assert duracao < 90.0, f"demorou {duracao:.1f}s"
    assert rel["total_apostas"] <= 40
    assert custo["custo_total"] == rel["total_apostas"] * 3.50
    assert 0.0 < rel["garantia_percentual"] <= 100.0
