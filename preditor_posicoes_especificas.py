#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preditor de Posições Específicas - Sistema Inteligente
Gera valores exatos para N1, N5, N8, N12, N15 baseado em:
- Padrões de repetição
- Ciclos alto/médio/baixo  
- Performance recente
- Pontos de virada
- Aprendizado dinâmico (ZERO hardcode)
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

class PreditorPosicoesEspecificas:
    def __init__(self):
        self.posicoes_chave = ['N1', 'N5', 'N8', 'N12', 'N15']
        self.historico_analise = 20  # Últimos 20 concursos para análise
        
    def categorizar_valor(self, valor, posicao):
        """Categoriza valor baseado em distribuição histórica dinâmica"""
        # Obter limites dinâmicos baseados no histórico
        query_limites = f"""
        SELECT 
            MIN({posicao}) as Min_Val,
            MAX({posicao}) as Max_Val,
            AVG(CAST({posicao} as FLOAT)) as Media,
            PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY {posicao}) as P33,
            PERCENTILE_CONT(0.67) WITHIN GROUP (ORDER BY {posicao}) as P67
        FROM Resultados_INT
        """
        resultado = db_config.execute_query(query_limites)
        
        if resultado:
            limites = resultado[0]
            p33, p67 = limites[3], limites[4]
            
            if valor <= p33:
                return 'BAIXO'
            elif valor <= p67:
                return 'MÉDIO'
            else:
                return 'ALTO'
        
        # Fallback estático se query falhar
        fallback_limits = {
            'N1': (2, 4), 'N5': (8, 11), 'N8': (11, 14), 
            'N12': (17, 20), 'N15': (22, 24)
        }
        low, high = fallback_limits.get(posicao, (10, 15))
        
        if valor <= low:
            return 'BAIXO'
        elif valor <= high:
            return 'MÉDIO'
        else:
            return 'ALTO'
    
    def analisar_repeticoes_recentes(self, posicao):
        """Analisa padrões de repetição nos últimos concursos"""
        query = f"""
        SELECT TOP {self.historico_analise} {posicao} 
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        resultado = db_config.execute_query(query)
        
        if not resultado:
            return None
            
        valores = [row[0] for row in resultado]
        
        # Análise de repetições
        ultimos_5 = valores[:5]
        ultimos_10 = valores[:10]
        
        freq_5 = Counter(ultimos_5)
        freq_10 = Counter(ultimos_10)
        
        # Valores que se repetiram recentemente
        repetidos_5 = [v for v, c in freq_5.items() if c > 1]
        repetidos_10 = [v for v, c in freq_10.items() if c > 1]
        
        # Valores únicos (não repetidos)
        unicos_5 = [v for v, c in freq_5.items() if c == 1]
        unicos_10 = [v for v, c in freq_10.items() if c == 1]
        
        return {
            'valores_historico': valores,
            'ultimo_valor': valores[0],
            'repetidos_5': repetidos_5,
            'repetidos_10': repetidos_10,
            'unicos_5': unicos_5,
            'unicos_10': unicos_10,
            'mais_frequente_5': freq_5.most_common(1)[0] if freq_5 else None,
            'mais_frequente_10': freq_10.most_common(1)[0] if freq_10 else None
        }
    
    def analisar_ciclos_categoria(self, posicao):
        """Analisa ciclos de alto/médio/baixo"""
        query = f"""
        SELECT TOP {self.historico_analise} {posicao} 
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        resultado = db_config.execute_query(query)
        
        if not resultado:
            return None
            
        valores = [row[0] for row in resultado]
        categorias = [self.categorizar_valor(v, posicao) for v in valores]
        
        # Detectar mudanças de padrão
        mudancas = []
        for i in range(1, len(categorias)):
            if categorias[i] != categorias[i-1]:
                mudancas.append({
                    'posicao': i,
                    'mudanca': f"{categorias[i-1]}→{categorias[i]}",
                    'valor_anterior': valores[i-1],
                    'valor_novo': valores[i]
                })
        
        # Análise de tendência
        categoria_atual = categorias[0]
        categoria_anterior = categorias[1] if len(categorias) > 1 else categoria_atual
        
        # Frequência de categorias
        freq_categorias = Counter(categorias[:10])
        
        return {
            'valores': valores,
            'categorias': categorias,
            'categoria_atual': categoria_atual,
            'categoria_anterior': categoria_anterior,
            'mudanca_recente': categoria_atual != categoria_anterior,
            'mudancas_historico': mudancas[-5:],  # Últimas 5 mudanças
            'frequencia_categorias': dict(freq_categorias),
            'tendencia_dominante': freq_categorias.most_common(1)[0][0] if freq_categorias else None
        }
    
    def detectar_pontos_virada(self, posicao):
        """Detecta pontos de virada baseado em múltiplos fatores"""
        repeticoes = self.analisar_repeticoes_recentes(posicao)
        ciclos = self.analisar_ciclos_categoria(posicao)
        
        if not repeticoes or not ciclos:
            return None
            
        # Critérios para ponto de virada
        criterios_virada = []
        
        # 1. Mudança recente de categoria
        if ciclos['mudanca_recente']:
            criterios_virada.append(f"Mudança {ciclos['categoria_anterior']}→{ciclos['categoria_atual']}")
        
        # 2. Valor repetiu muito nos últimos 5
        if repeticoes['repetidos_5']:
            criterios_virada.append(f"Repetições recentes: {repeticoes['repetidos_5']}")
        
        # 3. Tendência de alta/baixa nos valores
        ultimos_3 = repeticoes['valores_historico'][:3]
        if len(ultimos_3) >= 3:
            if ultimos_3[0] > ultimos_3[1] > ultimos_3[2]:
                criterios_virada.append("Tendência crescente")
            elif ultimos_3[0] < ultimos_3[1] < ultimos_3[2]:
                criterios_virada.append("Tendência decrescente")
        
        # 4. Categoria muito dominante (pode reverter)
        freq_cat = ciclos['frequencia_categorias']
        categoria_dominante = max(freq_cat, key=freq_cat.get)
        if freq_cat[categoria_dominante] >= 7:  # 70% dos últimos 10
            criterios_virada.append(f"Categoria {categoria_dominante} muito dominante ({freq_cat[categoria_dominante]}/10)")
        
        return {
            'ponto_virada_detectado': len(criterios_virada) >= 2,
            'criterios': criterios_virada,
            'confianca': 'ALTA' if len(criterios_virada) >= 3 else 'MÉDIA' if len(criterios_virada) >= 2 else 'BAIXA'
        }
    
    def prever_valores_especificos(self, posicao):
        """Prevê valores específicos para uma posição"""
        repeticoes = self.analisar_repeticoes_recentes(posicao)
        ciclos = self.analisar_ciclos_categoria(posicao)
        virada = self.detectar_pontos_virada(posicao)
        
        if not all([repeticoes, ciclos, virada]):
            return None
        
        candidatos = []
        reasoning = []
        
        # Estratégia 1: Evitar repetições recentes
        valores_evitar = set(repeticoes['repetidos_5'])
        reasoning.append(f"Evitando repetições recentes: {list(valores_evitar)}")
        
        # Estratégia 2: Considerar mudança de categoria se houver ponto de virada
        if virada['ponto_virada_detectado']:
            categoria_atual = ciclos['categoria_atual']
            
            # Sugerir categoria oposta
            if categoria_atual == 'ALTO':
                categoria_sugerida = 'BAIXO'
            elif categoria_atual == 'BAIXO':
                categoria_sugerida = 'ALTO'
            else:  # MÉDIO
                # Se é médio, escolher a categoria menos frequente entre ALTO/BAIXO
                freq = ciclos['frequencia_categorias']
                if freq.get('ALTO', 0) < freq.get('BAIXO', 0):
                    categoria_sugerida = 'ALTO'
                else:
                    categoria_sugerida = 'BAIXO'
                    
            reasoning.append(f"Ponto de virada: {categoria_atual} → {categoria_sugerida}")
        else:
            # Manter tendência dominante
            categoria_sugerida = ciclos['tendencia_dominante']
            reasoning.append(f"Mantendo tendência: {categoria_sugerida}")
        
        # Obter valores candidatos da categoria sugerida
        query_categoria = f"""
        SELECT DISTINCT {posicao}, COUNT(*) as freq
        FROM Resultados_INT 
        GROUP BY {posicao}
        ORDER BY freq DESC
        """
        resultado_freq = db_config.execute_query(query_categoria)
        
        if resultado_freq:
            for valor, freq in resultado_freq:
                cat_valor = self.categorizar_valor(valor, posicao)
                
                if cat_valor == categoria_sugerida and valor not in valores_evitar:
                    candidatos.append({
                        'valor': valor,
                        'categoria': cat_valor,
                        'frequencia_historica': freq,
                        'score': freq * (2 if valor not in repeticoes['repetidos_10'] else 1)
                    })
        
        # Ordenar por score e pegar os top 3-5
        candidatos.sort(key=lambda x: x['score'], reverse=True)
        top_candidatos = candidatos[:5] if len(candidatos) >= 5 else candidatos[:3]
        
        return {
            'posicao': posicao,
            'candidatos': top_candidatos,
            'reasoning': reasoning,
            'categoria_sugerida': categoria_sugerida,
            'confianca': virada['confianca'],
            'analise_base': {
                'ultimo_valor': repeticoes['ultimo_valor'],
                'categoria_atual': ciclos['categoria_atual'],
                'ponto_virada': virada['ponto_virada_detectado']
            }
        }
    
    def gerar_predicoes_completas(self):
        """Gera predições para todas as posições-chave"""
        print("🎯 SISTEMA PREDITOR DE POSIÇÕES ESPECÍFICAS")
        print("=" * 70)
        
        predicoes = {}
        
        for posicao in self.posicoes_chave:
            print(f"\n🔍 Analisando posição {posicao}...")
            predicao = self.prever_valores_especificos(posicao)
            
            if predicao:
                predicoes[posicao] = predicao
                
                print(f"\n📊 PREDIÇÃO PARA {posicao}:")
                print(f"   Último valor: {predicao['analise_base']['ultimo_valor']}")
                print(f"   Categoria atual: {predicao['analise_base']['categoria_atual']}")
                print(f"   Categoria sugerida: {predicao['categoria_sugerida']}")
                print(f"   Ponto de virada: {'SIM' if predicao['analise_base']['ponto_virada'] else 'NÃO'}")
                print(f"   Confiança: {predicao['confianca']}")
                
                print(f"\n   🎯 TOP CANDIDATOS:")
                for i, cand in enumerate(predicao['candidatos'][:3], 1):
                    print(f"      {i}º: {cand['valor']} (freq: {cand['frequencia_historica']}, score: {cand['score']})")
                
                print(f"\n   💡 REASONING:")
                for reason in predicao['reasoning']:
                    print(f"      • {reason}")
        
        return predicoes
    
    def gerar_query_otimizada(self, predicoes):
        """Gera query SQL otimizada com valores específicos"""
        if not predicoes:
            return None
            
        condicoes = []
        explicacao = []
        
        for posicao, pred in predicoes.items():
            if pred['candidatos']:
                # Pegar top 2-3 candidatos
                top_valores = [c['valor'] for c in pred['candidatos'][:3]]
                condicao = f"{posicao} IN ({','.join(map(str, top_valores))})"
                condicoes.append(condicao)
                
                explicacao.append(f"   • {posicao}: {top_valores} ({pred['categoria_sugerida']}, confiança {pred['confianca']})")
        
        if condicoes:
            query = f"""
SELECT TOP 50000
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
    preditor = PreditorPosicoesEspecificas()
    
    # Gerar predições
    predicoes = preditor.gerar_predicoes_completas()
    
    # Gerar query otimizada
    query_result = preditor.gerar_query_otimizada(predicoes)
    
    if query_result:
        print("\n" + "="*70)
        print("🚀 QUERY OTIMIZADA GERADA:")
        print("="*70)
        
        print("\n💡 ESTRATÉGIA APLICADA:")
        for exp in query_result['explicacao']:
            print(exp)
        
        print(f"\n💻 SQL QUERY:")
        print(query_result['query'])
        
        # Salvar em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"query_posicoes_especificas_{timestamp}.sql"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"-- Query Posições Específicas - {datetime.now()}\n")
            f.write(f"-- Estratégia: Valores exatos baseados em análise dinâmica\n\n")
            for exp in query_result['explicacao']:
                f.write(f"-- {exp}\n")
            f.write(f"\n{query_result['query']}")
            
        print(f"\n✅ Query salva em: {nome_arquivo}")
    
    else:
        print("\n❌ Erro ao gerar query otimizada")

if __name__ == "__main__":
    main()