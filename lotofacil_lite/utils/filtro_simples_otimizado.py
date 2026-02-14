#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 FILTRO INTERSECÇÃO SIMPLES E OTIMIZADO

Versão simplificada e super otimizada para filtrar combinações
de 15 números que tenham 11-15 números em comum com pelo menos
uma combinação de 20 números.

OTIMIZAÇÕES IMPLEMENTADAS:
- Sets para intersecção O(1)
- Early termination quando encontra match
- Carregamento único de dados
- Progress tracking inteligente
- Gestão de memória otimizada

Autor: AR CALHAU
Data: 10 de Setembro 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import time
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


def filtrar_combinacoes_intersecao():
    """
    Executa o filtro de intersecção otimizado
    """
    print("🚀 FILTRO DE INTERSECÇÃO - VERSÃO OTIMIZADA")
    print("=" * 60)
    
    inicio_total = time.time()
    
    # 1. CARREGAR DADOS
    print("📊 Carregando dados das tabelas...")
    inicio_carregamento = time.time()
    
    # Combinações de 15 números
    query_15 = "SELECT ID, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM COMBINACOES_LOTOFACIL ORDER BY ID"
    combo_15_data = db_config.execute_query(query_15)
    
    if not combo_15_data:
        print("❌ Erro ao carregar COMBINACOES_LOTOFACIL!")
        return
    
    print(f"✅ {len(combo_15_data):,} combinações de 15 números carregadas")
    
    # Combinações de 20 números - APENAS as que acertaram 15 números (QtdeRepetidos = 15)
    query_20 = """
        SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15,N16,N17,N18,N19,N20 
        FROM COMBINACOES_LOTOFACIL20_COMPLETO 
        WHERE QtdeRepetidos = 15
    """
    combo_20_data = db_config.execute_query(query_20)
    
    if not combo_20_data:
        print("❌ Nenhuma combinação de 20 números com QtdeRepetidos = 15 encontrada!")
        print("💡 Isso significa que nenhuma combinação de 20 acertou exatamente 15 números no último concurso")
        return
    
    print(f"✅ {len(combo_20_data):,} combinações de 20 números com QtdeRepetidos = 15 carregadas")
    
    # Converter combinações de 20 para sets (OTIMIZAÇÃO CRÍTICA)
    print("⚡ Convertendo combinações de 20 para sets...")
    combo_20_sets = []
    for combo_row in combo_20_data:
        # combo_row já é uma tupla com N1,N2,...,N20
        numeros = set(combo_row)  # Converte diretamente para set
        combo_20_sets.append(numeros)
    
    fim_carregamento = time.time()
    print(f"✅ Dados preparados em {fim_carregamento - inicio_carregamento:.2f} segundos")
    print(f"🔍 Realizará {len(combo_15_data):,} × {len(combo_20_sets):,} = {len(combo_15_data) * len(combo_20_sets):,} comparações")
    print(f"🎯 CRITÉRIO: Combinações de 15 números que tenham 14-15 números em comum")
    print(f"📊 COM: {len(combo_20_sets):,} combinações de 20 números que acertaram EXATAMENTE 15 no último concurso")
    print(f"⚡ FILTRO MAIS SELETIVO: Mudou de 11-15 para 14-15")
    
    # 2. PROCESSAMENTO OTIMIZADO
    print("\n🚀 Iniciando processamento otimizado...")
    print("-" * 60)
    
    resultados_validos = []
    total_combinacoes = len(combo_15_data)
    inicio_processamento = time.time()
    
    # Configurações de progresso
    intervalo_progresso = max(1000, total_combinacoes // 100)  # Progresso a cada 1%
    proximo_relatorio = intervalo_progresso
    
    for i, combo_15_row in enumerate(combo_15_data):
        # combo_15_row[0] é o ID, combo_15_row[1:] são N1,N2,...,N15
        combo_15_id = combo_15_row[0]
        combo_15_numeros = combo_15_row[1:]  # N1,N2,...,N15
        combo_15_set = set(combo_15_numeros)
        
        # Verificar intersecção com QUALQUER combinação de 20
        encontrou_valida = False
        melhor_intersecao = 0
        
        for combo_20_set in combo_20_sets:
            intersecao = len(combo_15_set & combo_20_set)
            
            if intersecao > melhor_intersecao:
                melhor_intersecao = intersecao
            
            # EARLY TERMINATION - Para quando encontra uma válida (FILTRO MAIS SELETIVO: 14-15)
            if 14 <= intersecao <= 15:
                # Converter números de volta para string para compatibilidade
                combo_15_str = ','.join(map(str, combo_15_numeros))
                
                resultados_validos.append({
                    'id': combo_15_id,
                    'combinacao': combo_15_str,
                    'intersecao': intersecao,
                    'indice': i
                })
                encontrou_valida = True
                break
        
        # Relatório de progresso
        if (i + 1) >= proximo_relatorio or (i + 1) == total_combinacoes:
            tempo_decorrido = time.time() - inicio_processamento
            progresso_pct = ((i + 1) / total_combinacoes) * 100
            
            if progresso_pct > 0:
                tempo_estimado_total = tempo_decorrido * (100 / progresso_pct)
                tempo_restante = tempo_estimado_total - tempo_decorrido
            else:
                tempo_restante = 0
            
            velocidade = (i + 1) / tempo_decorrido if tempo_decorrido > 0 else 0
            
            print(f"⏱️ {progresso_pct:5.1f}% | "
                  f"Processadas: {i+1:,}/{total_combinacoes:,} | "
                  f"Válidas: {len(resultados_validos):,} | "
                  f"Velocidade: {velocidade:,.0f}/s | "
                  f"Restante: ~{tempo_restante:.0f}s")
            
            proximo_relatorio += intervalo_progresso
    
    # 3. RESULTADOS FINAIS
    fim_processamento = time.time()
    tempo_processamento = fim_processamento - inicio_processamento
    tempo_total = fim_processamento - inicio_total
    
    print("\n" + "=" * 60)
    print("🎉 PROCESSAMENTO CONCLUÍDO!")
    print("=" * 60)
    print(f"📊 Total processado: {total_combinacoes:,} combinações")
    print(f"✅ Combinações válidas: {len(resultados_validos):,}")
    print(f"📉 Taxa de aprovação: {(len(resultados_validos) / total_combinacoes) * 100:.4f}%")
    print(f"⏱️ Tempo processamento: {tempo_processamento:.2f} segundos")
    print(f"⏱️ Tempo total: {tempo_total:.2f} segundos")
    print(f"🚀 Velocidade média: {total_combinacoes / tempo_processamento:,.0f} combinações/segundo")
    print("=" * 60)
    
    # 4. SALVAR RESULTADOS
    if resultados_validos:
        salvar_resultados(resultados_validos)
    else:
        print("⚠️ Nenhuma combinação válida encontrada!")

def salvar_resultados(resultados):
    """
    Salva os resultados em arquivo
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"combinacoes_filtradas_{timestamp}.txt"
    caminho_arquivo = Path(__file__).parent / nome_arquivo
    
    print(f"\n💾 Salvando {len(resultados):,} resultados...")
    
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write("COMBINAÇÕES DE 15 NÚMEROS - FILTRO POR INTERSECÇÃO\n")
            f.write("=" * 70 + "\n")
            f.write(f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de combinações válidas: {len(resultados):,}\n")
            f.write("Critério: 14-15 números em comum com combinações de 20 números\n")
            f.write("         que acertaram EXATAMENTE 15 números no último concurso\n")
            f.write("         (FILTRO MAIS SELETIVO - Reduzido de 11-15 para 14-15)\n")
            f.write("=" * 70 + "\n\n")
            
            # Estatísticas de intersecção
            intersecoes = [r['intersecao'] for r in resultados]
            f.write("ESTATÍSTICAS DE INTERSECÇÃO:\n")
            f.write("-" * 30 + "\n")
            for i in range(14, 16):  # Ajustado para 14-15
                count = sum(1 for x in intersecoes if x == i)
                if count > 0:
                    f.write(f"Intersecção {i}: {count:,} combinações\n")
            f.write("\n")
            
            # Lista detalhada
            f.write("LISTA DE COMBINAÇÕES VÁLIDAS:\n")
            f.write("-" * 30 + "\n")
            f.write("ID\tCOMBINAÇÃO\tINTERSECÇÃO\n")
            f.write("-" * 50 + "\n")
            
            for resultado in resultados:
                f.write(f"{resultado['id']}\t{resultado['combinacao']}\t{resultado['intersecao']}\n")
        
        print(f"✅ Resultados salvos em: {nome_arquivo}")
        
        # Estatísticas rápidas
        intersecoes = [r['intersecao'] for r in resultados]
        print("\n📊 DISTRIBUIÇÃO DE INTERSECÇÕES:")
        for i in range(14, 16):  # Ajustado para 14-15
            count = sum(1 for x in intersecoes if x == i)
            if count > 0:
                pct = (count / len(resultados)) * 100
                print(f"   {i} números: {count:,} ({pct:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar resultados: {e}")
        return False

def verificar_status_tabelas():
    """
    Verifica o status das tabelas necessárias
    """
    print("📊 VERIFICANDO STATUS DAS TABELAS...")
    print("-" * 40)
    
    if not db_config.test_connection():
        print("❌ Erro de conexão com banco de dados!")
        return False
    
    # Verificar COMBINACOES_LOTOFACIL
    count_15 = db_config.contar_registros('COMBINACOES_LOTOFACIL')
    if count_15 > 0:
        print(f"✅ COMBINACOES_LOTOFACIL: {count_15:,} registros")
        
        # Verificar estrutura
        query_sample = "SELECT TOP 1 ID, N1, N2, N3 FROM COMBINACOES_LOTOFACIL"
        sample = db_config.execute_query(query_sample)
        if sample:
            print(f"   📄 Exemplo: ID={sample[0][0]}, N1={sample[0][1]}, N2={sample[0][2]}, N3={sample[0][3]}...")
    else:
        print("❌ COMBINACOES_LOTOFACIL: Tabela vazia ou inexistente!")
        return False
    
    # Verificar COMBINACOES_LOTOFACIL20_COMPLETO
    count_20 = db_config.contar_registros('COMBINACOES_LOTOFACIL20_COMPLETO')
    if count_20 > 0:
        print(f"✅ COMBINACOES_LOTOFACIL20_COMPLETO: {count_20:,} registros")
        
        # Verificar quantas têm QtdeRepetidos = 15
        count_15_repetidos = db_config.execute_query("SELECT COUNT_BIG(*) FROM COMBINACOES_LOTOFACIL20_COMPLETO WHERE QtdeRepetidos = 15")
        if count_15_repetidos and count_15_repetidos[0][0] > 0:
            print(f"✅ Com QtdeRepetidos = 15: {count_15_repetidos[0][0]:,} combinações")
        else:
            print("⚠️ ATENÇÃO: Nenhuma combinação com QtdeRepetidos = 15 encontrada!")
            print("   Isso pode significar que o último concurso ainda não foi processado")
            print("   ou nenhuma combinação de 20 acertou exatamente 15 números")
        
        # Verificar estrutura
        query_sample = "SELECT TOP 1 N1, N2, N3, N20, QtdeRepetidos FROM COMBINACOES_LOTOFACIL20_COMPLETO WHERE QtdeRepetidos = 15"
        sample = db_config.execute_query(query_sample)
        if sample:
            print(f"   📄 Exemplo: N1={sample[0][0]}, N2={sample[0][1]}, N3={sample[0][2]}, N20={sample[0][3]}, QtdeRep={sample[0][4]}")
        else:
            print("   📄 Nenhum exemplo encontrado com QtdeRepetidos = 15")
    else:
        print("❌ COMBINACOES_LOTOFACIL20_COMPLETO: Tabela vazia ou inexistente!")
        return False
    
    print(f"\n🔍 Estimativa de comparações: {count_15:,} × {count_20:,} = {count_15 * count_20:,}")
    
    return True

def menu_principal():
    """
    Menu principal do sistema
    """
    while True:
        print("\n🚀 FILTRO DE INTERSECÇÃO - MENU PRINCIPAL")
        print("=" * 50)
        print("1️⃣  🔄 Executar Filtro Completo")
        print("2️⃣  📊 Verificar Status das Tabelas")
        print("3️⃣  📁 Ver Arquivos de Resultado")
        print("0️⃣  🚪 Sair")
        print("=" * 50)
        
        escolha = input("🎯 Escolha uma opção (0-3): ").strip()
        
        if escolha == "1":
            if verificar_status_tabelas():
                print("\n⚡ Iniciando filtro...")
                input("Pressione ENTER para continuar (ou Ctrl+C para cancelar)...")
                filtrar_combinacoes_intersecao()
            else:
                print("❌ Não é possível executar - problemas nas tabelas!")
        
        elif escolha == "2":
            verificar_status_tabelas()
        
        elif escolha == "3":
            print("📁 Arquivos de resultado na pasta:")
            pasta = Path(__file__).parent
            arquivos = list(pasta.glob("combinacoes_filtradas_*.txt"))
            if arquivos:
                for arquivo in sorted(arquivos, reverse=True):
                    tamanho = arquivo.stat().st_size
                    print(f"   📄 {arquivo.name} ({tamanho:,} bytes)")
            else:
                print("   ⚠️ Nenhum arquivo de resultado encontrado")
        
        elif escolha == "0":
            print("👋 Encerrando sistema...")
            break
        
        else:
            print("❌ Opção inválida!")
        
        if escolha != "0":
            input("\n⏸️ Pressione ENTER para continuar...")

def main():
    """
    Função principal
    """
    try:
        print("🚀" * 25)
        print("🚀 FILTRO DE INTERSECÇÃO OTIMIZADO")
        print("🚀" * 25)
        print("📊 Sistema para filtrar combinações de 15 números")
        print("🎯 Critério: 14-15 números em comum com combinações de 20")
        print("🔥 QUE ACERTARAM EXATAMENTE 15 NÚMEROS no último concurso")
        print("⚡ Versão otimizada - FILTRO MAIS SELETIVO (14-15)")
        print("🚀" * 25)
        
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
