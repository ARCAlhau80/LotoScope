import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLotteryConfigPublicAPI:
    def test_lottery_config_import(self):
        from shared.lottery_config import LotteryConfig, FaixaConfig, EstrategiaConfig
        cfg = LotteryConfig(
            id="teste",
            nome_jogo="Teste",
            total_numeros=10,
            numeros_por_jogo=3,
        )
        assert cfg.id == "teste"
        assert cfg.numero_minimo == 1
        assert cfg.numero_maximo == 10
        assert cfg.colunas_resultado == ["N1", "N2", "N3"]

    def test_validar_combinacao_valida(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=25, numeros_por_jogo=5)
        valida, msg = cfg.validar_combinacao([1, 5, 10, 15, 20])
        assert valida

    def test_validar_combinacao_tamanho_errado(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=25, numeros_por_jogo=5)
        valida, msg = cfg.validar_combinacao([1, 5, 10])
        assert not valida

    def test_validar_combinacao_repetidos(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=25, numeros_por_jogo=5)
        valida, msg = cfg.validar_combinacao([1, 5, 10, 10, 20])
        assert not valida

    def test_validar_combinacao_fora_faixa(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=25, numeros_por_jogo=5)
        valida, msg = cfg.validar_combinacao([1, 5, 10, 15, 30])
        assert not valida

    def test_get_faixa(self):
        from shared.lottery_config import LotteryConfig, FaixaConfig
        cfg = LotteryConfig(
            id="test", nome_jogo="Test", total_numeros=60, numeros_por_jogo=6,
            faixas={
                "baixa": FaixaConfig("Baixa", 1, 20),
                "alta": FaixaConfig("Alta", 21, 60),
            },
        )
        assert cfg.get_faixa(10) == "baixa"
        assert cfg.get_faixa(30) == "alta"
        assert cfg.get_faixa(99) is None

    def test_property_numeros(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=10, numeros_por_jogo=3, numero_minimo=0)
        assert cfg.numeros == list(range(0, 10))
        assert cfg.numero_maximo == 9

    def test_sql_select_resultados(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=10, numeros_por_jogo=3)
        sql = cfg.sql_select_resultados()
        assert "SELECT" in sql
        assert "N1, N2, N3" in sql or "Concurso" in sql
        assert "ORDER BY Concurso" in sql

    def test_is_positional_default_false(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=10, numeros_por_jogo=3)
        assert not cfg.is_positional

    def test_is_positional_true(self):
        from shared.lottery_config import LotteryConfig
        cfg = LotteryConfig(id="test", nome_jogo="Test", total_numeros=10, numeros_por_jogo=3, is_positional=True)
        assert cfg.is_positional


class TestLotteryLoader:
    def test_carregar_todas_configs(self):
        from shared.lottery_loader import carregar_todas_loterias
        configs = carregar_todas_loterias()
        assert len(configs) >= 9
        ids = [c.id for c in configs]
        assert "lotofacil" in ids
        assert "megasena" in ids
        assert "quina" in ids
        assert "duplasena" in ids
        assert "supersete" in ids
        assert "lotomania" in ids
        assert "diadesorte" in ids
        assert "timemania" in ids

    def test_get_loteria_existente(self):
        from shared.lottery_loader import get_loteria
        cfg = get_loteria("lotofacil")
        assert cfg is not None
        assert cfg.id == "lotofacil"
        assert cfg.total_numeros == 25

    def test_get_loteria_inexistente(self):
        from shared.lottery_loader import get_loteria
        cfg = get_loteria("nao_existe")
        assert cfg is None

    def test_listar_ids(self):
        from shared.lottery_loader import listar_ids_loterias
        ids = listar_ids_loterias()
        assert "lotofacil" in ids
        assert "megasena" in ids

    def test_supersete_config_posicional(self):
        from shared.lottery_loader import get_loteria
        cfg = get_loteria("supersete")
        assert cfg is not None
        assert cfg.is_positional
        assert cfg.numero_minimo == 0
        assert cfg.total_numeros == 10

    def test_megasena_id_correto(self):
        from shared.lottery_loader import get_loteria
        cfg = get_loteria("megasena")
        assert cfg is not None
        assert cfg.total_numeros == 60
        assert cfg.numeros_por_jogo == 6

    def test_quina_faixas(self):
        from shared.lottery_loader import get_loteria
        cfg = get_loteria("quina")
        assert cfg is not None
        assert "baixa" in cfg.faixas
        assert "media" in cfg.faixas
        assert "alta" in cfg.faixas


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
