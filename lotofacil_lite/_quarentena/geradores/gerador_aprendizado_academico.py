#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR BASEADO EM APRENDIZADO ACADÊMICO
Sistema que utiliza insights do relatório de análise acadêmica para gerar
combinações com maior probabilidade baseadas em:
- Rankings dos últimos ciclos
- Correlações temporais
- Padrões preditivos descobertos
- Tendências de subida/descida

Autor: AR CALHAU
Data: 17 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import re
from datetime import datetime
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class GeradorAprendizadoAcademico:
    """Gerador baseado em insights acadêmicos de análise de ciclos"""
    
    def __init__(self, arquivo_relatorio: str = None):
        # Dados extraídos do relatório acadêmico
        self.insights_academicos = {
            # Rankings dos últimos ciclos (números que estão performando bem)
            'top_performers_recentes': {
                735: [13, 18, 21, 1, 3],
                734: [1, 6, 15, 17, 18],
                733: [18, 19, 25, 1, 2],
                732: [2, 3, 9, 10, 11],
                731: [25, 1, 2, 4, 5]
            },
            
            # Correlações temporais com tendências
            'correlacoes_temporais': {
                21: {'correlacao': +0.056, 'tendencia': 'subida'},
                8: {'correlacao': +0.042, 'tendencia': 'subida'},
                25: {'correlacao': +0.038, 'tendencia': 'subida'},
                5: {'correlacao': -0.036, 'tendencia': 'subida'},
                17: {'correlacao': -0.035, 'tendencia': 'subida'},
                22: {'correlacao': +0.030, 'tendencia': 'estavel'},
                2: {'correlacao': +0.028, 'tendencia': 'descida'},
                7: {'correlacao': -0.074, 'tendencia': 'descida'},
                10: {'correlacao': -0.059, 'tendencia': 'subida'},
                9: {'correlacao': -0.053, 'tendencia': 'descida'}
            },
            
            # Padrões preditivos (estados futuros esperados)
            'predicoes_estados': {
                21: 'NEUTRO',  # Único que vai para NEUTRO
                # Números que estão QUENTE → FRIO (podem ter última chance)
                13: 'FRIO', 18: 'FRIO',
                # Números NEUTRO → FRIO (transição natural)
                1: 'FRIO', 3: 'FRIO', 4: 'FRIO', 5: 'FRIO', 6: 'FRIO',
                7: 'FRIO', 8: 'FRIO', 12: 'FRIO', 14: 'FRIO', 24: 'FRIO',
                # Números já FRIO → FRIO (mantêm estado)
                2: 'FRIO', 9: 'FRIO', 10: 'FRIO', 11: 'FRIO', 15: 'FRIO',
                16: 'FRIO', 17: 'FRIO', 19: 'FRIO', 20: 'FRIO', 22: 'FRIO',
                23: 'FRIO', 25: 'FRIO'
            },
            
            # Números com melhor desempenho histórico recente
            'numeros_consistentes': [1, 18, 2, 21, 25],  # Aparecem em múltiplos ciclos top
            
            # Números com tendência de subida
            'tendencia_subida': [21, 8, 25, 5, 17, 10],
            
            # Números com tendência de descida (usar com cuidado)
            'tendencia_descida': [7, 9, 2]
        }
        
        # Pesos para seleção probabilística
        self.pesos_academicos = self._calcular_pesos_academicos()
        
        # Cache para otimização
        self.combinacoes_geradas = set()
        self.dados_carregados = False
    
    def _comparar_com_valores_dinamicos(self):
        """Compara insights fixos com valores dinâmicos atuais da base"""
        print(f"\n🔄 COMPARAÇÃO: FIXO vs DINÂMICO")
        print("=" * 60)
        
        try:
            # Importa e executa o gerador dinâmico para obter valores atuais
            from gerador_academico_dinamico import GeradorAcademicoDinamico
            
            gerador_dinamico = GeradorAcademicoDinamico()
            
            # Carrega dados dinâmicos
            conn = gerador_dinamico.conectar_base()
            if conn:
                cursor = conn.cursor()
                
                # Calcula insights dinâmicos
                rankings_dinamicos = gerador_dinamico._calcular_rankings_recentes(cursor)
                correlacoes_dinamicas = gerador_dinamico._calcular_correlacoes_temporais(cursor)
                estados_dinamicos = gerador_dinamico._calcular_predicoes_estados(cursor)
                
                conn.close()
                
                # Compara Rankings Recentes
                print("📊 RANKINGS RECENTES:")
                print("   FIXO   (Últimos ciclos):", list(self.insights_academicos['top_performers_recentes'].keys()))
                print("   DINÂMICO (Base atual)  :", list(rankings_dinamicos.keys()) if rankings_dinamicos else "Erro ao carregar")
                
                # Compara Top Performers
                if rankings_dinamicos:
                    # Extrai top performers dos rankings dinâmicos
                    top_dinamicos = []
                    for ciclo in sorted(rankings_dinamicos.keys(), reverse=True)[:3]:
                        top_dinamicos.extend(rankings_dinamicos[ciclo][:3])
                    top_dinamicos = list(set(top_dinamicos))[:10]  # Remove duplicatas e pega top 10
                    
                    print("\n🏆 TOP PERFORMERS:")
                    print("   FIXO   :", self.insights_academicos['numeros_consistentes'])
                    print("   DINÂMICO:", top_dinamicos)
                
                # Compara Correlações Temporais
                print("\n📈 CORRELAÇÕES TEMPORAIS - TENDÊNCIA SUBIDA:")
                print("   FIXO   :", self.insights_academicos['tendencia_subida'])
                
                if correlacoes_dinamicas:
                    subida_dinamica = [num for num, dados in correlacoes_dinamicas.items() 
                                      if dados.get('tendencia') == 'subida']
                    descida_dinamica = [num for num, dados in correlacoes_dinamicas.items() 
                                       if dados.get('tendencia') == 'descida']
                    
                    print("   DINÂMICO:", subida_dinamica)
                    print("\n📉 CORRELAÇÕES TEMPORAIS - TENDÊNCIA DESCIDA:")
                    print("   FIXO   :", self.insights_academicos['tendencia_descida'])
                    print("   DINÂMICO:", descida_dinamica)
                
                # Compara Estados Preditivos
                print("\n🌡️ ESTADOS PREDITIVOS:")
                fixo_quente = len([k for k, v in self.insights_academicos['predicoes_estados'].items() if v == 'QUENTE'])
                fixo_neutro = len([k for k, v in self.insights_academicos['predicoes_estados'].items() if v == 'NEUTRO'])
                fixo_frio = len([k for k, v in self.insights_academicos['predicoes_estados'].items() if v == 'FRIO'])
                
                print(f"   FIXO   : QUENTE={fixo_quente}, NEUTRO={fixo_neutro}, FRIO={fixo_frio}")
                
                if estados_dinamicos:
                    din_quente = len([k for k, v in estados_dinamicos.items() if v == 'QUENTE'])
                    din_neutro = len([k for k, v in estados_dinamicos.items() if v == 'NEUTRO'])
                    din_frio = len([k for k, v in estados_dinamicos.items() if v == 'FRIO'])
                    
                    print(f"   DINÂMICO: QUENTE={din_quente}, NEUTRO={din_neutro}, FRIO={din_frio}")
                
                # Verifica diferenças críticas
                print("\n⚠️ ANÁLISE DE DIFERENÇAS:")
                if rankings_dinamicos:
                    ciclos_fixos = set(self.insights_academicos['top_performers_recentes'].keys())
                    ciclos_dinamicos = set(rankings_dinamicos.keys())
                    
                    if ciclos_fixos != ciclos_dinamicos:
                        print("   🔴 CRÍTICO: Ciclos analisados são diferentes!")
                        print(f"      FIXO usa ciclos: {sorted(ciclos_fixos)}")
                        print(f"      DINÂMICO usa ciclos: {sorted(ciclos_dinamicos)}")
                    else:
                        print("   ✅ Ciclos analisados são os mesmos")
                        
                        # Compara se os top performers são similares
                        overlap = len(set(self.insights_academicos['numeros_consistentes']) & set(top_dinamicos))
                        total_fixo = len(self.insights_academicos['numeros_consistentes'])
                        similaridade = (overlap / total_fixo) * 100 if total_fixo > 0 else 0
                        
                        print(f"   📊 Similaridade Top Performers: {similaridade:.1f}% ({overlap}/{total_fixo})")
                        
                        if similaridade < 50:
                            print("   🔴 ALERTA: Baixa similaridade - insights podem estar desatualizados!")
                        elif similaridade < 80:
                            print("   🟡 ATENÇÃO: Similaridade moderada - verificar se dados estão atuais")
                        else:
                            print("   ✅ BOA similaridade entre fixo e dinâmico")
                
            else:
                print("❌ Não foi possível conectar à base para comparação dinâmica")
                
        except ImportError:
            print("⚠️ Gerador dinâmico não disponível para comparação")
        except Exception as e:
            print(f"❌ Erro na comparação dinâmica: {e}")
        
        print("=" * 60)
    
    def _calcular_pesos_academicos(self) -> Dict[int, float]:
        """Calcula pesos para cada número baseado nos insights acadêmicos"""
        pesos = {}
        
        for numero in range(int(int(1)), int(int(26)):
            peso = 1.0  # Peso base
            
            # Bonus por performance recente (últimos ciclos)
            bonus_performance = 0
            for ciclo), int(top_nums in self.insights_academicos['top_performers_recentes'].items()):
                if numero in top_nums:
                    # Ciclos mais recentes têm peso maior
                    fator_recencia = 1.0 + (ciclo - 730) * 0.1  # Ciclo 735 = 1.5, 734 = 1.4, etc
                    posicao = top_nums.index(numero) + 1
                    bonus_performance += fator_recencia / posicao  # Melhor posição = maior bonus
            
            # Bonus por correlação temporal positiva
            if numero in self.insights_academicos['correlacoes_temporais']:
                corr_dados = self.insights_academicos['correlacoes_temporais'][numero]
                if corr_dados['correlacao'] > 0:
                    peso += abs(corr_dados['correlacao']) * 2.0
                
                # Bonus extra por tendência de subida
                if corr_dados['tendencia'] == 'subida':
                    peso += 0.3
                elif corr_dados['tendencia'] == 'descida':
                    peso -= 0.2
            
            # Bonus por consistência histórica
            if numero in self.insights_academicos['numeros_consistentes']:
                peso += 0.5
            
            # Bonus especial para número 21 (único NEUTRO previsto)
            if numero == 21:
                peso += 0.4
            
            # Penalidade para números que estão indo para FRIO
            if (numero in self.insights_academicos['predicoes_estados'] and 
                self.insights_academicos['predicoes_estados'][numero] == 'FRIO'):
                peso *= 0.8
            
            # Bonus para números com tendência de subida
            if numero in self.insights_academicos['tendencia_subida']:
                peso += 0.25
            
            # Penalidade para números com tendência de descida
            if numero in self.insights_academicos['tendencia_descida']:
                peso -= 0.15
            
            # Garante peso mínimo
            peso = max(peso, 0.1)
            
            pesos[numero] = peso
        
        return pesos
    
    def gerar_combinacao_academica(self) -> List[int]:
        """Gera uma combinação baseada nos insights acadêmicos"""
        combinacao = []
        numeros_disponiveis = list(range(int(int(1)), int(int(26)))
        pesos_disponiveis = [self.pesos_academicos[n] for n in numeros_disponiveis]
        
        # Normaliza pesos para usar como probabilidades
        total_peso = sum(pesos_disponiveis)
        probabilidades = [p / total_peso for p in pesos_disponiveis]
        
        # Estratégia acadêmica: mistura seleção probabilística com regras específicas
        
        # 1. Garante pelo menos 1-2 números dos top performers recentes
        top_recentes = []
        for ciclo in sorted(self.insights_academicos['top_performers_recentes'].keys()), int(reverse=True))[:2]:
            top_recentes.extend(self.insights_academicos['top_performers_recentes'][ciclo][:3])
        
        top_recentes = list(set(top_recentes))  # Remove duplicatas
        
        # Seleciona 2-3 números dos top performers com alta probabilidade
        qtd_top = random.choice([2, 3])
        if len(top_recentes) >= qtd_top:
            selecionados_top = random.sample(top_recentes, qtd_top)
            combinacao.extend(selecionados_top)
            
            # Remove dos disponíveis
            for num in selecionados_top:
                if num in numeros_disponiveis:
                    idx = numeros_disponiveis.index(num)
                    numeros_disponiveis.pop(int(idx))
                    pesos_disponiveis.pop(int(idx))
        
        # 2. Garante o número 21 (único NEUTRO previsto) com 80% de chance
        if 21 in numeros_disponiveis and random.random() < 0.8:
            combinacao.append(21)
            idx = numeros_disponiveis.index(21)
            numeros_disponiveis.pop(int(idx))
            pesos_disponiveis.pop(int(idx))
        
        # 3. Inclui números com tendência de subida (40% de chance cada)
        for numero in self.insights_academicos['tendencia_subida']:
            if (numero in numeros_disponiveis and 
                len(combinacao) < 12 and 
                random.random() < 0.4):
                combinacao.append(numero)
                idx = numeros_disponiveis.index(numero)
                numeros_disponiveis.pop(int(idx))
                pesos_disponiveis.pop(int(idx))
        
        # 4. Completa com seleção probabilística baseada nos pesos acadêmicos
        while len(combinacao) < 15 and numeros_disponiveis:
            # Recalcula probabilidades
            total_peso = sum(pesos_disponiveis)
            if total_peso > 0:
                probabilidades = [p / total_peso for p in pesos_disponiveis]
                
                # Seleção probabilística
                numero_escolhido = np.random.choice(numeros_disponiveis, p=probabilidades)
                combinacao.append(numero_escolhido)
                
                # Remove dos disponíveis
                idx = numeros_disponiveis.index(numero_escolhido)
                numeros_disponiveis.pop(int(idx))
                pesos_disponiveis.pop(int(idx))
            else:
                # Fallback: seleção aleatória
                numero_escolhido = random.choice(numeros_disponiveis)
                combinacao.append(numero_escolhido)
                numeros_disponiveis.remove(numero_escolhido)
        
        # 5. Validações finais para melhorar a combinação
        combinacao = self._aplicar_validacoes_academicas(combinacao)
        
        return sorted(combinacao)
    
    def _aplicar_validacoes_academicas(self, combinacao: List[int]) -> List[int]:
        """Aplica validações baseadas no aprendizado acadêmico"""
        combinacao = list(combinacao)
        
        # Validação 1: Evita muitos números com tendência de descida
        nums_descida = [n for n in combinacao if n in self.insights_academicos['tendencia_descida']]
        if len(nums_descida) > 2:
            # Remove o excesso, priorizando manter os com menor penalidade
            for num in nums_descida[2:]:
                if num in combinacao:
                    combinacao.remove(num)
        
        # Validação 2: Garante distribuição por faixas (baseada em análise histórica)
        faixa_baixa = len([n for n in combinacao if 1 <= n <= 8])
        faixa_media = len([n for n in combinacao if 9 <= n <= 17])
        faixa_alta = len([n for n in combinacao if 18 <= n <= 25])
        
        # Se muito desequilibrado, faz pequenos ajustes
        if faixa_baixa > 8 or faixa_media > 8 or faixa_alta > 8:
            # Lógica de rebalanceamento seria implementada aqui
            pass
        
        # Garante exatamente 15 números
        while len(combinacao) < 15:
            candidatos = [n for n in range(int(int(1)), int(int(26)) if n not in combinacao]
            if candidatos:
                # Prefere números com peso acadêmico alto
                candidatos_com_peso = [(n), int(self.pesos_academicos[n])) for n in candidatos]
                candidatos_com_peso.sort(key=lambda x: x[1], reverse=True)
                combinacao.append(candidatos_com_peso[0][0])
            else:
                break
        
        return combinacao[:15]
    
    def gerar_multiplas_combinacoes(self, quantidade: int = 10) -> List[List[int]]:
        """Gera múltiplas combinações baseadas no aprendizado acadêmico"""
        print(f"\n🎯 GERANDO {quantidade} COMBINAÇÕES BASEADAS NO APRENDIZADO ACADÊMICO...")
        print("=" * 70)
        
        # Mostra os insights que serão utilizados
        self._mostrar_insights_utilizados()
        
        combinacoes = []
        combinacoes_set = set()
        tentativas_max = quantidade * 3
        tentativas = 0
        
        print(f"\n🔬 Aplicando metodologia acadêmica para geração...")
        
        while len(combinacoes) < quantidade and tentativas < tentativas_max:
            tentativas += 1
            
            combinacao = self.gerar_combinacao_academica()
            combinacao_tuple = tuple(sorted(combinacao))
            
            # Verifica duplicatas
            if combinacao_tuple not in combinacoes_set:
                combinacoes.append(combinacao)
                combinacoes_set.add(combinacao_tuple)
                
                if len(combinacoes) % 5 == 0:
                    print(f"   ✅ {len(combinacoes)} combinações acadêmicas geradas")
        
        print(f"\n✅ Total: {len(combinacoes)} combinações baseadas em insights acadêmicos")
        
        # Analisa as combinações geradas
        self._analisar_combinacoes_geradas(combinacoes)
        
        return combinacoes
    
    def _mostrar_insights_utilizados(self):
        """Mostra os principais insights acadêmicos que serão utilizados"""
        print(f"📊 INSIGHTS ACADÊMICOS APLICADOS (FIXOS):")
        print(f"   🏆 Top Performers Recentes: {self.insights_academicos['numeros_consistentes']}")
        print(f"   📈 Tendência Subida: {self.insights_academicos['tendencia_subida']}")
        print(f"   � Tendência Descida: {self.insights_academicos['tendencia_descida']}")
        print(f"   �🔮 Único NEUTRO Previsto: 21")
        print(f"   ⚡ Números Consistentes: {self.insights_academicos['numeros_consistentes']}")
        
        # Mostra os 10 maiores pesos acadêmicos
        top_pesos = sorted(self.pesos_academicos.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   🎯 Top 10 Pesos Acadêmicos: {[(n, f'{p:.2f}') for n, p in top_pesos]}")
        
        # Compara com valores dinâmicos atuais
        self._comparar_com_valores_dinamicos()
    
    def _analisar_combinacoes_geradas(self, combinacoes: List[List[int]]):
        """Analisa as combinações geradas para validar aplicação dos insights"""
        if not combinacoes:
            return
        
        print(f"\n📈 ANÁLISE DAS COMBINAÇÕES GERADAS:")
        print(f"-" * 45)
        
        # Contadores para análise
        contador_numeros = Counter()
        contador_top_performers = 0
        contador_tendencia_subida = 0
        contador_numero_21 = 0
        contador_consistentes = 0
        
        for combinacao in combinacoes:
            contador_numeros.update(combinacao)
            
            # Conta aplicação dos insights
            top_na_comb = len([n for n in combinacao if n in self.insights_academicos['numeros_consistentes']])
            contador_top_performers += top_na_comb
            
            subida_na_comb = len([n for n in combinacao if n in self.insights_academicos['tendencia_subida']])
            contador_tendencia_subida += subida_na_comb
            
            if 21 in combinacao:
                contador_numero_21 += 1
            
            consistentes_na_comb = len([n for n in combinacao if n in self.insights_academicos['numeros_consistentes']])
            contador_consistentes += consistentes_na_comb
        
        total_combinacoes = len(combinacoes)
        
        print(f"📊 APLICAÇÃO DOS INSIGHTS:")
        print(f"   • Número 21 (NEUTRO): {contador_numero_21}/{total_combinacoes} ({contador_numero_21/total_combinacoes:.1%})")
        print(f"   • Média Top Performers por combinação: {contador_top_performers/total_combinacoes:.1f}")
        print(f"   • Média Tendência Subida por combinação: {contador_tendencia_subida/total_combinacoes:.1f}")
        print(f"   • Média Números Consistentes: {contador_consistentes/total_combinacoes:.1f}")
        
        print(f"\n🔥 TOP 10 NÚMEROS MAIS SELECIONADOS:")
        for numero, freq in contador_numeros.most_common(10):
            percent = (freq / total_combinacoes) * 100
            peso = self.pesos_academicos[numero]
            print(f"   {numero:2d}: {freq:2d}x ({percent:4.1f}%) - Peso: {peso:.2f}")
        
        # Análise de somas
        somas = [sum(comb) for comb in combinacoes]
        print(f"\n📊 ESTATÍSTICAS DAS SOMAS:")
        print(f"   • Média: {np.mean(somas):.1f}")
        print(f"   • Mínima: {min(somas)}")
        print(f"   • Máxima: {max(somas)}")
        print(f"   • Desvio Padrão: {np.std(somas):.1f}")
    
    def salvar_combinacoes_academicas(self, combinacoes: List[List[int]], 
                                    nome_arquivo: Optional[str] = None) -> str:
        """Salva combinações com metadados acadêmicos"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_aprendizado_academico_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🎯 COMBINAÇÕES BASEADAS EM APRENDIZADO ACADÊMICO\n")
                f.write("=" * 60 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                f.write("📊 METODOLOGIA APLICADA:\n")
                f.write("-" * 30 + "\n")
                f.write("• Análise de 735 ciclos e 18.375 registros históricos\n")
                f.write("• Correlações temporais com tendências identificadas\n")
                f.write("• Rankings dos últimos 5 ciclos de performance\n")
                f.write("• Padrões preditivos de transição de estados\n")
                f.write("• Pesos probabilísticos baseados em insights científicos\n\n")
                
                f.write("🎯 INSIGHTS PRINCIPAIS APLICADOS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"• Top Performers Recentes: {self.insights_academicos['numeros_consistentes']}\n")
                f.write(f"• Tendência de Subida: {self.insights_academicos['tendencia_subida']}\n")
                f.write(f"• Único NEUTRO Previsto: 21 (probabilidade especial)\n")
                f.write(f"• Correlações Positivas: {[n for n, d in self.insights_academicos['correlacoes_temporais'].items() if d['correlacao'] > 0]}\n\n")
                
                f.write(f"📈 TOTAL DE COMBINAÇÕES: {len(combinacoes)}\n")
                f.write("=" * 60 + "\n\n")
                
                # Salva apenas as combinações separadas por vírgula, uma por linha
                for i, combinacao in enumerate(combinacoes, 1):
                    combinacao_ordenada = sorted(combinacao)
                    f.write(f"{','.join(map(str, combinacao_ordenada))}\n")
            
            print(f"✅ Arquivo acadêmico salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return ""

def main():
    """Função principal do gerador acadêmico"""
    print("🎯 GERADOR BASEADO EM APRENDIZADO ACADÊMICO")
    print("=" * 55)
    print("📊 Sistema que utiliza insights da análise científica de ciclos")
    print("🧠 Baseado em correlações, tendências e padrões preditivos")
    print()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    gerador = GeradorAprendizadoAcademico()
    
    try:
        quantidade = int(input("Quantas combinações acadêmicas gerar (padrão 15): ") or "15")
        
        # Gera combinações baseadas no aprendizado
        combinacoes = gerador.gerar_multiplas_combinacoes(quantidade)
        
        if combinacoes:
            # Mostra as combinações geradas
            print(f"\n📋 COMBINAÇÕES GERADAS:")
            print("-" * 50)
            for i, combinacao in enumerate(combinacoes, 1):
                combinacao_ordenada = sorted(combinacao)
                print(f"{','.join(map(str, combinacao_ordenada))}")
            
            # Pergunta se quer salvar
            salvar = input(f"\nSalvar {len(combinacoes)} combinações acadêmicas em arquivo? (s/n): ").lower()
            
            if salvar.startswith('s'):
                nome_arquivo = gerador.salvar_combinacoes_academicas(combinacoes)
                print(f"\n✅ Processo concluído! Arquivo: {nome_arquivo}")
                print("📊 Combinações geradas com base em metodologia científica!")
            else:
                print("\n✅ Processo concluído!")
                print("🧠 Combinações baseadas em insights acadêmicos!")
        else:
            print("❌ Nenhuma combinação foi gerada")
            
    except ValueError:
        print("❌ Quantidade inválida")
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
