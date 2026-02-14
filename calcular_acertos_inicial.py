#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 CALCULADOR INICIAL DE ACERTOS - LOTOFÁCIL 20 NÚMEROS
======================================================
Processa TODOS os concursos históricos da tabela Resultados_INT
e calcula quantas vezes cada combinação de 20 números acertou 15 e 14.

EXECUÇÃO: Apenas uma vez para processar todo o histórico.
PRÓXIMAS: Usar o script incremental.

Autor: AR CALHAU
Data: 09/09/2025
"""

import os
import sys
from datetime import datetime
import math

# Adicionar path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotofacil_lite'))

try:
    from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

    print("✅ Importação OK")
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    sys.exit(1)

def verificar_estrutura_tabela():
    """
    Verifica se a tabela tem as novas colunas
    """
    print("🔍 Verificando estrutura da tabela...")
    
    try:
        db = DatabaseConfig()
        
        # Verificar se colunas existem
        query = """
        SELECT COUNT_BIG(*) as count
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
        AND COLUMN_NAME IN ('Acertos_15', 'Acertos_14')
        """
        
        resultado = db.execute_query_dataframe(query)
        colunas_existem = resultado.iloc[0]['count'] == 2
        
        if not colunas_existem:
            print("❌ Colunas Acertos_15 e Acertos_14 não encontradas!")
            print("💡 Execute primeiro: adicionar_colunas_acertos.sql")
            return False
        
        print("✅ Estrutura da tabela verificada")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def obter_estatisticas_iniciais():
    """
    Obtém estatísticas para dimensionar o processamento
    """
    print("📊 Coletando estatísticas...")
    
    try:
        db = DatabaseConfig()
        
        # Total de combinações
        total_combinacoes = db.contar_registros('COMBINACOES_LOTOFACIL20_COMPLETO')
        
        # Total de concursos
        total_concursos = db.contar_registros('Resultados_INT')
        
        # Range de concursos
        query_range = "SELECT MIN(Concurso) as min_conc, MAX(Concurso) as max_conc FROM Resultados_INT"
        resultado = db.execute_query_dataframe(query_range)
        min_conc = resultado.iloc[0]['min_conc']
        max_conc = resultado.iloc[0]['max_conc']
        
        print(f"📈 Total de combinações: {total_combinacoes:,}")
        print(f"🎯 Total de concursos: {total_concursos:,}")
        print(f"📅 Range: Concurso {min_conc} até {max_conc}")
        
        # Estimativa de tempo
        total_comparacoes = total_combinacoes * total_concursos
        print(f"⚡ Total de comparações: {total_comparacoes:,}")
        
        # Estimativa conservadora: 10.000 comparações por segundo
        tempo_estimado = total_comparacoes / 10000
        horas = int(tempo_estimado / 3600)
        minutos = int((tempo_estimado % 3600) / 60)
        
        print(f"⏱️ Tempo estimado: {horas}h {minutos}min")
        
        return {
            'total_combinacoes': total_combinacoes,
            'total_concursos': total_concursos,
            'min_concurso': min_conc,
            'max_concurso': max_conc,
            'tempo_estimado': tempo_estimado
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return None

def processar_acertos_historico():
    """
    Processa TODO o histórico de concursos
    Atualiza as colunas Acertos_15 e Acertos_14
    """
    print("\n🔄 INICIANDO PROCESSAMENTO HISTÓRICO...")
    print("=" * 60)
    
    try:
        db = DatabaseConfig()
        
        # SQL otimizado que conta acertos de uma vez
        # Para cada combinação, conta quantos concursos tiveram 15 e 14 acertos
        sql_update = """
        UPDATE c SET
            Acertos_15 = (
                SELECT COUNT_BIG(*)
                FROM Resultados_INT r
                WHERE (
                    SELECT COUNT_BIG(*)
                    FROM (VALUES (c.N1),(c.N2),(c.N3),(c.N4),(c.N5),(c.N6),(c.N7),(c.N8),(c.N9),(c.N10),
                                 (c.N11),(c.N12),(c.N13),(c.N14),(c.N15),(c.N16),(c.N17),(c.N18),(c.N19),(c.N20)) AS comb(numero)
                    WHERE numero IN (r.N1, r.N2, r.N3, r.N4, r.N5, r.N6, r.N7, r.N8, r.N9, r.N10, r.N11, r.N12, r.N13, r.N14, r.N15)
                ) = 15
            ),
            Acertos_14 = (
                SELECT COUNT_BIG(*)
                FROM Resultados_INT r
                WHERE (
                    SELECT COUNT_BIG(*)
                    FROM (VALUES (c.N1),(c.N2),(c.N3),(c.N4),(c.N5),(c.N6),(c.N7),(c.N8),(c.N9),(c.N10),
                                 (c.N11),(c.N12),(c.N13),(c.N14),(c.N15),(c.N16),(c.N17),(c.N18),(c.N19),(c.N20)) AS comb(numero)
                    WHERE numero IN (r.N1, r.N2, r.N3, r.N4, r.N5, r.N6, r.N7, r.N8, r.N9, r.N10, r.N11, r.N12, r.N13, r.N14, r.N15)
                ) = 14
            )
        FROM COMBINACOES_LOTOFACIL20_COMPLETO c
        """
        
        print("⏳ Executando cálculo de acertos para TODO o histórico...")
        print("💡 Isso pode demorar bastante tempo (estimativa mostrada anteriormente)...")
        print("🔄 Aguarde... (não interrompa o processamento)")
        
        inicio = datetime.now()
        
        # Executar a atualização
        sucesso = db.execute_command(sql_update)
        
        fim = datetime.now()
        tempo_total = (fim - inicio).total_seconds()
        
        if sucesso:
            print(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
            print(f"⏱️ Tempo real: {tempo_total/60:.1f} minutos")
            
            # Verificar resultados
            query_stats = """
            SELECT 
                COUNT(*) as total_processadas,
                SUM(Acertos_15) as total_acertos_15,
                SUM(Acertos_14) as total_acertos_14,
                AVG(CAST(Acertos_15 AS FLOAT)) as media_acertos_15,
                AVG(CAST(Acertos_14 AS FLOAT)) as media_acertos_14,
                MAX(Acertos_15) as max_acertos_15,
                MAX(Acertos_14) as max_acertos_14
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            """
            
            stats = db.execute_query_dataframe(query_stats).iloc[0]
            
            print(f"\n📊 ESTATÍSTICAS FINAIS:")
            print("=" * 40)
            print(f"📈 Combinações processadas: {int(stats['total_processadas']):,}")
            print(f"🎯 Total de acertos 15: {int(stats['total_acertos_15']):,}")
            print(f"🎯 Total de acertos 14: {int(stats['total_acertos_14']):,}")
            print(f"📊 Média acertos 15: {stats['media_acertos_15']:.3f}")
            print(f"📊 Média acertos 14: {stats['media_acertos_14']:.3f}")
            print(f"🏆 Máximo acertos 15: {int(stats['max_acertos_15'])}")
            print(f"🏆 Máximo acertos 14: {int(stats['max_acertos_14'])}")
            
            return True
            
        else:
            print("❌ Falha no processamento")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def gerar_relatorio_top_acertos():
    """
    Gera relatório com as combinações que mais acertaram
    """
    print("\n📋 GERANDO RELATÓRIO TOP ACERTOS...")
    
    try:
        db = DatabaseConfig()
        
        # Top 20 combinações com mais acertos 15
        query_top_15 = """
        SELECT TOP 20 
            ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19, N20,
            Acertos_15, Acertos_14
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        WHERE Acertos_15 > 0
        ORDER BY Acertos_15 DESC, Acertos_14 DESC
        """
        
        resultado = db.execute_query_dataframe(query_top_15)
        
        print(f"\n🏆 TOP 20 COMBINAÇÕES COM MAIS ACERTOS 15:")
        print("-" * 80)
        
        for _, row in resultado.iterrows():
            numeros = [row[f'N{i}'] for i in range(1, 21)]
            nums_str = ','.join(f'{n:2d}' for n in numeros)
            print(f"   ID {row['ID']:6d}: {nums_str} | 15️⃣:{row['Acertos_15']:2d} | 14️⃣:{row['Acertos_14']:2d}")
        
        # Distribuição de acertos
        query_dist = """
        SELECT 
            Acertos_15,
            COUNT(*) as quantidade
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        WHERE Acertos_15 >= 0
        GROUP BY Acertos_15
        ORDER BY Acertos_15 DESC
        """
        
        distribuicao = db.execute_query_dataframe(query_dist)
        
        print(f"\n📊 DISTRIBUIÇÃO DE ACERTOS 15:")
        print("-" * 30)
        for _, row in distribuicao.iterrows():
            if row['Acertos_15'] > 0:
                print(f"   {row['Acertos_15']:2d} acertos: {row['quantidade']:6,} combinações")
        
        # Salvar relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_relatorio = f"relatorio_acertos_historico_{timestamp}.txt"
        
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write("🎯 RELATÓRIO ACERTOS HISTÓRICO - COMBINAÇÕES LOTOFÁCIL 20\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"📅 Processamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"📊 Baseado em todo o histórico da tabela Resultados_INT\n\n")
            
            f.write("TOP 20 COMBINAÇÕES COM MAIS ACERTOS 15:\n")
            f.write("-" * 50 + "\n")
            
            for _, row in resultado.iterrows():
                numeros = [row[f'N{i}'] for i in range(1, 21)]
                nums_str = ' '.join(f'{n:2d}' for n in numeros)
                f.write(f"ID {row['ID']:6d}: {nums_str} | 15:{row['Acertos_15']:2d} | 14:{row['Acertos_14']:2d}\n")
        
        print(f"\n📁 Relatório salvo: {arquivo_relatorio}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🎯 CALCULADOR INICIAL DE ACERTOS - LOTOFÁCIL 20 NÚMEROS")
    print("=" * 65)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # 1. Verificar estrutura
    if not verificar_estrutura_tabela():
        return
    
    # 2. Obter estatísticas
    stats = obter_estatisticas_iniciais()
    if not stats:
        return
    
    # 3. Aviso sobre tempo
    if stats['tempo_estimado'] > 3600:  # Mais de 1 hora
        print(f"\n⚠️  ATENÇÃO:")
        print(f"   Este processamento pode demorar mais de 1 hora!")
        print(f"   São {stats['total_combinacoes']:,} combinações × {stats['total_concursos']:,} concursos")
        print(f"   = {stats['total_combinacoes'] * stats['total_concursos']:,} comparações")
        print()
        
        resposta = input("🤔 Tem certeza que quer continuar? (s/n): ").strip().lower()
        if not resposta.startswith('s'):
            print("❌ Processamento cancelado.")
            return
    
    # 4. Executar processamento
    print(f"\n🚀 INICIANDO PROCESSAMENTO COMPLETO...")
    print(f"⚡ Processando {stats['total_combinacoes']:,} combinações...")
    print(f"📊 Analisando {stats['total_concursos']:,} concursos...")
    
    if processar_acertos_historico():
        # 5. Gerar relatório
        gerar_relatorio_top_acertos()
        
        print("\n" + "=" * 65)
        print("🎊 PROCESSAMENTO HISTÓRICO CONCLUÍDO COM SUCESSO!")
        print("=" * 65)
        print("✅ Todas as combinações processadas")
        print("✅ Colunas Acertos_15 e Acertos_14 atualizadas")
        print("✅ Relatório detalhado gerado")
        print()
        print("🚀 PRÓXIMO PASSO: Use o script incremental para manter atualizado")
        print("   (processará apenas novos concursos)")
        print("=" * 65)
    
    else:
        print("\n❌ PROCESSAMENTO FALHOU!")
        print("💡 Verifique os logs de erro e tente novamente.")

if __name__ == "__main__":
    main()
