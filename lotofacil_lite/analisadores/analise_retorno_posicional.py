#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANALISE DE RETORNO POSICIONAL
==============================
Analisa padroes de retorno apos ausencia para cada posicao N1-N15.

PERGUNTA PRINCIPAL:
Quando o numero favorito de uma posicao NAO sai, qual a chance dele
voltar no proximo concurso vs continuar ausente?

METRICAS:
1. Taxa de retorno imediato (apos 1 ausencia)
2. Taxa de retorno apos N ausencias
3. Distribuicao de tempo de ausencia
4. Reversao a media vs Momentum

Autor: LotoScope AI
Data: Janeiro 2026
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter, defaultdict

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config


class AnaliseRetornoPosicional:
    """
    Analisa padroes de retorno apos ausencia para numeros favoritos
    em cada posicao N1-N15.
    """
    
    def __init__(self):
        self.db_config = db_config
        self.dados = []  # Lista de concursos com N1-N15
        self.favoritos = {}  # Numero mais frequente por posicao
        self.resultados = {}  # Resultados da analise
        
    def carregar_dados(self) -> bool:
        """Carrega todos os concursos ordenados"""
        print("[DATA] Carregando historico completo...")
        
        try:
            query = """
            SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso ASC
            """
            
            resultados = self.db_config.execute_query(query)
            
            for row in resultados:
                concurso = {
                    'num': row[0],
                    'posicoes': {i: row[i] for i in range(1, 16)}  # N1-N15
                }
                self.dados.append(concurso)
            
            print(f"   [OK] {len(self.dados)} concursos carregados")
            print(f"   [->] Primeiro: {self.dados[0]['num']} | Ultimo: {self.dados[-1]['num']}")
            
            return True
            
        except Exception as e:
            print(f"   [ERRO] {e}")
            return False
    
    def identificar_favoritos(self):
        """Identifica o numero mais frequente em cada posicao"""
        print("\n[FAV] Identificando numeros favoritos por posicao...")
        
        for pos in range(1, 16):
            contador = Counter()
            for d in self.dados:
                contador[d['posicoes'][pos]] += 1
            
            mais_comum = contador.most_common(1)[0]
            total = len(self.dados)
            
            self.favoritos[pos] = {
                'numero': mais_comum[0],
                'frequencia': mais_comum[1],
                'percentual': round(mais_comum[1] / total * 100, 1)
            }
        
        print("\n   Pos  | Num | Freq   | %")
        print("   " + "-" * 30)
        for pos in range(1, 16):
            f = self.favoritos[pos]
            print(f"   N{pos:02d} | {f['numero']:02d}  | {f['frequencia']:5d} | {f['percentual']:.1f}%")
    
    def analisar_retorno_apos_ausencia(self, posicao: int, numero: int) -> Dict:
        """
        Analisa padrao de retorno para um numero especifico em uma posicao.
        
        Retorna:
        - Taxa de retorno apos 1, 2, 3... ausencias
        - Distribuicao de duracao das ausencias
        - Media e mediana de tempo de ausencia
        """
        
        # Identificar todas as sequencias de ausencia
        ausencias = []
        ausencia_atual = 0
        retornos_por_duracao = defaultdict(lambda: {'retornou': 0, 'nao_retornou': 0})
        
        for i, d in enumerate(self.dados):
            valor_posicao = d['posicoes'][posicao]
            
            if valor_posicao == numero:
                # Numero saiu - se havia ausencia, ela terminou
                if ausencia_atual > 0:
                    ausencias.append(ausencia_atual)
                    ausencia_atual = 0
            else:
                # Numero NAO saiu - incrementa ausencia
                ausencia_atual += 1
                
                # Verificar proximo concurso (se existe)
                if i + 1 < len(self.dados):
                    proximo_valor = self.dados[i + 1]['posicoes'][posicao]
                    if proximo_valor == numero:
                        retornos_por_duracao[ausencia_atual]['retornou'] += 1
                    else:
                        retornos_por_duracao[ausencia_atual]['nao_retornou'] += 1
        
        # Se terminou em ausencia, registrar
        if ausencia_atual > 0:
            ausencias.append(ausencia_atual)
        
        # Calcular estatisticas
        if ausencias:
            media_ausencia = sum(ausencias) / len(ausencias)
            ausencias_ordenadas = sorted(ausencias)
            mediana = ausencias_ordenadas[len(ausencias_ordenadas) // 2]
            max_ausencia = max(ausencias)
        else:
            media_ausencia = 0
            mediana = 0
            max_ausencia = 0
        
        # Taxas de retorno por duracao
        taxas_retorno = {}
        for duracao in sorted(retornos_por_duracao.keys()):
            dados = retornos_por_duracao[duracao]
            total = dados['retornou'] + dados['nao_retornou']
            if total > 0:
                taxa = dados['retornou'] / total * 100
                taxas_retorno[duracao] = {
                    'retornou': dados['retornou'],
                    'nao_retornou': dados['nao_retornou'],
                    'total': total,
                    'taxa_retorno': round(taxa, 1)
                }
        
        # Distribuicao de ausencias
        distribuicao = Counter(ausencias)
        
        return {
            'posicao': posicao,
            'numero': numero,
            'total_ausencias': len(ausencias),
            'media_ausencia': round(media_ausencia, 2),
            'mediana_ausencia': mediana,
            'max_ausencia': max_ausencia,
            'taxas_retorno': taxas_retorno,
            'distribuicao': dict(distribuicao)
        }
    
    def executar_analise_completa(self):
        """Executa analise para todos os favoritos"""
        print("\n" + "=" * 70)
        print("[***] ANALISE DE RETORNO POSICIONAL")
        print("=" * 70)
        
        if not self.carregar_dados():
            return False
        
        self.identificar_favoritos()
        
        print("\n" + "=" * 70)
        print("[ANALISE] PADROES DE RETORNO APOS AUSENCIA")
        print("=" * 70)
        
        for pos in range(1, 16):
            fav = self.favoritos[pos]
            numero = fav['numero']
            
            resultado = self.analisar_retorno_apos_ausencia(pos, numero)
            self.resultados[pos] = resultado
            
            print(f"\n{'='*60}")
            print(f"[N{pos:02d}] NUMERO FAVORITO: {numero:02d} ({fav['percentual']}% frequencia)")
            print(f"{'='*60}")
            print(f"   Total de periodos de ausencia: {resultado['total_ausencias']}")
            print(f"   Media de concursos ausente: {resultado['media_ausencia']}")
            print(f"   Mediana: {resultado['mediana_ausencia']} | Max: {resultado['max_ausencia']}")
            
            # Mostrar taxas de retorno por duracao
            print(f"\n   [TAXAS DE RETORNO POR DURACAO DA AUSENCIA]")
            print(f"   {'Ausencias':<12} {'Retornou':<10} {'Nao Ret.':<10} {'Taxa %':<10}")
            print(f"   {'-'*45}")
            
            taxas = resultado['taxas_retorno']
            for duracao in sorted(taxas.keys())[:10]:  # Top 10
                t = taxas[duracao]
                if t['total'] >= 5:  # Minimo de 5 ocorrencias para ser relevante
                    print(f"   {duracao:<12} {t['retornou']:<10} {t['nao_retornou']:<10} {t['taxa_retorno']:<10.1f}%")
        
        # Resumo geral
        self.mostrar_resumo_geral()
        
        return True
    
    def mostrar_resumo_geral(self):
        """Mostra resumo consolidado de todas as posicoes"""
        print("\n" + "=" * 70)
        print("[RESUMO] TAXA DE RETORNO IMEDIATO (apos 1 ausencia)")
        print("=" * 70)
        print(f"{'Pos':<6} {'Num':<6} {'Retornou':<12} {'Total':<10} {'Taxa %':<10} {'Tendencia'}")
        print("-" * 60)
        
        for pos in range(1, 16):
            res = self.resultados[pos]
            taxas = res['taxas_retorno']
            
            if 1 in taxas:
                t = taxas[1]
                taxa = t['taxa_retorno']
                
                # Determinar tendencia
                if taxa > 55:
                    tendencia = "[RETORNO] -> Favorece voltar"
                elif taxa < 45:
                    tendencia = "[MOMENTUM] -> Favorece continuar fora"
                else:
                    tendencia = "[NEUTRO]"
                
                print(f"N{pos:02d}    {res['numero']:02d}     {t['retornou']:<12} {t['total']:<10} {taxa:<10.1f}% {tendencia}")
        
        # Analise de padroes mais longos
        print("\n" + "=" * 70)
        print("[INSIGHT] TAXA DE RETORNO APOS AUSENCIAS PROLONGADAS")
        print("=" * 70)
        
        for pos in range(1, 16):
            res = self.resultados[pos]
            taxas = res['taxas_retorno']
            
            # Verificar se ha padrao de "divida" (taxa aumenta com tempo)
            taxas_longas = [(d, taxas[d]['taxa_retorno']) for d in taxas if d >= 3 and taxas[d]['total'] >= 10]
            
            if taxas_longas:
                # Calcular tendencia
                if len(taxas_longas) >= 2:
                    primeira = taxas_longas[0][1]
                    ultima = taxas_longas[-1][1]
                    
                    if ultima > primeira + 10:
                        print(f"N{pos:02d} ({res['numero']:02d}): Taxa AUMENTA com tempo -> Candidato a REVERTER!")
                    elif ultima < primeira - 10:
                        print(f"N{pos:02d} ({res['numero']:02d}): Taxa DIMINUI com tempo -> MOMENTUM forte!")
        
        print("\n" + "=" * 70)
        print("[OK] ANALISE CONCLUIDA!")
        print("=" * 70)


def main():
    """Funcao principal"""
    analisador = AnaliseRetornoPosicional()
    analisador.executar_analise_completa()
    input("\n[PAUSE] Pressione ENTER para continuar...")


if __name__ == "__main__":
    main()
