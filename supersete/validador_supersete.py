from typing import List, Dict, Tuple, Optional
from collections import Counter

NUM_COLUNAS = 7
DIGITOS = list(range(10))


class ValidadorSuperSete:
    def __init__(self):
        pass

    def validar_jogo_simples(self, jogo: List[int]) -> Tuple[bool, str]:
        if len(jogo) != NUM_COLUNAS:
            return False, f"Jogo deve ter exatamente {NUM_COLUNAS} dígitos (um por coluna)"
        for i, d in enumerate(jogo):
            if not isinstance(d, int) or d < 0 or d > 9:
                return False, f"Dígito na coluna {i + 1} inválido: {d} (deve ser 0-9)"
        return True, "Jogo válido"

    def validar_aposta_multipla(
        self,
        digitos_por_coluna: Dict[int, List[int]],
    ) -> Tuple[bool, str]:
        if len(digitos_por_coluna) != NUM_COLUNAS:
            return False, f"Deve ter exatamente {NUM_COLUNAS} colunas"

        total_digitos = 0
        for col in range(NUM_COLUNAS):
            if col not in digitos_por_coluna:
                return False, f"Coluna {col + 1} ausente"
            digs = digitos_por_coluna[col]
            if not digs:
                return False, f"Coluna {col + 1} vazia"
            if len(digs) != len(set(digs)):
                return False, f"Coluna {col + 1} tem dígitos duplicados"
            for d in digs:
                if not isinstance(d, int) or d < 0 or d > 9:
                    return False, f"Coluna {col + 1}: dígito inválido {d}"
            total_digitos += len(digs)

        if total_digitos < 7:
            return False, f"Total de dígitos ({total_digitos}) menor que o mínimo (7)"
        if total_digitos > 21:
            return False, f"Total de dígitos ({total_digitos}) excede o máximo (21)"

        if 8 <= total_digitos <= 14:
            for col in range(NUM_COLUNAS):
                n = len(digitos_por_coluna[col])
                if n < 1 or n > 2:
                    return False, f"Com {total_digitos} dígitos: cada coluna deve ter 1-2 dígitos (coluna {col + 1} tem {n})"

        if 15 <= total_digitos <= 21:
            for col in range(NUM_COLUNAS):
                n = len(digitos_por_coluna[col])
                if n < 2 or n > 3:
                    return False, f"Com {total_digitos} dígitos: cada coluna deve ter 2-3 dígitos (coluna {col + 1} tem {n})"

        return True, "Aposta múltipla válida"

    def calcular_acertos(self, jogo: List[int], resultado: List[int]) -> Dict:
        acertos_por_coluna = []
        total_acertos = 0
        for i in range(NUM_COLUNAS):
            if i < len(jogo) and i < len(resultado):
                if jogo[i] == resultado[i]:
                    acertos_por_coluna.append(True)
                    total_acertos += 1
                else:
                    acertos_por_coluna.append(False)
            else:
                acertos_por_coluna.append(False)

        return {
            'total_acertos': total_acertos,
            'acertos_por_coluna': acertos_por_coluna,
            'faixa_premio': self._faixa_premio(total_acertos),
        }

    def calcular_acertos_multipla(
        self,
        digitos_por_coluna: Dict[int, List[int]],
        resultado: List[int],
    ) -> Dict:
        acertos_coluna = {}
        total_acertos = 0
        for col in range(NUM_COLUNAS):
            if col < len(resultado):
                dig_sorteado = resultado[col]
                digs_escolhidos = digitos_por_coluna.get(col, [])
                acertou = dig_sorteado in digs_escolhidos
                acertos_coluna[col] = {
                    'digito_sorteado': dig_sorteado,
                    'digitos_escolhidos': digs_escolhidos,
                    'acertou': acertou,
                }
                if acertou:
                    total_acertos += 1

        return {
            'total_acertos': total_acertos,
            'acertos_por_coluna': acertos_coluna,
            'faixa_premio': self._faixa_premio(total_acertos),
        }

    def _faixa_premio(self, acertos: int) -> str:
        faixas = {
            7: "1º Prêmio (7 acertos)",
            6: "2º Prêmio (6 acertos)",
            5: "3º Prêmio (5 acertos)",
            4: "4º Prêmio (4 acertos)",
            3: "5º Prêmio (3 acertos)",
        }
        return faixas.get(acertos, f"Sem prêmio ({acertos} acertos)")

    def validar_restricoes(self, jogo: List[int], restricoes: Dict) -> Tuple[bool, List[str]]:
        violacoes = []

        if 'soma_min' in restricoes:
            if sum(jogo) < restricoes['soma_min']:
                violacoes.append(f"Soma {sum(jogo)} < mínimo {restricoes['soma_min']}")

        if 'soma_max' in restricoes:
            if sum(jogo) > restricoes['soma_max']:
                violacoes.append(f"Soma {sum(jogo)} > máximo {restricoes['soma_max']}")

        if 'max_repeticoes' in restricoes:
            counter = Counter(jogo)
            reps = sum(c - 1 for c in counter.values() if c > 1)
            if reps > restricoes['max_repeticoes']:
                violacoes.append(f"Repetições {reps} > máximo {restricoes['max_repeticoes']}")

        if 'paridade_colunas' in restricoes:
            paridades = restricoes['paridade_colunas']
            for col, paridade in enumerate(paridades):
                if col < len(jogo):
                    d = jogo[col]
                    if paridade == 'par' and d % 2 != 0:
                        violacoes.append(f"Coluna {col + 1}: {d} não é par")
                    elif paridade == 'impar' and d % 2 != 1:
                        violacoes.append(f"Coluna {col + 1}: {d} não é ímpar")

        if 'digitos_excluidos' in restricoes:
            excluidos = restricoes['digitos_excluidos']
            for col, digs in excluidos.items():
                if col < len(jogo) and jogo[col] in digs:
                    violacoes.append(f"Coluna {col + 1}: dígito {jogo[col]} está excluído")

        return len(violacoes) == 0, violacoes
