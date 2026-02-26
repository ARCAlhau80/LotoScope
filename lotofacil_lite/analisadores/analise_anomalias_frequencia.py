"""
🔍 ANÁLISE DE ANOMALIAS DE FREQUÊNCIA - LOTOFÁCIL v2.0
======================================================

Adaptado do sistema MLMEGA para a Lotofácil.

⚠️ VALIDAÇÃO HISTÓRICA (23/02/2026):
- Análise de 3,617 concursos mostrou que frequência em janela NÃO é eficaz
- Números "quentes" (9+ em 10) NÃO esfriam (~60% vs esperado 60%)
- Números com 4-5 AUSÊNCIAS CONSECUTIVAS têm +3-4% chance de voltar ✅

NOVA ESTRATÉGIA v2.0:
- EVITAR: Apenas números com muitas consecutivas (8+) - tendência -5%
- FAVORECER: Números com 4-5 ausências consecutivas - tendência +3-4% ✅

Probabilidade teórica (cada número na Lotofácil):
- P(sair em 1 sorteio) = 15/25 = 60%

Autor: AR CALHAU / GitHub Copilot
Data: Fevereiro 2026 (Atualizado com validação histórica)
"""

import os
import sys
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Set
import math

# Configurar path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_dir)


class AnalisadorAnomalias:
    """
    Analisa anomalias de frequência em janelas deslizantes para Lotofácil.
    
    Uma "anomalia" é definida como:
    - ALTA: Número aparecendo 9+ vezes em janela de 10 (esperado: ~6)
    - BAIXA: Número aparecendo 3- vezes em janela de 10
    - CONSECUTIVAS: Número aparecendo 4+ vezes seguidas
    """
    
    # Constantes para Lotofácil
    TOTAL_NUMEROS = 25
    NUMEROS_POR_SORTEIO = 15
    PROB_APARECER = 15 / 25  # 60%
    
    def __init__(self, resultados: List[Dict] = None):
        """
        Inicializa o analisador.
        
        Args:
            resultados: Lista de dicts com {'concurso': int, 'numeros': list}
                       Ordenada do mais recente para o mais antigo
        """
        self.resultados = resultados or []
        
    def set_resultados(self, resultados: List[Dict]):
        """Define os resultados para análise."""
        self.resultados = resultados
    
    def calcular_probabilidade_binomial(self, n: int, k: int, p: float) -> float:
        """
        Calcula P(X = k) para distribuição binomial.
        n = número de tentativas (10 sorteios)
        k = número de sucessos (aparições do número)
        p = probabilidade de sucesso (60% para Lotofácil)
        """
        coef = math.comb(n, k)
        return coef * (p ** k) * ((1 - p) ** (n - k))
    
    def calcular_probabilidade_acumulada(self, n: int, k_min: int, p: float) -> float:
        """
        Calcula P(X >= k_min) - probabilidade de ter k_min ou mais sucessos.
        """
        total = 0
        for k in range(k_min, n + 1):
            total += self.calcular_probabilidade_binomial(n, k, p)
        return total
    
    def analisar_janela_atual(self, tamanho_janela: int = 10) -> Dict:
        """
        Analisa a janela mais recente e identifica anomalias.
        
        Args:
            tamanho_janela: Tamanho da janela deslizante (default: 10)
        
        Returns:
            Dict com:
            - anomalos_altos: números com 9+ aparições (muito quentes)
            - anomalos_baixos: números com 3- aparições (muito frios)
            - consecutivas: números com 4+ aparições seguidas
            - frequencias: frequência de cada número na janela
            - estatisticas: análise estatística geral
        """
        if len(self.resultados) < tamanho_janela:
            return {'erro': f'Poucos resultados para janela de {tamanho_janela}'}
        
        # Pegar últimos N sorteios
        janela = self.resultados[:tamanho_janela]
        
        # Contar frequência de cada número
        freq = Counter()
        for resultado in janela:
            for n in resultado['numeros']:
                freq[n] += 1
        
        # Preencher zeros para números que não apareceram
        for n in range(1, 26):
            if n not in freq:
                freq[n] = 0
        
        # Identificar anomalias
        anomalos_altos = []  # 9+ (muito quentes - tendem a esfriar)
        anomalos_baixos = []  # 3- (muito frios - tendem a voltar)
        
        # Thresholds baseados em análise estatística
        # P(X >= 9) ≈ 1.8% (raro estar TÃO quente)
        # P(X <= 3) ≈ 4.6% (raro estar TÃO frio)
        threshold_alto = 9
        threshold_baixo = 3
        
        for n in range(1, 26):
            f = freq[n]
            if f >= threshold_alto:
                prob = self.calcular_probabilidade_acumulada(tamanho_janela, f, self.PROB_APARECER)
                anomalos_altos.append({
                    'numero': n,
                    'frequencia': f,
                    'probabilidade': prob,
                    'status': 'MUITO QUENTE'
                })
            elif f <= threshold_baixo:
                prob = sum(self.calcular_probabilidade_binomial(tamanho_janela, k, self.PROB_APARECER) 
                          for k in range(0, f + 1))
                anomalos_baixos.append({
                    'numero': n,
                    'frequencia': f,
                    'probabilidade': prob,
                    'status': 'MUITO FRIO'
                })
        
        # Calcular consecutivas
        consecutivas = self._calcular_consecutivas_recente(tamanho_janela)
        
        # Estatísticas gerais
        valores_freq = list(freq.values())
        media = sum(valores_freq) / len(valores_freq)
        variancia = sum((f - media) ** 2 for f in valores_freq) / len(valores_freq)
        
        return {
            'janela': tamanho_janela,
            'concurso_inicio': janela[-1]['concurso'],
            'concurso_fim': janela[0]['concurso'],
            'anomalos_altos': sorted(anomalos_altos, key=lambda x: -x['frequencia']),
            'anomalos_baixos': sorted(anomalos_baixos, key=lambda x: x['frequencia']),
            'consecutivas': consecutivas,
            'frequencias': dict(freq),
            'estatisticas': {
                'media': media,
                'variancia': variancia,
                'desvio_padrao': variancia ** 0.5,
                'esperado': tamanho_janela * self.PROB_APARECER,
                'total_anomalos_altos': len(anomalos_altos),
                'total_anomalos_baixos': len(anomalos_baixos)
            }
        }
    
    def _calcular_consecutivas_recente(self, tamanho_janela: int) -> List[Dict]:
        """
        Encontra números que apareceram 4+ vezes consecutivas (recentemente).
        """
        janela = self.resultados[:tamanho_janela]
        resultados_consec = []
        
        for numero in range(1, 26):
            max_consec = 0
            atual_consec = 0
            inicio_seq = None
            
            # Percorrer do mais antigo para o mais recente (invertido)
            for i in range(len(janela) - 1, -1, -1):
                resultado = janela[i]
                if numero in resultado['numeros']:
                    if atual_consec == 0:
                        inicio_seq = resultado['concurso']
                    atual_consec += 1
                    max_consec = max(max_consec, atual_consec)
                else:
                    atual_consec = 0
            
            if max_consec >= 4:
                resultados_consec.append({
                    'numero': numero,
                    'consecutivas': max_consec,
                    'status': 'QUENTE CONSECUTIVO'
                })
        
        return sorted(resultados_consec, key=lambda x: -x['consecutivas'])
    
    def obter_numeros_a_evitar(self, tamanho_janela: int = 10) -> Set[int]:
        """
        Retorna conjunto de números que devem ser EVITADOS.
        
        v2.0 - Validação histórica mostrou:
        - Anômalos altos (9+ em 10) NÃO esfriam! Removido.
        - Apenas consecutivas 8+ mostram leve tendência de parar (-5%)
        """
        if len(self.resultados) < tamanho_janela:
            return set()
        
        evitar = set()
        
        # v2.0: Apenas consecutivas muito altas (8+)
        # Validação mostrou -5% ao parar após 8+ consecutivas
        consecutivas = self._calcular_consecutivas_atuais()
        for numero, qtd in consecutivas.items():
            if qtd >= 8:
                evitar.add(numero)
        
        return evitar
    
    def _calcular_consecutivas_atuais(self) -> Dict[int, int]:
        """
        Conta quantas vezes CADA número saiu consecutivamente (do mais recente).
        """
        consecutivas = {}
        for numero in range(1, 26):
            count = 0
            for resultado in self.resultados:
                if numero in resultado['numeros']:
                    count += 1
                else:
                    break  # Parou a sequência
            consecutivas[numero] = count
        return consecutivas
    
    def _calcular_ausencias_atuais(self) -> Dict[int, int]:
        """
        Conta há quantos sorteios CADA número está ausente (desde o mais recente).
        """
        ausencias = {}
        for numero in range(1, 26):
            count = 0
            for resultado in self.resultados:
                if numero not in resultado['numeros']:
                    count += 1
                else:
                    break  # Saiu, fim da ausência
            ausencias[numero] = count
        return ausencias
    
    def obter_numeros_favorecidos(self, tamanho_janela: int = 10) -> Set[int]:
        """
        Retorna conjunto de números que devem ser FAVORECIDOS.
        
        v2.0 - Validação histórica mostrou:
        - Números com 4-5 ausências consecutivas têm +3-4% mais chance de voltar! ✅
        - Frequência baixa em janela (3- em 10) NÃO é significativa
        """
        if len(self.resultados) < 5:
            return set()
        
        favorecer = set()
        
        # v2.0: Usar AUSÊNCIAS CONSECUTIVAS (validado historicamente)
        # 4 ausências: +3.6% de voltar
        # 5 ausências: +3.1% de voltar
        ausencias = self._calcular_ausencias_atuais()
        for numero, qtd in ausencias.items():
            if 4 <= qtd <= 5:
                favorecer.add(numero)
        
        return favorecer
    
    def calcular_score_combinacao(self, combinacao: List[int], 
                                   tamanho_janela: int = 10,
                                   peso_evitar: float = -2.0,
                                   peso_favorecer: float = 1.0) -> float:
        """
        Calcula score de uma combinação baseado em anomalias.
        
        Args:
            combinacao: Lista de 15 números
            tamanho_janela: Tamanho da janela de análise
            peso_evitar: Penalidade por número a evitar
            peso_favorecer: Bônus por número favorecido
        
        Returns:
            Score da combinação (maior = melhor)
        """
        evitar = self.obter_numeros_a_evitar(tamanho_janela)
        favorecer = self.obter_numeros_favorecidos(tamanho_janela)
        
        score = 0
        comb_set = set(combinacao)
        
        # Penalizar números a evitar
        nums_evitar_presentes = comb_set & evitar
        score += len(nums_evitar_presentes) * peso_evitar
        
        # Bonificar números favorecidos
        nums_favor_presentes = comb_set & favorecer
        score += len(nums_favor_presentes) * peso_favorecer
        
        return score
    
    def filtrar_combinacoes_anomalias(self, 
                                       combinacoes: List[List[int]],
                                       tamanho_janela: int = 10,
                                       max_evitar: int = 2,
                                       min_favor: int = 1) -> List[List[int]]:
        """
        Filtra combinações baseado em análise de anomalias.
        
        Args:
            combinacoes: Lista de combinações para filtrar
            tamanho_janela: Tamanho da janela de análise
            max_evitar: Máximo de números "a evitar" permitidos
            min_favor: Mínimo de números "favorecidos" necessários
        
        Returns:
            Lista de combinações que passam no filtro
        """
        evitar = self.obter_numeros_a_evitar(tamanho_janela)
        favorecer = self.obter_numeros_favorecidos(tamanho_janela)
        
        # Se não há dados suficientes, retornar todas
        if not evitar and not favorecer:
            return combinacoes
        
        filtradas = []
        for comb in combinacoes:
            comb_set = set(comb)
            
            # Contar números a evitar
            count_evitar = len(comb_set & evitar)
            
            # Contar números favorecidos
            count_favor = len(comb_set & favorecer) if favorecer else min_favor
            
            # Aplicar filtros
            if count_evitar <= max_evitar and count_favor >= min_favor:
                filtradas.append(comb)
        
        return filtradas
    
    def analisar_historico_anomalias(self, tamanho_janela: int = 10, 
                                      freq_minima: int = 9) -> Dict:
        """
        Analisa todo o histórico para estatísticas de anomalias.
        
        Similar ao método analisar_janelas do MLMEGA.
        """
        if len(self.resultados) < tamanho_janela:
            return {'erro': f'Poucos resultados para janela de {tamanho_janela}'}
        
        anomalias = []
        numeros_anomalos = Counter()
        total_janelas = len(self.resultados) - tamanho_janela + 1
        
        for i in range(total_janelas):
            janela = self.resultados[i:i + tamanho_janela]
            concurso_inicio = janela[-1]['concurso']
            concurso_fim = janela[0]['concurso']
            
            # Contar frequência
            freq = Counter()
            for r in janela:
                for n in r['numeros']:
                    freq[n] += 1
            
            # Verificar anomalias na janela
            for numero, contagem in freq.items():
                if contagem >= freq_minima:
                    anomalias.append({
                        'concurso_inicio': concurso_inicio,
                        'concurso_fim': concurso_fim,
                        'numero': numero,
                        'frequencia': contagem
                    })
                    numeros_anomalos[numero] += 1
        
        return {
            'total_janelas': total_janelas,
            'tamanho_janela': tamanho_janela,
            'freq_minima': freq_minima,
            'total_anomalias': len(anomalias),
            'numeros_mais_anomalos': numeros_anomalos.most_common(10),
            'anomalias_recentes': anomalias[:50]  # Últimas 50
        }
    
    def gerar_relatorio(self) -> str:
        """Gera relatório da análise atual."""
        analise = self.analisar_janela_atual(10)
        
        if 'erro' in analise:
            return f"❌ {analise['erro']}"
        
        linhas = []
        linhas.append("\n" + "🔬" * 40)
        linhas.append("📊 RELATÓRIO DE ANOMALIAS - LOTOFÁCIL")
        linhas.append("🔬" * 40)
        linhas.append(f"\n📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        linhas.append(f"📊 Janela: Concursos {analise['concurso_inicio']} a {analise['concurso_fim']}")
        linhas.append(f"🎯 Tamanho: {analise['janela']} sorteios")
        
        # Estatísticas
        stats = analise['estatisticas']
        linhas.append("\n" + "=" * 60)
        linhas.append("📐 ESTATÍSTICAS DA JANELA")
        linhas.append("=" * 60)
        linhas.append(f"   Frequência esperada: {stats['esperado']:.1f}")
        linhas.append(f"   Frequência média: {stats['media']:.1f}")
        linhas.append(f"   Desvio padrão: {stats['desvio_padrao']:.2f}")
        
        # Anômalos Altos (evitar)
        linhas.append("\n" + "=" * 60)
        linhas.append("🔥 NÚMEROS MUITO QUENTES (EVITAR)")
        linhas.append("=" * 60)
        if analise['anomalos_altos']:
            for a in analise['anomalos_altos']:
                linhas.append(f"   Número {a['numero']:02d}: {a['frequencia']}x (P={a['probabilidade']*100:.2f}%)")
        else:
            linhas.append("   Nenhum número anômalo alto")
        
        # Anômalos Baixos (favorecer)
        linhas.append("\n" + "=" * 60)
        linhas.append("❄️ NÚMEROS MUITO FRIOS (FAVORECER)")
        linhas.append("=" * 60)
        if analise['anomalos_baixos']:
            for a in analise['anomalos_baixos']:
                linhas.append(f"   Número {a['numero']:02d}: {a['frequencia']}x (P={a['probabilidade']*100:.2f}%)")
        else:
            linhas.append("   Nenhum número anômalo baixo")
        
        # Consecutivas
        linhas.append("\n" + "=" * 60)
        linhas.append("🔄 SEQUÊNCIAS CONSECUTIVAS")
        linhas.append("=" * 60)
        if analise['consecutivas']:
            for c in analise['consecutivas']:
                linhas.append(f"   Número {c['numero']:02d}: {c['consecutivas']}x consecutivas")
        else:
            linhas.append("   Nenhuma sequência de 4+ consecutivas")
        
        # Recomendações
        evitar = self.obter_numeros_a_evitar()
        favorecer = self.obter_numeros_favorecidos()
        
        linhas.append("\n" + "=" * 60)
        linhas.append("🎯 RECOMENDAÇÕES PARA PRÓXIMO CONCURSO")
        linhas.append("=" * 60)
        if evitar:
            linhas.append(f"   ⚠️ EVITAR: {sorted(evitar)}")
        if favorecer:
            linhas.append(f"   ⭐ FAVORECER: {sorted(favorecer)}")
        
        return "\n".join(linhas)


def verificar_combinacao_anomalias(combinacao: List[int], resultados: List[Dict]) -> Dict:
    """
    Função de conveniência para verificar uma combinação específica.
    
    Args:
        combinacao: Lista de 15 números
        resultados: Histórico de resultados
    
    Returns:
        Dict com análise da combinação
    """
    analisador = AnalisadorAnomalias(resultados)
    analise = analisador.analisar_janela_atual()
    
    if 'erro' in analise:
        return analise
    
    comb_set = set(combinacao)
    evitar = analisador.obter_numeros_a_evitar()
    favorecer = analisador.obter_numeros_favorecidos()
    
    nums_evitar = comb_set & evitar
    nums_favor = comb_set & favorecer
    score = analisador.calcular_score_combinacao(combinacao)
    
    return {
        'combinacao': combinacao,
        'score_anomalias': score,
        'numeros_quentes': list(nums_evitar),
        'numeros_frios': list(nums_favor),
        'qtd_evitar': len(nums_evitar),
        'qtd_favorecer': len(nums_favor),
        'recomendacao': 'BOA' if score >= 0 else 'RISCOS'
    }


# Teste local
if __name__ == "__main__":
    import pyodbc
    
    print("🔬 TESTE DO ANALISADOR DE ANOMALIAS - LOTOFÁCIL")
    print("=" * 60)
    
    # Conectar e carregar dados
    try:
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
        """)
        
        resultados = []
        for row in cursor.fetchall():
            resultados.append({
                'concurso': row[0],
                'numeros': list(row[1:16])
            })
        
        conn.close()
        print(f"✅ {len(resultados)} concursos carregados")
        
        # Executar análise
        analisador = AnalisadorAnomalias(resultados)
        relatorio = analisador.gerar_relatorio()
        print(relatorio)
        
        # Mostrar números a evitar/favorecer
        evitar = analisador.obter_numeros_a_evitar()
        favorecer = analisador.obter_numeros_favorecidos()
        
        print("\n" + "=" * 60)
        print("📋 RESUMO PARA GERADOR POOL 23")
        print("=" * 60)
        print(f"   🚫 Números a EVITAR (máx 2 por combinação): {sorted(evitar)}")
        print(f"   ⭐ Números a FAVORECER (mín 1 por combinação): {sorted(favorecer)}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
