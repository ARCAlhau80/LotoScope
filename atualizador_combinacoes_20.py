#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ATUALIZADOR COMBINAÇÕES LOTOFÁCIL20 - SEGUNDA ETAPA
=====================================================
Calcula e atualiza os campos QtdeRepetidos e RepetidosMesmaPosicao
na tabela COMBINACOES_LOTOFACIL20 baseado no último concurso da 
tabela Resultados_INT.

Baseado na lógica do menu_lotofacil.py - atualizar_campos_repetidos_combinacoes()
"""

import sys
import os
from datetime import datetime

# Adicionar path para database_config
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotofacil_lite'))

try:
    from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

    MODO_BANCO = True
    print("✅ Conectado ao SQL Server")
except ImportError:
    MODO_BANCO = False
    print("❌ Não foi possível conectar ao banco de dados")
    sys.exit(1)

def obter_ultimo_concurso():
    """
    Obtém os dados do último concurso da tabela Resultados_INT
    """
    try:
        db = DatabaseConfig()
        
        query = """
        SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        
        resultado = db.execute_query(query)
        
        if len(resultado) == 0:
            print("❌ Nenhum concurso encontrado na tabela Resultados_INT")
            return None
            
        concurso_data = resultado.iloc[0]
        ultimo_concurso = {
            'concurso': concurso_data['Concurso'],
            'numeros': [concurso_data[f'N{i}'] for i in range(1, 16)]
        }
        
        print(f"📊 Último concurso encontrado: {ultimo_concurso['concurso']}")
        print(f"🎯 Números: {', '.join(map(str, ultimo_concurso['numeros']))}")
        
        return ultimo_concurso
        
    except Exception as e:
        print(f"❌ Erro ao obter último concurso: {e}")
        return None

