#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análise de Posições-Chave - LotoScope
Baseado na descoberta do N8 como indicador de oscilação
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

class AnalisadorPosicoesChave:
    def __init__(self):
        self.posicoes_fixas = {
            'N1': 'SEMPRE_BAIXO',
            'N5': 'QUASE_SEMPRE_BAIXO', 
            'N15': 'SEMPRE_ALTO',
            'N12': 'QUASE_SEMPRE_ALTO'
        }
        self.posicao_indicadora = 'N8'
        
    def obter_ultimo_concurso(self):
        """Obtém dados do último concurso"""
        query = """
        SELECT TOP 1 
            Concurso, N1, N5, N8, N12, N15,
            Faixa_Baixa, Faixa_Media, Faixa_Alta
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        return db_config.execute_query(query)
    
    def analisar_padrao_atual(self):
        """Analisa o padrão atual baseado no último concurso"""
        ultimo = self.obter_ultimo_concurso()
        if not ultimo:
            return None
            
        dados = ultimo[0]
        concurso = dados[0]
        n1, n5, n8, n12, n15 = dados[1:6]
        fx_baixa, fx_media, fx_alta = dados[6:9]
        
        # Categorizar N8
        n8_categoria = 'BAIXO' if n8 <= 13 else 'ALTO'
        
        # Análise de distribuição
        distribuicao_atual = self._categorizar_distribuicao(fx_baixa, fx_media, fx_alta)
        
        return {
            'concurso': concurso,
            'posicoes': {'N1': n1, 'N5': n5, 'N8': n8, 'N12': n12, 'N15': n15},
            'n8_categoria': n8_categoria,
            'distribuicao': {'baixa': fx_baixa, 'media': fx_media, 'alta': fx_alta},
            'distribuicao_categoria': distribuicao_atual
        }
    
    def _categorizar_distribuicao(self, baixa, media, alta):
        """Categoriza a distribuição atual"""
        if alta >= 6:
            return 'ALTA'
        elif baixa >= 6:
            return 'BAIXA'
        else:
            return 'MÉDIA'
    
    def prever_proximo_n8(self, historico_n8):
        """Prediz próximo N8 baseado em padrões de oscilação"""
        if len(historico_n8) < 3:
            return None
            
        # Análise de tendência
        ultimos_3 = historico_n8[-3:]
        categorias = ['BAIXO' if x <= 13 else 'ALTO' for x in ultimos_3]
        
        # Estratégia contrária (como descoberto no N12)
        if categorias[-1] == 'ALTO':
            tendencia = 'BAIXO'
            faixa_sugerida = list(range(10, 14))  # 10-13
        else:
            tendencia = 'ALTO' 
            faixa_sugerida = list(range(14, 17))  # 14-16
            
        return {
            'tendencia': tendencia,
            'faixa_sugerida': faixa_sugerida,
            'confianca': self._calcular_confianca(categorias)
        }
    
    def _calcular_confianca(self, categorias):
        """Calcula confiança da previsão baseada em padrões"""
        # Se há alternância, maior confiança na reversão
        if len(set(categorias)) > 1:
            return 'ALTA'
        else:
            return 'MÉDIA'
    
    def gerar_filtro_n8_inteligente(self):
        """Gera filtro N8 para próximo concurso"""
        # Obter histórico do N8
        query_historico = """
        SELECT TOP 10 N8 
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        historico = db_config.execute_query(query_historico)
        
        if not historico:
            return None
            
        historico_n8 = [row[0] for row in historico]
        previsao = self.prever_proximo_n8(historico_n8)
        
        if previsao:
            # Gerar condição SQL
            valores = previsao['faixa_sugerida']
            condicao_n8 = f"N8 IN ({','.join(map(str, valores))})"
            
            return {
                'condicao_sql': condicao_n8,
                'valores': valores,
                'tendencia': previsao['tendencia'],
                'confianca': previsao['confianca'],
                'historico': historico_n8[:5]
            }
        
        return None
    
    def gerar_query_otimizada_3491(self):
        """Gera query otimizada para concurso 3491"""
        analise_atual = self.analisar_padrao_atual()
        filtro_n8 = self.gerar_filtro_n8_inteligente()
        
        if not analise_atual or not filtro_n8:
            return None
            
        # Query base otimizada
        query_base = f"""
        SELECT TOP 100000
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM COMBINACOES_LOTOFACIL
        WHERE 
            {filtro_n8['condicao_sql']}
            AND N1 <= 5
            AND N5 <= 13  
            AND N12 >= 14
            AND N15 >= 20
            AND (N1 + N2 + N3 + N4 + N5 + N6 + N7 + N8 + N9 + N10 + N11 + N12 + N13 + N14 + N15) BETWEEN 180 AND 220
        ORDER BY NEWID()
        """
        
        return {
            'query': query_base,
            'filtro_n8': filtro_n8,
            'analise_base': analise_atual,
            'explicacao': self._gerar_explicacao(analise_atual, filtro_n8)
        }
    
    def _gerar_explicacao(self, analise, filtro_n8):
        """Gera explicação da estratégia"""
        return f"""
🎯 ESTRATÉGIA POSIÇÕES-CHAVE PARA CONCURSO {analise['concurso'] + 1}:

📊 ANÁLISE DO CONCURSO {analise['concurso']}:
   • N8 = {analise['posicoes']['N8']} ({analise['n8_categoria']})
   • Distribuição: {analise['distribuicao']['baixa']}-{analise['distribuicao']['media']}-{analise['distribuicao']['alta']} ({analise['distribuicao_categoria']})

🎯 PREVISÃO PARA PRÓXIMO CONCURSO:
   • N8 Tendência: {filtro_n8['tendencia']}
   • N8 Valores: {filtro_n8['valores']}
   • Confiança: {filtro_n8['confianca']}

🔧 FILTROS APLICADOS:
   • N1 ≤ 5 (sempre baixo)
   • N5 ≤ 13 (quase sempre baixo) 
   • N8 IN {filtro_n8['valores']} (estratégia contrária)
   • N12 ≥ 14 (quase sempre alto)
   • N15 ≥ 20 (sempre alto)
   • Soma entre 180-220 (faixa típica)

🎯 Esta estratégia combina as descobertas das posições-chave
   com a teoria de reversão aplicada ao N8!
        """

