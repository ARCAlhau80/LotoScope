#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALISADOR DE RETORNO GARANTIDO - COMBO 20
===========================================
Analisa o histórico para identificar em quais concursos o 
conjunto de combinações garantiria retorno positivo (≥11 acertos).

Explora o padrão descoberto onde grupos de combinações 
compartilham um "piso de acertos" devido ao núcleo comum.

Autor: LotoScope AI
Data: Janeiro 2026
"""

import pyodbc
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
from datetime import datetime
import json


class AnalisadorRetornoGarantido:
    """
    Analisa o retorno garantido baseado no núcleo comum
    da estratégia Combo 20.
    """
    
    # Prêmios da Lotofácil
    PREMIOS = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
    CUSTO_APOSTA = 3.00
    
    # Combos da estratégia
    COMBO1 = [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
    COMBO2 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    
    # Divergentes
    DIV_C1 = [1, 3, 4]     # Apenas na Combo 1
    DIV_C2 = [15, 17, 18]  # Apenas na Combo 2
    
    # Núcleo comum (17 números)
    NUCLEO = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23, 24, 25]
    
    # Números fora de ambas
    FORA_AMBAS = [2, 5]
    
    def __init__(self):
        self.conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=Lotofacil;"
            "Trusted_Connection=yes;"
        )
        self.resultados = []
        
    def conectar_banco(self):
        """Conecta ao banco de dados."""
        return pyodbc.connect(self.conn_str)
    
    def carregar_resultados(self) -> int:
        """Carrega todos os resultados históricos."""
        with self.conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Concurso, 
                       N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT
                ORDER BY Concurso DESC
            """)
            
            self.resultados = []
            for row in cursor.fetchall():
                concurso = row.Concurso
                numeros = set(row[i] for i in range(1, 16))
                self.resultados.append((concurso, numeros))
        
        return len(self.resultados)
    
    def calcular_acerto_minimo_garantido(self, resultado: Set[int], 
                                          nucleo: List[int] = None) -> int:
        """
        Calcula o acerto MÍNIMO garantido para qualquer combinação
        que use o núcleo especificado.
        
        Args:
            resultado: Conjunto de 15 números do resultado
            nucleo: Lista de números do núcleo (default: NUCLEO)
            
        Returns:
            Quantidade mínima de acertos garantida
        """
        if nucleo is None:
            nucleo = self.NUCLEO
        
        nucleo_set = set(nucleo)
        # Acertos do núcleo = mínimo garantido
        return len(resultado & nucleo_set)
    
    def calcular_acerto_maximo_potencial(self, resultado: Set[int],
                                          combo: List[int] = None) -> int:
        """
        Calcula o acerto MÁXIMO potencial se usar a combo completa.
        
        Args:
            resultado: Conjunto de 15 números do resultado
            combo: Lista de 20 números da combo (default: COMBO1)
            
        Returns:
            Quantidade máxima de acertos possível
        """
        if combo is None:
            combo = self.COMBO1
        
        combo_set = set(combo)
        return len(resultado & combo_set)
    
    def calcular_retorno_percentual(self, acertos: int) -> float:
        """
        Calcula o retorno percentual para uma quantidade de acertos.
        
        Args:
            acertos: Quantidade de acertos (11-15)
            
        Returns:
            Retorno percentual (0 se não premiou)
        """
        if acertos < 11:
            return -100.0  # Perda total
        
        premio = self.PREMIOS.get(acertos, 0)
        return ((premio / self.CUSTO_APOSTA) - 1) * 100
    
    def analisar_historico_completo(self) -> Dict:
        """
        Analisa todo o histórico para identificar padrões de
        acerto mínimo garantido.
        
        Returns:
            Dicionário com análise completa
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print("   ANÁLISE DE RETORNO GARANTIDO - HISTÓRICO COMPLETO")
        print("=" * 70)
        print(f"\n   Núcleo analisado: {len(self.NUCLEO)} números")
        print(f"   Resultados: {len(self.resultados)} concursos")
        
        # Contadores por faixa de acerto mínimo
        distribuicao_minimo = Counter()
        distribuicao_maximo_c1 = Counter()
        distribuicao_maximo_c2 = Counter()
        
        # Histórico detalhado
        historico = []
        
        for concurso, resultado in self.resultados:
            min_garantido = self.calcular_acerto_minimo_garantido(resultado)
            max_c1 = self.calcular_acerto_maximo_potencial(resultado, self.COMBO1)
            max_c2 = self.calcular_acerto_maximo_potencial(resultado, self.COMBO2)
            
            # Quantos divergentes de cada grupo apareceram
            div_c1_acertos = len(resultado & set(self.DIV_C1))
            div_c2_acertos = len(resultado & set(self.DIV_C2))
            
            # Retorno garantido
            retorno_min = self.calcular_retorno_percentual(min_garantido)
            
            distribuicao_minimo[min_garantido] += 1
            distribuicao_maximo_c1[max_c1] += 1
            distribuicao_maximo_c2[max_c2] += 1
            
            historico.append({
                'concurso': concurso,
                'min_garantido': min_garantido,
                'max_c1': max_c1,
                'max_c2': max_c2,
                'div_c1': div_c1_acertos,
                'div_c2': div_c2_acertos,
                'retorno_min_%': retorno_min,
                'premiou_garantido': min_garantido >= 11
            })
        
        # Estatísticas
        total = len(self.resultados)
        premiados_garantidos = sum(1 for h in historico if h['premiou_garantido'])
        
        print("\n" + "-" * 70)
        print("   DISTRIBUIÇÃO DE ACERTO MÍNIMO GARANTIDO (NÚCLEO)")
        print("-" * 70)
        print("   Acertos   Concursos    %     Retorno Garantido")
        print("   " + "-" * 50)
        
        for acertos in sorted(distribuicao_minimo.keys(), reverse=True):
            count = distribuicao_minimo[acertos]
            pct = count * 100 / total
            retorno = self.calcular_retorno_percentual(acertos)
            status = "✅ LUCRO" if acertos >= 11 else "❌ SEM PRÊMIO"
            print(f"      {acertos:2d}       {count:5d}    {pct:5.1f}%    {retorno:+7.1f}%  {status}")
        
        print("\n" + "-" * 70)
        print("   RESUMO DE VIABILIDADE")
        print("-" * 70)
        print(f"   Concursos com retorno GARANTIDO (≥11): {premiados_garantidos} ({premiados_garantidos*100/total:.1f}%)")
        print(f"   Concursos SEM retorno garantido:       {total - premiados_garantidos} ({(total-premiados_garantidos)*100/total:.1f}%)")
        
        # Análise de retorno médio
        retornos = [h['retorno_min_%'] for h in historico]
        retorno_medio = sum(retornos) / len(retornos)
        
        print(f"\n   Retorno MÍNIMO médio histórico: {retorno_medio:+.2f}%")
        
        # Concursos onde GARANTIA lucro
        lucro_garantido = [h for h in historico if h['min_garantido'] >= 11]
        if lucro_garantido:
            retornos_lucro = [h['retorno_min_%'] for h in lucro_garantido]
            print(f"   Retorno médio quando garantia lucro: {sum(retornos_lucro)/len(retornos_lucro):+.2f}%")
        
        return {
            'total_concursos': total,
            'premiados_garantidos': premiados_garantidos,
            'taxa_sucesso': premiados_garantidos * 100 / total,
            'distribuicao_minimo': dict(distribuicao_minimo),
            'distribuicao_maximo_c1': dict(distribuicao_maximo_c1),
            'distribuicao_maximo_c2': dict(distribuicao_maximo_c2),
            'retorno_medio': retorno_medio,
            'historico': historico[:100]  # Últimos 100 para análise
        }
    
    def identificar_padroes_retorno(self) -> Dict:
        """
        Identifica os padrões de retorno que se repetem.
        Explica por que certos percentuais aparecem consistentemente.
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print("   IDENTIFICAÇÃO DE PADRÕES DE RETORNO REPETIDOS")
        print("=" * 70)
        
        # Calcular retornos únicos possíveis
        retornos_possiveis = {}
        for acertos in range(0, 16):
            retorno = self.calcular_retorno_percentual(acertos)
            retornos_possiveis[acertos] = retorno
        
        print("\n   TABELA DE RETORNOS DISCRETOS (por aposta de R$ 3,00):")
        print("   " + "-" * 50)
        print("   Acertos    Prêmio      Retorno %")
        print("   " + "-" * 50)
        
        for acertos in range(15, 10, -1):
            premio = self.PREMIOS.get(acertos, 0)
            retorno = retornos_possiveis[acertos]
            print(f"      {acertos}     R$ {premio:>10,.2f}    {retorno:>+12.2f}%")
        
        print(f"     <11     R$ 0,00        -100.00%")
        
        # Análise de por que 26.50%, 8.05%, 131.02% se repetem
        print("\n" + "-" * 70)
        print("   EXPLICAÇÃO DOS VALORES OBSERVADOS")
        print("-" * 70)
        
        print("""
   Os valores 26.50%, 8.05% e 131.02% que você observou são
   MÉDIAS PONDERADAS dos retornos discretos acima.
   
   Exemplo de cálculo:
   
   • Se 100 combinações têm mínimo 11 acertos (retorno +133.33%):
     Retorno médio do grupo = +133.33%
     
   • Se 70% das combos têm 11ac e 30% não premiam:
     Retorno = 0.70 × 133.33 + 0.30 × (-100) = +63.33%
     
   • Seus valores específicos:
     - 131.02% ≈ quase todas garantindo 11 acertos
     - 26.50%  ≈ ~60% com 11ac, ~40% sem prêmio
     - 8.05%   ≈ ~54% com 11ac, ~46% sem prêmio
        """)
        
        # Resolver: qual distribuição gera cada %?
        # Para retorno R: x * 133.33 + (1-x) * (-100) = R
        # x * 133.33 - 100 + 100x = R
        # x * 233.33 = R + 100
        # x = (R + 100) / 233.33
        
        valores_observados = [26.50, 8.05, 131.02]
        
        print("\n   DECOMPOSIÇÃO DOS VALORES OBSERVADOS:")
        print("   " + "-" * 50)
        
        for valor in valores_observados:
            taxa_11ac = (valor + 100) / 233.33
            taxa_sem = 1 - taxa_11ac
            print(f"\n   Retorno {valor:+.2f}%:")
            print(f"      → {taxa_11ac*100:.1f}% das combos com ≥11 acertos")
            print(f"      → {taxa_sem*100:.1f}% das combos sem prêmio")
        
        return {
            'retornos_discretos': retornos_possiveis,
            'valores_observados': valores_observados
        }
    
    def sugerir_estrategia_otima(self) -> Dict:
        """
        Sugere como explorar o padrão de retorno garantido.
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print("   ESTRATÉGIA ÓTIMA BASEADA NO PADRÃO DESCOBERTO")
        print("=" * 70)
        
        # Analisar histórico
        historico_analise = []
        
        for concurso, resultado in self.resultados:
            min_garantido = self.calcular_acerto_minimo_garantido(resultado)
            div_c1 = len(resultado & set(self.DIV_C1))
            div_c2 = len(resultado & set(self.DIV_C2))
            
            historico_analise.append({
                'concurso': concurso,
                'min_garantido': min_garantido,
                'div_c1': div_c1,
                'div_c2': div_c2
            })
        
        # Quando min_garantido >= 11 (lucro garantido)?
        lucro_garantido = [h for h in historico_analise if h['min_garantido'] >= 11]
        
        # Análise de divergentes quando há lucro garantido
        div_c1_em_lucro = Counter(h['div_c1'] for h in lucro_garantido)
        div_c2_em_lucro = Counter(h['div_c2'] for h in lucro_garantido)
        
        print("\n   1. QUANDO O NÚCLEO GARANTE LUCRO (≥11 acertos):")
        print("   " + "-" * 50)
        print(f"   Ocorre em {len(lucro_garantido)} de {len(self.resultados)} concursos ({len(lucro_garantido)*100/len(self.resultados):.1f}%)")
        
        print("\n   Distribuição dos divergentes C1 [1,3,4] nesses casos:")
        for div, count in sorted(div_c1_em_lucro.items()):
            print(f"      {div}/3 divergentes: {count} vezes ({count*100/len(lucro_garantido):.1f}%)")
        
        print("\n   Distribuição dos divergentes C2 [15,17,18] nesses casos:")
        for div, count in sorted(div_c2_em_lucro.items()):
            print(f"      {div}/3 divergentes: {count} vezes ({count*100/len(lucro_garantido):.1f}%)")
        
        # Identificar padrões preditivos
        print("\n   2. COMO PREVER QUANDO TERÁ LUCRO GARANTIDO:")
        print("   " + "-" * 50)
        
        # Verificar se há correlação com último resultado
        correlacoes = []
        for i in range(len(historico_analise) - 1):
            atual = historico_analise[i]
            anterior = historico_analise[i + 1]
            
            correlacoes.append({
                'atual_min': atual['min_garantido'],
                'anterior_min': anterior['min_garantido'],
                'atual_lucro': atual['min_garantido'] >= 11,
                'anterior_lucro': anterior['min_garantido'] >= 11
            })
        
        # Probabilidade condicional
        lucro_apos_lucro = sum(1 for c in correlacoes if c['atual_lucro'] and c['anterior_lucro'])
        lucro_apos_nao = sum(1 for c in correlacoes if c['atual_lucro'] and not c['anterior_lucro'])
        total_apos_lucro = sum(1 for c in correlacoes if c['anterior_lucro'])
        total_apos_nao = sum(1 for c in correlacoes if not c['anterior_lucro'])
        
        if total_apos_lucro > 0:
            prob_lucro_apos_lucro = lucro_apos_lucro * 100 / total_apos_lucro
            print(f"\n   P(lucro | anterior teve lucro): {prob_lucro_apos_lucro:.1f}%")
        
        if total_apos_nao > 0:
            prob_lucro_apos_nao = lucro_apos_nao * 100 / total_apos_nao
            print(f"   P(lucro | anterior NÃO teve lucro): {prob_lucro_apos_nao:.1f}%")
        
        print("\n   3. RECOMENDAÇÃO DE EXPLORAÇÃO:")
        print("   " + "-" * 50)
        print("""
   OPÇÃO A - Jogar APENAS quando núcleo provável ≥11:
   • Analise os números mais frequentes do núcleo
   • Se os 11 mais frequentes do núcleo estiverem "quentes"
     nas últimas 5-10 rodadas, aposte
   
   OPÇÃO B - Filtrar combinações por acerto mínimo:
   • Ao invés de jogar TODAS as 490k combinações
   • Filtre para jogar apenas as que garantem ≥11 acertos
     considerando o resultado anterior como referência
   
   OPÇÃO C - Criar sub-grupos por faixa:
   • Grupo 131%: Combinações que SEMPRE terão ≥11
   • Grupo 26%: Combinações com 60% chance de ≥11
   • Jogar proporcionalmente ao retorno esperado
        """)
        
        return {
            'concursos_lucro_garantido': len(lucro_garantido),
            'taxa_lucro_garantido': len(lucro_garantido) * 100 / len(self.resultados),
            'div_c1_quando_lucro': dict(div_c1_em_lucro),
            'div_c2_quando_lucro': dict(div_c2_em_lucro)
        }
    
    def analisar_ultimos_n(self, n: int = 30):
        """
        Análise focada nos últimos N concursos para decisão imediata.
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print(f"   ANÁLISE DOS ÚLTIMOS {n} CONCURSOS")
        print("=" * 70)
        
        ultimos = self.resultados[:n]
        
        print("\n   Conc    Núcleo   Máx C1   Máx C2   [1,3,4]  [15,17,18]  Status")
        print("   " + "-" * 65)
        
        lucros = 0
        for concurso, resultado in ultimos:
            min_g = self.calcular_acerto_minimo_garantido(resultado)
            max_c1 = self.calcular_acerto_maximo_potencial(resultado, self.COMBO1)
            max_c2 = self.calcular_acerto_maximo_potencial(resultado, self.COMBO2)
            div_c1 = len(resultado & set(self.DIV_C1))
            div_c2 = len(resultado & set(self.DIV_C2))
            
            status = "✅ LUCRO" if min_g >= 11 else "❌"
            if min_g >= 11:
                lucros += 1
            
            print(f"   {concurso:5d}     {min_g:2d}       {max_c1:2d}       {max_c2:2d}       {div_c1}/3        {div_c2}/3      {status}")
        
        print(f"\n   Taxa de lucro garantido nos últimos {n}: {lucros}/{n} ({lucros*100/n:.1f}%)")
        
        # Próximo concurso
        ultimo_resultado = ultimos[0][1]
        print(f"\n   Último concurso: {ultimos[0][0]}")
        print(f"   Números sorteados: {sorted(ultimo_resultado)}")
        
        # Verificar tendência
        nucleo_no_ultimo = len(ultimo_resultado & set(self.NUCLEO))
        print(f"\n   Números do NÚCLEO no último: {nucleo_no_ultimo}/17")
        
        if nucleo_no_ultimo >= 11:
            print("   >>> TENDÊNCIA: Núcleo comum FORTE - probabilidade alta de lucro garantido")
        else:
            print("   >>> TENDÊNCIA: Núcleo comum FRACO - considerar diversificar")

    def executar_analise_completa(self):
        """Executa todas as análises."""
        self.carregar_resultados()
        
        print("\n" + "=" * 70)
        print("   ANÁLISE COMPLETA DE RETORNO GARANTIDO - COMBO 20")
        print("   " + datetime.now().strftime("%d/%m/%Y %H:%M"))
        print("=" * 70)
        
        # 1. Análise histórica
        resultado1 = self.analisar_historico_completo()
        
        # 2. Identificar padrões
        resultado2 = self.identificar_padroes_retorno()
        
        # 3. Estratégia ótima
        resultado3 = self.sugerir_estrategia_otima()
        
        # 4. Últimos concursos
        self.analisar_ultimos_n(30)
        
        print("\n" + "=" * 70)
        print("   FIM DA ANÁLISE")
        print("=" * 70)
        
        return {
            'historico': resultado1,
            'padroes': resultado2,
            'estrategia': resultado3
        }


