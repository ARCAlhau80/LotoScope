import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supersete.gerador_supersete import GeradorSuperSete
from supersete.validador_supersete import ValidadorSuperSete
from supersete.backtest_supersete import BacktestSuperSete


RESULTADOS_MOCK = [
    [2, 3, 1, 0, 2, 3, 1],
    [5, 6, 4, 5, 6, 6, 5],
    [7, 8, 9, 7, 8, 9, 8],
    [2, 3, 1, 0, 2, 3, 1],
    [5, 6, 4, 5, 6, 6, 5],
    [7, 8, 9, 7, 8, 9, 8],
    [0, 0, 0, 0, 0, 0, 0],
    [9, 9, 9, 9, 9, 9, 9],
    [3, 4, 5, 6, 7, 8, 2],
    [1, 2, 3, 4, 5, 6, 7],
    [2, 3, 1, 0, 2, 3, 1],
    [5, 6, 4, 5, 6, 6, 5],
    [7, 8, 9, 7, 8, 9, 8],
    [0, 1, 2, 3, 4, 5, 6],
    [9, 8, 7, 6, 5, 4, 3],
    [2, 3, 1, 0, 2, 3, 1],
    [5, 6, 4, 5, 6, 6, 5],
    [7, 8, 9, 7, 8, 9, 8],
    [4, 5, 6, 7, 8, 9, 0],
    [1, 2, 3, 4, 5, 6, 7],
]


class TestValidadorSuperSete:
    def setup_method(self):
        self.validador = ValidadorSuperSete()

    def test_jogo_simples_valido(self):
        jogo = [2, 3, 1, 0, 5, 6, 7]
        valido, msg = self.validador.validar_jogo_simples(jogo)
        assert valido
        assert msg == "Jogo válido"

    def test_jogo_simples_tamanho_errado(self):
        jogo = [2, 3, 1]
        valido, msg = self.validador.validar_jogo_simples(jogo)
        assert not valido

    def test_jogo_simples_digito_invalido(self):
        jogo = [2, 3, 1, 0, 5, 6, 10]
        valido, msg = self.validador.validar_jogo_simples(jogo)
        assert not valido

    def test_jogo_simples_digito_negativo(self):
        jogo = [2, 3, -1, 0, 5, 6, 7]
        valido, msg = self.validador.validar_jogo_simples(jogo)
        assert not valido

    def test_aposta_multipla_valida_2_por_coluna(self):
        aposta = {col: [0, 5] for col in range(7)}
        valido, msg = self.validador.validar_aposta_multipla(aposta)
        assert valido

    def test_aposta_multipla_coluna_ausente(self):
        aposta = {col: [0, 5] for col in range(6)}
        valido, msg = self.validador.validar_aposta_multipla(aposta)
        assert not valido

    def test_aposta_multipla_digito_duplicado(self):
        aposta = {col: [0, 5] for col in range(7)}
        aposta[3] = [5, 5]
        valido, msg = self.validador.validar_aposta_multipla(aposta)
        assert not valido

    def test_calcular_acertos_7(self):
        jogo = [2, 3, 1, 0, 5, 6, 7]
        resultado = [2, 3, 1, 0, 5, 6, 7]
        acertos = self.validador.calcular_acertos(jogo, resultado)
        assert acertos['total_acertos'] == 7
        assert '1º Prêmio' in acertos['faixa_premio']

    def test_calcular_acertos_3(self):
        jogo = [2, 3, 1, 0, 5, 6, 7]
        resultado = [2, 3, 1, 9, 9, 9, 9]
        acertos = self.validador.calcular_acertos(jogo, resultado)
        assert acertos['total_acertos'] == 3
        assert '5º Prêmio' in acertos['faixa_premio']

    def test_calcular_acertos_zero(self):
        jogo = [0, 0, 0, 0, 0, 0, 0]
        resultado = [1, 1, 1, 1, 1, 1, 1]
        acertos = self.validador.calcular_acertos(jogo, resultado)
        assert acertos['total_acertos'] == 0

    def test_calcular_acertos_multipla(self):
        aposta = {0: [2, 5], 1: [3, 6], 2: [1, 4], 3: [0, 5], 4: [2, 8], 5: [3, 9], 6: [1, 8]}
        resultado = [2, 3, 1, 0, 2, 3, 1]
        acertos = self.validador.calcular_acertos_multipla(aposta, resultado)
        assert acertos['total_acertos'] == 7

    def test_validar_restricoes_soma(self):
        jogo = [9, 9, 9, 9, 9, 9, 9]
        valido, violacoes = self.validador.validar_restricoes(jogo, {'soma_max': 50})
        assert not valido
        assert len(violacoes) > 0

    def test_validar_restricoes_ok(self):
        jogo = [2, 3, 1, 0, 5, 6, 7]
        valido, violacoes = self.validador.validar_restricoes(jogo, {'soma_min': 10, 'soma_max': 50})
        assert valido
        assert len(violacoes) == 0


