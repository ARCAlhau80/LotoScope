#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
⚡ GERADOR RÁPIDO DE COMBINAÇÕES - SEM INTELIGÊNCIA POSICIONAL
===============================================================
🏎️ VERSÃO ULTRA-RÁPIDA (segundos em vez de horas!) 🏎️

Gera combinações usando itertools.combinations ao invés de product.
- 3.268.760 combinações possíveis (vs 66 bilhões do posicional)
- Completa em SEGUNDOS
- Aplica filtros de encalhados e obrigatórios

⚠️ LIMITAÇÃO: Não usa inteligência posicional!
   O gerador original respeita probabilidades por posição (N1, N2, etc).
   Este gerador trata todos os números igualmente.

QUANDO USAR:
- Quando o gerador original demora demais
- Quando quer gerar TODAS as combinações rapidamente
- Para testes e validações

Autor: LotoScope AI
Data: Janeiro 2026
"""

import sys
import os
import glob
from datetime import datetime
from itertools import combinations
from typing import List, Set
import random
import pyodbc

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def get_connection():
    """Conecta ao banco de dados."""
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=DESKTOP-K6JPBDS;'
        'DATABASE=LOTOFACIL;'
        'Trusted_Connection=yes;'
    )


def limpar_arquivos_anteriores():
    """Remove arquivos TXT de combinações anteriores."""
    padrao = "combinacoes_rapido_*.txt"
    arquivos = glob.glob(padrao)
    
    if arquivos:
        print(f"\n🗑️ Encontrados {len(arquivos)} arquivo(s) anterior(es):")
        for arq in arquivos:
            print(f"   • {arq}")
            os.remove(arq)
        print(f"   ✅ Arquivos removidos!")
    else:
        print("\n✅ Nenhum arquivo anterior encontrado.")


def obter_numeros_encalhados(limite_encalhado: int) -> Set[int]:
    """
    Obtém números que não saem há X concursos (encalhados).
    Diferente do posicional, aqui olhamos globalmente, não por posição.
    
    Returns:
        Set de números considerados encalhados
    """
    if limite_encalhado <= 0:
        return set()  # Nenhum encalhado
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Pegar o último concurso
        cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
        ultimo = cursor.fetchone()[0]
        
        # Pegar últimos X concursos
        cursor.execute(f"""
            SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            WHERE Concurso > {ultimo - limite_encalhado}
            ORDER BY Concurso DESC
        """)
        
        # Coletar todos os números que saíram
        numeros_quentes = set()
        for row in cursor.fetchall():
            for n in row:
                if n:
                    numeros_quentes.add(n)
        
        conn.close()
        
        # Encalhados são os que NÃO saíram
        todos = set(range(1, 26))
        encalhados = todos - numeros_quentes
        
        return encalhados
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar encalhados: {e}")
        return set()


def gerar_combinacoes_rapido(
    limite_encalhado: int = 10,
    numeros_obrigatorios: List[int] = None,
    numeros_excluidos: List[int] = None
) -> List[List[int]]:
    """
    Gera todas as combinações válidas usando combinations(25, 15).
    
    Args:
        limite_encalhado: 0 = desativado, >0 = exclui números encalhados
        numeros_obrigatorios: Números que devem estar em TODAS as combinações
        numeros_excluidos: Números que NÃO devem aparecer
    
    Returns:
        Lista de combinações válidas
    """
    numeros_obrigatorios = numeros_obrigatorios or []
    numeros_excluidos = numeros_excluidos or []
    obrigatorios_set = set(numeros_obrigatorios)
    excluidos_set = set(numeros_excluidos)
    
    # Obter encalhados
    encalhados = obter_numeros_encalhados(limite_encalhado)
    
    # Determinar números disponíveis
    todos = set(range(1, 26))
    
    # Remover excluídos e encalhados
    disponiveis = todos - excluidos_set - encalhados
    
    # Garantir que obrigatórios estão disponíveis
    if not obrigatorios_set.issubset(disponiveis):
        conflito = obrigatorios_set - disponiveis
        print(f"❌ Erro: Números obrigatórios {conflito} estão excluídos ou encalhados!")
        return []
    
    disponiveis_list = sorted(disponiveis)
    
    print(f"\n📊 CONFIGURAÇÃO:")
    print(f"   • Números disponíveis: {len(disponiveis_list)}")
    print(f"   • Lista: {disponiveis_list}")
    
    if encalhados:
        print(f"   • Encalhados removidos: {sorted(encalhados)}")
    
    if numeros_excluidos:
        print(f"   • Excluídos manualmente: {sorted(numeros_excluidos)}")
    
    if numeros_obrigatorios:
        print(f"   • Obrigatórios: {sorted(numeros_obrigatorios)}")
    
    # Calcular total teórico
    from math import comb
    n_disponiveis = len(disponiveis_list)
    
    if numeros_obrigatorios:
        # Se tem X obrigatórios, precisa escolher 15-X dos restantes
        restantes = [n for n in disponiveis_list if n not in obrigatorios_set]
        n_restantes = len(restantes)
        n_escolher = 15 - len(numeros_obrigatorios)
        
        if n_escolher < 0:
            print(f"❌ Erro: Mais de 15 números obrigatórios!")
            return []
        
        if n_restantes < n_escolher:
            print(f"❌ Erro: Poucos números disponíveis ({n_restantes}) para completar {n_escolher}!")
            return []
        
        total_teorico = comb(n_restantes, n_escolher)
        print(f"   • Total teórico: C({n_restantes},{n_escolher}) = {total_teorico:,}")
    else:
        if n_disponiveis < 15:
            print(f"❌ Erro: Apenas {n_disponiveis} números disponíveis, precisa de 15!")
            return []
        
        total_teorico = comb(n_disponiveis, 15)
        print(f"   • Total teórico: C({n_disponiveis},15) = {total_teorico:,}")
    
    # Gerar combinações
    print(f"\n🔄 Gerando combinações...")
    inicio = datetime.now()
    
    combinacoes = []
    contador = 0
    
    if numeros_obrigatorios:
        # Gerar apenas os complementos
        restantes = [n for n in disponiveis_list if n not in obrigatorios_set]
        n_escolher = 15 - len(numeros_obrigatorios)
        
        for complemento in combinations(restantes, n_escolher):
            contador += 1
            
            if contador % 500000 == 0:
                pct = contador / total_teorico * 100
                print(f"   Processando... {contador:,}/{total_teorico:,} ({pct:.1f}%)")
            
            # Combinar obrigatórios + complemento
            combo = sorted(list(obrigatorios_set) + list(complemento))
            combinacoes.append(combo)
    else:
        # Gerar todas
        for combo in combinations(disponiveis_list, 15):
            contador += 1
            
            if contador % 500000 == 0:
                pct = contador / total_teorico * 100
                print(f"   Processando... {contador:,}/{total_teorico:,} ({pct:.1f}%)")
            
            combinacoes.append(list(combo))
    
    duracao = (datetime.now() - inicio).total_seconds()
    
    print(f"\n✅ Geradas {len(combinacoes):,} combinações em {duracao:.2f} segundos!")
    
    return combinacoes


def salvar_combinacoes(combinacoes, quantidade_solicitada):
    """Salva as combinações em arquivo TXT."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if quantidade_solicitada == 0:
        arquivo = f"combinacoes_rapido_{timestamp}_TODAS_{len(combinacoes)}.txt"
    else:
        arquivo = f"combinacoes_rapido_{timestamp}_{len(combinacoes)}.txt"
    
    print(f"\n💾 Salvando em: {arquivo}")
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        for comb in combinacoes:
            linha = ",".join(f"{n:02d}" for n in comb)
            f.write(linha + "\n")
    
    print(f"✅ Arquivo salvo com sucesso!")
    print(f"   • {len(combinacoes):,} combinações")
    print(f"   • Formato: uma por linha, separadas por vírgula")
    
    return arquivo