def main():
    print("🎯 ANALISADOR DE POSIÇÕES-CHAVE - SISTEMA AVANÇADO")
    print("=" * 60)
    
    analisador = AnalisadorPosicoesChave()
    
    # Análise do padrão atual
    print("\n📊 ANÁLISE DO PADRÃO ATUAL:")
    analise = analisador.analisar_padrao_atual()
    if analise:
        print(f"Último concurso: {analise['concurso']}")
        print(f"Posições: N1={analise['posicoes']['N1']}, N5={analise['posicoes']['N5']}, "
              f"N8={analise['posicoes']['N8']}, N12={analise['posicoes']['N12']}, N15={analise['posicoes']['N15']}")
        print(f"N8 Categoria: {analise['n8_categoria']}")
        print(f"Distribuição: {analise['distribuicao']['baixa']}-{analise['distribuicao']['media']}-{analise['distribuicao']['alta']} ({analise['distribuicao_categoria']})")
    
    # Gerar query otimizada
    print("\n🚀 GERANDO QUERY OTIMIZADA PARA PRÓXIMO CONCURSO:")
    resultado = analisador.gerar_query_otimizada_3491()
    
    if resultado:
        print(resultado['explicacao'])
        print("\n💻 QUERY GERADA:")
        print(resultado['query'])
        
        # Salvar query em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"query_posicoes_chave_{timestamp}.sql"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(f"-- Query Posições-Chave - {datetime.now()}\n")
            f.write(f"-- {resultado['explicacao']}\n\n")
            f.write(resultado['query'])
            
        print(f"\n✅ Query salva em: {nome_arquivo}")
        
    else:
        print("❌ Erro ao gerar query otimizada")

if __name__ == "__main__":
    main()