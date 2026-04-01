# -*- coding: utf-8 -*-
"""
=============================================================================
FILTRO DE SUB-COMBOS QUENTES (COMBIN_10)
=============================================================================
Baseado na análise da tabela COMBIN_10 (C(25,10) = 3.268.760 combinações de 10):
- Cada combo-15 contém C(15,10) = 3003 sub-combinações de 10 números
- Combos com mais sub-combos "quentes" (QTDE_ACERTOS alto) têm maior probabilidade
- Lift de 2.45x para combos com QTDE_ACERTOS >= 8

Uso:
    filtro = FiltroSubcombosQuentes()
    filtro.carregar(min_acertos=8)
    combos_filtradas = filtro.filtrar_lista(combinacoes, min_hot=50)

Performance:
    - Carga: ~2s (46k-181k combos de 10 como frozensets)
    - Filtragem: ~0.3s por combo-15 (3003 lookups em set)
    - Recomendação: aplicar APÓS outros filtros para reduzir volume
=============================================================================
"""

import sys
import os
import time
from itertools import combinations

_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
sys.path.insert(0, os.path.join(_parent_dir, 'utils'))

try:
    from database_config import DatabaseConfig
except ImportError as e:
    print(f"[DEBUG] Erro ao importar database_config: {e}")
    raise


class FiltroSubcombosQuentes:
    """
    Filtro que avalia combinações de 15 números pela quantidade de
    sub-combinações de 10 que são "quentes" (QTDE_ACERTOS alto na COMBIN_10).
    """

    def __init__(self):
        self.hot_set = set()          # set de frozensets com 10 números
        self.carregado = False
        self.min_acertos = 0
        self.total_combin10 = 0
        self.hot_count = 0
        self.concurso_atualizado = 0

    def carregar(self, min_acertos=8, verbose=True):
        """
        Carrega sub-combinações quentes da COMBIN_10 para memória.

        Args:
            min_acertos: Mínimo de QTDE_ACERTOS para considerar "quente"
            verbose: Mostrar progresso
        """
        if verbose:
            print("   ⏳ Carregando filtro de sub-combos quentes (COMBIN_10)...")

        t0 = time.time()
        db = DatabaseConfig()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Verificar concurso atualizado
        cursor.execute("SELECT ISNULL(MAX(CONCURSO), 0) FROM COMBIN_10")
        self.concurso_atualizado = cursor.fetchone()[0]

        # Carregar combos quentes
        cursor.execute(
            "SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10 "
            "FROM COMBIN_10 WHERE QTDE_ACERTOS >= ?",
            (min_acertos,)
        )

        self.hot_set = set()
        for row in cursor:
            self.hot_set.add(frozenset(row))

        self.hot_count = len(self.hot_set)
        self.min_acertos = min_acertos

        # Total para estatísticas
        cursor.execute("SELECT COUNT(*) FROM COMBIN_10")
        self.total_combin10 = cursor.fetchone()[0]

        conn.close()
        self.carregado = True

        elapsed = time.time() - t0
        if verbose:
            pct = self.hot_count / self.total_combin10 * 100 if self.total_combin10 > 0 else 0
            print(f"   ✅ Filtro carregado: {self.hot_count:,} sub-combos quentes "
                  f"({pct:.1f}%) em {elapsed:.1f}s")
            print(f"      Critério: QTDE_ACERTOS >= {min_acertos} | "
                  f"Concurso: {self.concurso_atualizado}")

        return self

    def contar_hot(self, combo):
        """
        Conta quantas sub-combinações de 10 de um combo-15 são "quentes".

        Args:
            combo: Tupla/lista com 15 números

        Returns:
            int: Quantidade de sub-combos quentes (0 a 3003)
        """
        if not self.carregado:
            raise RuntimeError("Filtro não carregado. Chame carregar() primeiro.")

        count = 0
        combo_sorted = sorted(combo)
        for sub in combinations(combo_sorted, 10):
            if frozenset(sub) in self.hot_set:
                count += 1
        return count

    def passa(self, combo, min_hot=50):
        """
        Verifica se combo-15 tem sub-combos quentes suficientes.

        Args:
            combo: Tupla/lista com 15 números
            min_hot: Mínimo de sub-combos quentes para passar

        Returns:
            bool
        """
        return self.contar_hot(combo) >= min_hot

    def filtrar_lista(self, combinacoes, min_hot=50, verbose=True):
        """
        Filtra lista de combinações, retornando apenas as com sub-combos quentes suficientes.

        Args:
            combinacoes: Lista de tuplas/listas com 15 números cada
            min_hot: Mínimo de sub-combos quentes para passar
            verbose: Mostrar progresso

        Returns:
            Lista filtrada de combinações
        """
        if not self.carregado:
            raise RuntimeError("Filtro não carregado. Chame carregar() primeiro.")

        if not combinacoes:
            return combinacoes

        t0 = time.time()
        total = len(combinacoes)
        resultado = []

        for i, combo in enumerate(combinacoes):
            hot = self.contar_hot(combo)
            if hot >= min_hot:
                resultado.append(combo)

            if verbose and (i + 1) % 5000 == 0:
                elapsed = time.time() - t0
                pct = (i + 1) / total * 100
                print(f"      Sub-combos: {i+1:,}/{total:,} ({pct:.0f}%) "
                      f"| Aprovadas: {len(resultado):,} | {elapsed:.1f}s", end='\r')

        elapsed = time.time() - t0
        if verbose:
            print(f"\n   ✅ Filtro sub-combos: {len(resultado):,}/{total:,} aprovadas "
                  f"({len(resultado)/total*100:.1f}%) em {elapsed:.1f}s")

        return resultado

    def diagnostico(self, combo, top_n=10):
        """
        Retorna diagnóstico detalhado de um combo-15.

        Args:
            combo: Tupla/lista com 15 números
            top_n: Quantos sub-combos mostrar no ranking

        Returns:
            dict com contagem total e sub-combos mais/menos quentes
        """
        if not self.carregado:
            raise RuntimeError("Filtro não carregado. Chame carregar() primeiro.")

        combo_sorted = sorted(combo)
        hot_count = 0
        total_subs = 0

        for sub in combinations(combo_sorted, 10):
            total_subs += 1
            if frozenset(sub) in self.hot_set:
                hot_count += 1

        return {
            'combo': combo_sorted,
            'total_subcombos': total_subs,
            'hot_count': hot_count,
            'hot_pct': hot_count / total_subs * 100 if total_subs > 0 else 0,
            'cold_count': total_subs - hot_count,
        }