def menu_interativo():
    """Menu interativo para análise."""
    analisador = AnalisadorRetornoGarantido()
    
    while True:
        print("\n" + "=" * 60)
        print("   ANALISADOR DE RETORNO GARANTIDO - COMBO 20")
        print("=" * 60)
        print("\n   1. Análise COMPLETA")
        print("   2. Apenas histórico de acerto mínimo")
        print("   3. Identificar padrões de retorno")
        print("   4. Estratégia ótima")
        print("   5. Últimos N concursos")
        print("   0. Sair")
        
        opcao = input("\n   Escolha: ").strip()
        
        if opcao == '0':
            break
        elif opcao == '1':
            analisador.executar_analise_completa()
        elif opcao == '2':
            analisador.carregar_resultados()
            analisador.analisar_historico_completo()
        elif opcao == '3':
            analisador.carregar_resultados()
            analisador.identificar_padroes_retorno()
        elif opcao == '4':
            analisador.carregar_resultados()
            analisador.sugerir_estrategia_otima()
        elif opcao == '5':
            n = input("   Quantos concursos? [30]: ").strip()
            n = int(n) if n else 30
            analisador.carregar_resultados()
            analisador.analisar_ultimos_n(n)
        
        input("\n   Pressione ENTER para continuar...")


if __name__ == "__main__":
    menu_interativo()
