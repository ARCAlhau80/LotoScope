#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 DETECTOR DE PADRÕES INTEGRADO - LOTOFÁCIL
===========================================
Sistema de detecção de padrões baseado nos achados estatisticamente significativos
Combina ciclos temporais + comportamentos específicos por número
"""

import pyodbc
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import json
from typing import Dict, List, Tuple, Optional

# Importa configuração de banco existente
try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    try:
        from database_config import db_config
        USE_OPTIMIZER = False
    except ImportError:
        USE_OPTIMIZER = None

class DetectorPadroes:
    """🎯 Detector de padrões integrado baseado em análise estatística"""
    
    def __init__(self):
        self.conexao = None
        self.dados_historicos = None
        self.padroes_ativos = {
            'ciclos_temporais': {
                365: {'peso': 0.35, 'confianca': 0.95},  # Anual - mais forte
                91: {'peso': 0.25, 'confianca': 0.90},   # Trimestral 
                30: {'peso': 0.15, 'confianca': 0.85},   # Mensal
                28: {'peso': 0.10, 'confianca': 0.80}    # Lunar
            },
            'numeros_especiais': {
                # Padrões descobertos na análise refinada
                1: {'tipo': 'baixo_forte', 'impacto_pares': -0.071, 'impacto_soma': -0.062, 'peso': 0.20},
                23: {'tipo': 'alto_impar', 'impacto_pares': -0.065, 'impacto_soma': +0.050, 'peso': 0.18},
                24: {'tipo': 'alto_par', 'impacto_pares': +0.081, 'impacto_soma': +0.059, 'peso': 0.18},
                25: {'tipo': 'alto_especial', 'impacto_pares': -0.058, 'impacto_soma': +0.065, 'peso': 0.22}
            }
        }
    
    def conectar_banco(self) -> bool:
        """🔌 Conecta ao banco de dados"""
        try:
            if USE_OPTIMIZER:
                self.conexao = get_optimized_connection()
            elif USE_OPTIMIZER is False:
                self.conexao = db_config.get_connection()
            else:
                connection_string = (
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=VADER\\SQLEXPRESS;"  # Usa servidor correto
                    "DATABASE=LotofacilDB;"
                    "Trusted_Connection=yes;"
                    "MARS_Connection=Yes;"
                )
                self.conexao = pyodbc.connect(connection_string)
            
            print("✅ Detector de padrões conectado ao banco")
            return True
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def carregar_historico(self) -> bool:
        """📊 Carrega histórico para análise de padrões"""
        if not self.conexao:
            return False
        
        try:
            query = """
            SELECT TOP 100 
                Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                (N1 + N2 + N3 + N4 + N5 + N6 + N7 + N8 + N9 + N10 + N11 + N12 + N13 + N14 + N15) as SomaTotal
            FROM resultados_int 
            WHERE Concurso IS NOT NULL
            ORDER BY Concurso DESC
            """
            
            self.dados_historicos = pd.read_sql(query, self.conexao)
            print(f"📊 Carregados últimos {len(self.dados_historicos)} concursos para análise")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            return False
    
    def obter_proximo_concurso(self) -> int:
        """🎯 Obtém número do próximo concurso"""
        if self.dados_historicos is None or len(self.dados_historicos) == 0:
            return 1
        return int(self.dados_historicos['Concurso'].max()) + 1
    
    def calcular_impacto_ciclo_temporal(self, concurso: int) -> Dict[str, float]:
        """⏰ Calcula impacto dos ciclos temporais para um concurso específico"""
        impactos = {}
        
        for ciclo, config in self.padroes_ativos['ciclos_temporais'].items():
            fase_ciclo = concurso % ciclo
            peso = config['peso']
            confianca = config['confianca']
            
            # Fases com padrões específicos descobertos
            if ciclo == 365:
                # Fase 345: +20.6% soma, +34.4% pares, +36.1% baixos
                # Fase 17: Valores baixos
                if fase_ciclo == 345:
                    impactos[f'ciclo_{ciclo}'] = +0.25 * peso * confianca
                elif fase_ciclo == 17:
                    impactos[f'ciclo_{ciclo}'] = -0.20 * peso * confianca
                elif fase_ciclo in [84, 50]:  # Fases com padrões de pares
                    impactos[f'ciclo_{ciclo}'] = +0.15 * peso * confianca
                else:
                    impactos[f'ciclo_{ciclo}'] = 0.0
                    
            elif ciclo == 91:
                # Fase 61: +8.9% soma, Fase 74: +14.4% pares, Fase 16: +16.1% baixos
                if fase_ciclo in [61, 74]:
                    impactos[f'ciclo_{ciclo}'] = +0.12 * peso * confianca
                elif fase_ciclo in [16, 4]:
                    impactos[f'ciclo_{ciclo}'] = +0.08 * peso * confianca
                else:
                    impactos[f'ciclo_{ciclo}'] = 0.0
                    
            elif ciclo == 30:
                # Fase 18: +7.5% pares, Fase 7: +7.6% baixos
                if fase_ciclo in [18, 7]:
                    impactos[f'ciclo_{ciclo}'] = +0.08 * peso * confianca
                elif fase_ciclo in [21, 16]:
                    impactos[f'ciclo_{ciclo}'] = -0.07 * peso * confianca
                else:
                    impactos[f'ciclo_{ciclo}'] = 0.0
                    
            elif ciclo == 28:
                # Fase 6: +6.9% pares
                if fase_ciclo == 6:
                    impactos[f'ciclo_{ciclo}'] = +0.07 * peso * confianca
                elif fase_ciclo == 3:
                    impactos[f'ciclo_{ciclo}'] = -0.06 * peso * confianca
                else:
                    impactos[f'ciclo_{ciclo}'] = 0.0
        
        return impactos
    
    def calcular_score_numero(self, numero: int, contexto_concurso: Dict) -> float:
        """🎲 Calcula score de um número específico baseado nos padrões"""
        if numero not in self.padroes_ativos['numeros_especiais']:
            return 0.5  # Score neutro para números sem padrões específicos
        
        config = self.padroes_ativos['numeros_especiais'][numero]
        score_base = 0.5
        
        # Ajusta baseado no tipo e impactos descobertos
        if config['tipo'] == 'baixo_forte':  # Número 1
            # Quando aparece: -6.2% soma, -7.1% pares, +7.8% baixos
            score_ajuste = config['peso'] * 0.15  # Favorece contextos de baixos
            score_base += score_ajuste
            
        elif config['tipo'] == 'alto_impar':  # Número 23
            # Quando aparece: +5.0% soma, -6.5% pares, -5.9% baixos
            score_ajuste = config['peso'] * 0.12
            score_base += score_ajuste
            
        elif config['tipo'] == 'alto_par':  # Número 24
            # Quando aparece: +5.9% soma, +8.1% pares, -6.3% baixos
            score_ajuste = config['peso'] * 0.14
            score_base += score_ajuste
            
        elif config['tipo'] == 'alto_especial':  # Número 25
            # Quando aparece: +6.5% soma, -5.8% pares, -6.0% baixos, +6.6% gap
            score_ajuste = config['peso'] * 0.16  # Maior peso por múltiplos padrões
            score_base += score_ajuste
        
        return min(1.0, max(0.0, score_base))
    
    def analisar_proximo_concurso(self) -> Dict:
        """🎯 Análise completa do próximo concurso baseada em padrões"""
        proximo_concurso = self.obter_proximo_concurso()
        
        print(f"\n🎯 ANÁLISE POR PADRÕES - CONCURSO {proximo_concurso}")
        print("=" * 50)
        
        # Impactos dos ciclos temporais
        impactos_temporais = self.calcular_impacto_ciclo_temporal(proximo_concurso)
        
        print("⏰ IMPACTOS TEMPORAIS:")
        impacto_total_temporal = 0.0
        for ciclo, impacto in impactos_temporais.items():
            if abs(impacto) > 0.01:  # Só mostra impactos significativos
                print(f"   • {ciclo}: {impacto:+.3f} ({'Forte' if abs(impacto) > 0.15 else 'Moderado' if abs(impacto) > 0.05 else 'Fraco'})")
                impacto_total_temporal += impacto
        
        if abs(impacto_total_temporal) < 0.01:
            print("   • Sem impactos temporais significativos")
        else:
            print(f"   📊 IMPACTO TOTAL TEMPORAL: {impacto_total_temporal:+.3f}")
        
        # Scores por número baseados nos padrões
        print("\n🎲 NÚMEROS COM PADRÕES ESPECIAIS:")
        scores_especiais = {}
        for numero in self.padroes_ativos['numeros_especiais'].keys():
            score = self.calcular_score_numero(numero, {'concurso': proximo_concurso})
            scores_especiais[numero] = score
            tendencia = "Alta" if score > 0.6 else "Baixa" if score < 0.4 else "Neutra"
            print(f"   • Número {numero:2d}: {score:.3f} (Tendência {tendencia})")
        
        # Recomendações baseadas nos padrões
        print("\n💡 RECOMENDAÇÕES BASEADAS NOS PADRÕES:")
        
        if impacto_total_temporal > 0.1:
            print("   🔼 Ciclos favorecem: Somas altas, mais pares, mais altos")
        elif impacto_total_temporal < -0.1:
            print("   🔽 Ciclos favorecem: Somas baixas, menos pares, mais baixos")
        else:
            print("   ⚪ Ciclos temporais neutros")
        
        # Números recomendados/evitados
        nums_recomendados = [n for n, s in scores_especiais.items() if s > 0.6]
        nums_evitados = [n for n, s in scores_especiais.items() if s < 0.4]
        
        if nums_recomendados:
            print(f"   ✅ Números favorecidos: {nums_recomendados}")
        if nums_evitados:
            print(f"   ❌ Números desfavorecidos: {nums_evitados}")
        
        return {
            'concurso': proximo_concurso,
            'impacto_temporal_total': impacto_total_temporal,
            'impactos_por_ciclo': impactos_temporais,
            'scores_numeros_especiais': scores_especiais,
            'recomendacao_geral': 'positiva' if impacto_total_temporal > 0.05 else 'negativa' if impacto_total_temporal < -0.05 else 'neutra'
        }
    
    def gerar_sugestao_jogo(self) -> List[int]:
        """🎰 Gera sugestão de jogo baseada nos padrões detectados"""
        analise = self.analisar_proximo_concurso()
        
        print(f"\n🎰 SUGESTÃO DE JOGO - CONCURSO {analise['concurso']}")
        print("=" * 45)
        
        # Base: distribuição típica da Lotofácil
        numeros_base = []
        
        # Aplica os números especiais conforme seus scores
        for numero, score in analise['scores_numeros_especiais'].items():
            if score > 0.6:  # Alta probabilidade
                numeros_base.append(numero)
                print(f"   ✅ Incluído {numero} (score: {score:.3f})")
        
        # Completa com números baseados nos padrões temporais
        impacto_temporal = analise['impacto_temporal_total']
        
        if impacto_temporal > 0.1:  # Favorece altos/pares
            candidatos = [13, 14, 16, 18, 20, 22, 24]
        elif impacto_temporal < -0.1:  # Favorece baixos/ímpares  
            candidatos = [2, 3, 5, 7, 9, 11]
        else:  # Neutro - distribuição equilibrada
            candidatos = [6, 8, 10, 12, 15, 17, 19, 21]
        
        # Adiciona candidatos até completar 15
        for num in candidatos:
            if len(numeros_base) >= 15:
                break
            if num not in numeros_base:
                numeros_base.append(num)
        
        # Completa aleatoriamente se necessário
        import random
        todos_numeros = list(range(1, 26))
        for num in todos_numeros:
            if len(numeros_base) >= 15:
                break
            if num not in numeros_base:
                numeros_base.append(num)
        
        numeros_finais = sorted(numeros_base[:15])
        
        print(f"   🎲 Jogo sugerido: {numeros_finais}")
        print(f"   📊 Baseado em: {len(analise['scores_numeros_especiais'])} padrões especiais")
        print(f"   ⏰ Impacto temporal: {impacto_temporal:+.3f}")
        
        return numeros_finais
    
    def menu_interativo(self):
        """📋 Menu interativo do detector de padrões"""
        if not self.conectar_banco() or not self.carregar_historico():
            print("❌ Falha na inicialização")
            return
        
        while True:
            print("\n" + "="*50)
            print("🎯 DETECTOR DE PADRÕES INTEGRADO")
            print("="*50)
            print("1. 📊 Analisar próximo concurso")
            print("2. 🎰 Gerar sugestão de jogo")
            print("3. ⏰ Ver impactos dos ciclos temporais")
            print("4. 🎲 Ver padrões dos números especiais")
            print("5. 📈 Relatório completo")
            print("0. 🚪 Voltar")
            
            try:
                opcao = input("\n👉 Escolha: ").strip()
                
                if opcao == "0":
                    break
                elif opcao == "1":
                    self.analisar_proximo_concurso()
                elif opcao == "2":
                    self.gerar_sugestao_jogo()
                elif opcao == "3":
                    concurso = self.obter_proximo_concurso()
                    impactos = self.calcular_impacto_ciclo_temporal(concurso)
                    print(f"\n⏰ Impactos temporais para concurso {concurso}:")
                    for ciclo, impacto in impactos.items():
                        print(f"   {ciclo}: {impacto:+.3f}")
                elif opcao == "4":
                    print("\n🎲 Padrões dos números especiais:")
                    for num, config in self.padroes_ativos['numeros_especiais'].items():
                        print(f"   Número {num}: {config['tipo']} (peso: {config['peso']:.2f})")
                elif opcao == "5":
                    analise = self.analisar_proximo_concurso()
                    self.gerar_sugestao_jogo()
                else:
                    print("❌ Opção inválida!")
                    
                input("\n📱 Pressione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    detector = DetectorPadroes()
    detector.menu_interativo()

if __name__ == "__main__":
    main()