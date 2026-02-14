#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ATUALIZADOR INCREMENTAL DE ACERTOS - LOTOFÁCIL 20 NÚMEROS
===========================================================
Processa APENAS o último concurso da tabela Resultados_INT
e atualiza os campos Acertos_15 e Acertos_14 incrementalmente.

EXECUÇÃO: Sempre que houver um novo concurso.
PRÉ-REQUISITO: Ter executado o calcular_acertos_inicial.py pelo menos uma vez.

Autor: AR CALHAU
Data: 09/09/2025
"""

import os
import sys
from datetime import datetime

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

def obter_ultimo_concurso_processado():
    """
    Verifica qual foi o último concurso processado
    (guardamos essa informação para controle)
    """
    try:
        db = DatabaseConfig()
        
        # Verificar se temos uma tabela de controle
        # Se não tiver, assumimos que nunca foi processado
        query_controle = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'CONTROLE_PROCESSAMENTO_ACERTOS')
        BEGIN
            CREATE TABLE CONTROLE_PROCESSAMENTO_ACERTOS (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                UltimoConcursoProcessado INT NOT NULL,
                DataProcessamento DATETIME DEFAULT GETDATE(),
                TipoProcessamento VARCHAR(20) NOT NULL
            );
            INSERT INTO CONTROLE_PROCESSAMENTO_ACERTOS (UltimoConcursoProcessado, TipoProcessamento) 
            VALUES (0, 'INICIAL');
        END
        """
        
        db.execute_command(query_controle)
        
        # Obter último concurso processado
        query_ultimo = """
        SELECT TOP 1 UltimoConcursoProcessado 
        FROM CONTROLE_PROCESSAMENTO_ACERTOS 
        ORDER BY ID DESC
        """
        
        resultado = db.execute_query_dataframe(query_ultimo)
        ultimo_processado = resultado.iloc[0]['UltimoConcursoProcessado'] if len(resultado) > 0 else 0
        
        return ultimo_processado
        
    except Exception as e:
        print(f"❌ Erro ao obter último processado: {e}")
        return 0

