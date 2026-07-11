from typing import List, Dict, Optional, Tuple
from collections import Counter
import math

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

NUM_COLUNAS = 7
DIGITOS = list(range(10))
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)


class BacktestSuperSete:
    def __init__(self, resultados: Optional[List[Dict]] = None, carregar_banco: bool = True):
        self.resultados: List[Dict] = []
        if resultados is not None:
            self.resultados = resultados
        elif carregar_banco and HAS_PYODBC:
            self._carregar_do_banco()

    def _carregar_do_banco(self) -> None:
        try:
            conn = pyodbc.connect(CONN_STR)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Concurso, N1, N2, N3, N4, N5, N6, N7 "
                "FROM Resultados_SuperSete ORDER BY Concurso"
            )
            rows = cursor.fetchall()
            conn.close()
            self.resultados = [
                {
                    'concurso': int(r[0]),
                    'numeros': [int(r[i + 1]) for i in range(7)],
                }
                for r in rows
            ]
        except Exception:
            pass

    def backtest_estrategia(
        self,
        gerador_fn,
        jogos_por_concurso: int = 1,
        ultimos_n: Optional[int] = None,
    ) -> Dict:
        if not self.resultados:
            return {'erro': 'Nenhum resultado disponível'}

        resultados_teste = self.resultados
        if ultimos_n:
            resultados_teste = self.resultados[-ultimos_n:]

        total_acertos_dist: Dict[int, int] = {i: 0 for i in range(8)}
        total_jogos = 0
        acertos_por_coluna: Dict[int, int] = {i: 0 for i in range(NUM_COLUNAS)}
        soma_acertos = 0
        premios: Dict[str, int] = {}

        for idx, resultado in enumerate(resultados_teste):
            historico = [r['numeros'] for r in self.resultados[:self.resultados.index(resultado)]]
            if not historico:
                continue

            jogos = gerador_fn(historico, jogos_por_concurso)

            for jogo in jogos:
                acertos = 0
                for col in range(NUM_COLUNAS):
                    if col < len(jogo) and col < len(resultado['numeros']):
                        if jogo[col] == resultado['numeros'][col]:
                            acertos += 1
                            acertos_por_coluna[col] += 1

                total_acertos_dist[acertos] += 1
                soma_acertos += acertos
                total_jogos += 1

                faixa = self._faixa_premio(acertos)
                if 'Prêmio' in faixa:
                    premios[faixa] = premios.get(faixa, 0) + 1

        media_acertos = soma_acertos / total_jogos if total_jogos > 0 else 0

        return {
            'total_jogos': total_jogos,
            'total_concursos_testados': len(resultados_teste),
            'jogos_por_concurso': jogos_por_concurso,
            'media_acertos': round(media_acertos, 4),
            'distribuicao_acertos': total_acertos_dist,
            'acertos_por_coluna': acertos_por_coluna,
            'premios': premios,
            'taxa_acerto_3plus': round(
                sum(total_acertos_dist[i] for i in range(3, 8)) / total_jogos * 100, 2
            ) if total_jogos > 0 else 0,
            'taxa_acerto_4plus': round(
                sum(total_acertos_dist[i] for i in range(4, 8)) / total_jogos * 100, 2
            ) if total_jogos > 0 else 0,
        }

    def backtest_frequencia_historica(self, janela: int = 30) -> Dict:
        def gerador_freq(historico: List[List[int]], qtd: int) -> List[List[int]]:
            jogos = []
            for _ in range(qtd):
                jogo = []
                for col in range(NUM_COLUNAS):
                    freq: Dict[int, int] = {d: 0 for d in DIGITOS}
                    inicio = max(0, len(historico) - janela)
                    for h in historico[inicio:]:
                        if col < len(h):
                            d = h[col]
                            if 0 <= d <= 9:
                                freq[d] += 1
                    top = sorted(DIGITOS, key=lambda d: freq[d], reverse=True)
                    jogo.append(top[0])
                jogos.append(jogo)
            return jogos

        return self.backtest_estrategia(gerador_freq, jogos_por_concurso=1)

    def backtest_aleatorio(self) -> Dict:
        import random

        def gerador_aleatorio(historico: List[List[int]], qtd: int) -> List[List[int]]:
            jogos = []
            for _ in range(qtd):
                jogo = [random.choice(DIGITOS) for _ in range(NUM_COLUNAS)]
                jogos.append(jogo)
            return jogos

        return self.backtest_estrategia(gerador_aleatorio, jogos_por_concurso=1)

    def backtest_lambda_blend(self, janela: int = 50, alpha: float = 0.6) -> Dict:
        import random

        def gerador_lambda(historico: List[List[int]], qtd: int) -> List[List[int]]:
            jogos = []
            total = len(historico)
            cutoff = max(0, total - janela)

            lambdas: Dict[int, Dict[int, float]] = {}
            for col in range(NUM_COLUNAS):
                lambdas[col] = {}
                for d in DIGITOS:
                    ch = sum(1 for h in historico if col < len(h) and h[col] == d)
                    lh = ch / total if total > 0 else 0
                    cr = sum(1 for h in historico[cutoff:] if col < len(h) and h[col] == d)
                    lr = cr / janela if total >= janela else 0
                    lambdas[col][d] = alpha * lh + (1 - alpha) * lr

            for _ in range(qtd):
                jogo = []
                for col in range(NUM_COLUNAS):
                    pesos = [max(lambdas[col][d], 0.001) for d in DIGITOS]
                    escolhido = random.choices(DIGITOS, weights=pesos, k=1)[0]
                    jogo.append(escolhido)
                jogos.append(jogo)
            return jogos

        return self.backtest_estrategia(gerador_lambda, jogos_por_concurso=3)

    def comparar_estrategias(self) -> Dict:
        resultado_aleatorio = self.backtest_aleatorio()
        resultado_freq = self.backtest_frequencia_historica()
        resultado_lambda = self.backtest_lambda_blend()

        return {
            'aleatorio': resultado_aleatorio,
            'frequencia_historica': resultado_freq,
            'lambda_blend': resultado_lambda,
            'melhor_estrategia': self._melhor(resultado_aleatorio, resultado_freq, resultado_lambda),
        }

    def _melhor(self, aleatorio: Dict, freq: Dict, lam: Dict) -> str:
        estrategias = {
            'aleatorio': aleatorio.get('media_acertos', 0),
            'frequencia_historica': freq.get('media_acertos', 0),
            'lambda_blend': lam.get('media_acertos', 0),
        }
        return max(estrategias, key=estrategias.get)

    def _faixa_premio(self, acertos: int) -> str:
        faixas = {
            7: "1º Prêmio (7 acertos)",
            6: "2º Prêmio (6 acertos)",
            5: "3º Prêmio (5 acertos)",
            4: "4º Prêmio (4 acertos)",
            3: "5º Prêmio (3 acertos)",
        }
        return faixas.get(acertos, f"Sem prêmio ({acertos} acertos)")

    def analisar_padroes_historicos(self) -> Dict:
        if not self.resultados:
            return {'erro': 'Nenhum resultado disponível'}

        somas = []
        paridades = []
        repeticoes = []
        digitos_freq: Dict[int, int] = {d: 0 for d in DIGITOS}
        coluna_freq: Dict[int, Dict[int, int]] = {c: {d: 0 for d in DIGITOS} for c in range(NUM_COLUNAS)}

        for r in self.resultados:
            nums = r['numeros']
            somas.append(sum(nums))
            paridades.append(sum(1 for n in nums if n % 2 == 0))
            counter = Counter(nums)
            reps = sum(c - 1 for c in counter.values() if c > 1)
            repeticoes.append(reps)
            for d in nums:
                digitos_freq[d] += 1
            for col, d in enumerate(nums):
                if col < NUM_COLUNAS:
                    coluna_freq[col][d] += 1

        n = len(self.resultados)
        media_soma = sum(somas) / n
        desvio_soma = math.sqrt(sum((s - media_soma) ** 2 for s in somas) / n)

        return {
            'total_sorteios': n,
            'soma': {
                'media': round(media_soma, 2),
                'desvio': round(desvio_soma, 2),
                'min': min(somas),
                'max': max(somas),
            },
            'paridade': {
                'media_pares': round(sum(paridades) / n, 2),
                'media_impares': round(n - sum(paridades) / n, 2),
            },
            'repeticoes': {
                'media': round(sum(repeticoes) / n, 2),
                'pct_com_repeticao': round(sum(1 for r in repeticoes if r > 0) / n * 100, 2),
            },
            'digitos_mais_frequentes': sorted(DIGITOS, key=lambda d: digitos_freq[d], reverse=True)[:5],
            'digitos_menos_frequentes': sorted(DIGITOS, key=lambda d: digitos_freq[d])[:5],
            'frequencia_por_coluna': {
                col: sorted(DIGITOS, key=lambda d: coluna_freq[col][d], reverse=True)[:3]
                for col in range(NUM_COLUNAS)
            },
        }
