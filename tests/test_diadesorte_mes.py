from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_config_diadesorte_tem_mes_sorte_e_apostas_multiplas():
    from shared.lottery_loader import get_loteria

    cfg = get_loteria("diadesorte")
    assert cfg is not None
    assert cfg.mes_sorte is True
    assert cfg.mes_sorte_col == "Mes_Sorte"
    assert cfg.max_dezenas == 15


def test_mes_por_nome_tolera_acento_e_prefixo():
    from shared.loterias.mes_sorte import mes_por_nome, nome_mes

    assert mes_por_nome("Outubro") == 10
    assert mes_por_nome("MARÇO") == 3
    assert mes_por_nome("Mês de Fevereiro") == 2
    assert mes_por_nome("") is None
    assert nome_mes(12) == "Dezembro"
    assert nome_mes(13) is None


def test_parser_reconhece_sufixo_m_do_mes():
    from shared.apostador.parser import parse_jogos_texto

    jogos = parse_jogos_texto(
        "1,2,3,4,5,6,7|M:10\n8,9,10,11,12,13,14|M:3\n15,16,17,18,19,20,21",
        mes_sorte=True,
    )
    assert len(jogos) == 3
    assert jogos[0].numeros == [1, 2, 3, 4, 5, 6, 7]
    assert jogos[0].mes == 10
    assert jogos[1].mes == 3
    assert jogos[2].mes is None


def test_validar_jogos_aceita_e_rejeita_mes():
    from shared.lottery_loader import get_loteria
    from shared.apostador.parser import JogoApostador, validar_jogos

    cfg = get_loteria("diadesorte")
    ok = validar_jogos(cfg, [JogoApostador(numeros=[1, 2, 3, 4, 5, 6, 7], mes=10)])
    assert len(ok["validos"]) == 1
    assert ok["validos"][0]["mes"] == 10

    invalido = validar_jogos(cfg, [JogoApostador(numeros=[1, 2, 3, 4, 5, 6, 7], mes=13)])
    assert len(invalido["invalids"]) == 1
    assert "Mês da Sorte inválido" in invalido["invalids"][0]["mensagem"]


def test_atualizador_extrai_mes_da_api_da_caixa():
    from shared.loterias.atualizador_diadesorte import AtualizadorDiaDeSorte

    atualizador = AtualizadorDiaDeSorte(get_connection=lambda: None)
    extras = atualizador.extra_campos_estatisticos(
        1, [1, 2, 3, 4, 5, 6, 7], "16/11/2026", {"nomeTimeCoracaoMesSorte": "Outubro"}
    )
    assert extras == {"Mes_Sorte": 10}