def obter_ultimo_concurso_disponivel():
    """
    Obtém o último concurso disponível na tabela Resultados_INT
    """
    try:
        db = DatabaseConfig()
        
        query = """
        SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        
        resultado = db.execute_query_dataframe(query)
        
        if len(resultado) == 0:
            return None
        
        concurso_data = resultado.iloc[0]
        return {
            'concurso': concurso_data['Concurso'],
            'numeros': [concurso_data[f'N{i}'] for i in range(1, 16)]
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter último concurso: {e}")
        return None

def processar_acertos_incremental(ultimo_concurso):
    """
    Processa apenas o último concurso e atualiza os acertos incrementalmente
    """
    print(f"\n🔄 PROCESSAMENTO INCREMENTAL - CONCURSO {ultimo_concurso['concurso']}")
    print("=" * 60)
    
    try:
        db = DatabaseConfig()
        numeros = ultimo_concurso['numeros']
        
        print(f"🎯 Concurso: {ultimo_concurso['concurso']}")
        print(f"📈 Números: {', '.join(map(str, numeros))}")
        
        # SQL para incrementar apenas as combinações que acertaram 15 ou 14
        sql_acertos_15 = f"""
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET Acertos_15 = Acertos_15 + 1
        WHERE (
            SELECT COUNT_BIG(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN ({','.join(map(str, numeros))})
        ) = 15
        """
        
        sql_acertos_14 = f"""
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
        SET Acertos_14 = Acertos_14 + 1
        WHERE (
            SELECT COUNT_BIG(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN ({','.join(map(str, numeros))})
        ) = 14
        """
        
        inicio = datetime.now()
        
        print("⏳ Atualizando acertos de 15...")
        sucesso_15 = db.execute_command(sql_acertos_15)
        
        print("⏳ Atualizando acertos de 14...")
        sucesso_14 = db.execute_command(sql_acertos_14)
        
        fim = datetime.now()
        tempo = (fim - inicio).total_seconds()
        
        if sucesso_15 and sucesso_14:
            # Verificar quantas combinações foram afetadas
            query_verificacao = f"""
            SELECT 
                SUM(CASE WHEN (
                    SELECT COUNT_BIG(*)
                    FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                 (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                    WHERE numero IN ({','.join(map(str, numeros))})
                ) = 15 THEN 1 ELSE 0 END) as combinacoes_15_acertos,
                SUM(CASE WHEN (
                    SELECT COUNT_BIG(*)
                    FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                 (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                    WHERE numero IN ({','.join(map(str, numeros))})
                ) = 14 THEN 1 ELSE 0 END) as combinacoes_14_acertos
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            """
            
            resultado = db.execute_query_dataframe(query_verificacao)
            stats = resultado.iloc[0]
            
            # Atualizar controle
            query_controle = f"""
            INSERT INTO CONTROLE_PROCESSAMENTO_ACERTOS (UltimoConcursoProcessado, TipoProcessamento)
            VALUES ({ultimo_concurso['concurso']}, 'INCREMENTAL')
            """
            
            db.execute_command(query_controle)
            
            print(f"\n✅ PROCESSAMENTO INCREMENTAL CONCLUÍDO!")
            print(f"⏱️ Tempo: {tempo:.2f} segundos")
            print(f"🎯 Combinações com 15 acertos: {int(stats['combinacoes_15_acertos']):,}")
            print(f"🎯 Combinações com 14 acertos: {int(stats['combinacoes_14_acertos']):,}")
            
            return True
            
        else:
            print("❌ Falha no processamento incremental")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def gerar_relatorio_incremental(ultimo_concurso):
    """
    Gera relatório do processamento incremental
    """
    print(f"\n📋 RELATÓRIO DO CONCURSO {ultimo_concurso['concurso']}")
    
    try:
        db = DatabaseConfig()
        numeros = ultimo_concurso['numeros']
        
        # Buscar combinações que acertaram 15 ou 14 neste concurso
        query_acertos = f"""
        SELECT 
            ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19, N20,
            Acertos_15, Acertos_14,
            (SELECT COUNT_BIG(*)
             FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                          (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
             WHERE numero IN ({','.join(map(str, numeros))})) as AcertosNesteConcurso
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        WHERE (
            SELECT COUNT_BIG(*)
            FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                         (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
            WHERE numero IN ({','.join(map(str, numeros))})
        ) >= 14
        ORDER BY AcertosNesteConcurso DESC
        """
        
        resultado = db.execute_query_dataframe(query_acertos)
        
        if len(resultado) > 0:
            print(f"\n🎯 COMBINAÇÕES QUE ACERTARAM 14+ NO CONCURSO {ultimo_concurso['concurso']}:")
            print("-" * 90)
            
            for _, row in resultado.iterrows():
                numeros_comb = [row[f'N{i}'] for i in range(1, 21)]
                nums_str = ','.join(f'{n:2d}' for n in numeros_comb)
                acertos_concurso = int(row['AcertosNesteConcurso'])
                
                emoji = "🥇" if acertos_concurso == 15 else "🥈"
                print(f"   {emoji} ID {row['ID']:6d}: {nums_str} | "
                      f"Acertos: {acertos_concurso} | Total 15: {row['Acertos_15']} | Total 14: {row['Acertos_14']}")
        else:
            print(f"\n💭 Nenhuma combinação acertou 14+ no concurso {ultimo_concurso['concurso']}")
        
        # Salvar relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo = f"relatorio_incremental_{ultimo_concurso['concurso']}_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(f"🔄 RELATÓRIO INCREMENTAL - CONCURSO {ultimo_concurso['concurso']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"📅 Processamento: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"🎯 Números sorteados: {', '.join(map(str, numeros))}\n\n")
            
            if len(resultado) > 0:
                f.write("COMBINAÇÕES COM 14+ ACERTOS:\n")
                f.write("-" * 40 + "\n")
                
                for _, row in resultado.iterrows():
                    numeros_comb = [row[f'N{i}'] for i in range(1, 21)]
                    nums_str = ' '.join(f'{n:2d}' for n in numeros_comb)
                    f.write(f"ID {row['ID']:6d}: {nums_str} | "
                           f"Acertos: {int(row['AcertosNesteConcurso'])} | "
                           f"Total 15: {row['Acertos_15']} | Total 14: {row['Acertos_14']}\n")
            else:
                f.write("Nenhuma combinação acertou 14+ neste concurso.\n")
        
        print(f"\n📁 Relatório salvo: {arquivo}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔄 ATUALIZADOR INCREMENTAL DE ACERTOS - LOTOFÁCIL 20")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    try:
        # 1. Verificar último concurso processado
        ultimo_processado = obter_ultimo_concurso_processado()
        print(f"📊 Último concurso processado: {ultimo_processado}")
        
        # 2. Obter último concurso disponível
        ultimo_disponivel = obter_ultimo_concurso_disponivel()
        if not ultimo_disponivel:
            print("❌ Nenhum concurso encontrado na tabela Resultados_INT")
            return
        
        print(f"📈 Último concurso disponível: {ultimo_disponivel['concurso']}")
        
        # 3. Verificar se há novos concursos
        if ultimo_disponivel['concurso'] <= ultimo_processado:
            print(f"✅ Nenhum concurso novo encontrado.")
            print(f"💡 Último processado: {ultimo_processado}")
            print(f"💡 Último disponível: {ultimo_disponivel['concurso']}")
            return
        
        # 4. Processar incrementalmente
        print(f"\n🆕 NOVO CONCURSO DETECTADO: {ultimo_disponivel['concurso']}")
        
        if processar_acertos_incremental(ultimo_disponivel):
            # 5. Gerar relatório
            gerar_relatorio_incremental(ultimo_disponivel)
            
            print(f"\n🎊 ATUALIZAÇÃO INCREMENTAL CONCLUÍDA!")
            print("=" * 50)
            print(f"✅ Concurso {ultimo_disponivel['concurso']} processado")
            print("✅ Acertos_15 e Acertos_14 atualizados")
            print("✅ Relatório gerado")
        else:
            print("❌ Falha na atualização incremental")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
