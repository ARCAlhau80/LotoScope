import random
import math
from typing import List, Dict, Optional, Tuple
from collections import Counter

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False

DIGITOS = list(range(10))
NUM_COLUNAS = 7
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-K6JPBDS;"
    "DATABASE=LOTOFACIL;"
    "Trusted_Connection=yes;"
)


class GeradorSuperSete:
    def __init__(
        self,
        resultados: Optional[List[List[int]]] = None,
        janela_recente: int = 0,
        alpha: float = 0.6,
        restricoes: Optional[Dict] = None,
    ):
        self.janela_recente = janela_recente
        self.alpha = alpha
        self.restricoes = restricoes or {}
        self.freq_total: Dict[int, Dict[int, int]] = {c: {d: 0 for d in DIGITOS} for c in range(NUM_COLUNAS)}
        self.freq_recente: Dict[int, Dict[int, int]] = {c: {d: 0 for d in DIGITOS} for c in range(NUM_COLUNAS)}
        self.lambda_blend: Dict[int, Dict[int, float]] = {c: {d: 0.0 for d in DIGITOS} for c in range(NUM_COLUNAS)}
        self.gap: Dict[int, Dict[int, int]] = {c: {d: 0 for d in DIGITOS} for c in range(NUM_COLUNAS)}
        self.total_sorteios = 0

        if resultados:
            self._processar_resultados(resultados)
        elif HAS_PYODBC:
            self._carregar_do_banco()

    def _processar_resultados(self, resultados: List[List[int]]) -> None:
        self.total_sorteios = len(resultados)
        
        if self.janela_recente == 0:
            self.janela_recente = self.total_sorteios
        
        cutoff = max(0, self.total_sorteios - self.janela_recente)

        for idx, nums in enumerate(resultados):
            is_recent = idx >= cutoff
            for col in range(NUM_COLUNAS):
                if col < len(nums):
                    d = nums[col]
                    if 0 <= d <= 9:
                        self.freq_total[col][d] += 1
                        if is_recent:
                            self.freq_recente[col][d] += 1

        for col in range(NUM_COLUNAS):
            for d in DIGITOS:
                ch = self.freq_total[col][d]
                lh = ch / self.total_sorteios if self.total_sorteios > 0 else 0
                cr = self.freq_recente[col][d]
                lr = cr / self.janela_recente if self.janela_recente > 0 else 0
                self.lambda_blend[col][d] = self.alpha * lh + (1 - self.alpha) * lr

            last_seen: Dict[int, int] = {}
            for idx in range(self.total_sorteios - 1, -1, -1):
                if idx < len(resultados) and col < len(resultados[idx]):
                    d = resultados[idx][col]
                    if d not in last_seen:
                        last_seen[d] = self.total_sorteios - 1 - idx
                if len(last_seen) == 10:
                    break
            for d in DIGITOS:
                self.gap[col][d] = last_seen.get(d, self.total_sorteios)

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
            resultados = [[int(r[i + 1]) for i in range(7)] for r in rows]
            if resultados:
                self._processar_resultados(resultados)
        except Exception:
            pass

    def gerar_jogo_simples(self) -> List[int]:
        jogo = []
        for col in range(NUM_COLUNAS):
            pesos = [max(self.lambda_blend[col][d], 0.001) for d in DIGITOS]
            escolhido = random.choices(DIGITOS, weights=pesos, k=1)[0]
            jogo.append(escolhido)
        return jogo

    def gerar_jogo_com_restricoes(self) -> List[int]:
        soma_min = self.restricoes.get('soma_min', 0)
        soma_max = self.restricoes.get('soma_max', 63)
        max_repeticoes = self.restricoes.get('max_repeticoes', 3)
        paridade_colunas = self.restricoes.get('paridade_colunas', None)
        digitos_excluidos_coluna = self.restricoes.get('digitos_excluidos', {})
        digitos_obrigatorios_coluna = self.restricoes.get('digitos_obrigatorios', {})

        for _ in range(1000):
            jogo = []
            valido = True
            for col in range(NUM_COLUNAS):
                disponiveis = list(DIGITOS)

                if col in digitos_excluidos_coluna:
                    disponiveis = [d for d in disponiveis if d not in digitos_excluidos_coluna[col]]

                if paridade_colunas:
                    if col < len(paridade_colunas):
                        paridade = paridade_colunas[col]
                        if paridade == 'par':
                            disponiveis = [d for d in disponiveis if d % 2 == 0]
                        elif paridade == 'impar':
                            disponiveis = [d for d in disponiveis if d % 2 == 1]

                if col in digitos_obrigatorios_coluna:
                    obrig = digitos_obrigatorios_coluna[col]
                    disponiveis = [d for d in disponiveis if d in obrig]

                if not disponiveis:
                    valido = False
                    break

                pesos = [max(self.lambda_blend[col][d], 0.001) for d in disponiveis]
                escolhido = random.choices(disponiveis, weights=pesos, k=1)[0]
                jogo.append(escolhido)

            if not valido:
                continue

            soma = sum(jogo)
            if not (soma_min <= soma <= soma_max):
                continue

            counter = Counter(jogo)
            reps = sum(c - 1 for c in counter.values() if c > 1)
            if reps > max_repeticoes:
                continue

            return jogo

        return self.gerar_jogo_simples()

    def gerar_multiplos_jogos(self, quantidade: int = 5, com_restricoes: bool = False) -> List[List[int]]:
        jogos = []
        vistos = set()
        tentativas = 0
        max_tentativas = quantidade * 200

        while len(jogos) < quantidade and tentativas < max_tentativas:
            jogo = self.gerar_jogo_com_restricoes() if com_restricoes else self.gerar_jogo_simples()
            chave = tuple(jogo)
            if chave not in vistos:
                vistos.add(chave)
                jogos.append(jogo)
            tentativas += 1

        return jogos

    def gerar_aposta_multipla(self, digitos_por_coluna: int = 2) -> Dict[int, List[int]]:
        resultado: Dict[int, List[int]] = {}
        for col in range(NUM_COLUNAS):
            ranked = sorted(DIGITOS, key=lambda d: self.lambda_blend[col][d], reverse=True)
            resultado[col] = ranked[:digitos_por_coluna]
        return resultado

    def get_analise_coluna(self, col: int) -> Dict:
        if col < 0 or col >= NUM_COLUNAS:
            raise ValueError(f"Coluna deve ser 0-{NUM_COLUNAS - 1}")

        ranked = sorted(DIGITOS, key=lambda d: self.lambda_blend[col][d], reverse=True)
        quentes = ranked[:3]
        frios = sorted(DIGITOS, key=lambda d: (self.freq_recente[col][d], self.freq_total[col][d]))[:3]
        mornos = [d for d in DIGITOS if d not in quentes and d not in frios]

        return {
            'coluna': col,
            'frequencia_total': dict(self.freq_total[col]),
            'frequencia_recente': dict(self.freq_recente[col]),
            'lambda_blend': {d: round(self.lambda_blend[col][d], 4) for d in DIGITOS},
            'gap': dict(self.gap[col]),
            'quentes': quentes,
            'mornos': mornos,
            'frios': frios,
            'top5': ranked[:5],
        }

    def get_analise_completa(self) -> Dict:
        return {
            'total_sorteios': self.total_sorteios,
            'colunas': {col: self.get_analise_coluna(col) for col in range(NUM_COLUNAS)},
        }
