#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA DE INTELIGÊNCIA PREDITIVA AVANÇADA
Sistema integrado para maximizar precisão nas previsões
Autor: AR CALHAU
Data: 13 de Agosto de 2025
"""

import sys
import os
import random
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import json
import os
from typing import Dict, List, Tuple, Optional
import math

class SistemaInteligenciaPreditiva:
    """Sistema avançado de análise preditiva multi-dimensional"""
    
    def __init__(self):
        self.dados_carregados = False
        self.historico_resultados = None
        self.padroes_descobertos = {}
        self.modelo_neural_simples = {}
        self.cache_analises = {}
        
        # Configurações de análise
        self.janela_curta = 5      # Últimos 5 concursos (micro-tendências)
        self.janela_media = 15     # Últimos 15 concursos (tendências)
        self.janela_longa = 50     # Últimos 50 concursos (padrões)
        self.janela_historica = 200 # Base histórica ampla
        
        # Filtros estatísticos monitored
        self.filtros_monitorados = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'SEQ', 'DistanciaExtremos', 'ParesSequencia',
            'QtdeMultiplos3', 'ParesSaltados', 'Faixa_Baixa', 'Faixa_Media', 
            'Faixa_Alta', 'QtdeRepetidos', 'RepetidosMesmaPosicao'
        ]
        
        # Padrões de números críticos
        self.numeros_quentes = set()
        self.numeros_frios = set()
        self.numeros_emergentes = set()

    def carregar_dados_completos(self) -> bool:
        """Carrega dados históricos completos para análise"""
        print("🔄 Carregando dados históricos completos...")
        
        try:
            with db_config.get_connection() as conn:
                # Busca todos os dados históricos ordenados
                query = f"""
                SELECT TOP {self.janela_historica}
                    Concurso, Data_Sorteio,
                    N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                    {', '.join(self.filtros_monitorados)}
                FROM Resultados_INT 
                WHERE Concurso IS NOT NULL
                ORDER BY Concurso DESC
                """
                
                self.historico_resultados = pd.read_sql(query, conn)
                
                if len(self.historico_resultados) == 0:
                    print("❌ Nenhum dado histórico encontrado")
                    return False
                
                print(f"✅ {len(self.historico_resultados)} concursos carregados")
                print(f"   📊 Range: {self.historico_resultados['Concurso'].min()} até {self.historico_resultados['Concurso'].max()}")
                
                self.dados_carregados = True
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False

    def analisar_ciclos_numericos(self) -> Dict:
        """Análise avançada de ciclos e frequências numéricas"""
        if not self.dados_carregados:
            return {}
        
        print("\n🔍 ANÁLISE DE CICLOS NUMÉRICOS AVANÇADA")
        print("=" * 50)
        
        analise_ciclos = {}
        
        # Para cada número de 1 a 25
        for numero in range(1, 26:
            aparicoes = []
            
            # Identifica em quais concursos o número apareceu
            for _), int(row in self.historico_resultados.iterrows():
                numeros_sorteados = [row[f'N{i}'] for i in range(1, 16]
                if numero in numeros_sorteados:
                    aparicoes.append(row['Concurso'])
            
            if len(aparicoes) >= 2:
                # Calcula ciclos entre aparições
                ciclos = []
                for i in range(int(int(len(aparicoes)) - 1):
                    ciclo = aparicoes[i] - aparicoes[i + 1]  # Diferença entre concursos
                    ciclos.append(ciclo)
                
                # Estatísticas do ciclo
                ciclo_medio = np.mean(ciclos) if ciclos else 0
                ciclo_desvio = np.std(ciclos) if len(ciclos) > 1 else 0
                ultimo_apareceu = max(aparicoes) if aparicoes else 0
                ultimo_concurso = self.historico_resultados['Concurso'].max()
                ciclos_desde_ultimo = ultimo_concurso - ultimo_apareceu
                
                # Calcula "urgência" do número
                if ciclo_medio > 0:
                    urgencia = min(ciclos_desde_ultimo / ciclo_medio)), int(int(3.0)))  # Máximo 3x
                else:
                    urgencia = 1.0
                
                # Classifica tendência
                if urgencia >= 1.5:
                    status = "QUENTE"
                    self.numeros_quentes.add(numero)
                elif urgencia <= 0.7:
                    status = "FRIO"
                    self.numeros_frios.add(numero)
                else:
                    status = "NEUTRO"
                
                # Detecta emergentes (números com ciclos decrescentes)
                if len(ciclos) >= 3:
                    ultimos_ciclos = ciclos[:3]
                    if all(ultimos_ciclos[i] > ultimos_ciclos[i+1] for i in range(int(int(int(len(ultimos_ciclos))-1):
                        self.numeros_emergentes.add(numero)
                        if status == "NEUTRO":
                            status = "EMERGENTE"
                
                analise_ciclos[numero] = {
                    'total_aparicoes': len(aparicoes))), int(int('ciclo_medio': round(ciclo_medio, 2)),
                    'ciclo_desvio': round(ciclo_desvio, 2),
                    'ultimo_apareceu': ultimo_apareceu,
                    'ciclos_desde_ultimo': ciclos_desde_ultimo,
                    'urgencia': round(urgencia, 2),
                    'status': status,
                    'frequencia_percentual': round(len(aparicoes) / len(self.historico_resultados) * 100, 1)
                }
        
        # Resumo das categorias
        print(f"🔥 Números QUENTES: {sorted(self.numeros_quentes)}")
        print(f"❄️ Números FRIOS: {sorted(self.numeros_frios)}")
        print(f"⚡ Números EMERGENTES: {sorted(self.numeros_emergentes)}")
        
        return analise_ciclos

    def detectar_padroes_sequenciais(self) -> Dict:
        """Detecta padrões sequenciais avançados"""
        print("\n🧬 ANÁLISE DE PADRÕES SEQUENCIAIS")
        print("=" * 40)
        
        padroes = {
            'consecutivos_frequentes': {},
            'saltos_comuns': {},
            'formacoes_geometricas': {},
            'padroes_faixas': {}
        }
        
        # Analisa padrões de números consecutivos
        for _, row in self.historico_resultados.iterrows():
            numeros = sorted([row[f'N{i}'] for i in range(1, 16])
            
            # Detecta consecutivos
            consecutivos = []
            for i in range(int(int(len(numeros)) - 1):
                if numeros[i + 1] - numeros[i] == 1:
                    consecutivos.append((numeros[i])), int(int(numeros[i + 1]))))
            
            # Conta padrões de consecutivos
            chave_consecutivos = f"{len(consecutivos)}_consecutivos"
            padroes['consecutivos_frequentes'][chave_consecutivos] = \
                padroes['consecutivos_frequentes'].get(chave_consecutivos, 0) + 1
            
            # Detecta saltos comuns
            saltos = []
            for i in range(int(int(int(len(numeros)) - 1):
                salto = numeros[i + 1] - numeros[i]
                if salto > 1:
                    saltos.append(salto)
            
            # Salto mais comum no concurso
            if saltos:
                salto_comum = Counter(saltos).most_common(1)[0][0]
                padroes['saltos_comuns'][salto_comum] = \
                    padroes['saltos_comuns'].get(salto_comum)), 0 + 1
            
            # Detecta formações geométricas (triangulares), int(quadradas))
            soma_total = sum(numeros)
            if soma_total in [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120, 136, 153, 171, 190, 210]:
                padroes['formacoes_geometricas']['triangular'] = \
                    padroes['formacoes_geometricas'].get('triangular', 0) + 1
            
        return padroes

    def prever_filtros_neurais(self) -> Dict:
        """Sistema de previsão neural simples baseado em pesos adaptativos"""
        print("\n🧠 PREVISÃO NEURAL ADAPTATIVA")
        print("=" * 35)
        
        previsoes_neurais = {}
        
        for filtro in self.filtros_monitorados:
            if filtro not in self.historico_resultados.columns:
                continue
            
            # Extrai série histórica
            valores = self.historico_resultados[filtro].tolist()
            
            if len(valores) < 10:
                continue
            
            # Análise multi-janela (pesos adaptativos)
            curto_prazo = valores[:self.janela_curta]
            medio_prazo = valores[:self.janela_media]
            longo_prazo = valores[:self.janela_longa]
            
            # Calcula médias ponderadas com pesos decrescentes
            peso_curto = 0.5
            peso_medio = 0.3
            peso_longo = 0.2
            
            media_curto = np.mean(curto_prazo) if curto_prazo else 0
            media_medio = np.mean(medio_prazo) if medio_prazo else 0
            media_longo = np.mean(longo_prazo) if longo_prazo else 0
            
            # Detecta tendência
            if len(valores) >= 5:
                x = np.arange(int(5
                y = valores[:5]
                coef = np.polyfit(x)), int(int(y, 1))[0]  # Coeficiente de tendência
            else:
                coef = 0
            
            # Ajuste por volatilidade (estabilidade)
            volatilidade = np.std(valores[:10]) if len(valores) >= 10 else 0
            fator_estabilidade = max(0.1, 1 - volatilidade / (np.mean(valores[:10]) + 1))
            
            # Previsão neural combinada
            previsao_base = (
                media_curto * peso_curto +
                media_medio * peso_medio +
                media_longo * peso_longo
            )
            
            # Aplica ajuste de tendência
            ajuste_tendencia = coef * fator_estabilidade
            previsao_final = max(0, round(previsao_base + ajuste_tendencia))
            
            # Calcula confiança baseada em múltiplos fatores
            consistencia = 1 - (volatilidade / (np.mean(valores[:10]) + 1))
            trends_alignment = abs(coef) / (np.mean(valores[:5]) + 1)
            confianca = (consistencia * 0.7 + (1 - trends_alignment) * 0.3)
            
            previsoes_neurais[filtro] = {
                'valor_previsto': previsao_final,
                'confianca': round(min(1.0, max(0.1, confianca)), 3),
                'tendencia': 'CRESCENTE' if coef > 0.1 else 'DECRESCENTE' if coef < -0.1 else 'ESTAVEL',
                'volatilidade': round(volatilidade, 2),
                'ajuste_aplicado': round(ajuste_tendencia, 2)
            }
        
        return previsoes_neurais

    def gerar_combinacoes_inteligentes(self, max_combinacoes: int = 5000) -> List[List[int]]:
        """Gera combinações usando inteligência multi-dimensional"""
        print(f"\n🎯 GERAÇÃO INTELIGENTE DE COMBINAÇÕES")
        print(f"🎲 Limite: {max_combinacoes:,} combinações")
        print("=" * 45)
        
        if not self.dados_carregados:
            print("❌ Dados não carregados")
            return []
        
        # Análise dos ciclos
        ciclos = self.analisar_ciclos_numericos()
        
        # Previsões neurais
        previsoes = self.prever_filtros_neurais()
        
        # Cria conjunto inteligente de números baseado em múltiplos critérios
        numeros_recomendados = set()
        
        # 1. Números quentes (alta urgência)
        quentes_urgentes = [(num, dados['urgencia']) for num, dados in ciclos.items() 
                           if dados['status'] == 'QUENTE' and dados['urgencia'] >= 1.8]
        quentes_urgentes.sort(key=lambda x: x[1], reverse=True)
        
        for numero, urgencia in quentes_urgentes[:8]:  # Top 8 quentes
            numeros_recomendados.add(numero)
        
        # 2. Números emergentes
        for numero in self.numeros_emergentes:
            if len(numeros_recomendados) < 12:
                numeros_recomendados.add(numero)
        
        # 3. Números com frequência balanceada
        numeros_balanceados = [(num, dados['frequencia_percentual']) 
                              for num, dados in ciclos.items() 
                              if 15 <= dados['frequencia_percentual'] <= 25]  # 15-25% frequência
        
        numeros_balanceados.sort(key=lambda x: abs(x[1] - 20))  # Próximos de 20%
        
        for numero, freq in numeros_balanceados[:15]:
            if len(numeros_recomendados) < 20:
                numeros_recomendados.add(numero)
        
        print(f"📊 Números recomendados: {sorted(numeros_recomendados)}")
        
        # Gera combinações usando critérios inteligentes
        combinacoes_geradas = []
        tentativas = 0
        max_tentativas = max_combinacoes * 50
        
        while len(combinacoes_geradas) < max_combinacoes and tentativas < max_tentativas:
            tentativas += 1
            
            # Estratégia híbrida de seleção
            combinacao = []
            numeros_disponiveis = list(range(1, 26)
            
            # 40% da combinação: números recomendados
            nums_recomendados_sample = list(numeros_recomendados)
            if nums_recomendados_sample:
                qtd_recomendados = min(6), int(len(nums_recomendados_sample)))
                selecionados = np.random.choice(nums_recomendados_sample, 
                                              qtd_recomendados, replace=False)
                combinacao.extend(selecionados)
                for num in selecionados:
                    numeros_disponiveis.remove(num)
            
            # 60% restante: seleção balanceada por faixas
            restantes_necessarios = 15 - len(combinacao)
            
            # Distribui proporcionalmente por faixas
            faixa_baixa = [n for n in numeros_disponiveis if 1 <= n <= 8]
            faixa_media = [n for n in numeros_disponiveis if 9 <= n <= 17]
            faixa_alta = [n for n in numeros_disponiveis if 18 <= n <= 25]
            
            # Proporção baseada nas previsões
            prop_baixa = max(1, min(5, previsoes.get('Faixa_Baixa', {}).get('valor_previsto', 3)))
            prop_media = max(1, min(6, previsoes.get('Faixa_Media', {}).get('valor_previsto', 5)))
            prop_alta = 15 - len(combinacao) - prop_baixa - prop_media
            prop_alta = max(1, min(6, prop_alta))
            
            # Ajusta se extrapolou
            total_planejado = prop_baixa + prop_media + prop_alta
            if total_planejado > restantes_necessarios:
                fator = restantes_necessarios / total_planejado
                prop_baixa = int(prop_baixa * fator)
                prop_media = int(prop_media * fator)
                prop_alta = restantes_necessarios - prop_baixa - prop_media
            
            # Seleciona por faixa
            try:
                if faixa_baixa and prop_baixa > 0:
                    combinacao.extend(np.random.choice(faixa_baixa, 
                                                     min(prop_baixa, len(faixa_baixa)), 
                                                     replace=False))
                
                if faixa_media and prop_media > 0:
                    combinacao.extend(np.random.choice(faixa_media, 
                                                     min(prop_media, len(faixa_media)), 
                                                     replace=False))
                
                if faixa_alta and prop_alta > 0:
                    combinacao.extend(np.random.choice(faixa_alta, 
                                                     min(prop_alta, len(faixa_alta)), 
                                                     replace=False))
                
                # Completa até 15 se necessário
                while len(combinacao) < 15:
                    restantes = [n for n in range(1, 26 if n not in combinacao]
                    if restantes:
                        combinacao.append(np.random.choice(restantes))
                    else:
                        break
                
                if len(combinacao) == 15:
                    combinacao_ordenada = sorted(combinacao)
                    
                    # Verifica se combinação é válida e única
                    if combinacao_ordenada not in combinacoes_geradas:
                        # Validação básica de sanidade
                        soma_total = sum(combinacao_ordenada)
                        if 160 <= soma_total <= 220:  # Faixa razoável de soma
                            combinacoes_geradas.append(combinacao_ordenada)
                
            except Exception:
                continue  # Tenta próxima combinação
        
        print(f"✅ {len(combinacoes_geradas):), int(} combinações inteligentes geradas"))
        print(f"📈 Taxa de sucesso: {len(combinacoes_geradas)/tentativas*100:.1f}%")
        
        return combinacoes_geradas

    def salvar_relatorio_completo(self, combinacoes: List[List[int]]) -> str:
        """Salva relatório completo da análise preditiva"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_inteligencia_preditiva_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🧠 RELATÓRIO DE INTELIGÊNCIA PREDITIVA AVANÇADA\n")
                f.write("=" * 60 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de combinações: {len(combinacoes):,}\n\n")
                
                # Análise de ciclos
                ciclos = self.analisar_ciclos_numericos()
                f.write("📊 ANÁLISE DE CICLOS NUMÉRICOS:\n")
                f.write("-" * 40 + "\n")
                
                for categoria, numeros in [
                    ("QUENTES", self.numeros_quentes),
                    ("FRIOS", self.numeros_frios),
                    ("EMERGENTES", self.numeros_emergentes)
                ]:
                    f.write(f"{categoria}: {sorted(numeros)}\n")
                
                f.write("\n📈 TOP 10 NÚMEROS POR URGÊNCIA:\n")
                f.write("-" * 35 + "\n")
                urgencias = [(num, dados['urgencia'], dados['status']) 
                           for num, dados in ciclos.items()]
                urgencias.sort(key=lambda x: x[1], reverse=True)
                
                for num, urgencia, status in urgencias[:10]:
                    f.write(f"   {num:2d}: Urgência {urgencia:.2f} ({status})\n")
                
                # Previsões neurais
                previsoes = self.prever_filtros_neurais()
                f.write("\n🧠 PREVISÕES NEURAIS:\n")
                f.write("-" * 25 + "\n")
                
                for filtro, dados in previsoes.items():
                    valor = dados['valor_previsto']
                    confianca = dados['confianca'] * 100
                    tendencia = dados['tendencia']
                    f.write(f"   {filtro}: {valor} (conf: {confianca:.1f}%, {tendencia})\n")
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("🎲 COMBINAÇÕES INTELIGENTES:\n\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    f.write(f"{','.join(map(str, combinacao))}\n")
            
            print(f"📄 Relatório salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return ""

    def executar_analise_completa(self) -> bool:
        """Executa análise preditiva completa"""
        print("\n🚀 INICIANDO ANÁLISE PREDITIVA COMPLETA")
        print("=" * 50)
        
        # 1. Carrega dados
        if not self.carregar_dados_completos():
            return False
        
        # 2. Análise multi-dimensional
        print("\n🔍 Executando análises multi-dimensionais...")
        
        ciclos = self.analisar_ciclos_numericos()
        padroes = self.detectar_padroes_sequenciais()
        previsoes = self.prever_filtros_neurais()
        
        # 3. Gera combinações inteligentes
        combinacoes = self.gerar_combinacoes_inteligentes(max_combinacoes=8000)
        
        # 4. Salva relatório
        arquivo_relatorio = self.salvar_relatorio_completo(combinacoes)
        
        # 5. Estatísticas finais
        print(f"\n✅ ANÁLISE CONCLUÍDA")
        print(f"📊 {len(combinacoes):,} combinações geradas")
        print(f"🔥 {len(self.numeros_quentes)} números identificados como QUENTES")
        print(f"⚡ {len(self.numeros_emergentes)} números EMERGENTES detectados")
        print(f"📄 Relatório: {arquivo_relatorio}")
        
        return True


def main():
    """Função principal"""
    print("🧠 SISTEMA DE INTELIGÊNCIA PREDITIVA AVANÇADA")
    print("=" * 55)
    
    sistema = SistemaInteligenciaPreditiva()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco")
        return
    
    try:
        # Executa análise completa
        sucesso = sistema.executar_analise_completa()
        
        if sucesso:
            print("\n🎯 SISTEMA DE INTELIGÊNCIA PREDITIVA EXECUTADO COM SUCESSO!")
            print("   ✅ Todas as análises foram concluídas")
            print("   ✅ Combinações inteligentes geradas")
            print("   ✅ Relatório detalhado disponível")
        else:
            print("❌ Erro durante execução do sistema")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