def verificar_tabela_combinacoes():
    """
    Verifica se a tabela COMBINACOES_LOTOFACIL20_COMPLETO existe e tem registros
    """
    try:
        db = DatabaseConfig()
        
        # Verifica se tabela existe
        query_exists = """
        SELECT COUNT_BIG(*) as existe
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
        """
        
        resultado = db.execute_query(query_exists)
        existe = resultado.iloc[0]['existe'] > 0
        
        if not existe:
            print("❌ Tabela COMBINACOES_LOTOFACIL20_COMPLETO não encontrada!")
            print("💡 Execute primeiro o gerador_combinacoes_20.py")
            return False
        
        # Conta registros
        query_count = "SELECT COUNT_BIG(*) as total FROM COMBINACOES_LOTOFACIL20_COMPLETO"
        resultado = db.execute_query(query_count)
        total = resultado.iloc[0]['total']
        
        print(f"✅ Tabela COMBINACOES_LOTOFACIL20_COMPLETO encontrada")
        print(f"📊 Total de combinações: {total:,}")
        
        # Verifica quantas já estão processadas
        query_processadas = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN QtdeRepetidos IS NOT NULL THEN 1 ELSE 0 END) as processadas
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        """
        
        resultado = db.execute_query(query_processadas)
        stats = resultado.iloc[0]
        
        print(f"📈 Já processadas: {stats['processadas']:,} / {stats['total']:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        return False

def atualizar_campos_repetidos(ultimo_concurso):
    """
    Atualiza os campos QtdeRepetidos e RepetidosMesmaPosicao
    baseado no último concurso
    """
    print("\n🔄 ATUALIZANDO CAMPOS DE REPETIÇÃO...")
    print("="*50)
    
    try:
        db = DatabaseConfig()
        numeros_ultimo = ultimo_concurso['numeros']
        
        print(f"📊 Referência: Concurso {ultimo_concurso['concurso']}")
        print(f"🎯 Números de referência: {', '.join(map(str, numeros_ultimo))}")
        print()
        
        # SQL para atualizar TODAS as combinações de uma vez
        # Usa a mesma lógica do menu_lotofacil.py mas adaptada para 20 números
        sql_update = """
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO SET
            QtdeRepetidos = (
                SELECT COUNT_BIG(*)
                FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                             (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS combinacao(numero)
                WHERE numero IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ),
            RepetidosMesmaPosicao = (
                CASE WHEN N1 = ? THEN 1 ELSE 0 END +
                CASE WHEN N2 = ? THEN 1 ELSE 0 END +
                CASE WHEN N3 = ? THEN 1 ELSE 0 END +
                CASE WHEN N4 = ? THEN 1 ELSE 0 END +
                CASE WHEN N5 = ? THEN 1 ELSE 0 END +
                CASE WHEN N6 = ? THEN 1 ELSE 0 END +
                CASE WHEN N7 = ? THEN 1 ELSE 0 END +
                CASE WHEN N8 = ? THEN 1 ELSE 0 END +
                CASE WHEN N9 = ? THEN 1 ELSE 0 END +
                CASE WHEN N10 = ? THEN 1 ELSE 0 END +
                CASE WHEN N11 = ? THEN 1 ELSE 0 END +
                CASE WHEN N12 = ? THEN 1 ELSE 0 END +
                CASE WHEN N13 = ? THEN 1 ELSE 0 END +
                CASE WHEN N14 = ? THEN 1 ELSE 0 END +
                CASE WHEN N15 = ? THEN 1 ELSE 0 END +
                CASE WHEN N16 = ? THEN 1 ELSE 0 END +
                CASE WHEN N17 = ? THEN 1 ELSE 0 END +
                CASE WHEN N18 = ? THEN 1 ELSE 0 END +
                CASE WHEN N19 = ? THEN 1 ELSE 0 END +
                CASE WHEN N20 = ? THEN 1 ELSE 0 END
            ),
            DataGeracao = GETDATE(),
            Processado = 1
        """
        
        # Preparar parâmetros
        # 15 parâmetros para QtdeRepetidos (números do último concurso)
        # 20 parâmetros para RepetidosMesmaPosicao (números do último concurso repetidos)
        params = (
            # QtdeRepetidos - números do último concurso (15 números)
            *numeros_ultimo,
            # RepetidosMesmaPosicao - números para comparar em cada posição (20 posições)
            # Como só temos 15 números do concurso, usamos os primeiros 15 para as primeiras 15 posições
            # e colocamos 0 nas posições 16-20 (que nunca vão coincidir)
            *numeros_ultimo,  # Posições 1-15
            0, 0, 0, 0, 0     # Posições 16-20 (nunca vão coincidir)
        )
        
        print("⏳ Executando atualização em massa...")
        print("💡 Isso pode demorar alguns minutos para 53.130 combinações...")
        
        inicio = datetime.now()
        
        # Executa a atualização
        db.execute_non_query(sql_update, params)
        
        fim = datetime.now()
        tempo_total = (fim - inicio).total_seconds()
        
        # Verifica quantos registros foram atualizados
        query_verificacao = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN QtdeRepetidos IS NOT NULL THEN 1 ELSE 0 END) as processadas,
            AVG(CAST(QtdeRepetidos AS FLOAT)) as media_repetidos,
            MAX(QtdeRepetidos) as max_repetidos,
            MIN(QtdeRepetidos) as min_repetidos
        FROM COMBINACOES_LOTOFACIL20
        """
        
        resultado = db.execute_query(query_verificacao)
        stats = resultado.iloc[0]
        
        print("\n" + "="*50)
        print("🏆 ATUALIZAÇÃO CONCLUÍDA!")
        print("="*50)
        print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
        print(f"📊 Registros processados: {stats['processadas']:,} / {stats['total']:,}")
        print(f"📈 Média de repetições: {stats['media_repetidos']:.2f}")
        print(f"📈 Máximo de repetições: {stats['max_repetidos']}")
        print(f"📈 Mínimo de repetições: {stats['min_repetidos']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar campos: {e}")
        return False

def gerar_relatorio_final():
    """
    Gera relatório final com estatísticas das combinações processadas
    """
    print("\n📊 GERANDO RELATÓRIO FINAL...")
    print("="*40)
    
    try:
        db = DatabaseConfig()
        
        # Estatísticas detalhadas
        query_stats = """
        SELECT 
            QtdeRepetidos,
            COUNT(*) as quantidade,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        WHERE QtdeRepetidos IS NOT NULL
        GROUP BY QtdeRepetidos
        ORDER BY QtdeRepetidos
        """
        
        resultado = db.execute_query(query_stats)
        
        print("📈 DISTRIBUIÇÃO DE REPETIÇÕES:")
        print("-" * 40)
        for _, row in resultado.iterrows():
            print(f"   {row['QtdeRepetidos']:2d} repetições: {row['quantidade']:6,} combinações ({row['percentual']:5.2f}%)")
        
        # Top 10 combinações com mais repetições
        query_top = """
        SELECT TOP 10 
            ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19, N20,
            QtdeRepetidos, RepetidosMesmaPosicao
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        WHERE QtdeRepetidos IS NOT NULL
        ORDER BY QtdeRepetidos DESC, RepetidosMesmaPosicao DESC
        """
        
        resultado = db.execute_query(query_top)
        
        print(f"\n🏆 TOP 10 COMBINAÇÕES COM MAIS REPETIÇÕES:")
        print("-" * 60)
        for _, row in resultado.iterrows():
            numeros = [row[f'N{i}'] for i in range(1, 21)]
            print(f"   ID {row['ID']:6d}: {','.join(f'{n:2d}' for n in numeros)} | "
                  f"Rep: {row['QtdeRepetidos']:2d} | MesmaPos: {row['RepetidosMesmaPosicao']:2d}")
        
        # Salvar relatório em arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_relatorio = f"relatorio_combinacoes_20_{timestamp}.txt"
        
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write("🎯 RELATÓRIO FINAL - COMBINAÇÕES LOTOFÁCIL 20 NÚMEROS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"📊 Total de combinações: {len(resultado):,}\n")
            f.write(f"🎯 Baseado no último concurso processado\n\n")
            
            f.write("DISTRIBUIÇÃO DE REPETIÇÕES:\n")
            f.write("-" * 30 + "\n")
            
            query_all = "SELECT QtdeRepetidos, COUNT(*) as qtd FROM COMBINACOES_LOTOFACIL20_COMPLETO GROUP BY QtdeRepetidos ORDER BY QtdeRepetidos"
            all_stats = db.execute_query(query_all)
            
            for _, row in all_stats.iterrows():
                f.write(f"{row['QtdeRepetidos']:2d} repetições: {row['qtd']:6,} combinações\n")
        
        print(f"\n📁 Relatório salvo: {arquivo_relatorio}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔄 ATUALIZADOR COMBINAÇÕES LOTOFÁCIL20 - SEGUNDA ETAPA")
    print("=" * 65)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # 1. Verificar se tabela existe
    if not verificar_tabela_combinacoes():
        return
    
    # 2. Obter último concurso
    ultimo_concurso = obter_ultimo_concurso()
    if not ultimo_concurso:
        return
    
    # 3. Confirmar execução
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   Esta operação vai calcular QtdeRepetidos e RepetidosMesmaPosicao")
    print(f"   para TODAS as 53.130 combinações baseado no concurso {ultimo_concurso['concurso']}")
    print(f"   Isso pode demorar alguns minutos.")
    print()
    
    resposta = input("🤔 Continuar? (s/n): ").strip().lower()
    if not resposta.startswith('s'):
        print("❌ Operação cancelada.")
        return
    
    # 4. Atualizar campos
    if atualizar_campos_repetidos(ultimo_concurso):
        # 5. Gerar relatório
        gerar_relatorio_final()
        
        print("\n" + "=" * 65)
        print("🎊 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 65)
        print("✅ Tabela COMBINACOES_LOTOFACIL20_COMPLETO totalmente atualizada")
        print("✅ Todos os campos calculados:")
        print("   • QtdeRepetidos: quantos números repetem do último concurso")
        print("   • RepetidosMesmaPosicao: quantos números repetem na mesma posição")
        print("✅ Relatório detalhado gerado")
        print()
        print("🚀 PRÓXIMO PASSO: A tabela está pronta para uso em análises e predições!")
        print("=" * 65)
    
    else:
        print("\n❌ PROCESSO FALHOU!")
        print("💡 Verifique os logs de erro acima e tente novamente.")

if __name__ == "__main__":
    main()