def mostrar_amostra(combinacoes, n=5):
    """Mostra primeiras e últimas combinações."""
    print(f"\n📋 PRIMEIRAS {n} COMBINAÇÕES:")
    for i, comb in enumerate(combinacoes[:n], 1):
        nums = " - ".join(f"{n:02d}" for n in comb)
        print(f"   {i}. {nums}")
    
    if len(combinacoes) > n * 2:
        print(f"\n📋 ÚLTIMAS {n} COMBINAÇÕES:")
        for i, comb in enumerate(combinacoes[-n:], len(combinacoes)-n+1):
            nums = " - ".join(f"{n:02d}" for n in comb)
            print(f"   {i}. {nums}")


def main():
    print("=" * 70)
    print("⚡ GERADOR RÁPIDO DE COMBINAÇÕES")
    print("🏎️ VERSÃO ULTRA-RÁPIDA (segundos!) 🏎️")
    print("=" * 70)
    print()
    print("⚠️  ATENÇÃO: Este gerador NÃO usa inteligência posicional!")
    print("   O gerador original (Trator/Turbo) respeita probabilidades")
    print("   históricas por posição (N1, N2, etc).")
    print("   Este gerador trata todos os números igualmente.")
    print()
    print("   Use quando precisar de velocidade máxima!")
    print("=" * 70)
    
    # Limpar arquivos anteriores
    limpar_arquivos_anteriores()
    
    # Prompt de entrada
    print("\n📝 CONFIGURAÇÃO:")
    print("   • Digite 0 para gerar TODAS as combinações válidas")
    print("   • Digite um número para gerar essa quantidade (aleatoriamente)")
    print()
    
    while True:
        try:
            entrada = input("   Quantas combinações deseja gerar? [0=TODAS]: ").strip()
            if entrada == "":
                quantidade = 0
            else:
                quantidade = int(entrada)
            
            if quantidade < 0:
                print("   ❌ Digite um número >= 0")
                continue
            break
        except ValueError:
            print("   ❌ Digite um número válido!")
    
    # ========== LIMITE ENCALHADO ==========
    print("\n" + "=" * 70)
    print("🧊 LIMITE ENCALHADO (números que não saem há X concursos)")
    print("=" * 70)
    print("   • Números que não saem há X concursos são excluídos")
    print("   • Padrão: 10 concursos")
    print("   • Quanto menor, mais agressivo (exclui mais números)")
    print("   • Digite 0 para DESATIVAR (usa todos os 25 números)")
    print()
    
    while True:
        try:
            entrada = input("   Limite encalhado [Enter=10, 0=desativado]: ").strip()
            if entrada == "":
                limite_encalhado = 10
            else:
                limite_encalhado = int(entrada)
            
            if limite_encalhado < 0:
                print("   ❌ Digite um número >= 0")
                continue
            if limite_encalhado > 50:
                print("   ⚠️ Valor muito alto, usando 50")
                limite_encalhado = 50
            break
        except ValueError:
            print("   ❌ Digite um número válido!")
    
    if limite_encalhado == 0:
        print("   ✅ Filtro de encalhados: DESATIVADO")
    else:
        print(f"   ✅ Limite encalhado: {limite_encalhado} concursos")
    
    # ========== NÚMEROS OBRIGATÓRIOS ==========
    print("\n" + "=" * 70)
    print("⭐ NÚMEROS OBRIGATÓRIOS (aparecem em TODAS as combinações)")
    print("=" * 70)
    print("   • Digite 0 para NÃO usar números obrigatórios")
    print("   • Digite de 1 a 14 para escolher quantos")
    print()
    
    numeros_obrigatorios = []
    
    while True:
        try:
            entrada = input("   Quantos números obrigatórios? [0=nenhum]: ").strip()
            if entrada == "":
                qtd_obrigatorios = 0
            else:
                qtd_obrigatorios = int(entrada)
            
            if qtd_obrigatorios < 0 or qtd_obrigatorios > 14:
                print("   ❌ Digite um número entre 0 e 14")
                continue
            break
        except ValueError:
            print("   ❌ Digite um número válido!")
    
    if qtd_obrigatorios > 0:
        print(f"\n   📝 Informe os {qtd_obrigatorios} número(s):")
        print("   Exemplo: 1, 14, 25")
        print()
        
        while True:
            try:
                entrada = input(f"   Números obrigatórios ({qtd_obrigatorios}): ").strip()
                entrada = entrada.replace(",", " ")
                partes = entrada.split()
                nums = [int(p.strip()) for p in partes if p.strip()]
                
                if len(nums) != qtd_obrigatorios:
                    print(f"   ❌ Informe exatamente {qtd_obrigatorios} número(s)")
                    continue
                
                invalidos = [n for n in nums if n < 1 or n > 25]
                if invalidos:
                    print(f"   ❌ Números fora do range 1-25: {invalidos}")
                    continue
                
                if len(nums) != len(set(nums)):
                    print("   ❌ Números duplicados não permitidos")
                    continue
                
                numeros_obrigatorios = nums
                break
            except ValueError:
                print("   ❌ Formato inválido!")
        
        print(f"\n   ✅ Obrigatórios: {sorted(numeros_obrigatorios)}")
    
    # ========== EXCLUSÃO GLOBAL ==========
    print("\n" + "=" * 70)
    print("🚫 EXCLUSÃO GLOBAL (números que NÃO aparecem)")
    print("=" * 70)
    print("   • Enter para não excluir nenhum")
    print("   • Informe até 9 números para excluir")
    print()
    
    numeros_excluidos = []
    entrada = input("   Números a EXCLUIR [Enter=nenhum]: ").strip()
    
    if entrada:
        try:
            entrada = entrada.replace(",", " ")
            partes = entrada.split()
            nums = [int(p.strip()) for p in partes if p.strip()]
            nums = [n for n in nums if 1 <= n <= 25][:9]
            
            # Remover conflitos com obrigatórios
            conflito = set(nums) & set(numeros_obrigatorios)
            if conflito:
                print(f"   ⚠️ {list(conflito)} são obrigatórios, ignorados!")
                nums = [n for n in nums if n not in numeros_obrigatorios]
            
            if nums:
                numeros_excluidos = nums
                print(f"   ✅ Excluídos: {sorted(numeros_excluidos)}")
        except:
            print("   ⚠️ Formato inválido, nenhum excluído")
    
    # ========== GERAR ==========
    inicio = datetime.now()
    
    print("\n" + "=" * 70)
    print("⚡ GERANDO COMBINAÇÕES (modo rápido)...")
    print("=" * 70)
    
    todas_combinacoes = gerar_combinacoes_rapido(
        limite_encalhado=limite_encalhado,
        numeros_obrigatorios=numeros_obrigatorios,
        numeros_excluidos=numeros_excluidos
    )
    
    if not todas_combinacoes:
        print("\n❌ Nenhuma combinação gerada!")
        return
    
    # Selecionar quantidade
    if quantidade == 0:
        combinacoes_selecionadas = todas_combinacoes
        print(f"\n🎯 Gerando TODAS as {len(combinacoes_selecionadas):,} combinações!")
    else:
        if quantidade > len(todas_combinacoes):
            print(f"\n⚠️ Solicitado {quantidade:,}, mas só existem {len(todas_combinacoes):,}")
            quantidade = len(todas_combinacoes)
        
        combinacoes_selecionadas = random.sample(todas_combinacoes, quantidade)
        combinacoes_selecionadas.sort()
        print(f"\n🎯 Selecionadas {len(combinacoes_selecionadas):,} aleatoriamente!")
    
    # Salvar
    arquivo = salvar_combinacoes(combinacoes_selecionadas, quantidade)
    
    # Mostrar amostra
    mostrar_amostra(combinacoes_selecionadas)
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print("\n" + "=" * 70)
    print("⚡ PROCESSO CONCLUÍDO!")
    print("=" * 70)
    print(f"   ⏱️ Tempo total: {duracao:.2f} segundos")
    print(f"   📁 Arquivo: {arquivo}")
    print(f"   🎰 Combinações: {len(combinacoes_selecionadas):,}")
    
    if numeros_obrigatorios:
        print(f"   ⭐ Obrigatórios: {sorted(numeros_obrigatorios)}")
    
    if numeros_excluidos:
        print(f"   🚫 Excluídos: {sorted(numeros_excluidos)}")
    
    if quantidade > 0:
        custo = len(combinacoes_selecionadas) * 3.50
        print(f"   💰 Custo estimado: R$ {custo:,.2f}")
    
    print()
    print("⚠️  Lembre-se: Este gerador NÃO usa inteligência posicional!")
    print("=" * 70)


if __name__ == "__main__":
    main()
