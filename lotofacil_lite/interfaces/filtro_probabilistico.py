# -*- coding: utf-8 -*-
"""
=============================================================================
FILTRO PROBABILÍSTICO - COMBINAÇÕES COM HISTÓRICO DE ACERTOS
=============================================================================
Baseado na análise de Hidden Patterns:
- Combinações com Acertos_11 >= 317 têm 11% mais chance de acertar 11+
- Combinações com Acertos_11 >= 329 têm 18% mais chance de acertar 11+
- Combinações "recentes" (acertaram 11 nos últimos 20 concursos) têm melhor performance

Este módulo carrega um dicionário em memória para lookup rápido (<1ms/100k combinações)
=============================================================================
"""

import sys
import os

# Adicionar paths para imports - compatível com execução de qualquer diretório
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_root_dir = os.path.dirname(_parent_dir)

# Paths possíveis para database_config
sys.path.insert(0, os.path.join(_parent_dir, 'utils'))  # lotofacil_lite/utils
sys.path.insert(0, os.path.join(_root_dir, 'lotofacil_lite', 'utils'))  # caso execute da raiz

try:
    from database_config import DatabaseConfig
except ImportError as e:
    print(f"[DEBUG] Erro ao importar database_config: {e}")
    print(f"[DEBUG] sys.path: {sys.path[:5]}")
    raise


