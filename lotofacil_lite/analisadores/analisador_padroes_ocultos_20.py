#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ANALISADOR DE PADRÕES OCULTOS - COMBINAÇÕES DE 20 NÚMEROS
============================================================
Analisa a tabela COMBINACOES_LOTOFACIL20_COMPLETO para descobrir
padrões ocultos nas combinações com maior taxa de acertos históricos.

Este sistema encontra:
1. Padrões de números que aparecem juntos em combinações vencedoras
2. Características estatísticas das combinações com mais acertos
3. Regras de associação entre números
4. Padrões posicionais

Os padrões descobertos são salvos em JSON para uso pelos geradores.

Autor: LotoScope
Data: 20/01/2026
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils'))

try:
    from database_config import DatabaseConfig
    db_config = DatabaseConfig()
except ImportError:
    from utils.database_config import DatabaseConfig
    db_config = DatabaseConfig()


@dataclass
class PadraoOculto:
    """Representa um padrão oculto descoberto."""
    tipo: str  # 'PAR', 'TRIO', 'QUADRA', 'CARACTERISTICA', 'POSICIONAL'
    descricao: str
    numeros: List[int]
    suporte: float  # % de combinações onde aparece
    confianca: float  # Taxa de sucesso quando presente
    lift: float  # Quanto aumenta a probabilidade
    acertos_medios: float  # Média de acertos quando padrão presente
    exemplos: int  # Quantidade de combinações com o padrão


