#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANALISADOR DE PARÂMETROS DINÂMICOS PARA LOTOFÁCIL
====================================================
Sistema que analisa histórico em diferentes janelas temporais
para calcular valores ótimos dos 7 parâmetros críticos
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import statistics
from datetime import datetime
import json
import sqlite3
from typing import Dict, List, Tuple, Any

class AnalisadorParametrosDinamicos:
    """
    Analisa histórico em múltiplas janelas para prever parâmetros ótimos
    """
    
    def __init__(self, caminho_db: str = None):
        self.caminho_db = caminho_db
        self.historico_completo = []
        self.janelas_analise = [3, 5, 10, 15, 30, 'total']
        
        # Resultados das análises
        self.analises = {}
        self.predicoes = {}
        
    def carregar_historico(self, dados: List[Dict] = None):
        """Carrega dados históricos"""
        if dados:
            self.historico_completo = dados
        elif self.caminho_db:
            self._carregar_do_banco()
        else:
            self._carregar_dados_simulados()
        
        print(f"[CARREGADO] {len(self.historico_completo)} concursos no histórico")
    
    def _carregar_dados_simulados(self):
        """Cria dados simulados para teste"""
        import random
        
        print("[SIMULACAO] Gerando dados históricos simulados...")
        
        for i in range(3500, 3550):  # 50 concursos simulados
            # Simula uma combinação realística
            nums = sorted(random.sample(range(1, 26), 15))
            
            # Calcula parâmetros do concurso
            n1, n15 = nums[0], nums[-1]
            
            # Simula comparação com concurso anterior
            maior_que_ultimo = random.randint(5, 12)
            menor_que_ultimo = random.randint(3, 10)
            
            # Conta números em faixas específicas
            qtde_6_a_25 = sum(1 for n in nums if 6 <= n <= 25)
            qtde_6_a_20 = sum(1 for n in nums if 6 <= n <= 20)
            
            # Conta posições ótimas (simulado)
            posicoes_otimas = [1, 2, 4, 6, 8, 9, 11, 13, 15, 16, 19, 20, 22, 24, 25]
            melhores_posicoes = sum(1 for j, num in enumerate(nums) if num in posicoes_otimas[:j+1])
            
            concurso = {
                'concurso': i,
                'numeros': nums,
                'n1': n1,
                'n15': n15,
                'maior_que_ultimo': maior_que_ultimo,
                'menor_que_ultimo': menor_que_ultimo,
                'qtde_6_a_25': qtde_6_a_25,
                'qtde_6_a_20': qtde_6_a_20,
                'melhores_posicoes': melhores_posicoes,
                'soma_total': sum(nums)
            }
            
            self.historico_completo.append(concurso)
    
    def analisar_todas_janelas(self):
        """Executa análise em todas as janelas temporais"""
        print("\n[ANALISE] Processando janelas temporais...")
        
        for janela in self.janelas_analise:
            print(f"   Analisando janela: {janela}")
            self.analises[janela] = self._analisar_janela(janela)
        
        print(f"[CONCLUIDO] {len(self.analises)} análises completadas")
    
    def _analisar_janela(self, janela) -> Dict[str, Any]:
        """Analisa uma janela temporal específica"""
        
        # Seleciona dados da janela
        if janela == 'total':
            dados_janela = self.historico_completo
        else:
            dados_janela = self.historico_completo[-janela:] if len(self.historico_completo) >= janela else self.historico_completo
        
        if not dados_janela:
            return {}
        
        # Extrai valores de cada parâmetro
        parametros = {
            'n1': [c['n1'] for c in dados_janela],
            'n15': [c['n15'] for c in dados_janela],
            'maior_que_ultimo': [c['maior_que_ultimo'] for c in dados_janela],
            'menor_que_ultimo': [c['menor_que_ultimo'] for c in dados_janela],
            'qtde_6_a_25': [c['qtde_6_a_25'] for c in dados_janela],
            'qtde_6_a_20': [c['qtde_6_a_20'] for c in dados_janela],
            'melhores_posicoes': [c['melhores_posicoes'] for c in dados_janela]
        }
        
        # Análise estatística de cada parâmetro
        resultado = {}
        
        for param, valores in parametros.items():
            if valores:
                resultado[param] = {
                    'valores': valores,
                    'media': statistics.mean(valores),
                    'mediana': statistics.median(valores),
                    'moda': self._calcular_moda(valores),
                    'min': min(valores),
                    'max': max(valores),
                    'desvio': statistics.stdev(valores) if len(valores) > 1 else 0,
                    'frequencias': Counter(valores),
                    'tendencia': self._calcular_tendencia(valores),
                    'estabilidade': self._calcular_estabilidade(valores)
                }
        
        resultado['meta'] = {
            'janela': janela,
            'total_concursos': len(dados_janela),
            'periodo': f"{dados_janela[0]['concurso']} a {dados_janela[-1]['concurso']}"
        }
        
        return resultado
    
    def _calcular_moda(self, valores: List[int]) -> int:
        """Calcula moda dos valores"""
        contador = Counter(valores)
        return contador.most_common(1)[0][0] if contador else 0
    
    def _calcular_tendencia(self, valores: List[int]) -> str:
        """Identifica tendência dos valores"""
        if len(valores) < 3:
            return 'insuficiente'
        
        # Compara primeira e segunda metade
        meio = len(valores) // 2
        primeira_metade = statistics.mean(valores[:meio])
        segunda_metade = statistics.mean(valores[meio:])
        
        if segunda_metade > primeira_metade * 1.1:
            return 'crescente'
        elif segunda_metade < primeira_metade * 0.9:
            return 'decrescente'
        else:
            return 'estavel'
    
    def _calcular_estabilidade(self, valores: List[int]) -> float:
        """Calcula índice de estabilidade (0-1)"""
        if len(valores) <= 1:
            return 1.0
        
        desvio = statistics.stdev(valores)
        media = statistics.mean(valores)
        
        # Coeficiente de variação invertido
        cv = desvio / media if media > 0 else 1
        return max(0, 1 - cv)
    
    def calcular_parametros_otimos(self) -> Dict[str, int]:
        """
        Calcula valores ótimos para os 7 parâmetros baseado nas análises
        """
        print("\n[OTIMIZACAO] Calculando parâmetros ótimos...")
        
        parametros_otimos = {}
        
        # Pesos para cada janela temporal (mais recente = maior peso)
        pesos = {
            3: 0.35,      # Últimos 3 concursos - maior peso
            5: 0.25,      # Últimos 5 concursos
            10: 0.20,     # Últimos 10 concursos
            15: 0.10,     # Últimos 15 concursos
            30: 0.07,     # Últimos 30 concursos
            'total': 0.03 # Histórico total - menor peso
        }
        
        parametros = ['n1', 'n15', 'maior_que_ultimo', 'menor_que_ultimo', 
                     'qtde_6_a_25', 'qtde_6_a_20', 'melhores_posicoes']
        
        for param in parametros:
            valor_ponderado = 0
            peso_total = 0
            
            # Combina análises de todas as janelas com pesos
            for janela, peso in pesos.items():
                if janela in self.analises and param in self.analises[janela]:
                    analise = self.analises[janela][param]
                    
                    # Estratégia: moda para valores discretos, mediana para tendência
                    if analise['estabilidade'] > 0.7:
                        valor_janela = analise['moda']
                    elif analise['tendencia'] == 'crescente':
                        valor_janela = min(analise['max'], analise['moda'] + 1)
                    elif analise['tendencia'] == 'decrescente':
                        valor_janela = max(analise['min'], analise['moda'] - 1)
                    else:
                        valor_janela = analise['mediana']
                    
                    valor_ponderado += valor_janela * peso
                    peso_total += peso
            
            if peso_total > 0:
                parametros_otimos[param] = round(valor_ponderado / peso_total)
            else:
                # Fallback para valores padrão
                parametros_otimos[param] = self._valor_padrao(param)
        
        # VALIDAÇÃO CRÍTICA: maior_que + menor_que + igual = 15
        if ('maior_que_ultimo' in parametros_otimos and 
            'menor_que_ultimo' in parametros_otimos):
            
            maior_que = parametros_otimos['maior_que_ultimo']
            menor_que = parametros_otimos['menor_que_ultimo']
            igual_ao = 15 - maior_que - menor_que
            
            # Garante que igual_ao está em faixa válida (0-3)
            if igual_ao < 0:
                # Reduz maior_que ou menor_que
                if maior_que > menor_que:
                    parametros_otimos['maior_que_ultimo'] = maior_que + igual_ao
                    igual_ao = 0
                else:
                    parametros_otimos['menor_que_ultimo'] = menor_que + igual_ao
                    igual_ao = 0
            elif igual_ao > 3:
                # Aumenta maior_que e/ou menor_que
                excesso = igual_ao - 3
                if excesso <= 3:
                    parametros_otimos['maior_que_ultimo'] += excesso // 2
                    parametros_otimos['menor_que_ultimo'] += (excesso + 1) // 2
                    igual_ao = 3
                else:
                    # Ajuste mais drástico
                    parametros_otimos['maior_que_ultimo'] = 8
                    parametros_otimos['menor_que_ultimo'] = 6
                    igual_ao = 1
            
            parametros_otimos['igual_ao_ultimo'] = igual_ao
            
            print(f"[VALIDACAO] Soma dos parâmetros: {parametros_otimos['maior_que_ultimo']} + {parametros_otimos['menor_que_ultimo']} + {igual_ao} = {parametros_otimos['maior_que_ultimo'] + parametros_otimos['menor_que_ultimo'] + igual_ao}")
        
        self.predicoes = parametros_otimos
        
        print(f"[CALCULADO] Parâmetros ótimos para próximo concurso:")
        for param, valor in parametros_otimos.items():
            print(f"   {param}: {valor}")
        
        return parametros_otimos
    
    def _valor_padrao(self, parametro: str) -> int:
        """Retorna valor padrão para parâmetro"""
        padroes = {
            'n1': 2,
            'n15': 25,
            'maior_que_ultimo': 8,
            'menor_que_ultimo': 6,
            'qtde_6_a_25': 13,
            'qtde_6_a_20': 9,
            'melhores_posicoes': 7
        }
        return padroes.get(parametro, 0)
    
    def gerar_query_dinamica(self, parametros_otimos: Dict[str, int] = None) -> str:
        """
        Gera query SQL com parâmetros otimizados dinamicamente
        """
        if not parametros_otimos:
            parametros_otimos = self.predicoes
        
        if not parametros_otimos:
            parametros_otimos = self.calcular_parametros_otimos()
        
        # Template da query com parâmetros dinâmicos
        query = f"""
        SELECT *
        FROM COMBINACOES_LOTOFACIL
        WHERE
            QtdePrimos in (2,3,4,5,6,7,8) 
            AND QtdeFibonacci in (2,3,4,5,6) 
            AND QtdeImpares in (6,7,8,9,10) 
            AND QtdeRepetidos in (7,8,9,10) 
            AND Quintil1 in (1,2,3,4,5) 
            AND Quintil2 in (1,2,3,4,5) 
            AND Quintil3 in (1,2,3,4,5) 
            AND Quintil4 in (1,2,3,4,5) 
            AND Quintil5 in (1,2,3,4,5)
            AND seq in (6,7,8,9,10,11,12,13,14) 
            AND qtdeMultiplos3 in (3,4,5,6) 
            AND distanciaExtremos in (19,20,21,22,23,24)
            
            -- PARÂMETROS DINÂMICOS OTIMIZADOS:
            AND N1 IN ({parametros_otimos['n1']})
            AND N15 IN ({parametros_otimos['n15']})
            AND maior_que_ultimo IN ({parametros_otimos['maior_que_ultimo']})
            AND menor_que_ultimo IN ({parametros_otimos['menor_que_ultimo']})
            AND igual_ao_ultimo IN ({parametros_otimos.get('igual_ao_ultimo', 1)})
            
            -- Posições otimizadas
            AND n1 in (1,2,3,4,5) 
            AND n2 in (2,3,4,5,6,7) 
            AND n3 in (3,4,5,6,7,8) 
            AND n4 in (4,5,6,7,8,9,10) 
            AND n5 in (5,6,7,8,9,10,11) 
            AND n6 in (6,7,8,9,10,11,12,13) 
            AND n7 in (8,9,10,11,12,13,14,15)
            AND n8 in (9,10,11,12,13,14,15,16,17) 
            AND n9 in (11,12,13,14,15,16,17,18) 
            AND n10 in (12,13,14,15,16,17,18,19,20) 
            AND n11 in (14,15,16,17,18,19,20,21) 
            AND n12 in (16,17,18,19,20,21,22)
            AND n13 in (18,19,20,21,22,23) 
            AND n14 in (20,21,22,23,24) 
            AND n15 in (22,23,24,25)
            
            -- QTDE de 6 a 25 (DINÂMICO)
            AND (CASE WHEN 6 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 7 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 8 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 9 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 10 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 11 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 12 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 13 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 14 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 15 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 16 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 17 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 18 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 19 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 20 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 21 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 22 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 23 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 24 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 25 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END) IN ({parametros_otimos['qtde_6_a_25']})

            -- QTDE DE 6 a 20 (DINÂMICO)
            AND (CASE WHEN 6 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 7 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 8 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 9 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 10 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 11 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 12 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 13 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END +
                CASE WHEN 14 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 15 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 16 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 17 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 18 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 19 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END + 
                CASE WHEN 20 IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END) IN ({parametros_otimos['qtde_6_a_20']}) 
                        
            -- MELHORES NÚMEROS NA POSIÇÃO (DINÂMICO)
            AND (CASE WHEN  n1 IN (1) THEN 1 ELSE 0 END +
                CASE WHEN  n2 IN (2) THEN 1 ELSE 0 END +
                CASE WHEN  n3 IN (4) THEN 1 ELSE 0 END +
                CASE WHEN  n4 IN (6) THEN 1 ELSE 0 END +
                CASE WHEN  n5 IN (8) THEN 1 ELSE 0 END +
                CASE WHEN  n6 IN (9) THEN 1 ELSE 0 END +
                CASE WHEN  n7 IN (11) THEN 1 ELSE 0 END +
                CASE WHEN  n8 IN (13) THEN 1 ELSE 0 END +
                CASE WHEN  n9 IN (15) THEN 1 ELSE 0 END +
                CASE WHEN  n10 IN (16) THEN 1 ELSE 0 END +
                CASE WHEN  n11 IN (19) THEN 1 ELSE 0 END +
                CASE WHEN  n12 IN (20) THEN 1 ELSE 0 END +
                CASE WHEN  n13 IN (22) THEN 1 ELSE 0 END +
                CASE WHEN  n14 IN (24) THEN 1 ELSE 0 END +                                    
                CASE WHEN n15 IN (25) THEN 1 ELSE 0 END) IN ({parametros_otimos['melhores_posicoes']})

            AND SomaTotal < 210

        ORDER BY CRYPT_GEN_RANDOM(4)
        """
        
        return query.strip()
    
    def salvar_analise(self, caminho_arquivo: str = None):
        """Salva análises para arquivo JSON"""
        if not caminho_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_arquivo = f"analise_parametros_{timestamp}.json"
        
        dados_exportacao = {
            'analises': self.analises,
            'predicoes': self.predicoes,
            'meta': {
                'total_concursos': len(self.historico_completo),
                'janelas_analisadas': list(self.janelas_analise),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_exportacao, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"[SALVO] Análise salva em: {caminho_arquivo}")
        return caminho_arquivo
    
    def gerar_relatorio_detalhado(self):
        """Gera relatório detalhado das análises"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DETALHADO - ANÁLISE DE PARÂMETROS DINÂMICOS")
        print("="*80)
        
        for janela in self.janelas_analise:
            if janela not in self.analises:
                continue
                
            analise = self.analises[janela]
            print(f"\n🔍 JANELA: {janela} concursos")
            print("-" * 40)
            
            if 'meta' in analise:
                print(f"Período: {analise['meta']['periodo']}")
                print(f"Total concursos: {analise['meta']['total_concursos']}")
            
            for param in ['n1', 'n15', 'maior_que_ultimo', 'menor_que_ultimo', 
                         'qtde_6_a_25', 'qtde_6_a_20', 'melhores_posicoes']:
                if param in analise:
                    dados = analise[param]
                    print(f"\n  📈 {param.upper()}:")
                    print(f"     Média: {dados['media']:.1f} | Moda: {dados['moda']} | Mediana: {dados['mediana']}")
                    print(f"     Tendência: {dados['tendencia']} | Estabilidade: {dados['estabilidade']:.2f}")
                    print(f"     Variação: {dados['min']}-{dados['max']} | Desvio: {dados['desvio']:.1f}")
        
        print(f"\n🎯 PARÂMETROS ÓTIMOS CALCULADOS:")
        print("-" * 40)
        for param, valor in self.predicoes.items():
            print(f"   {param}: {valor}")
        
        print("\n✅ Análise completa!")

def main():
    """Função principal para teste"""
    print("🔍 ANALISADOR DE PARÂMETROS DINÂMICOS")
    print("="*50)
    
    # Cria analisador
    analisador = AnalisadorParametrosDinamicos()
    
    # Carrega dados (simulados para teste)
    analisador.carregar_historico()
    
    # Executa análises
    analisador.analisar_todas_janelas()
    
    # Calcula parâmetros ótimos
    parametros_otimos = analisador.calcular_parametros_otimos()
    
    # Gera query dinâmica
    print("\n📝 QUERY DINÂMICA GERADA:")
    print("-" * 50)
    query = analisador.gerar_query_dinamica()
    print(query[:500] + "...")
    
    # Gera relatório
    analisador.gerar_relatorio_detalhado()
    
    # Salva análise
    analisador.salvar_analise()

if __name__ == "__main__":
    main()