class FiltroProbabilistico:
    """
    Filtro baseado em histórico de acertos das combinações.
    
    Uso:
        filtro = FiltroProbabilistico()
        filtro.carregar(min_acertos_11=317, max_concursos_sem_11=20)
        
        # Verificar se combinação passa no filtro
        if filtro.passa((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)):
            # combinação aprovada
    """
    
    def __init__(self):
        self.lookup = {}
        self.carregado = False
        self.min_acertos_11 = 0
        self.max_concursos_sem_11 = None
        self.min_score_composto = None
        self.ultimo_acertos_14_window = None
        self.ultimo_concurso = 0
        self.total_combinacoes = 0
        self.combinacoes_filtradas = 0
    
    def carregar(self, min_acertos_11=317, max_concursos_sem_11=None,
                 min_score_composto=None, ultimo_acertos_14_window=None,
                 verbose=True):
        """
        Carrega combinações que atendem aos critérios em um dicionário para lookup rápido.

        Args:
            min_acertos_11: Mínimo de acertos de 11 no histórico (default: 317 = mediana).
                            Ignorado quando min_score_composto ou ultimo_acertos_14_window forem definidos.
            max_concursos_sem_11: Máximo de concursos desde último acerto de 11 (None = sem limite).
                                  Aplicado apenas em modos A11 (modos 1-4).
            min_score_composto: Filtro por Score Composto mínimo
                                (A11×1 + A12×2 + A13×10 + A14×100 + A15×1000).
                                Exemplos calibrados: 565 → 16%, 616 → 6%.
            ultimo_acertos_14_window: Janela em concursos para "Candidata de Ouro".
                                      Ex: 100 → inclui combos com Ultimo_Acertos_14 >= (atual-100).
            verbose: Mostrar progresso.
        """
        if verbose:
            print("   ⏳ Carregando filtro probabilístico...")

        db = DatabaseConfig()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Obter último concurso
        cursor.execute("SELECT MAX(UltimoConcursoAtualizado) FROM COMBINACOES_LOTOFACIL")
        self.ultimo_concurso = cursor.fetchone()[0] or 0

        usar_score = min_score_composto is not None
        usar_ouro  = ultimo_acertos_14_window is not None

        # Colunas extras necessárias para score/ouro
        cols_extras = ""
        if usar_score or usar_ouro:
            cols_extras = (", Acertos_12, Acertos_13, Acertos_14, "
                           "ISNULL(Acertos_15, 0) AS Acertos_15, Ultimo_Acertos_14")

        # Construir condição WHERE
        if usar_score:
            score_expr = ("(Acertos_11*1 + Acertos_12*2 + Acertos_13*10 "
                          "+ Acertos_14*100 + ISNULL(Acertos_15,0)*1000)")
            conditions = [f"{score_expr} >= {min_score_composto}"]
        elif usar_ouro:
            conc_limite = self.ultimo_concurso - ultimo_acertos_14_window
            conditions = [
                "Acertos_14 > 0",
                f"Ultimo_Acertos_14 >= {conc_limite}"
            ]
        else:
            conditions = [f"Acertos_11 >= {min_acertos_11}"]
            if max_concursos_sem_11 is not None:
                limite_concurso = self.ultimo_concurso - max_concursos_sem_11
                conditions.append(f"Ultimo_Acertos_11 >= {limite_concurso}")

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT
            CONCAT(N1,'-',N2,'-',N3,'-',N4,'-',N5,'-',N6,'-',N7,'-',N8,
                   '-',N9,'-',N10,'-',N11,'-',N12,'-',N13,'-',N14,'-',N15),
            Acertos_11,
            Ultimo_Acertos_11
            {cols_extras}
        FROM COMBINACOES_LOTOFACIL
        WHERE {where_clause}
        """

        cursor.execute(query)

        # Carregar em memória
        self.lookup = {}
        if usar_score or usar_ouro:
            for row in cursor:
                chave = row[0]
                a11, u11 = row[1], row[2]
                a12, a13, a14, a15, u14 = row[3], row[4], row[5], row[6], row[7]
                score = a11 * 1 + a12 * 2 + a13 * 10 + a14 * 100 + a15 * 1000
                nm_ratio = round(a13 / a12, 3) if a12 > 0 else 0.0
                self.lookup[chave] = {
                    'acertos_11': a11, 'ultimo_11': u11,
                    'acertos_12': a12, 'acertos_13': a13,
                    'acertos_14': a14, 'acertos_15': a15,
                    'ultimo_14': u14,
                    'score': score, 'nm_ratio': nm_ratio,
                }
        else:
            for row in cursor:
                chave = row[0]
                self.lookup[chave] = {
                    'acertos_11': row[1],
                    'ultimo_11': row[2],
                }

        self.min_acertos_11 = min_acertos_11 if not (usar_score or usar_ouro) else 0
        self.max_concursos_sem_11 = max_concursos_sem_11
        self.min_score_composto = min_score_composto
        self.ultimo_acertos_14_window = ultimo_acertos_14_window
        self.combinacoes_filtradas = len(self.lookup)
        
        # Obter total para estatísticas
        cursor.execute("SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL")
        self.total_combinacoes = cursor.fetchone()[0]
        
        self.carregado = True
        
        if verbose:
            pct = self.combinacoes_filtradas / self.total_combinacoes * 100
            print(f"   ✅ Filtro carregado: {self.combinacoes_filtradas:,} combinações ({pct:.1f}%)")
            if usar_score:
                print(f"      Critério: Score Composto >= {min_score_composto}")
            elif usar_ouro:
                print(f"      Critério: Candidata de Ouro — Ultimo_Acertos_14 nos últimos {ultimo_acertos_14_window} concursos")
            else:
                print(f"      Critério: Acertos_11 >= {min_acertos_11}", end="")
                if max_concursos_sem_11:
                    print(f", Recentes <= {max_concursos_sem_11} concursos")
                else:
                    print()
        
        conn.close()
        return self
    
    def _combo_para_chave(self, combo):
        """Converte tupla de combinação para chave de lookup."""
        return '-'.join(str(n) for n in sorted(combo))
    
    def passa(self, combo):
        """
        Verifica se a combinação passa no filtro probabilístico.
        
        Args:
            combo: Tupla ou lista com 15 números
            
        Returns:
            True se a combinação está no lookup (passa no filtro)
        """
        if not self.carregado:
            raise RuntimeError("Filtro não carregado. Chame carregar() primeiro.")
        
        chave = self._combo_para_chave(combo)
        return chave in self.lookup
    
    def get_info(self, combo):
        """
        Retorna informações da combinação se existir no lookup.
        
        Returns:
            dict com 'acertos_11' e 'ultimo_11' ou None se não encontrada
        """
        if not self.carregado:
            raise RuntimeError("Filtro não carregado. Chame carregar() primeiro.")
        
        chave = self._combo_para_chave(combo)
        return self.lookup.get(chave)
    
    def filtrar_lista(self, combinacoes, verbose=True):
        """
        Filtra uma lista de combinações, retornando apenas as que passam.
        
        Args:
            combinacoes: Lista de tuplas/listas com 15 números cada
            verbose: Mostrar progresso
            
        Returns:
            Lista filtrada de combinações
        """
        if not self.carregado:
            raise RuntimeError("Filtro não carregado. Chame carregar() primeiro.")
        
        if verbose:
            print(f"   ⏳ Aplicando filtro probabilístico em {len(combinacoes):,} combinações...")
        
        resultado = []
        for combo in combinacoes:
            if self.passa(combo):
                resultado.append(combo)
        
        if verbose:
            taxa = len(resultado) / len(combinacoes) * 100 if combinacoes else 0
            print(f"   ✅ {len(resultado):,} combinações passaram ({taxa:.1f}%)")
        
        return resultado
    
    def get_estatisticas(self):
        """Retorna estatísticas do filtro."""
        return {
            'carregado': self.carregado,
            'total_combinacoes': self.total_combinacoes,
            'combinacoes_filtradas': self.combinacoes_filtradas,
            'percentual': self.combinacoes_filtradas / self.total_combinacoes * 100 if self.total_combinacoes else 0,
            'min_acertos_11': self.min_acertos_11,
            'min_score_composto': self.min_score_composto,
            'ultimo_acertos_14_window': self.ultimo_acertos_14_window,
            'max_concursos_sem_11': self.max_concursos_sem_11,
            'ultimo_concurso': self.ultimo_concurso
        }


# Instância global para reuso (evita recarregar)
_filtro_global = None

def get_filtro_probabilistico(min_acertos_11=317, max_concursos_sem_11=None,
                              min_score_composto=None, ultimo_acertos_14_window=None,
                              forcar_reload=False):
    """
    Retorna instância do filtro probabilístico (singleton com lazy loading).

    Args:
        min_acertos_11: Mínimo de acertos de 11 no histórico
        max_concursos_sem_11: Máximo de concursos desde último acerto de 11
        min_score_composto: Score Composto mínimo (substitui A11 se definido)
        ultimo_acertos_14_window: Janela para Candidata de Ouro (substitui A11 se definido)
        forcar_reload: Forçar recarga mesmo se já carregado

    Returns:
        Instância de FiltroProbabilistico carregada
    """
    global _filtro_global

    if _filtro_global is None or forcar_reload:
        _filtro_global = FiltroProbabilistico()
        _filtro_global.carregar(
            min_acertos_11=min_acertos_11,
            max_concursos_sem_11=max_concursos_sem_11,
            min_score_composto=min_score_composto,
            ultimo_acertos_14_window=ultimo_acertos_14_window,
        )

    return _filtro_global


# Teste standalone
if __name__ == "__main__":
    print("="*70)
    print("TESTE DO FILTRO PROBABILÍSTICO")
    print("="*70)
    
    # Testar com diferentes configurações
    print("\n📊 Teste 1: Acertos_11 >= 317 (mediana)")
    filtro1 = FiltroProbabilistico()
    filtro1.carregar(min_acertos_11=317)
    print(f"   Estatísticas: {filtro1.get_estatisticas()}")
    
    # Testar lookup da combinação vencedora do 3614
    combo_3614 = (2, 4, 5, 6, 9, 10, 11, 12, 14, 15, 16, 17, 20, 23, 25)
    info = filtro1.get_info(combo_3614)
    print(f"\n   Combinação vencedora 3614: {combo_3614}")
    print(f"   Passa no filtro? {filtro1.passa(combo_3614)}")
    if info:
        print(f"   Info: Acertos_11={info['acertos_11']}, Último_11={info['ultimo_11']}")
    
    print("\n📊 Teste 2: Acertos_11 >= 329 + Recentes <= 20")
    filtro2 = FiltroProbabilistico()
    filtro2.carregar(min_acertos_11=329, max_concursos_sem_11=20)
    print(f"   Estatísticas: {filtro2.get_estatisticas()}")
    print(f"   Combinação 3614 passa? {filtro2.passa(combo_3614)}")
    
    print("\n✅ Testes concluídos!")
