#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILTRO DE RETORNO GARANTIDO - COMBO 20
======================================
Filtra combinações para selecionar apenas aquelas com 
maior probabilidade de garantir ≥11 acertos.

Estratégias de filtragem:
1. Por intersecção com últimos resultados
2. Por cobertura do núcleo comum
3. Por frequência dos números escolhidos
4. Por padrão de divergentes

Autor: LotoScope AI
Data: Janeiro 2026
"""

import pyodbc
from collections import Counter
from typing import List, Dict, Set, Tuple
from datetime import datetime
from itertools import combinations
import os


class FiltroRetornoGarantido:
    """
    Filtra combinações para maximizar probabilidade de retorno garantido.
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
        self.ultimo_resultado = None
        self.frequencias = {}
        
    def conectar_banco(self):
        """Conecta ao banco de dados."""
        return pyodbc.connect(self.conn_str)
    
    def carregar_resultados(self, ultimos_n: int = 100) -> int:
        """Carrega os últimos N resultados."""
        with self.conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT TOP {ultimos_n} Concurso, 
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
        
        if self.resultados:
            self.ultimo_resultado = self.resultados[0]
        
        # Calcular frequências
        self.frequencias = Counter()
        for _, nums in self.resultados:
            self.frequencias.update(nums)
        
        return len(self.resultados)
    
    def carregar_combinacoes_arquivo(self, arquivo: str) -> List[List[int]]:
        """
        Carrega combinações de um arquivo TXT.
        
        Args:
            arquivo: Caminho do arquivo
            
        Returns:
            Lista de combinações
        """
        combinacoes = []
        
        with open(arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#'):
                    try:
                        nums = [int(n) for n in linha.split(',')]
                        if len(nums) == 15:
                            combinacoes.append(nums)
                    except:
                        continue
        
        return combinacoes
    
    def calcular_score_combinacao(self, combo: List[int]) -> Dict:
        """
        Calcula o score de uma combinação baseado em múltiplos critérios.
        
        Args:
            combo: Lista de 15 números
            
        Returns:
            Dicionário com scores e métricas
        """
        combo_set = set(combo)
        nucleo_set = set(self.NUCLEO)
        
        # 1. Cobertura do núcleo (quantos do núcleo estão na combo)
        nucleo_na_combo = len(combo_set & nucleo_set)
        
        # 2. Intersecção com últimos resultados
        intersecoes = []
        for _, resultado in self.resultados[:10]:  # Últimos 10
            intersecoes.append(len(combo_set & resultado))
        
        media_intersecao = sum(intersecoes) / len(intersecoes) if intersecoes else 0
        min_intersecao = min(intersecoes) if intersecoes else 0
        max_intersecao = max(intersecoes) if intersecoes else 0
        
        # 3. Score de frequência (números quentes)
        score_frequencia = sum(self.frequencias.get(n, 0) for n in combo)
        max_freq = max(self.frequencias.values()) if self.frequencias else 1
        score_frequencia_norm = score_frequencia / (15 * max_freq)
        
        # 4. Divergentes usados
        div_c1_usados = len(combo_set & set(self.DIV_C1))
        div_c2_usados = len(combo_set & set(self.DIV_C2))
        
        # 5. Probabilidade estimada de ≥11 acertos
        # Baseado na cobertura do núcleo e frequências
        prob_11_mais = self._estimar_probabilidade_11(combo_set)
        
        # 6. Score composto
        score_total = (
            nucleo_na_combo * 10 +           # Peso alto para núcleo
            media_intersecao * 5 +            # Peso médio para intersecção
            min_intersecao * 8 +              # Peso alto para mínimo (garantia)
            score_frequencia_norm * 20 +      # Peso para números quentes
            prob_11_mais * 50                 # Peso máximo para probabilidade
        )
        
        return {
            'combinacao': combo,
            'nucleo_cobertura': nucleo_na_combo,
            'media_intersecao': media_intersecao,
            'min_intersecao': min_intersecao,
            'max_intersecao': max_intersecao,
            'score_frequencia': score_frequencia_norm,
            'div_c1': div_c1_usados,
            'div_c2': div_c2_usados,
            'prob_11_mais': prob_11_mais,
            'score_total': score_total
        }
    
    def _estimar_probabilidade_11(self, combo_set: Set[int]) -> float:
        """
        Estima a probabilidade de conseguir ≥11 acertos.
        Baseado no histórico de interseções.
        """
        if not self.resultados:
            return 0.5
        
        acertos_11_mais = 0
        total = len(self.resultados)
        
        for _, resultado in self.resultados:
            if len(combo_set & resultado) >= 11:
                acertos_11_mais += 1
        
        return acertos_11_mais / total
    
    def filtrar_por_nucleo_minimo(self, combinacoes: List[List[int]], 
                                   min_nucleo: int = 12) -> List[List[int]]:
        """
        Filtra combinações que têm pelo menos N números do núcleo.
        
        Combinações com mais números do núcleo têm maior chance
        de garantir retorno quando o resultado favorece o núcleo.
        
        Args:
            combinacoes: Lista de combinações
            min_nucleo: Mínimo de números do núcleo
            
        Returns:
            Combinações filtradas
        """
        nucleo_set = set(self.NUCLEO)
        filtradas = []
        
        for combo in combinacoes:
            combo_set = set(combo)
            if len(combo_set & nucleo_set) >= min_nucleo:
                filtradas.append(combo)
        
        return filtradas
    
    def filtrar_por_intersecao_minima(self, combinacoes: List[List[int]],
                                       min_intersecao: int = 11,
                                       ultimos_n: int = 5) -> List[List[int]]:
        """
        Filtra combinações que têm intersecção mínima garantida
        com os últimos N resultados.
        
        Essa é a filtragem mais conservadora - garante que
        a combinação teria premiado nos últimos jogos.
        
        Args:
            combinacoes: Lista de combinações
            min_intersecao: Mínimo de intersecção com cada resultado
            ultimos_n: Considerar os últimos N resultados
            
        Returns:
            Combinações filtradas
        """
        if not self.resultados:
            self.carregar_resultados()
        
        ultimos = [r for _, r in self.resultados[:ultimos_n]]
        filtradas = []
        
        for combo in combinacoes:
            combo_set = set(combo)
            
            # Verificar intersecção com cada resultado
            todas_ok = True
            for resultado in ultimos:
                if len(combo_set & resultado) < min_intersecao:
                    todas_ok = False
                    break
            
            if todas_ok:
                filtradas.append(combo)
        
        return filtradas
    
    def filtrar_por_frequencia(self, combinacoes: List[List[int]],
                                percentil: float = 0.7) -> List[List[int]]:
        """
        Filtra combinações com números mais frequentes (quentes).
        
        Args:
            combinacoes: Lista de combinações
            percentil: Manter top X% por frequência
            
        Returns:
            Combinações filtradas
        """
        if not self.frequencias:
            self.carregar_resultados()
        
        # Calcular score de frequência para cada combo
        scores = []
        for combo in combinacoes:
            score = sum(self.frequencias.get(n, 0) for n in combo)
            scores.append((combo, score))
        
        # Ordenar por score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Manter top percentil
        n_manter = int(len(scores) * percentil)
        return [combo for combo, _ in scores[:n_manter]]
    
    def filtrar_por_probabilidade(self, combinacoes: List[List[int]],
                                    min_prob: float = 0.4) -> List[List[int]]:
        """
        Filtra combinações com probabilidade mínima de ≥11 acertos.
        
        Args:
            combinacoes: Lista de combinações
            min_prob: Probabilidade mínima (0-1)
            
        Returns:
            Combinações filtradas
        """
        if not self.resultados:
            self.carregar_resultados()
        
        filtradas = []
        
        for combo in combinacoes:
            combo_set = set(combo)
            prob = self._estimar_probabilidade_11(combo_set)
            
            if prob >= min_prob:
                filtradas.append(combo)
        
        return filtradas
    
    def filtrar_top_score(self, combinacoes: List[List[int]],
                          top_n: int = None,
                          top_percentil: float = None) -> List[Dict]:
        """
        Retorna as combinações com melhor score total.
        
        Args:
            combinacoes: Lista de combinações
            top_n: Retornar top N (se especificado)
            top_percentil: Retornar top X% (se top_n não especificado)
            
        Returns:
            Lista de dicionários com combinação e métricas
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print(f"\n   Calculando scores para {len(combinacoes):,} combinações...")
        
        # Calcular score de todas
        scores = []
        for i, combo in enumerate(combinacoes):
            if i % 50000 == 0 and i > 0:
                print(f"   ... {i:,} processadas")
            scores.append(self.calcular_score_combinacao(combo))
        
        # Ordenar por score total
        scores.sort(key=lambda x: x['score_total'], reverse=True)
        
        # Determinar quantos retornar
        if top_n:
            return scores[:top_n]
        elif top_percentil:
            n_manter = int(len(scores) * top_percentil)
            return scores[:n_manter]
        else:
            return scores
    
    def aplicar_filtros_cascata(self, combinacoes: List[List[int]],
                                 filtros: Dict = None) -> Tuple[List[List[int]], Dict]:
        """
        Aplica múltiplos filtros em cascata para reduzir progressivamente.
        
        Args:
            combinacoes: Lista de combinações original
            filtros: Dicionário com parâmetros dos filtros
            
        Returns:
            Tuple (combinações filtradas, estatísticas)
        """
        if filtros is None:
            # Filtros calibrados - sem probabilidade pois é muito restritiva
            filtros = {
                'nucleo_minimo': 13,           # 13+ números do núcleo
                'frequencia_percentil': 0.20,  # Top 20% por frequência
                # probabilidade removida - usar score total ao invés
            }
        
        stats = {'original': len(combinacoes)}
        resultado = combinacoes
        
        print(f"\n   APLICANDO FILTROS EM CASCATA")
        print(f"   Original: {len(combinacoes):,} combinações")
        print("   " + "-" * 50)
        
        # Filtro 1: Núcleo mínimo
        if 'nucleo_minimo' in filtros:
            resultado = self.filtrar_por_nucleo_minimo(resultado, filtros['nucleo_minimo'])
            stats['apos_nucleo'] = len(resultado)
            print(f"   Após núcleo ≥{filtros['nucleo_minimo']}: {len(resultado):,}")
        
        # Filtro 2: Frequência
        if 'frequencia_percentil' in filtros and len(resultado) > 0:
            resultado = self.filtrar_por_frequencia(resultado, filtros['frequencia_percentil'])
            stats['apos_frequencia'] = len(resultado)
            print(f"   Após top {filtros['frequencia_percentil']*100:.0f}% frequência: {len(resultado):,}")
        
        # Filtro 3: Probabilidade
        if 'probabilidade_minima' in filtros and len(resultado) > 0:
            resultado = self.filtrar_por_probabilidade(resultado, filtros['probabilidade_minima'])
            stats['apos_probabilidade'] = len(resultado)
            print(f"   Após prob ≥{filtros['probabilidade_minima']*100:.0f}%: {len(resultado):,}")
        
        reducao = (1 - len(resultado) / len(combinacoes)) * 100 if combinacoes else 0
        stats['final'] = len(resultado)
        stats['reducao_%'] = reducao
        
        print("   " + "-" * 50)
        print(f"   RESULTADO: {len(resultado):,} combinações ({reducao:.1f}% reduzidas)")
        
        return resultado, stats
    
    def salvar_combinacoes(self, combinacoes: List, arquivo: str = None,
                           incluir_scores: bool = False):
        """
        Salva as combinações filtradas em arquivo.
        
        Args:
            combinacoes: Lista de combinações ou dicionários com scores
            arquivo: Nome do arquivo
            incluir_scores: Se True, inclui métricas no arquivo
        """
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"combo20_filtradas_{timestamp}.txt"
        
        with open(arquivo, 'w') as f:
            f.write(f"# COMBINAÇÕES FILTRADAS - RETORNO GARANTIDO\n")
            f.write(f"# Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"# Total: {len(combinacoes)} combinações\n")
            
            if self.ultimo_resultado:
                f.write(f"# Baseado no concurso: {self.ultimo_resultado[0]}\n")
            
            f.write("\n")
            
            for item in combinacoes:
                if isinstance(item, dict):
                    combo = item['combinacao']
                    if incluir_scores:
                        f.write(f"# Score: {item['score_total']:.2f} | ")
                        f.write(f"Prob≥11: {item['prob_11_mais']*100:.1f}% | ")
                        f.write(f"Núcleo: {item['nucleo_cobertura']}/17\n")
                else:
                    combo = item
                
                f.write(','.join(map(str, combo)) + '\n')
        
        print(f"\n   Salvo em: {arquivo}")
        return arquivo
    
    def analisar_e_filtrar_arquivo(self, arquivo_entrada: str,
                                    filtros: Dict = None,
                                    salvar: bool = True) -> Tuple[List, Dict]:
        """
        Carrega arquivo, aplica filtros e salva resultado.
        
        Args:
            arquivo_entrada: Arquivo com combinações originais
            filtros: Parâmetros dos filtros
            salvar: Se True, salva o resultado
            
        Returns:
            Tuple (combinações filtradas, estatísticas)
        """
        print("\n" + "=" * 70)
        print("   FILTRO DE RETORNO GARANTIDO - COMBO 20")
        print("=" * 70)
        
        # Carregar dados
        print(f"\n   Carregando resultados históricos...")
        n_resultados = self.carregar_resultados(100)
        print(f"   {n_resultados} resultados carregados")
        
        print(f"\n   Carregando combinações de: {arquivo_entrada}")
        combinacoes = self.carregar_combinacoes_arquivo(arquivo_entrada)
        print(f"   {len(combinacoes):,} combinações carregadas")
        
        # Aplicar filtros
        filtradas, stats = self.aplicar_filtros_cascata(combinacoes, filtros)
        
        # Calcular scores das filtradas
        if filtradas:
            print(f"\n   Calculando scores das {len(filtradas):,} filtradas...")
            top_scores = self.filtrar_top_score(filtradas, top_n=min(1000, len(filtradas)))
            
            # Mostrar top 10
            print("\n   TOP 10 COMBINAÇÕES:")
            print("   " + "-" * 65)
            print("   #   Score   Prob≥11  Núcleo  MédiaInt  Combinação")
            print("   " + "-" * 65)
            
            for i, item in enumerate(top_scores[:10], 1):
                combo_str = ','.join(f'{n:02d}' for n in item['combinacao'][:5]) + "..."
                print(f"   {i:2d}  {item['score_total']:6.1f}  {item['prob_11_mais']*100:5.1f}%   "
                      f"{item['nucleo_cobertura']:2d}/17   {item['media_intersecao']:5.2f}    {combo_str}")
            
            if salvar:
                # Salvar filtradas com scores
                nome_base = os.path.splitext(arquivo_entrada)[0]
                arquivo_saida = f"{nome_base}_FILTRADAS.txt"
                self.salvar_combinacoes(top_scores, arquivo_saida, incluir_scores=True)
                
                stats['arquivo_saida'] = arquivo_saida
        
        return filtradas, stats
    
    def gerar_combinacoes_otimas(self, quantidade: int = 100) -> List[Dict]:
        """
        Gera combinações otimizadas do zero, focando em maximizar
        a probabilidade de ≥11 acertos.
        
        Args:
            quantidade: Número de combinações a gerar
            
        Returns:
            Lista de combinações com scores
        """
        if not self.resultados:
            self.carregar_resultados()
        
        print(f"\n   Gerando {quantidade} combinações otimizadas...")
        print(f"   Estratégia: Maximizar cobertura do núcleo + números quentes")
        
        # Identificar os números mais frequentes do núcleo
        nucleo_freq = [(n, self.frequencias.get(n, 0)) for n in self.NUCLEO]
        nucleo_freq.sort(key=lambda x: x[1], reverse=True)
        
        # Top 12 do núcleo (garantir boa cobertura)
        top_nucleo = [n for n, _ in nucleo_freq[:12]]
        
        # Divergentes mais frequentes
        div_c1_freq = [(n, self.frequencias.get(n, 0)) for n in self.DIV_C1]
        div_c2_freq = [(n, self.frequencias.get(n, 0)) for n in self.DIV_C2]
        
        print(f"   Top 12 do núcleo: {top_nucleo}")
        print(f"   Divergentes C1 (freq): {div_c1_freq}")
        print(f"   Divergentes C2 (freq): {div_c2_freq}")
        
        combinacoes = []
        
        # Estratégia: combinar top_nucleo com variações de divergentes
        # e completar com os demais números do núcleo
        
        restante_nucleo = [n for n, _ in nucleo_freq[12:]]
        
        for _ in range(quantidade):
            combo = set(top_nucleo.copy())  # 12 números base
            
            # Adicionar 1-2 divergentes de cada grupo (os mais frequentes)
            import random
            
            # Selecionar divergentes
            n_div_c1 = random.randint(1, 2)
            n_div_c2 = random.randint(1, 2)
            
            divs_c1 = sorted(self.DIV_C1, key=lambda x: self.frequencias.get(x, 0), reverse=True)
            divs_c2 = sorted(self.DIV_C2, key=lambda x: self.frequencias.get(x, 0), reverse=True)
            
            combo.update(divs_c1[:n_div_c1])
            combo.update(divs_c2[:n_div_c2])
            
            # Completar com restante do núcleo se necessário
            faltam = 15 - len(combo)
            if faltam > 0:
                disponiveis = [n for n in restante_nucleo if n not in combo]
                combo.update(random.sample(disponiveis, min(faltam, len(disponiveis))))
            
            # Se ainda faltar, adicionar qualquer número disponível
            if len(combo) < 15:
                todos = list(range(1, 26))
                disponiveis = [n for n in todos if n not in combo]
                faltam = 15 - len(combo)
                combo.update(random.sample(disponiveis, faltam))
            
            combo_list = sorted(list(combo))[:15]
            if combo_list not in [c['combinacao'] for c in combinacoes]:
                score_info = self.calcular_score_combinacao(combo_list)
                combinacoes.append(score_info)
        
        # Ordenar por score
        combinacoes.sort(key=lambda x: x['score_total'], reverse=True)
        
        return combinacoes


def menu_interativo():
    """Menu interativo para filtragem."""
    filtro = FiltroRetornoGarantido()
    
    while True:
        print("\n" + "=" * 60)
        print("   FILTRO DE RETORNO GARANTIDO - COMBO 20")
        print("=" * 60)
        print("\n   1. Filtrar arquivo de combinações")
        print("   2. Gerar combinações otimizadas")
        print("   3. Filtrar com parâmetros personalizados")
        print("   4. Analisar arquivo (sem filtrar)")
        print("   0. Sair")
        
        opcao = input("\n   Escolha: ").strip()
        
        if opcao == '0':
            break
            
        elif opcao == '1':
            arquivo = input("   Arquivo de entrada: ").strip()
            if os.path.exists(arquivo):
                filtro.analisar_e_filtrar_arquivo(arquivo)
            else:
                print(f"   Arquivo não encontrado: {arquivo}")
                
        elif opcao == '2':
            n = input("   Quantas combinações? [100]: ").strip()
            n = int(n) if n else 100
            
            filtro.carregar_resultados()
            combos = filtro.gerar_combinacoes_otimas(n)
            
            print(f"\n   Geradas {len(combos)} combinações otimizadas")
            
            salvar = input("   Salvar? (s/n) [s]: ").strip().lower()
            if salvar != 'n':
                filtro.salvar_combinacoes(combos, incluir_scores=True)
                
        elif opcao == '3':
            arquivo = input("   Arquivo de entrada: ").strip()
            if not os.path.exists(arquivo):
                print(f"   Arquivo não encontrado: {arquivo}")
                continue
            
            print("\n   Configure os filtros:")
            nucleo = input("   Núcleo mínimo [12]: ").strip()
            nucleo = int(nucleo) if nucleo else 12
            
            freq = input("   Percentil frequência (0-1) [0.5]: ").strip()
            freq = float(freq) if freq else 0.5
            
            prob = input("   Probabilidade mínima (0-1) [0.35]: ").strip()
            prob = float(prob) if prob else 0.35
            
            filtros = {
                'nucleo_minimo': nucleo,
                'frequencia_percentil': freq,
                'probabilidade_minima': prob
            }
            
            filtro.analisar_e_filtrar_arquivo(arquivo, filtros)
            
        elif opcao == '4':
            arquivo = input("   Arquivo para analisar: ").strip()
            if os.path.exists(arquivo):
                filtro.carregar_resultados()
                combos = filtro.carregar_combinacoes_arquivo(arquivo)
                
                print(f"\n   Analisando {len(combos):,} combinações...")
                
                # Calcular scores de uma amostra
                amostra = combos[:1000] if len(combos) > 1000 else combos
                scores = [filtro.calcular_score_combinacao(c) for c in amostra]
                
                probs = [s['prob_11_mais'] for s in scores]
                nucleos = [s['nucleo_cobertura'] for s in scores]
                
                print(f"\n   ANÁLISE DA AMOSTRA ({len(amostra)} combos):")
                print(f"   Prob ≥11 média: {sum(probs)/len(probs)*100:.1f}%")
                print(f"   Núcleo médio: {sum(nucleos)/len(nucleos):.1f}/17")
                print(f"   Score médio: {sum(s['score_total'] for s in scores)/len(scores):.1f}")
            else:
                print(f"   Arquivo não encontrado: {arquivo}")
        
        input("\n   Pressione ENTER para continuar...")


if __name__ == "__main__":
    menu_interativo()