@dataclass
class AnalisadorPadroesOcultos:
    """
    Analisador de Padrões Ocultos para tabela de 20 números.
    
    Estratégias:
    1. Association Rule Mining - encontra números que aparecem juntos
    2. Análise de Características - features das combinações vencedoras
    3. Padrões Posicionais - quais números em quais posições
    4. Clustering - agrupa combinações similares
    """
    
    # Parâmetros
    min_suporte: float = 0.01  # Mínimo 1% das combinações
    min_confianca: float = 0.6  # Mínimo 60% de confiança
    min_lift: float = 1.1  # Mínimo 10% de aumento na probabilidade
    
    # Padrões descobertos
    padroes_pares: List[PadraoOculto] = field(default_factory=list)
    padroes_trios: List[PadraoOculto] = field(default_factory=list)
    padroes_caracteristicas: List[PadraoOculto] = field(default_factory=list)
    padroes_posicionais: List[PadraoOculto] = field(default_factory=list)
    
    # Estatísticas gerais
    total_combinacoes: int = 0
    media_acertos_global: Dict[str, float] = field(default_factory=dict)
    
    # Regras de associação descobertas
    regras_associacao: List[Dict] = field(default_factory=list)
    
    # Números mais frequentes em combinações vencedoras
    numeros_vencedores: Dict[int, float] = field(default_factory=dict)
    
    def conectar_banco(self):
        """Conecta ao banco de dados."""
        return db_config.get_connection()
    
    def analisar_tabela_completa(self, verbose: bool = True) -> Dict:
        """
        Analisa a tabela COMBINACOES_LOTOFACIL20_COMPLETO por completo.
        
        Returns:
            Dict com todos os padrões descobertos
        """
        if verbose:
            print("\n" + "=" * 70)
            print("🔍 ANALISADOR DE PADRÕES OCULTOS - COMBINAÇÕES 20 NÚMEROS")
            print("=" * 70)
        
        with self.conectar_banco() as conn:
            cursor = conn.cursor()
            
            # 1. Estatísticas gerais
            if verbose:
                print("\n📊 1. COLETANDO ESTATÍSTICAS GERAIS...")
            self._coletar_estatisticas_gerais(cursor, verbose)
            
            # 2. Analisar combinações com mais acertos
            if verbose:
                print("\n🏆 2. ANALISANDO COMBINAÇÕES VENCEDORAS...")
            self._analisar_combinacoes_vencedoras(cursor, verbose)
            
            # 3. Encontrar padrões de pares frequentes
            if verbose:
                print("\n🔢 3. DESCOBRINDO PADRÕES DE PARES...")
            self._descobrir_padroes_pares(cursor, verbose)
            
            # 4. Encontrar padrões de trios
            if verbose:
                print("\n🎯 4. DESCOBRINDO PADRÕES DE TRIOS...")
            self._descobrir_padroes_trios(cursor, verbose)
            
            # 5. Analisar características estatísticas
            if verbose:
                print("\n📈 5. ANALISANDO CARACTERÍSTICAS ESTATÍSTICAS...")
            self._analisar_caracteristicas(cursor, verbose)
            
            # 6. Analisar padrões posicionais
            if verbose:
                print("\n📍 6. ANALISANDO PADRÕES POSICIONAIS...")
            self._analisar_padroes_posicionais(cursor, verbose)
            
            # 7. Gerar regras de associação
            if verbose:
                print("\n🧠 7. GERANDO REGRAS DE ASSOCIAÇÃO...")
            self._gerar_regras_associacao(cursor, verbose)
        
        # Compilar resultados
        resultados = self._compilar_resultados()
        
        if verbose:
            self._exibir_resumo(resultados)
        
        return resultados
    
    def _coletar_estatisticas_gerais(self, cursor, verbose: bool):
        """Coleta estatísticas gerais da tabela."""
        cursor.execute("SELECT COUNT(*) FROM COMBINACOES_LOTOFACIL20_COMPLETO")
        self.total_combinacoes = cursor.fetchone()[0]
        
        # Médias de acertos
        cursor.execute("""
            SELECT 
                AVG(CAST(Acertos_15 AS FLOAT)) as media_15,
                AVG(CAST(Acertos_14 AS FLOAT)) as media_14,
                AVG(CAST(Acertos_13 AS FLOAT)) as media_13,
                AVG(CAST(Acertos_12 AS FLOAT)) as media_12,
                AVG(CAST(Acertos_11 AS FLOAT)) as media_11,
                SUM(Acertos_15) as total_15,
                SUM(Acertos_14) as total_14,
                SUM(Acertos_13) as total_13,
                SUM(Acertos_12) as total_12,
                SUM(Acertos_11) as total_11
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
        """)
        
        row = cursor.fetchone()
        self.media_acertos_global = {
            'media_15': row[0] or 0,
            'media_14': row[1] or 0,
            'media_13': row[2] or 0,
            'media_12': row[3] or 0,
            'media_11': row[4] or 0,
            'total_15': row[5] or 0,
            'total_14': row[6] or 0,
            'total_13': row[7] or 0,
            'total_12': row[8] or 0,
            'total_11': row[9] or 0,
        }
        
        if verbose:
            print(f"   ✅ Total de combinações: {self.total_combinacoes:,}")
            print(f"   📊 Média Acertos_15: {self.media_acertos_global['media_15']:.2f}")
            print(f"   📊 Total Acertos_15: {self.media_acertos_global['total_15']:,}")
            print(f"   📊 Total Acertos_14: {self.media_acertos_global['total_14']:,}")
            print(f"   📊 Total Acertos_13: {self.media_acertos_global['total_13']:,}")
    
    def _analisar_combinacoes_vencedoras(self, cursor, verbose: bool):
        """Analisa as combinações com mais acertos."""
        # Top combinações por acertos_15
        cursor.execute("""
            SELECT TOP 100
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15, N16, N17, N18, N19, N20,
                Acertos_15, Acertos_14, Acertos_13
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            ORDER BY Acertos_15 DESC, Acertos_14 DESC, Acertos_13 DESC
        """)
        
        top_combinacoes = cursor.fetchall()
        
        # Contar frequência de cada número nas top combinações
        frequencia_numeros = defaultdict(int)
        for comb in top_combinacoes:
            numeros = list(comb[:20])
            for n in numeros:
                frequencia_numeros[n] += 1
        
        # Normalizar
        total = len(top_combinacoes)
        for n in range(1, 26):
            self.numeros_vencedores[n] = frequencia_numeros[n] / total if total > 0 else 0
        
        if verbose:
            # Top 10 números mais frequentes
            top_numeros = sorted(self.numeros_vencedores.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"   🏆 Top 10 números em combinações vencedoras:")
            for num, freq in top_numeros:
                print(f"      Número {num:2d}: {freq*100:.1f}% das top 100 combinações")
    
    def _descobrir_padroes_pares(self, cursor, verbose: bool):
        """Descobre pares de números que aparecem juntos em combinações vencedoras."""
        # Buscar combinações com acertos_15 > média
        cursor.execute("""
            SELECT 
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15, N16, N17, N18, N19, N20,
                Acertos_15 + Acertos_14 as total_acertos
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            WHERE Acertos_15 > 0 OR Acertos_14 > 5
        """)
        
        combinacoes_vencedoras = cursor.fetchall()
        
        # Contar pares
        contagem_pares = defaultdict(lambda: {'count': 0, 'acertos': 0})
        
        for comb in combinacoes_vencedoras:
            numeros = sorted(comb[:20])
            total_acertos = comb[20]
            
            for i, n1 in enumerate(numeros):
                for n2 in numeros[i+1:]:
                    par = (n1, n2)
                    contagem_pares[par]['count'] += 1
                    contagem_pares[par]['acertos'] += total_acertos
        
        # Calcular métricas para cada par
        total_vencedoras = len(combinacoes_vencedoras)
        
        pares_significativos = []
        for par, dados in contagem_pares.items():
            if dados['count'] >= total_vencedoras * self.min_suporte:
                suporte = dados['count'] / total_vencedoras
                media_acertos = dados['acertos'] / dados['count']
                
                # Lift: comparar com frequência esperada
                # Cada par deveria aparecer em ~60% das combinações por acaso
                lift = suporte / 0.6 if suporte > 0.6 else suporte / 0.6
                
                if lift >= self.min_lift:
                    pares_significativos.append({
                        'par': par,
                        'suporte': suporte,
                        'media_acertos': media_acertos,
                        'lift': lift,
                        'exemplos': dados['count']
                    })
        
        # Ordenar por lift
        pares_significativos.sort(key=lambda x: x['lift'], reverse=True)
        
        # Converter para PadraoOculto
        for p in pares_significativos[:50]:
            self.padroes_pares.append(PadraoOculto(
                tipo='PAR',
                descricao=f"Par {p['par'][0]}-{p['par'][1]} frequente em vencedoras",
                numeros=list(p['par']),
                suporte=p['suporte'],
                confianca=p['suporte'],
                lift=p['lift'],
                acertos_medios=p['media_acertos'],
                exemplos=p['exemplos']
            ))
        
        if verbose:
            print(f"   ✅ {len(self.padroes_pares)} pares significativos descobertos")
            if self.padroes_pares:
                print(f"   🔝 Top 5 pares:")
                for p in self.padroes_pares[:5]:
                    print(f"      {p.numeros}: lift={p.lift:.2f}, suporte={p.suporte*100:.1f}%")
    
    def _descobrir_padroes_trios(self, cursor, verbose: bool):
        """Descobre trios de números que aparecem juntos."""
        # Similar ao de pares, mas com trios
        cursor.execute("""
            SELECT TOP 5000
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15, N16, N17, N18, N19, N20,
                Acertos_15 + Acertos_14 + Acertos_13 as total_acertos
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            WHERE Acertos_15 > 0 OR Acertos_14 > 3
            ORDER BY Acertos_15 DESC, Acertos_14 DESC
        """)
        
        combinacoes = cursor.fetchall()
        
        # Contar trios (limitado para performance)
        contagem_trios = defaultdict(lambda: {'count': 0, 'acertos': 0})
        
        for comb in combinacoes[:1000]:  # Limitar para performance
            numeros = sorted(comb[:20])
            total_acertos = comb[20]
            
            for i, n1 in enumerate(numeros):
                for j, n2 in enumerate(numeros[i+1:], i+1):
                    for n3 in numeros[j+1:]:
                        trio = (n1, n2, n3)
                        contagem_trios[trio]['count'] += 1
                        contagem_trios[trio]['acertos'] += total_acertos
        
        # Filtrar trios significativos
        total = len(combinacoes[:1000])
        
        for trio, dados in contagem_trios.items():
            if dados['count'] >= 10:  # Mínimo 10 ocorrências
                suporte = dados['count'] / total
                media_acertos = dados['acertos'] / dados['count']
                lift = suporte / 0.3  # Trio esperado em ~30%
                
                if lift >= 1.2:
                    self.padroes_trios.append(PadraoOculto(
                        tipo='TRIO',
                        descricao=f"Trio {trio[0]}-{trio[1]}-{trio[2]}",
                        numeros=list(trio),
                        suporte=suporte,
                        confianca=suporte,
                        lift=lift,
                        acertos_medios=media_acertos,
                        exemplos=dados['count']
                    ))
        
        # Ordenar e limitar
        self.padroes_trios.sort(key=lambda x: x.lift, reverse=True)
        self.padroes_trios = self.padroes_trios[:30]
        
        if verbose:
            print(f"   ✅ {len(self.padroes_trios)} trios significativos descobertos")
            if self.padroes_trios:
                print(f"   🔝 Top 5 trios:")
                for p in self.padroes_trios[:5]:
                    print(f"      {p.numeros}: lift={p.lift:.2f}, média acertos={p.acertos_medios:.1f}")
    
    def _analisar_caracteristicas(self, cursor, verbose: bool):
        """Analisa características estatísticas das combinações vencedoras."""
        # Analisar combinações com acertos
        cursor.execute("""
            SELECT 
                QtdePares, QtdeImpares, QtdePrimos, QtdeFibonacci,
                QtdeConsecutivos, SomaTotal, MaiorGap,
                QtdeDezena1, QtdeDezena2, QtdeDezena3, QtdeDezena4, QtdeDezena5,
                Acertos_15, Acertos_14, Acertos_13
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            WHERE Acertos_15 > 0 OR Acertos_14 > 0
        """)
        
        dados_vencedoras = cursor.fetchall()
        
        # Calcular médias das vencedoras
        if dados_vencedoras:
            medias_vencedoras = {
                'QtdePares': sum(d[0] for d in dados_vencedoras) / len(dados_vencedoras),
                'QtdeImpares': sum(d[1] for d in dados_vencedoras) / len(dados_vencedoras),
                'QtdePrimos': sum(d[2] for d in dados_vencedoras) / len(dados_vencedoras),
                'QtdeFibonacci': sum(d[3] for d in dados_vencedoras) / len(dados_vencedoras),
                'QtdeConsecutivos': sum(d[4] for d in dados_vencedoras) / len(dados_vencedoras),
                'SomaTotal': sum(d[5] for d in dados_vencedoras) / len(dados_vencedoras),
                'MaiorGap': sum(d[6] for d in dados_vencedoras) / len(dados_vencedoras),
            }
            
            # Criar padrões de características
            for carac, media in medias_vencedoras.items():
                self.padroes_caracteristicas.append(PadraoOculto(
                    tipo='CARACTERISTICA',
                    descricao=f"{carac} ideal para vencedoras: {media:.1f}",
                    numeros=[],
                    suporte=len(dados_vencedoras) / self.total_combinacoes,
                    confianca=0.8,
                    lift=1.2,
                    acertos_medios=media,
                    exemplos=len(dados_vencedoras)
                ))
            
            if verbose:
                print(f"   ✅ Características das combinações vencedoras:")
                print(f"      • Pares: {medias_vencedoras['QtdePares']:.1f}")
                print(f"      • Ímpares: {medias_vencedoras['QtdeImpares']:.1f}")
                print(f"      • Primos: {medias_vencedoras['QtdePrimos']:.1f}")
                print(f"      • Consecutivos: {medias_vencedoras['QtdeConsecutivos']:.1f}")
                print(f"      • Soma Total: {medias_vencedoras['SomaTotal']:.1f}")
    
    def _analisar_padroes_posicionais(self, cursor, verbose: bool):
        """Analisa quais números aparecem mais em cada posição nas vencedoras."""
        for pos in range(1, 21):
            col = f"N{pos}"
            
            cursor.execute(f"""
                SELECT {col}, COUNT(*) as freq, AVG(CAST(Acertos_15 + Acertos_14 AS FLOAT)) as media
                FROM COMBINACOES_LOTOFACIL20_COMPLETO
                WHERE Acertos_15 > 0 OR Acertos_14 > 3
                GROUP BY {col}
                ORDER BY media DESC, freq DESC
            """)
            
            resultados = cursor.fetchall()
            
            if resultados:
                melhor = resultados[0]
                self.padroes_posicionais.append(PadraoOculto(
                    tipo='POSICIONAL',
                    descricao=f"Posição N{pos}: número {melhor[0]} é o melhor",
                    numeros=[melhor[0]],
                    suporte=melhor[1] / self.total_combinacoes,
                    confianca=0.7,
                    lift=1.15,
                    acertos_medios=melhor[2] if melhor[2] else 0,
                    exemplos=melhor[1]
                ))
        
        if verbose:
            print(f"   ✅ {len(self.padroes_posicionais)} padrões posicionais descobertos")
            print(f"   🔝 Melhores números por posição (N1-N5):")
            for p in self.padroes_posicionais[:5]:
                print(f"      {p.descricao}")
    
    def _gerar_regras_associacao(self, cursor, verbose: bool):
        """Gera regras de associação: Se X então Y."""
        # Usar os pares já descobertos
        for par in self.padroes_pares[:20]:
            n1, n2 = par.numeros
            
            # Regra: Se n1 está presente -> n2 deveria estar
            self.regras_associacao.append({
                'antecedente': [n1],
                'consequente': [n2],
                'suporte': par.suporte,
                'confianca': par.confianca,
                'lift': par.lift,
                'descricao': f"Se {n1} → inclua {n2}"
            })
            
            # Regra inversa
            self.regras_associacao.append({
                'antecedente': [n2],
                'consequente': [n1],
                'suporte': par.suporte,
                'confianca': par.confianca,
                'lift': par.lift,
                'descricao': f"Se {n2} → inclua {n1}"
            })
        
        if verbose:
            print(f"   ✅ {len(self.regras_associacao)} regras de associação geradas")
            print(f"   🔝 Top 5 regras:")
            for r in self.regras_associacao[:5]:
                print(f"      {r['descricao']} (lift={r['lift']:.2f})")
    
    def _compilar_resultados(self) -> Dict:
        """Compila todos os resultados em um dicionário."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_combinacoes': self.total_combinacoes,
            'estatisticas_gerais': self.media_acertos_global,
            'numeros_vencedores': dict(sorted(
                self.numeros_vencedores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )),
            'padroes_pares': [asdict(p) for p in self.padroes_pares],
            'padroes_trios': [asdict(p) for p in self.padroes_trios],
            'padroes_caracteristicas': [asdict(p) for p in self.padroes_caracteristicas],
            'padroes_posicionais': [asdict(p) for p in self.padroes_posicionais],
            'regras_associacao': self.regras_associacao,
            'resumo': {
                'total_padroes': (
                    len(self.padroes_pares) + 
                    len(self.padroes_trios) + 
                    len(self.padroes_caracteristicas) +
                    len(self.padroes_posicionais)
                ),
                'total_regras': len(self.regras_associacao)
            }
        }
    
    def _exibir_resumo(self, resultados: Dict):
        """Exibe resumo dos resultados."""
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS PADRÕES OCULTOS DESCOBERTOS")
        print("=" * 70)
        
        print(f"\n🔢 Total de combinações analisadas: {resultados['total_combinacoes']:,}")
        print(f"\n📈 Padrões Descobertos:")
        print(f"   • Pares significativos: {len(self.padroes_pares)}")
        print(f"   • Trios significativos: {len(self.padroes_trios)}")
        print(f"   • Características: {len(self.padroes_caracteristicas)}")
        print(f"   • Posicionais: {len(self.padroes_posicionais)}")
        print(f"   • Regras de associação: {len(self.regras_associacao)}")
        
        print(f"\n🏆 Top 10 Números Vencedores:")
        top_nums = list(resultados['numeros_vencedores'].items())[:10]
        for num, freq in top_nums:
            print(f"   Número {num:2d}: {freq*100:.1f}%")
        
        print("\n" + "=" * 70)
    
    def salvar_padroes(self, arquivo: str = None) -> str:
        """Salva os padrões descobertos em arquivo JSON."""
        if arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"padroes_ocultos_{timestamp}.json"
        
        resultados = self._compilar_resultados()
        
        # Caminho completo
        diretorio = os.path.dirname(os.path.abspath(__file__))
        caminho = os.path.join(diretorio, arquivo)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Padrões salvos em: {caminho}")
        return caminho


def carregar_padroes_ocultos(arquivo: str = None) -> Dict:
    """
    Carrega os padrões ocultos de um arquivo JSON.
    
    Se não especificado, busca o arquivo mais recente.
    """
    diretorio = os.path.dirname(os.path.abspath(__file__))
    
    if arquivo is None:
        # Buscar arquivo mais recente
        arquivos = [f for f in os.listdir(diretorio) if f.startswith('padroes_ocultos_') and f.endswith('.json')]
        if not arquivos:
            return None
        arquivo = sorted(arquivos)[-1]
    
    caminho = os.path.join(diretorio, arquivo)
    
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None


def obter_numeros_recomendados_padroes(padroes: Dict, quantidade: int = 20) -> List[int]:
    """
    Obtém os números mais recomendados baseado nos padrões descobertos.
    
    Args:
        padroes: Dicionário com padrões carregados
        quantidade: Quantidade de números a retornar
        
    Returns:
        Lista de números recomendados
    """
    if not padroes:
        return []
    
    scores = defaultdict(float)
    
    # Score baseado em frequência nas vencedoras
    for num_str, freq in padroes.get('numeros_vencedores', {}).items():
        num = int(num_str)
        scores[num] += freq * 10  # Peso 10
    
    # Score baseado em pares
    for par in padroes.get('padroes_pares', [])[:20]:
        for num in par.get('numeros', []):
            scores[num] += par.get('lift', 1) * 2  # Peso 2
    
    # Score baseado em trios
    for trio in padroes.get('padroes_trios', [])[:10]:
        for num in trio.get('numeros', []):
            scores[num] += trio.get('lift', 1) * 3  # Peso 3
    
    # Score baseado em posicionais
    for pos in padroes.get('padroes_posicionais', []):
        for num in pos.get('numeros', []):
            scores[num] += 1  # Peso 1
    
    # Ordenar e retornar top
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [num for num, score in sorted_nums[:quantidade]]


def obter_pares_recomendados(padroes: Dict, quantidade: int = 10) -> List[Tuple[int, int]]:
    """Obtém os pares mais recomendados."""
    if not padroes:
        return []
    
    pares = []
    for par in padroes.get('padroes_pares', [])[:quantidade]:
        nums = par.get('numeros', [])
        if len(nums) >= 2:
            pares.append(tuple(nums[:2]))
    
    return pares


def obter_trios_recomendados(padroes: Dict, quantidade: int = 5) -> List[Tuple[int, int, int]]:
    """Obtém os trios mais recomendados."""
    if not padroes:
        return []
    
    trios = []
    for trio in padroes.get('padroes_trios', [])[:quantidade]:
        nums = trio.get('numeros', [])
        if len(nums) >= 3:
            trios.append(tuple(nums[:3]))
    
    return trios


def executar_analise():
    """Executa a análise completa."""
    print("\n" + "🔍" * 35)
    print("    ANALISADOR DE PADRÕES OCULTOS - LOTOFÁCIL 20")
    print("🔍" * 35)
    
    analisador = AnalisadorPadroesOcultos()
    resultados = analisador.analisar_tabela_completa(verbose=True)
    
    # Salvar padrões
    arquivo = analisador.salvar_padroes()
    
    print(f"\n✅ Análise concluída!")
    print(f"📁 Arquivo salvo: {arquivo}")
    
    # Mostrar recomendações
    print("\n🎯 NÚMEROS MAIS RECOMENDADOS:")
    numeros_rec = obter_numeros_recomendados_padroes(resultados, 15)
    print(f"   {numeros_rec}")
    
    print("\n🔢 PARES MAIS RECOMENDADOS:")
    pares_rec = obter_pares_recomendados(resultados, 10)
    for p in pares_rec:
        print(f"   {p[0]} - {p[1]}")
    
    print("\n🎲 TRIOS MAIS RECOMENDADOS:")
    trios_rec = obter_trios_recomendados(resultados, 5)
    for t in trios_rec:
        print(f"   {t[0]} - {t[1]} - {t[2]}")
    
    return resultados


if __name__ == "__main__":
    executar_analise()
    input("\n⏸️ Pressione ENTER para sair...")
