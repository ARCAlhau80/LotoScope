#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preditor Posições CORRIGIDO - Versão Conservadora
Aplica limites históricos realistas para cada posição
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'lotofacil_lite'))
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from datetime import datetime
from collections import Counter

class PreditorConservador:
    def __init__(self):
        self.posicoes_chave = ['N1', 'N5', 'N8', 'N12', 'N15']
        self.limites_realistas = self._calcular_limites_realistas()
        
    def _calcular_limites_realistas(self):
        """Calcula limites realistas baseados em frequência histórica"""
        limites = {}
        
        for pos in self.posicoes_chave:
            query = f"""
            SELECT {pos}, COUNT(*) as freq,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT_BIG(*) FROM Resultados_INT), 2) as perc
            FROM Resultados_INT 
            GROUP BY {pos}
            HAVING COUNT(*) >= 10  -- Apenas valores com pelo menos 10 ocorrências
            ORDER BY freq DESC
            """
            resultado = db_config.execute_query(query)
            
            if resultado:
                # Valores que aparecem em pelo menos 1% dos casos
                valores_viaveis = [row[0] for row in resultado if row[2] >= 1.0]
                
                # Se não há valores com 1%+, pegar os top 80% da frequência
                if not valores_viaveis:
                    total_freq = sum(row[1] for row in resultado)
                    freq_acumulada = 0
                    for valor, freq, perc in resultado:
                        freq_acumulada += freq
                        valores_viaveis.append(valor)
                        if freq_acumulada >= total_freq * 0.8:  # 80% da frequência
                            break
                
                limites[pos] = {
                    'valores_viaveis': sorted(valores_viaveis),
                    'min_valor': min(valores_viaveis),
                    'max_valor': max(valores_viaveis),
                    'frequencias': {row[0]: row[1] for row in resultado}
                }
                
                print(f"📊 {pos}: Valores viáveis = {sorted(valores_viaveis)}")
                print(f"    Faixa: {min(valores_viaveis)} a {max(valores_viaveis)}")
        
        return limites
    
    def prever_valores_conservadores(self, posicao):
        """Prevê valores dentro dos limites históricos realistas"""
        if posicao not in self.limites_realistas:
            return None
            
        # Obter últimos valores
        query = f"""
        SELECT TOP 10 {posicao} 
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        resultado = db_config.execute_query(query)
        
        if not resultado:
            return None
            
        ultimos_valores = [row[0] for row in resultado]
        valores_recentes = set(ultimos_valores[:5])  # Últimos 5 para evitar
        
        # Limites realistas para esta posição
        limites = self.limites_realistas[posicao]
        valores_viaveis = limites['valores_viaveis']
        frequencias = limites['frequencias']
        
        # Filtrar candidatos
        candidatos = []
        for valor in valores_viaveis:
            if valor not in valores_recentes:  # Evitar repetições muito recentes
                score = frequencias.get(valor, 0)
                # Boost para valores que não apareceram nos últimos 10
                if valor not in ultimos_valores:
                    score *= 1.5
                    
                candidatos.append({
                    'valor': valor,
                    'frequencia': frequencias.get(valor, 0),
                    'score': score
                })
        
        # Ordenar por score e pegar top 3-5
        candidatos.sort(key=lambda x: x['score'], reverse=True)
        
        # Para posições muito conservadoras (N1), limitar ainda mais
        if posicao == 'N1':
            # N1: priorizar apenas 1,2,3,4 (99.2% dos casos)
            candidatos = [c for c in candidatos if c['valor'] <= 4]
        elif posicao == 'N15':
            # N15: priorizar apenas valores >= 20 (mais comum)
            candidatos = [c for c in candidatos if c['valor'] >= 20]
        
        top_candidatos = candidatos[:3] if len(candidatos) >= 3 else candidatos
        
        return {
            'posicao': posicao,
            'candidatos': top_candidatos,
            'valores_evitados': list(valores_recentes),
            'limite_conservador': f"{limites['min_valor']}-{limites['max_valor']}",
            'reasoning': f"Conservador: evitando {list(valores_recentes)}, priorizando frequentes"
        }
    
    def gerar_predicoes_conservadoras(self):
        """Gera predições conservadoras para todas as posições"""
        print("🎯 PREDITOR CONSERVADOR - LIMITES REALISTAS")
        print("=" * 70)
        
        predicoes = {}
        
        for posicao in self.posicoes_chave:
            print(f"\n🔍 Analisando {posicao}...")
            predicao = self.prever_valores_conservadores(posicao)
            
            if predicao:
                predicoes[posicao] = predicao
                
                print(f"\n📊 PREDIÇÃO CONSERVADORA PARA {posicao}:")
                print(f"   Limite histórico: {predicao['limite_conservador']}")
                print(f"   Valores evitados: {predicao['valores_evitados']}")
                
                print(f"\n   🎯 CANDIDATOS CONSERVADORES:")
                for i, cand in enumerate(predicao['candidatos'], 1):
                    print(f"      {i}º: {cand['valor']} (freq: {cand['frequencia']}, score: {cand['score']:.1f})")
                
                print(f"\n   💡 REASONING: {predicao['reasoning']}")
        
        return predicoes
    
    def gerar_query_conservadora(self, predicoes):
        """Gera query conservadora com valores realistas"""
        if not predicoes:
            return None
            
        condicoes = []
        explicacao = []
        
        for posicao, pred in predicoes.items():
            if pred['candidatos']:
                valores = [c['valor'] for c in pred['candidatos']]
                condicao = f"{posicao} IN ({','.join(map(str, valores))})"
                condicoes.append(condicao)
                
                explicacao.append(f"   • {posicao}: {valores} (conservador: {pred['limite_conservador']})")
        
        if condicoes:
            query = f"""
SELECT TOP 100000
    N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
FROM COMBINACOES_LOTOFACIL
WHERE 
    {' AND '.join(condicoes)}
    AND (N1 + N2 + N3 + N4 + N5 + N6 + N7 + N8 + N9 + N10 + N11 + N12 + N13 + N14 + N15) BETWEEN 180 AND 220
ORDER BY NEWID()
"""
            
            return {
                'query': query,
                'explicacao': explicacao,
                'predicoes': predicoes
            }
        
        return None

def main():
    print("🚀 INICIANDO PREDITOR CONSERVADOR...")
    
    preditor = PreditorConservador()
    
    # Gerar predições conservadoras
    predicoes = preditor.gerar_predicoes_conservadoras()
    
    # Gerar query
    query_result = preditor.gerar_query_conservadora(predicoes)
    
    if query_result:
        print("\n" + "="*70)
        print("🚀 QUERY CONSERVADORA GERADA:")
        print("="*70)
        
        print("\n💡 ESTRATÉGIA CONSERVADORA:")
        for exp in query_result['explicacao']:
            print(exp)
        
        print(f"\n💻 SQL QUERY:")
        print(query_result['query'])
        
        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"query_conservadora_{timestamp}.sql"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"-- Query Conservadora - {datetime.now()}\n")
            f.write(f"-- Estratégia: Valores dentro de limites históricos realistas\n\n")
            for exp in query_result['explicacao']:
                f.write(f"-- {exp}\n")
            f.write(f"\n{query_result['query']}")
            
        print(f"\n✅ Query conservadora salva em: {nome_arquivo}")
    
    else:
        print("\n❌ Erro ao gerar query conservadora")

if __name__ == "__main__":
    main()