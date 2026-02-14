#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ATUALIZADOR SIMPLES - COMBINAÇÕES LOTOFÁCIL20 
================================================
Versão simplificada para atualizar QtdeRepetidos e RepetidosMesmaPosicao
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

def main():
    print("🔄 ATUALIZADOR COMBINAÇÕES LOTOFÁCIL20")
    print("=" * 50)
    
    try:
        # Conectar
        db = DatabaseConfig()
        print("✅ Configuração carregada")
        
        # Testar conexão
        if not db.test_connection():
            print("❌ Falha na conexão")
            return
        
        print("✅ Conexão estabelecida")
        
        # Verificar tabela
        if not db.verificar_tabela_existe('COMBINACOES_LOTOFACIL20_COMPLETO'):
            print("❌ Tabela COMBINACOES_LOTOFACIL20_COMPLETO não encontrada")
            return
        
        total = db.contar_registros('COMBINACOES_LOTOFACIL20_COMPLETO')
        print(f"📊 Total de combinações: {total:,}")
        
        # Obter último concurso
        query_ultimo = """
        SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        
        resultado = db.execute_query_dataframe(query_ultimo)
        
        if resultado is None or len(resultado) == 0:
            print("❌ Nenhum concurso encontrado")
            return
        
        concurso_data = resultado.iloc[0]
        ultimo_concurso = concurso_data['Concurso']
        numeros = [concurso_data[f'N{i}'] for i in range(1, 16)]
        
        print(f"🎯 Último concurso: {ultimo_concurso}")
        print(f"📈 Números: {', '.join(map(str, numeros))}")
        
        # Confirmar
        resposta = input("\n🤔 Continuar com a atualização? (s/n): ").strip().lower()
        if not resposta.startswith('s'):
            print("❌ Cancelado")
            return
        
        print("\n⏳ Iniciando atualização...")
        inicio = datetime.now()
        
        # SQL de atualização - versão mais simples
        sql_update = f"""
        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO SET
            QtdeRepetidos = (
                SELECT COUNT_BIG(*)
                FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                             (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS combinacao(numero)
                WHERE numero IN ({','.join(map(str, numeros))})
            ),
            RepetidosMesmaPosicao = (
                CASE WHEN N1 = {numeros[0]} THEN 1 ELSE 0 END +
                CASE WHEN N2 = {numeros[1]} THEN 1 ELSE 0 END +
                CASE WHEN N3 = {numeros[2]} THEN 1 ELSE 0 END +
                CASE WHEN N4 = {numeros[3]} THEN 1 ELSE 0 END +
                CASE WHEN N5 = {numeros[4]} THEN 1 ELSE 0 END +
                CASE WHEN N6 = {numeros[5]} THEN 1 ELSE 0 END +
                CASE WHEN N7 = {numeros[6]} THEN 1 ELSE 0 END +
                CASE WHEN N8 = {numeros[7]} THEN 1 ELSE 0 END +
                CASE WHEN N9 = {numeros[8]} THEN 1 ELSE 0 END +
                CASE WHEN N10 = {numeros[9]} THEN 1 ELSE 0 END +
                CASE WHEN N11 = {numeros[10]} THEN 1 ELSE 0 END +
                CASE WHEN N12 = {numeros[11]} THEN 1 ELSE 0 END +
                CASE WHEN N13 = {numeros[12]} THEN 1 ELSE 0 END +
                CASE WHEN N14 = {numeros[13]} THEN 1 ELSE 0 END +
                CASE WHEN N15 = {numeros[14]} THEN 1 ELSE 0 END
            )
        """
        
        # Executar
        sucesso = db.execute_command(sql_update)
        
        fim = datetime.now()
        tempo = (fim - inicio).total_seconds()
        
        if sucesso:
            print(f"✅ Atualização concluída em {tempo:.1f} segundos")
            
            # Verificar resultados
            query_stats = """
            SELECT 
                COUNT(*) as total,
                AVG(CAST(QtdeRepetidos AS FLOAT)) as media,
                MAX(QtdeRepetidos) as maximo,
                MIN(QtdeRepetidos) as minimo
            FROM COMBINACOES_LOTOFACIL20_COMPLETO
            WHERE QtdeRepetidos IS NOT NULL
            """
            
            stats = db.execute_query_dataframe(query_stats).iloc[0]
            
            print(f"📊 Estatísticas:")
            print(f"   • Total processado: {int(stats['total']):,}")
            print(f"   • Média repetições: {stats['media']:.2f}")
            print(f"   • Máximo: {int(stats['maximo'])}")
            print(f"   • Mínimo: {int(stats['minimo'])}")
            
            print("\n🎊 SUCESSO! Tabela COMBINACOES_LOTOFACIL20_COMPLETO atualizada!")
            
        else:
            print("❌ Falha na atualização")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
