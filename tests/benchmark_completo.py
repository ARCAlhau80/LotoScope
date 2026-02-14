#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏆 BENCHMARK COMPLETO DE GERADORES - LOTOSCOPE
Testa os geradores principais contra últimos N concursos
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import statistics

# Configurar paths
ROOT_DIR = Path(__file__).parent.parent
LOTOFACIL_DIR = ROOT_DIR / 'lotofacil_lite'
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR / 'utils'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'geradores'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'ia'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'sistemas'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'analisadores'))

# Suprimir warnings
import warnings
warnings.filterwarnings('ignore')

from database_config import db_config


class BenchmarkCompleto:
    """Benchmark completo dos geradores principais"""
    
    def __init__(self, ultimos_n_concursos: int = 10):
        self.ultimos_n = ultimos_n_concursos
        self.resultados_historicos = []
        self.resultados_benchmark = []
        
        self._carregar_resultados_historicos()
    
    def _carregar_resultados_historicos(self):
        """Carrega últimos N resultados do banco"""
        print(f"\n📊 Carregando últimos {self.ultimos_n} concursos...")
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT TOP {self.ultimos_n} Concurso, 
                       N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT
                ORDER BY Concurso DESC
            """)
            
            for row in cursor.fetchall():
                self.resultados_historicos.append({
                    'concurso': row[0],
                    'numeros': set(row[1:16])
                })
            
            cursor.close()
            conn.close()
            
            print(f"   ✅ {len(self.resultados_historicos)} concursos carregados")
            print(f"   📅 Concursos: {self.resultados_historicos[-1]['concurso']} a {self.resultados_historicos[0]['concurso']}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    def _contar_acertos(self, combinacao: Set[int], resultado: Set[int]) -> int:
        """Conta acertos de uma combinação"""
        return len(combinacao.intersection(resultado))
    
    def _avaliar_combinacoes(self, combinacoes: List[Set[int]], nome_gerador: str) -> Dict:
        """Avalia combinações contra histórico"""
        if not combinacoes or not self.resultados_historicos:
            return None
        
        resultados_por_concurso = []
        
        for resultado in self.resultados_historicos:
            melhor_acerto = 0
            acertos_todas = []
            
            for comb in combinacoes:
                acertos = self._contar_acertos(comb, resultado['numeros'])
                acertos_todas.append(acertos)
                melhor_acerto = max(melhor_acerto, acertos)
            
            resultados_por_concurso.append({
                'concurso': resultado['concurso'],
                'melhor_acerto': melhor_acerto,
                'media_acertos': statistics.mean(acertos_todas),
                'acertos_11_mais': sum(1 for a in acertos_todas if a >= 11),
                'acertos_12_mais': sum(1 for a in acertos_todas if a >= 12),
                'acertos_13_mais': sum(1 for a in acertos_todas if a >= 13),
            })
        
        # Estatísticas globais
        melhores = [r['melhor_acerto'] for r in resultados_por_concurso]
        medias = [r['media_acertos'] for r in resultados_por_concurso]
        
        return {
            'nome': nome_gerador,
            'qtd_combinacoes': len(combinacoes),
            'media_melhor_acerto': statistics.mean(melhores),
            'max_acerto': max(melhores),
            'media_geral': statistics.mean(medias),
            'concursos_11+': sum(1 for m in melhores if m >= 11),
            'concursos_12+': sum(1 for m in melhores if m >= 12),
            'concursos_13+': sum(1 for m in melhores if m >= 13),
            'taxa_11+': sum(1 for m in melhores if m >= 11) / len(melhores) * 100,
            'detalhes': resultados_por_concurso
        }
    
    def testar_super_gerador_ia(self) -> Dict:
        """Testa o SuperGeradorIA"""
        print("\n" + "-" * 60)
        print("🔥 SUPER GERADOR IA")
        print("-" * 60)
        
        try:
            inicio = time.perf_counter()
            from super_gerador_ia import SuperGeradorIA
            
            gerador = SuperGeradorIA()
            resultado = gerador.gerar_super_combinacoes(quantidade=10)
            tempo = (time.perf_counter() - inicio) * 1000
            
            if resultado and 'combinacoes' in resultado:
                combinacoes = [set(c['numeros']) for c in resultado['combinacoes']]
                avaliacao = self._avaliar_combinacoes(combinacoes, "SuperGeradorIA")
                if avaliacao:
                    avaliacao['tempo_ms'] = tempo
                    print(f"   ✅ {len(combinacoes)} combinações em {tempo:.0f}ms")
                    return avaliacao
            
            print(f"   ❌ Não gerou combinações válidas")
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:60]}")
            return None
    
    def testar_piramide_invertida(self) -> Dict:
        """Testa a Pirâmide Invertida Dinâmica"""
        print("\n" + "-" * 60)
        print("🔺 PIRÂMIDE INVERTIDA DINÂMICA")
        print("-" * 60)
        
        try:
            inicio = time.perf_counter()
            from piramide_invertida_dinamica import PiramideInvertidaDinamica
            
            gerador = PiramideInvertidaDinamica()
            # Método correto: gerar_baseado_transicoes
            combinacoes_raw = gerador.gerar_baseado_transicoes(qtd_numeros=15, quantidade=10)
            tempo = (time.perf_counter() - inicio) * 1000
            
            if combinacoes_raw:
                combinacoes = []
                for c in combinacoes_raw:
                    if isinstance(c, dict) and 'numeros' in c:
                        combinacoes.append(set(c['numeros']))
                    elif isinstance(c, (list, tuple, set)):
                        combinacoes.append(set(c))
                
                if combinacoes:
                    avaliacao = self._avaliar_combinacoes(combinacoes, "PiramideInvertida")
                    if avaliacao:
                        avaliacao['tempo_ms'] = tempo
                        print(f"   ✅ {len(combinacoes)} combinações em {tempo:.0f}ms")
                        return avaliacao
            
            print(f"   ❌ Não gerou combinações válidas")
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:60]}")
            return None
    
    def testar_gerador_academico(self) -> Dict:
        """Testa o Gerador Acadêmico Dinâmico"""
        print("\n" + "-" * 60)
        print("🎓 GERADOR ACADÊMICO DINÂMICO")
        print("-" * 60)
        
        try:
            inicio = time.perf_counter()
            from gerador_academico_dinamico import GeradorAcademicoDinamico
            
            gerador = GeradorAcademicoDinamico()
            # Método correto: gerar_multiplas_combinacoes
            combinacoes_raw = gerador.gerar_multiplas_combinacoes(quantidade=10, qtd_numeros=15)
            tempo = (time.perf_counter() - inicio) * 1000
            
            if combinacoes_raw:
                combinacoes = []
                for c in combinacoes_raw:
                    if isinstance(c, dict) and 'numeros' in c:
                        combinacoes.append(set(c['numeros']))
                    elif isinstance(c, (list, tuple, set)):
                        combinacoes.append(set(c))
                
                if combinacoes:
                    avaliacao = self._avaliar_combinacoes(combinacoes, "GeradorAcademico")
                    if avaliacao:
                        avaliacao['tempo_ms'] = tempo
                        print(f"   ✅ {len(combinacoes)} combinações em {tempo:.0f}ms")
                        return avaliacao
            
            print(f"   ❌ Não gerou combinações válidas")
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:60]}")
            return None
    
    def testar_sistema_neural_v7(self) -> Dict:
        """Testa o Sistema Neural Network V7"""
        print("\n" + "-" * 60)
        print("🧠 SISTEMA NEURAL NETWORK V7")
        print("-" * 60)
        
        try:
            inicio = time.perf_counter()
            from sistema_neural_network_v7 import SistemaNeuralV7
            
            sistema = SistemaNeuralV7()
            combinacoes_raw = sistema.gerar_combinacoes(quantidade=10)
            tempo = (time.perf_counter() - inicio) * 1000
            
            if combinacoes_raw:
                combinacoes = []
                for c in combinacoes_raw:
                    if isinstance(c, dict) and 'numeros' in c:
                        combinacoes.append(set(c['numeros']))
                    elif isinstance(c, (list, tuple, set)):
                        combinacoes.append(set(c))
                
                if combinacoes:
                    avaliacao = self._avaliar_combinacoes(combinacoes, "NeuralNetworkV7")
                    if avaliacao:
                        avaliacao['tempo_ms'] = tempo
                        print(f"   ✅ {len(combinacoes)} combinações em {tempo:.0f}ms")
                        return avaliacao
            
            print(f"   ❌ Não gerou combinações válidas")
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:60]}")
            return None
    
    def testar_sistema_ultra_precisao(self) -> Dict:
        """Testa o Sistema Ultra Precisão V4"""
        print("\n" + "-" * 60)
        print("🎯 SISTEMA ULTRA PRECISÃO V4")
        print("-" * 60)
        
        try:
            inicio = time.perf_counter()
            from sistema_ultra_precisao_v4 import SistemaUltraPrecisaoV4
            
            sistema = SistemaUltraPrecisaoV4()
            # Método correto: gerar_combinacoes_ultra_precisas
            combinacoes_raw = sistema.gerar_combinacoes_ultra_precisas()
            tempo = (time.perf_counter() - inicio) * 1000
            
            if combinacoes_raw:
                combinacoes = []
                for c in combinacoes_raw:
                    if isinstance(c, dict) and 'numeros' in c:
                        combinacoes.append(set(c['numeros']))
                    elif isinstance(c, (list, tuple, set)):
                        combinacoes.append(set(c))
                
                if combinacoes:
                    avaliacao = self._avaliar_combinacoes(combinacoes, "UltraPrecisaoV4")
                    if avaliacao:
                        avaliacao['tempo_ms'] = tempo
                        print(f"   ✅ {len(combinacoes)} combinações em {tempo:.0f}ms")
                        return avaliacao
            
            print(f"   ❌ Não gerou combinações válidas")
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:60]}")
            return None
    
    def testar_analisador_hibrido(self) -> Dict:
        """Testa o Analisador Híbrido V3"""
        print("\n" + "-" * 60)
        print("🔬 ANALISADOR HÍBRIDO V3")
        print("-" * 60)
        
        try:
            inicio = time.perf_counter()
            from analisador_hibrido_v3 import AnalisadorHibridoV3
            
            analisador = AnalisadorHibridoV3()
            # Tentar gerar combinações através do analisador
            if hasattr(analisador, 'gerar_combinacoes'):
                combinacoes_raw = analisador.gerar_combinacoes(10)
            elif hasattr(analisador, 'sugerir_numeros'):
                sugestao = analisador.sugerir_numeros(15)
                combinacoes_raw = [sugestao] if sugestao else []
            else:
                print(f"   ⚠️ Analisador não gera combinações")
                return None
            
            tempo = (time.perf_counter() - inicio) * 1000
            
            if combinacoes_raw:
                combinacoes = []
                for c in combinacoes_raw:
                    if isinstance(c, dict) and 'numeros' in c:
                        combinacoes.append(set(c['numeros']))
                    elif isinstance(c, (list, tuple, set)):
                        combinacoes.append(set(c))
                
                if combinacoes:
                    avaliacao = self._avaliar_combinacoes(combinacoes, "AnalisadorHibridoV3")
                    if avaliacao:
                        avaliacao['tempo_ms'] = tempo
                        print(f"   ✅ {len(combinacoes)} combinações em {tempo:.0f}ms")
                        return avaliacao
            
            print(f"   ❌ Não gerou combinações válidas")
            return None
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:60]}")
            return None
    
    def executar_benchmark(self):
        """Executa benchmark completo"""
        print("\n" + "=" * 70)
        print("🏆 BENCHMARK COMPLETO DE GERADORES - LOTOSCOPE")
        print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Avaliação contra últimos {self.ultimos_n} concursos")
        print("=" * 70)
        
        # Executar testes
        testes = [
            self.testar_super_gerador_ia,
            self.testar_piramide_invertida,
            self.testar_gerador_academico,
            self.testar_sistema_neural_v7,
            self.testar_sistema_ultra_precisao,
            self.testar_analisador_hibrido,
        ]
        
        resultados = []
        for teste in testes:
            try:
                resultado = teste()
                if resultado:
                    resultados.append(resultado)
            except Exception as e:
                print(f"   ❌ Erro no teste: {e}")
        
        # Gerar ranking
        self._gerar_ranking(resultados)
        
        return resultados
    
    def _gerar_ranking(self, resultados: List[Dict]):
        """Gera ranking final"""
        if not resultados:
            print("\n❌ Nenhum gerador funcionou corretamente")
            return
        
        # Ordenar por taxa de 11+ acertos (decrescente)
        resultados.sort(key=lambda x: (-x['taxa_11+'], -x['media_melhor_acerto']))
        
        print("\n" + "=" * 70)
        print("🏆 RANKING FINAL - MELHOR GERADOR")
        print("=" * 70)
        
        print(f"\n{'Pos':<4} {'Gerador':<25} {'Taxa 11+':<12} {'Média':<10} {'Max':<6} {'Tempo':<10}")
        print("-" * 70)
        
        for i, r in enumerate(resultados, 1):
            medalha = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else f"{i} "
            taxa = f"{r['taxa_11+']:.0f}%"
            media = f"{r['media_melhor_acerto']:.1f}"
            maximo = f"{r['max_acerto']}"
            tempo = f"{r.get('tempo_ms', 0):.0f}ms"
            
            print(f"{medalha:<4} {r['nome']:<25} {taxa:<12} {media:<10} {maximo:<6} {tempo:<10}")
        
        # Detalhes do campeão
        campeao = resultados[0]
        print("\n" + "=" * 70)
        print(f"🥇 CAMPEÃO: {campeao['nome']}")
        print("=" * 70)
        print(f"""
   📊 Estatísticas:
      • Taxa 11+ acertos: {campeao['taxa_11+']:.0f}%
      • Taxa 12+ acertos: {campeao['concursos_12+']}/{self.ultimos_n} ({campeao['concursos_12+']/self.ultimos_n*100:.0f}%)
      • Taxa 13+ acertos: {campeao['concursos_13+']}/{self.ultimos_n} ({campeao['concursos_13+']/self.ultimos_n*100:.0f}%)
      • Média melhor acerto: {campeao['media_melhor_acerto']:.2f}
      • Máximo acertos: {campeao['max_acerto']}
      • Tempo de geração: {campeao.get('tempo_ms', 0):.0f}ms
      • Combinações geradas: {campeao['qtd_combinacoes']}
        """)
        
        # Resultados por concurso do campeão
        print("   📅 Resultados por concurso:")
        for det in campeao['detalhes'][:5]:
            emoji = "✅" if det['melhor_acerto'] >= 11 else "⚠️"
            print(f"      {emoji} Concurso {det['concurso']}: {det['melhor_acerto']} acertos")


def main():
    benchmark = BenchmarkCompleto(ultimos_n_concursos=10)
    resultados = benchmark.executar_benchmark()
    
    # Propostas de melhoria
    print("\n" + "=" * 70)
    print("💡 PROPOSTAS DE MELHORIA IDENTIFICADAS")
    print("=" * 70)
    
    if resultados:
        melhor_taxa = max(r['taxa_11+'] for r in resultados)
        
        if melhor_taxa < 50:
            print("""
    ⚠️ NENHUM GERADOR ATINGE 50% DE TAXA 11+
    
    Propostas:
    1. 🔄 ENSEMBLE: Combinar os top 3 geradores por votação
    2. 📊 ANÁLISE POSICIONAL: Melhorar detecção de padrões por posição
    3. 🧪 BACKTESTING: Testar contra mais concursos históricos
    4. 🤖 IA AVANÇADA: Implementar LSTM/Transformer para séries temporais
    5. 📈 CALIBRAÇÃO: Ajustar parâmetros baseado em performance real
            """)
        elif melhor_taxa < 70:
            print("""
    📊 TAXA MODERADA - PODE MELHORAR
    
    Propostas:
    1. 🎯 FOCO: Otimizar o gerador campeão
    2. 🔧 TUNING: Ajustar hiperparâmetros
    3. 📉 ANÁLISE: Entender padrões de falha
            """)
        else:
            print("""
    ✅ BOA PERFORMANCE!
    
    Propostas:
    1. 🏆 CONSISTÊNCIA: Manter e monitorar performance
    2. 📊 TRACKING: Dashboard de acompanhamento
    3. 🔄 ATUALIZAÇÃO: Recalibrar periodicamente
            """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
