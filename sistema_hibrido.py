#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Híbrido: Conservador + Alertas de Oportunidade
Combina estratégia segura com sinais de valores "em atraso"
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

class SistemaHibrido:
    def __init__(self):
        self.posicoes_chave = ['N1', 'N5', 'N8', 'N12', 'N15']
        
    def analisar_oportunidades_atraso(self, posicao):
        """Identifica valores em atraso que podem ser oportunidades"""
        # Obter frequência e última ocorrência de cada valor
        query_oportunidades = f"""
        WITH UltimaOcorrencia AS (
            SELECT {posicao} as Valor, 
                   MAX(Concurso) as Ultimo_Concurso,
                   COUNT(*) as Freq_Total
            FROM Resultados_INT
            GROUP BY {posicao}
        ),
        Estatisticas AS (
            SELECT Valor, Freq_Total, Ultimo_Concurso,
                   (SELECT MAX(Concurso) FROM Resultados_INT) as Ultimo_Concurso_Geral,
                   (SELECT MAX(Concurso) FROM Resultados_INT) - Ultimo_Concurso as Concursos_Sem_Sair,
                   CASE 
                       WHEN Freq_Total > 0 THEN (SELECT COUNT_BIG(*) FROM Resultados_INT) / Freq_Total 
                       ELSE 999 
                   END as Media_Intervalo
            FROM UltimaOcorrencia
        )
        SELECT Valor, Freq_Total, Ultimo_Concurso, Concursos_Sem_Sair, 
               ROUND(Media_Intervalo, 1) as Media_Intervalo,
               ROUND(Freq_Total * 100.0 / (SELECT COUNT_BIG(*) FROM Resultados_INT), 2) as Percentual,
               CASE 
                   WHEN Concursos_Sem_Sair > Media_Intervalo * 1.5 THEN 'MUITO_ATRASADO'
                   WHEN Concursos_Sem_Sair > Media_Intervalo THEN 'ATRASADO'
                   WHEN Concursos_Sem_Sair < Media_Intervalo * 0.5 THEN 'RECENTE'
                   ELSE 'NORMAL'
               END as Status_Atraso
        FROM Estatisticas
        ORDER BY Concursos_Sem_Sair DESC, Freq_Total DESC
        """
        
        resultado = db_config.execute_query(query_oportunidades)
        
        if resultado:
            oportunidades = []
            conservadores = []
            
            for row in resultado:
                valor, freq, ultimo, sem_sair, media_int, perc, status = row
                
                info = {
                    'valor': valor,
                    'frequencia_total': freq,
                    'ultimo_concurso': ultimo,
                    'concursos_sem_sair': sem_sair,
                    'media_intervalo': media_int,
                    'percentual': perc,
                    'status': status
                }
                
                # Categorizar como oportunidade ou conservador
                if status in ['MUITO_ATRASADO', 'ATRASADO'] and perc >= 0.5:  # Pelo menos 0.5%
                    oportunidades.append(info)
                elif status in ['NORMAL', 'RECENTE'] and perc >= 5.0:  # Valores frequentes
                    conservadores.append(info)
            
            return {
                'posicao': posicao,
                'oportunidades': oportunidades[:3],  # Top 3 oportunidades
                'conservadores': conservadores[:3],   # Top 3 conservadores
                'todos_valores': [{'valor': row[0], 'freq': row[1], 'ultimo': row[2], 
                                 'sem_sair': row[3], 'media': row[4], 'perc': row[5], 'status': row[6]} 
                                for row in resultado]
            }
        
        return None
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo com opções conservadoras e oportunidades"""
        print("🎯 SISTEMA HÍBRIDO: CONSERVADOR + OPORTUNIDADES")
        print("=" * 80)
        print("📊 Estratégia: Valores seguros + Alertas de oportunidade para decisão manual")
        print("=" * 80)
        
        relatorio = {}
        
        for posicao in self.posicoes_chave:
            print(f"\n🔍 ANÁLISE COMPLETA - {posicao}:")
            print("-" * 50)
            
            analise = self.analisar_oportunidades_atraso(posicao)
            
            if analise:
                relatorio[posicao] = analise
                
                # Mostrar oportunidades em atraso
                if analise['oportunidades']:
                    print(f"\n🚨 OPORTUNIDADES EM ATRASO ({posicao}):")
                    for i, oport in enumerate(analise['oportunidades'], 1):
                        print(f"   {i}º: {posicao}={oport['valor']} - {oport['concursos_sem_sair']} concursos sem sair")
                        print(f"       Média intervalo: {oport['media_intervalo']} | Freq: {oport['percentual']}%")
                        print(f"       Status: {oport['status']} | Último: concurso {oport['ultimo_concurso']}")
                        
                        # Calcular "pressão de saída"
                        pressao = oport['concursos_sem_sair'] / oport['media_intervalo']
                        if pressao >= 2.0:
                            print(f"       🔥 PRESSÃO ALTA: {pressao:.1f}x o intervalo normal!")
                        elif pressao >= 1.5:
                            print(f"       ⚡ PRESSÃO MÉDIA: {pressao:.1f}x o intervalo normal")
                        print()
                
                # Mostrar opções conservadoras
                if analise['conservadores']:
                    print(f"✅ OPÇÕES CONSERVADORAS ({posicao}):")
                    for i, cons in enumerate(analise['conservadores'], 1):
                        print(f"   {i}º: {posicao}={cons['valor']} - {cons['percentual']}% de frequência")
                        print(f"       Saiu há {cons['concursos_sem_sair']} concursos | Média: {cons['media_intervalo']}")
                        print()
                
                # Mostrar resumo executivo
                print(f"📋 RESUMO EXECUTIVO ({posicao}):")
                if analise['oportunidades']:
                    oport_top = analise['oportunidades'][0]
                    print(f"   🎯 OPORTUNIDADE TOP: {oport_top['valor']} ({oport_top['concursos_sem_sair']} sem sair)")
                
                if analise['conservadores']:
                    cons_top = analise['conservadores'][0]
                    print(f"   🛡️ CONSERVADOR TOP: {cons_top['valor']} ({cons_top['percentual']}% freq)")
        
        return relatorio
    
    def gerar_sugestoes_hibridas(self, relatorio):
        """Gera 3 estratégias: Ultra-Conservadora, Equilibrada, Oportunista"""
        print(f"\n" + "=" * 80)
        print("🚀 ESTRATÉGIAS HÍBRIDAS SUGERIDAS")
        print("=" * 80)
        
        estrategias = {
            'ultra_conservadora': {},
            'equilibrada': {},
            'oportunista': {}
        }
        
        for posicao, analise in relatorio.items():
            # Ultra Conservadora: apenas os mais frequentes e recentes
            if analise['conservadores']:
                estrategias['ultra_conservadora'][posicao] = [
                    analise['conservadores'][0]['valor']
                ]
            
            # Equilibrada: mix de conservador + 1 oportunidade moderada
            equilibrada_vals = []
            if analise['conservadores']:
                equilibrada_vals.append(analise['conservadores'][0]['valor'])
            
            # Adicionar oportunidade moderada (não muito arriscada)
            for oport in analise['oportunidades']:
                if oport['percentual'] >= 1.0:  # Pelo menos 1% de frequência
                    equilibrada_vals.append(oport['valor'])
                    break
            
            estrategias['equilibrada'][posicao] = equilibrada_vals
            
            # Oportunista: focar nas oportunidades em atraso
            oportunista_vals = []
            if analise['oportunidades']:
                oportunista_vals = [oport['valor'] for oport in analise['oportunidades'][:2]]
            
            # Se não há oportunidades viáveis, usar conservador
            if not oportunista_vals and analise['conservadores']:
                oportunista_vals = [analise['conservadores'][0]['valor']]
            
            estrategias['oportunista'][posicao] = oportunista_vals
        
        # Mostrar as 3 estratégias
        print(f"\n1️⃣ ESTRATÉGIA ULTRA-CONSERVADORA (Máxima Segurança):")
        self._mostrar_estrategia(estrategias['ultra_conservadora'], relatorio)
        
        print(f"\n2️⃣ ESTRATÉGIA EQUILIBRADA (Segurança + Oportunidade):")
        self._mostrar_estrategia(estrategias['equilibrada'], relatorio)
        
        print(f"\n3️⃣ ESTRATÉGIA OPORTUNISTA (Foco em Valores Atrasados):")
        self._mostrar_estrategia(estrategias['oportunista'], relatorio)
        
        return estrategias
    
    def _mostrar_estrategia(self, estrategia, relatorio):
        """Mostra detalhes de uma estratégia"""
        condicoes = []
        total_combinacoes_estimada = 1
        
        for posicao, valores in estrategia.items():
            if valores:
                condicao = f"{posicao} IN ({','.join(map(str, valores))})"
                condicoes.append(condicao)
                total_combinacoes_estimada *= len(valores)
                
                # Mostrar reasoning para cada valor
                for valor in valores:
                    # Encontrar info deste valor no relatório
                    for item in relatorio[posicao]['todos_valores']:
                        if item['valor'] == valor:
                            print(f"   • {posicao}={valor}: {item['perc']}% freq, {item['sem_sair']} sem sair ({item['status']})")
                            break
        
        if condicoes:
            print(f"\n   💻 SQL: WHERE {' AND '.join(condicoes)}")
            print(f"   📊 Combinações estimadas: ~{total_combinacoes_estimada:,} posições-chave")
        
        print()

def main():
    sistema = SistemaHibrido()
    
    # Gerar relatório completo
    relatorio = sistema.gerar_relatorio_completo()
    
    # Gerar estratégias híbridas
    estrategias = sistema.gerar_sugestoes_hibridas(relatorio)
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_hibrido_{timestamp}.txt"
    
    print(f"\n✅ Relatório completo será salvo em: {nome_arquivo}")
    print(f"🎯 Use essas informações para decisão manual inteligente!")
    
    # TODO: Implementar salvamento do relatório em arquivo

if __name__ == "__main__":
    main()