class TestGeradorSuperSete:
    def setup_method(self):
        self.gerador = GeradorSuperSete(resultados=RESULTADOS_MOCK, janela_recente=10)

    def test_gerar_jogo_simples_tamanho(self):
        jogo = self.gerador.gerar_jogo_simples()
        assert len(jogo) == 7

    def test_gerar_jogo_simples_range(self):
        jogo = self.gerador.gerar_jogo_simples()
        for d in jogo:
            assert 0 <= d <= 9

    def test_gerar_multiplos_jogos(self):
        jogos = self.gerador.gerar_multiplos_jogos(quantidade=10)
        assert len(jogos) == 10
        for jogo in jogos:
            assert len(jogo) == 7

    def test_gerar_multiplos_jogos_unicos(self):
        jogos = self.gerador.gerar_multiplos_jogos(quantidade=10)
        tuplas = [tuple(j) for j in jogos]
        assert len(set(tuplas)) == len(tuplas)

    def test_gerar_com_restricoes_soma(self):
        gerador = GeradorSuperSete(
            resultados=RESULTADOS_MOCK,
            janela_recente=10,
            restricoes={'soma_min': 20, 'soma_max': 40},
        )
        jogo = gerador.gerar_jogo_com_restricoes()
        assert 20 <= sum(jogo) <= 40

    def test_gerar_aposta_multipla(self):
        aposta = self.gerador.gerar_aposta_multipla(digitos_por_coluna=2)
        assert len(aposta) == 7
        for col in range(7):
            assert len(aposta[col]) == 2
            for d in aposta[col]:
                assert 0 <= d <= 9

    def test_get_analise_coluna(self):
        analise = self.gerador.get_analise_coluna(0)
        assert analise['coluna'] == 0
        assert 'frequencia_total' in analise
        assert 'quentes' in analise
        assert 'frios' in analise
        assert len(analise['quentes']) == 3

    def test_get_analise_coluna_invalida(self):
        with pytest.raises(ValueError):
            self.gerador.get_analise_coluna(7)

    def test_get_analise_completa(self):
        analise = self.gerador.get_analise_completa()
        assert analise['total_sorteios'] == len(RESULTADOS_MOCK)
        assert len(analise['colunas']) == 7

    def test_lambda_blend_existem(self):
        for col in range(7):
            for d in range(10):
                assert self.gerador.lambda_blend[col][d] >= 0

    def test_gap_existem(self):
        for col in range(7):
            for d in range(10):
                assert self.gerador.gap[col][d] >= 0


class TestBacktestSuperSete:
    def setup_method(self):
        resultados_dicts = [
            {'concurso': i + 1, 'numeros': nums}
            for i, nums in enumerate(RESULTADOS_MOCK)
        ]
        self.backtest = BacktestSuperSete(resultados=resultados_dicts)

    def test_backtest_aleatorio(self):
        resultado = self.backtest.backtest_aleatorio()
        assert resultado['total_jogos'] > 0
        assert 0 <= resultado['media_acertos'] <= 7

    def test_backtest_frequencia(self):
        resultado = self.backtest.backtest_frequencia_historica(janela=5)
        assert resultado['total_jogos'] > 0
        assert 'distribuicao_acertos' in resultado

    def test_backtest_lambda(self):
        resultado = self.backtest.backtest_lambda_blend(janela=10)
        assert resultado['total_jogos'] > 0
        assert 'acertos_por_coluna' in resultado

    def test_comparar_estrategias(self):
        resultado = self.backtest.comparar_estrategias()
        assert 'aleatorio' in resultado
        assert 'frequencia_historica' in resultado
        assert 'lambda_blend' in resultado
        assert 'melhor_estrategia' in resultado

    def test_analisar_padroes(self):
        padroes = self.backtest.analisar_padroes_historicos()
        assert padroes['total_sorteios'] == len(RESULTADOS_MOCK)
        assert 'soma' in padroes
        assert 'paridade' in padroes
        assert 'repeticoes' in padroes
        assert 'frequencia_por_coluna' in padroes

    def test_backtest_vazio(self):
        bt = BacktestSuperSete(resultados=[])
        resultado = bt.backtest_aleatorio()
        assert 'erro' in resultado


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
