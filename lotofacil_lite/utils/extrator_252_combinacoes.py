#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 EXTRATOR DAS 252 COMBINAÇÕES DE 20 NÚMEROS
==============================================

Script para extrair suas 252 combinações que batem 15 números
da tabela COMBINACOES_LOTOFACIL20_COMPLETO e salvar em TXT.

Autor: AR CALHAU
Data: 12 de Setembro 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import conectar_banco

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import time
from pathlib import Path

def extrair_252_combinacoes():
    """
    Extrai as 252 combinações que batem 15 números e salva em TXT
    """
    print("🎯" * 25)
    print("🎯 EXTRATOR DAS 252 COMBINAÇÕES DE 20 NÚMEROS")
    print("🎯" * 25)
    
    try:
        # Conectar ao banco
        print("🔌 Conectando ao banco de dados...")
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Query para buscar as 252 combinações
        query = """
        SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
               N11, N12, N13, N14, N15, N16, N17, N18, N19, N20
        FROM COMBINACOES_LOTOFACIL20_COMPLETO
        WHERE QtdeRepetidos = 15
        ORDER BY CombinacaoId
        """
        
        print("🔍 Extraindo combinações que batem 15 números...")
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        print(f"✅ {len(resultados)} combinações encontradas")
        
        if len(resultados) != 252:
            print(f"⚠️ ATENÇÃO: Esperava 252 combinações, mas encontrou {len(resultados)}")
            resposta = input("Deseja continuar mesmo assim? (s/n): ").strip().lower()
            if resposta != 's':
                print("❌ Operação cancelada pelo usuário")
                return None
        
        # Gerar nome do arquivo
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"combinacoes_252_20numeros_{timestamp}.txt"
        caminho_arquivo = Path(__file__).parent / nome_arquivo
        
        # Salvar no arquivo
        print(f"💾 Salvando em: {nome_arquivo}")
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("# COMBINAÇÕES DE 20 NÚMEROS QUE BATEM 15 NÚMEROS\n")
            f.write("# =============================================\n")
            f.write(f"# Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"# Total de combinações: {len(resultados)}\n")
            f.write("# Fonte: COMBINACOES_LOTOFACIL20_COMPLETO (QtdeRepetidos = 15)\n")
            f.write("# Formato: 20 números separados por vírgula (1-25)\n")
            f.write("# =============================================\n")
            f.write("\n")
            
            # Escrever combinações
            for resultado in resultados:
                # Extrair os 20 números da linha
                numeros = [str(resultado[i]) for i in range(20)]
                linha = ','.join(numeros)
                f.write(f"{linha}\n")
        
        cursor.close()
        conn.close()
        
        print(f"✅ Arquivo criado com sucesso: {caminho_arquivo}")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1️⃣ Execute o gerador_15_rankeado.py")
        print(f"2️⃣ Use o arquivo: {nome_arquivo}")
        print("3️⃣ Aguarde o processamento das 3.268.760 combinações de 15 números")
        print("4️⃣ Receba o ranking da MAIS para MENOS provável!")
        
        return caminho_arquivo
        
    except Exception as e:
        print(f"❌ Erro durante a extração: {e}")
        return None

def main():
    """
    Função principal
    """
    print("🎯 EXTRATOR DAS 252 COMBINAÇÕES DE 20 NÚMEROS")
    print("=" * 55)
    print("💡 Este script extrai suas 252 combinações que batem")
    print("   15 números e salva em formato TXT para usar no")
    print("   gerador de combinações de 15 números rankeadas.")
    print()
    
    resposta = input("🚀 Deseja extrair as 252 combinações? (s/n): ").strip().lower()
    
    if resposta == 's':
        extrair_252_combinacoes()
    else:
        print("❌ Operação cancelada pelo usuário")

if __name__ == "__main__":
    main()
