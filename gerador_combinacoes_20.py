#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 GERADOR DE COMBINAÇÕES LOTOFÁCIL - 20 NÚMEROS
===============================================
Cria tabela COMBINACOES_LOTOFACIL20 com TODAS as combinações possíveis
de 20 números únicos da Lotofácil (1 a 25).

Total de combinações possíveis: C(25,20) = 53.130 combinações
"""

import sys
import os
from itertools import combinations
import time
from datetime import datetime

# Adicionar path para database_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

    import pandas as pd
    MODO_BANCO = True
    print("✅ Modo BANCO DE DADOS - Conectando ao SQL Server")
except ImportError:
    MODO_BANCO = False
    print("⚠️ Modo LOCAL - Gerando arquivo CSV")
    # Importar pandas mesmo no modo local
    try:
        import pandas as pd
    except ImportError:
        print("❌ Pandas não disponível - salvando como CSV simples")
        pd = None

def calcular_total_combinacoes():
    """Calcula o total de combinações C(25,20)"""
    import math
    total = math.comb(25, 20)
    return total

def gerar_combinacoes_lotofacil20():
    """
    Gera todas as combinações possíveis de 20 números da Lotofácil
    """
    print("🔢 GERANDO COMBINAÇÕES DE 20 NÚMEROS...")
    
    # Números disponíveis na Lotofácil (1 a 25)
    numeros_lotofacil = list(range(1, 26))
    
    # Total de combinações
    total_combinacoes = calcular_total_combinacoes()
    print(f"📊 Total de combinações a gerar: {total_combinacoes:,}")
    
    # Gerar todas as combinações de 20 números
    print("⏳ Gerando combinações... (pode demorar alguns minutos)")
    
    combinacoes = []
    contador = 0
    inicio = time.time()
    
    for combo in combinations(numeros_lotofacil, 20):
        contador += 1
        
        # Progresso a cada 5000 combinações
        if contador % 5000 == 0:
            tempo_decorrido = time.time() - inicio
            percentual = (contador / total_combinacoes) * 100
            print(f"   📈 Progresso: {contador:,}/{total_combinacoes:,} ({percentual:.1f}%) - "
                  f"{tempo_decorrido:.1f}s")
        
        # Criar registro da combinação
        registro = {
            'ID': contador,
            'N1': combo[0], 'N2': combo[1], 'N3': combo[2], 'N4': combo[3], 'N5': combo[4],
            'N6': combo[5], 'N7': combo[6], 'N8': combo[7], 'N9': combo[8], 'N10': combo[9],
            'N11': combo[10], 'N12': combo[11], 'N13': combo[12], 'N14': combo[13], 'N15': combo[14],
            'N16': combo[15], 'N17': combo[16], 'N18': combo[17], 'N19': combo[18], 'N20': combo[19],
            
            # Campos calculados (serão preenchidos depois)
            'QtdeRepetidos': None,
            'RepetidosMesmaPosicao': None,
            
            # Metadata
            'DataGeracao': datetime.now(),
            'Processado': False
        }
        
        combinacoes.append(registro)
    
    tempo_total = time.time() - inicio
    print(f"✅ Geração concluída! {len(combinacoes):,} combinações em {tempo_total:.1f} segundos")
    
    return combinacoes

def criar_tabela_banco(db):
    """
    Cria a tabela COMBINACOES_LOTOFACIL20 no banco de dados
    """
    print("🗄️ CRIANDO TABELA NO BANCO DE DADOS...")
    
    sql_create_table = """
    IF OBJECT_ID('COMBINACOES_LOTOFACIL20', 'U') IS NOT NULL
        DROP TABLE COMBINACOES_LOTOFACIL20;
    
    CREATE TABLE COMBINACOES_LOTOFACIL20 (
        ID INT PRIMARY KEY,
        N1 TINYINT NOT NULL,
        N2 TINYINT NOT NULL,
        N3 TINYINT NOT NULL,
        N4 TINYINT NOT NULL,
        N5 TINYINT NOT NULL,
        N6 TINYINT NOT NULL,
        N7 TINYINT NOT NULL,
        N8 TINYINT NOT NULL,
        N9 TINYINT NOT NULL,
        N10 TINYINT NOT NULL,
        N11 TINYINT NOT NULL,
        N12 TINYINT NOT NULL,
        N13 TINYINT NOT NULL,
        N14 TINYINT NOT NULL,
        N15 TINYINT NOT NULL,
        N16 TINYINT NOT NULL,
        N17 TINYINT NOT NULL,
        N18 TINYINT NOT NULL,
        N19 TINYINT NOT NULL,
        N20 TINYINT NOT NULL,
        QtdeRepetidos TINYINT NULL,
        RepetidosMesmaPosicao TINYINT NULL,
        DataGeracao DATETIME2 DEFAULT GETDATE(),
        Processado BIT DEFAULT 0
    );
    
    -- Índices para otimização
    CREATE INDEX IX_COMBINACOES_20_Processado ON COMBINACOES_LOTOFACIL20(Processado);
    CREATE INDEX IX_COMBINACOES_20_QtdeRepetidos ON COMBINACOES_LOTOFACIL20(QtdeRepetidos);
    """
    
    try:
        db.execute_non_query(sql_create_table)
        print("✅ Tabela COMBINACOES_LOTOFACIL20 criada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False

def inserir_combinacoes_banco(db, combinacoes):
    """
    Insere as combinações no banco de dados em lotes
    """
    print("💾 INSERINDO COMBINAÇÕES NO BANCO...")
    
    # Inserir em lotes de 1000 para otimização
    tamanho_lote = 1000
    total_lotes = len(combinacoes) // tamanho_lote + (1 if len(combinacoes) % tamanho_lote > 0 else 0)
    
    for i in range(0, len(combinacoes), tamanho_lote):
        lote = combinacoes[i:i+tamanho_lote]
        
        # Preparar valores para INSERT
        valores = []
        for combo in lote:
            valores_linha = f"({combo['ID']}, " + \
                           ", ".join([str(combo[f'N{j}']) for j in range(1, 21)]) + \
                           ", NULL, NULL, GETDATE(), 0)"
            valores.append(valores_linha)
        
        sql_insert = f"""
        INSERT INTO COMBINACOES_LOTOFACIL20 
        (ID, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, 
         N11, N12, N13, N14, N15, N16, N17, N18, N19, N20, 
         QtdeRepetidos, RepetidosMesmaPosicao, DataGeracao, Processado)
        VALUES {', '.join(valores)};
        """
        
        try:
            db.execute_non_query(sql_insert)
            lote_num = (i // tamanho_lote) + 1
            print(f"   ✅ Lote {lote_num}/{total_lotes} inserido ({len(lote)} combinações)")
        except Exception as e:
            print(f"   ❌ Erro no lote {lote_num}: {e}")
            return False
    
    print("✅ Todas as combinações inseridas com sucesso!")
    return True

def salvar_csv_local(combinacoes):
    """
    Salva as combinações em arquivo CSV local
    """
    print("💾 SALVANDO EM ARQUIVO CSV...")
    
    arquivo = "COMBINACOES_LOTOFACIL20.csv"
    
    if pd is not None:
        # Usar pandas se disponível
        df = pd.DataFrame(combinacoes)
        df.to_csv(arquivo, index=False, encoding='utf-8')
    else:
        # Fallback: salvar manualmente
        import csv
        
        # Obter cabeçalhos
        if combinacoes:
            cabecalhos = list(combinacoes[0].keys())
            
            with open(arquivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=cabecalhos)
                writer.writeheader()
                writer.writerows(combinacoes)
    
    print(f"✅ Arquivo salvo: {arquivo}")
    print(f"📊 Total de linhas: {len(combinacoes):,}")
    
    return arquivo

def main():
    """
    Função principal
    """
    print("🚀 GERADOR DE COMBINAÇÕES LOTOFÁCIL - 20 NÚMEROS")
    print("="*60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Calcular total
    total = calcular_total_combinacoes()
    print(f"🎯 Objetivo: Gerar {total:,} combinações únicas de 20 números")
    print()
    
    # Confirmar execução
    print("▶️ Iniciando geração automática...")
    # resposta = input("⚠️  Esta operação pode demorar vários minutos. Continuar? (s/n): ")
    # if resposta.lower() != 's':
    #     print("❌ Operação cancelada.")
    #     return
    
    # Gerar combinações
    inicio_total = time.time()
    combinacoes = gerar_combinacoes_lotofacil20()
    
    if MODO_BANCO:
        # Modo banco de dados
        try:
            db = DatabaseConfig()
            
            # Criar tabela
            if criar_tabela_banco(db):
                # Inserir dados
                if inserir_combinacoes_banco(db, combinacoes):
                    print("🎊 SUCESSO TOTAL! Tabela criada e populada no banco!")
                else:
                    print("⚠️ Tabela criada, mas houve erros na inserção.")
            
        except Exception as e:
            print(f"❌ Erro de banco: {e}")
            print("🔄 Salvando em CSV como fallback...")
            salvar_csv_local(combinacoes)
    else:
        # Modo local (CSV)
        salvar_csv_local(combinacoes)
    
    tempo_total = time.time() - inicio_total
    print()
    print("="*60)
    print("🏆 RELATÓRIO FINAL:")
    print(f"📊 Combinações geradas: {len(combinacoes):,}")
    print(f"⏱️ Tempo total: {tempo_total:.1f} segundos ({tempo_total/60:.1f} minutos)")
    print(f"🎯 Taxa: {len(combinacoes)/tempo_total:.0f} combinações/segundo")
    print()
    
    if MODO_BANCO:
        print("✅ TABELA COMBINACOES_LOTOFACIL20 CRIADA E POPULADA!")
        print("🔄 Próximo passo: Calcular QtdeRepetidos e RepetidosMesmaPosicao")
    else:
        print("✅ ARQUIVO CSV GERADO!")
        print("💡 Para usar no banco, importe o CSV para COMBINACOES_LOTOFACIL20")
    
    print("="*60)

if __name__ == "__main__":
    main()
