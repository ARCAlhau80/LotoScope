#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 GERADOR POSICIONAL PROBABILÍSTICO - TODAS AS COMBINAÇÕES VÁLIDAS
=====================================================================
⭐ GERADOR MAIS PROMISSOR DO LOTOSCOPE ⭐

Gera combinações usando regras posicionais com remoção de números encalhados.
- Remove números "frios" (que não saem há X concursos)
- Usa probabilidades históricas por posição
- Gera apenas combinações válidas (sem repetição)

FUNCIONALIDADES:
- Prompt interativo: informe quantas combinações deseja
- 0 = gera TODAS as combinações válidas
- Exclui arquivos anteriores automaticamente
- Salva em TXT, uma por linha, separadas por vírgula

Autor: LotoScope AI
Data: Dezembro 2025
"""

import sys
import os
import glob
from datetime import datetime
from itertools import product
from typing import List
import random

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerador_posicional_probabilistico import GeradorPosicionalProbabilistico


def limpar_arquivos_anteriores():
    """Remove arquivos TXT de combinações anteriores."""
    padrao = "combinacoes_validas_posicional_*.txt"
    arquivos = glob.glob(padrao)
    
    if arquivos:
        print(f"\n🗑️ Encontrados {len(arquivos)} arquivo(s) anterior(es):")
        for arq in arquivos:
            print(f"   • {arq}")
            os.remove(arq)
        print(f"   ✅ Arquivos removidos!")
    else:
        print("\n✅ Nenhum arquivo anterior encontrado.")


def gerar_todas_combinacoes_validas(
    limite_encalhado: int = 10, 
    numeros_obrigatorios: List[int] = None,
    numeros_excluidos: List[int] = None,
    exclusoes_posicionais: dict = None
):
    """
    Gera TODAS as combinações válidas possíveis.
    
    Args:
        limite_encalhado: Quantos concursos sem sair para considerar encalhado
        numeros_obrigatorios: Lista de números que devem estar em TODAS as combinações
        numeros_excluidos: Lista de números que NÃO devem aparecer (exclusão global)
        exclusoes_posicionais: Dict {posição: set de números} para exclusão por posição
    
    Returns:
        Lista de todas as combinações válidas e números disponíveis por posição
    """
    numeros_obrigatorios = numeros_obrigatorios or []
    obrigatorios_set = set(numeros_obrigatorios)
    
    # Criar gerador com exclusões
    # Se limite_encalhado == 0, desativa o filtro de encalhados
    remover_encalhados = limite_encalhado > 0
    
    g = GeradorPosicionalProbabilistico(
        limite_encalhado=limite_encalhado if limite_encalhado > 0 else 999,  # 999 = nenhum número será encalhado
        remover_encalhados=remover_encalhados,
        numeros_excluidos=numeros_excluidos,
        exclusoes_posicionais=exclusoes_posicionais
    )
    
    # Validar números obrigatórios se houver
    if numeros_obrigatorios:
        valido, msg = g.validar_numeros_obrigatorios(numeros_obrigatorios)
        if not valido:
            print(f"❌ Erro: {msg}")
            return [], g
    
    # Obter números disponíveis para cada posição
    numeros_por_posicao = []
    print("\n📊 NÚMEROS DISPONÍVEIS POR POSIÇÃO:")
    print("-" * 60)
    
    for pos in range(1, 16):
        probs_filtradas = g.get_probabilidades_filtradas(pos)
        nums = sorted([n for n, p in probs_filtradas])
        numeros_por_posicao.append(nums)
        
        # Marcar números obrigatórios
        if numeros_obrigatorios:
            obrig_na_pos = [n for n in nums if n in obrigatorios_set]
            if obrig_na_pos:
                print(f"   N{pos:2}: {len(nums)} números: {nums} ⭐ Obrig: {obrig_na_pos}")
            else:
                print(f"   N{pos:2}: {len(nums)} números: {nums}")
        else:
            print(f"   N{pos:2}: {len(nums)} números: {nums}")
    
    print("-" * 60)
    
    if numeros_obrigatorios:
        print(f"   ⭐ Números OBRIGATÓRIOS: {sorted(numeros_obrigatorios)}")
    
    # Calcular total teórico
    total_teorico = 1
    for nums in numeros_por_posicao:
        total_teorico *= len(nums)
    print(f"   Total teórico (com repetições): {total_teorico:,}")
    
    # Gerar todas as combinações válidas
    print("\n🔄 Gerando combinações válidas...")
    
    combinacoes_validas = []
    combinacoes_set = set()  # Para evitar duplicatas
    
    contador = 0
    for combo in product(*numeros_por_posicao):
        contador += 1
        
        if contador % 1000000 == 0:
            print(f"   Processando... {contador:,}/{total_teorico:,} ({contador/total_teorico*100:.1f}%)")
        
        # Verificar se todos os números são únicos
        if len(set(combo)) == 15:
            # Se tem obrigatórios, verificar se a combinação contém TODOS
            if numeros_obrigatorios:
                combo_set = set(combo)
                if not obrigatorios_set.issubset(combo_set):
                    continue  # Não tem todos os obrigatórios, pular
            
            # Ordenar a combinação
            combo_ordenada = tuple(sorted(combo))
            
            # Verificar se não é duplicata
            if combo_ordenada not in combinacoes_set:
                combinacoes_set.add(combo_ordenada)
                combinacoes_validas.append(list(combo_ordenada))
    
    print(f"\n✅ Total de combinações VÁLIDAS: {len(combinacoes_validas):,}")
    print(f"   (de {total_teorico:,} teóricas, {len(combinacoes_validas)/total_teorico*100:.2f}% são válidas)")
    
    if numeros_obrigatorios:
        print(f"   ⭐ Todas contêm os números: {sorted(numeros_obrigatorios)}")
    
    return combinacoes_validas, g


def salvar_combinacoes(combinacoes, quantidade_solicitada):
    """Salva as combinações em arquivo TXT."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if quantidade_solicitada == 0:
        arquivo = f"combinacoes_validas_posicional_{timestamp}_TODAS_{len(combinacoes)}.txt"
    else:
        arquivo = f"combinacoes_validas_posicional_{timestamp}_{len(combinacoes)}.txt"
    
    print(f"\n💾 Salvando em: {arquivo}")
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        for comb in combinacoes:
            # Formatar: 01,02,03,...
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
    print("🎯 GERADOR POSICIONAL PROBABILÍSTICO - COMBINAÇÕES VÁLIDAS")
    print("⭐ GERADOR MAIS PROMISSOR DO LOTOSCOPE ⭐")
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
    print("🧊 LIMITE ENCALHADO (quantos concursos sem sair = número 'frio')")
    print("=" * 70)
    print("   • Números que não saem há X concursos em uma posição são excluídos")
    print("   • Padrão: 10 concursos")
    print("   • Quanto menor, mais agressivo (exclui mais números)")
    print("   • Digite 0 para DESATIVAR este filtro (usa todos os 25 números)")
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
                print("   ⚠️ Valor muito alto, usando 50 (máximo recomendado)")
                limite_encalhado = 50
            break
        except ValueError:
            print("   ❌ Digite um número válido!")
    
    if limite_encalhado == 0:
        print("   ✅ Filtro de encalhados: DESATIVADO (todos os 25 números disponíveis)")
    else:
        print(f"   ✅ Limite encalhado: {limite_encalhado} concursos")
    
    # ========== NÚMEROS OBRIGATÓRIOS ==========
    print("\n" + "=" * 70)
    print("⭐ NÚMEROS OBRIGATÓRIOS (aparecem em TODAS as combinações)")
    print("=" * 70)
    print("   • Digite 0 para NÃO usar números obrigatórios")
    print("   • Digite de 1 a 14 para escolher quantos números obrigatórios")
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
        print(f"\n   📝 Informe os {qtd_obrigatorios} número(s) obrigatório(s):")
        print("   (Digite cada número separado por vírgula ou espaço)")
        print("   Exemplo: 1, 14, 25")
        print()
        
        while True:
            try:
                entrada = input(f"   Números obrigatórios ({qtd_obrigatorios}): ").strip()
                
                # Aceitar vírgula ou espaço como separador
                entrada = entrada.replace(",", " ")
                partes = entrada.split()
                
                nums = [int(p.strip()) for p in partes if p.strip()]
                
                if len(nums) != qtd_obrigatorios:
                    print(f"   ❌ Você precisa informar exatamente {qtd_obrigatorios} número(s). Informou {len(nums)}.")
                    continue
                
                # Verificar range
                invalidos = [n for n in nums if n < 1 or n > 25]
                if invalidos:
                    print(f"   ❌ Números fora do range 1-25: {invalidos}")
                    continue
                
                # Verificar duplicatas
                if len(nums) != len(set(nums)):
                    print("   ❌ Números duplicados não são permitidos")
                    continue
                
                numeros_obrigatorios = nums
                break
                
            except ValueError:
                print("   ❌ Formato inválido! Use: 1, 14, 25 ou 1 14 25")
        
        print(f"\n   ✅ Números obrigatórios: {sorted(numeros_obrigatorios)}")
    
    # ========== EXCLUSÃO GLOBAL ==========
    print("\n" + "=" * 70)
    print("🚫 EXCLUSÃO GLOBAL (números que NÃO aparecem em NENHUMA posição)")
    print("=" * 70)
    print("   • Digite 0 ou Enter para NÃO excluir números")
    print("   • Informe até 9 números que NÃO devem aparecer")
    print("   • Exemplo: 3, 9, 16 ou 3 9 16")
    print()
    
    numeros_excluidos = None
    entrada = input("   Números a EXCLUIR globalmente [Enter=nenhum]: ").strip()
    
    if entrada and entrada != "0":
        try:
            entrada = entrada.replace(",", " ")
            partes = entrada.split()
            nums = [int(p.strip()) for p in partes if p.strip()]
            
            # Validar
            nums = [n for n in nums if 1 <= n <= 25][:9]
            
            if nums:
                # Verificar conflito com obrigatórios
                conflito = set(nums) & set(numeros_obrigatorios)
                if conflito:
                    print(f"   ⚠️ Números {list(conflito)} são obrigatórios, não podem ser excluídos!")
                    nums = [n for n in nums if n not in numeros_obrigatorios]
                
                if nums:
                    numeros_excluidos = nums
                    excl_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                    print(f"   ✅ Exclusão GLOBAL: {excl_str}")
        except:
            print("   ⚠️ Formato inválido. Nenhum número será excluído.")
    
    # ========== EXCLUSÃO POSICIONAL ==========
    print("\n" + "=" * 70)
    print("🎯 EXCLUSÃO POSICIONAL (números excluídos apenas de posições específicas)")
    print("=" * 70)
    print("   • Digite S para configurar exclusões por posição")
    print("   • Enter ou N para pular")
    print("   • Ex: Excluir 7,8 apenas de N2 (podem aparecer em N3, N4, etc)")
    print()
    
    exclusoes_posicionais = {}
    
    configurar = input("   Deseja configurar exclusões posicionais? [s/N]: ").strip().lower()
    
    if configurar in ('s', 'sim', 'y', 'yes'):
        print("\n   Para cada posição, digite os números a excluir.")
        print("   Exemplo: 7, 8 ou 7 8")
        print("   Enter para pular a posição.")
        print()
        
        for pos in range(1, 16):
            nums_str = input(f"   N{pos:2} - Números a excluir: ").strip()
            
            if nums_str:
                try:
                    nums_str = nums_str.replace(",", " ")
                    nums = [int(n.strip()) for n in nums_str.split() if n.strip()]
                    nums = [n for n in nums if 1 <= n <= 25]
                    
                    # Remover números que são obrigatórios
                    if numeros_obrigatorios:
                        conflito = set(nums) & set(numeros_obrigatorios)
                        if conflito:
                            print(f"        ⚠️ {list(conflito)} são obrigatórios, ignorados!")
                            nums = [n for n in nums if n not in numeros_obrigatorios]
                    
                    if nums:
                        exclusoes_posicionais[pos] = set(nums)
                        nums_fmt = ", ".join(f"{n:02d}" for n in sorted(nums))
                        print(f"        ✅ N{pos}: excluídos [{nums_fmt}]")
                except:
                    print(f"        ⚠️ Formato inválido, ignorado.")
        
        if exclusoes_posicionais:
            print("\n   📋 Resumo das exclusões posicionais:")
            for pos in sorted(exclusoes_posicionais.keys()):
                nums = exclusoes_posicionais[pos]
                nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                print(f"      N{pos:2}: excluídos [{nums_str}]")
    
    inicio = datetime.now()
    
    # Gerar todas as combinações
    print("\n" + "=" * 70)
    print("🔄 GERANDO COMBINAÇÕES...")
    print("=" * 70)
    
    todas_combinacoes, gerador = gerar_todas_combinacoes_validas(
        limite_encalhado=limite_encalhado,
        numeros_obrigatorios=numeros_obrigatorios,
        numeros_excluidos=numeros_excluidos,
        exclusoes_posicionais=exclusoes_posicionais if exclusoes_posicionais else None
    )
    
    if not todas_combinacoes:
        print("\n❌ Nenhuma combinação válida encontrada!")
        return
    
    # Selecionar quantidade desejada
    if quantidade == 0:
        # Gerar todas
        combinacoes_selecionadas = todas_combinacoes
        print(f"\n🎯 Gerando TODAS as {len(combinacoes_selecionadas):,} combinações!")
    else:
        # Selecionar aleatoriamente
        if quantidade > len(todas_combinacoes):
            print(f"\n⚠️ Solicitado {quantidade:,}, mas só existem {len(todas_combinacoes):,} válidas.")
            quantidade = len(todas_combinacoes)
        
        combinacoes_selecionadas = random.sample(todas_combinacoes, quantidade)
        # Ordenar para manter consistência
        combinacoes_selecionadas.sort()
        print(f"\n🎯 Selecionadas {len(combinacoes_selecionadas):,} combinações aleatoriamente!")
    
    # Salvar
    arquivo = salvar_combinacoes(combinacoes_selecionadas, quantidade)
    
    # Mostrar amostra
    mostrar_amostra(combinacoes_selecionadas)
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print("\n" + "=" * 70)
    print("✅ PROCESSO CONCLUÍDO!")
    print("=" * 70)
    print(f"   ⏱️ Tempo total: {duracao:.2f} segundos")
    print(f"   📁 Arquivo: {arquivo}")
    print(f"   🎰 Combinações: {len(combinacoes_selecionadas):,}")
    
    if numeros_obrigatorios:
        print(f"   ⭐ Números obrigatórios: {sorted(numeros_obrigatorios)}")
    
    if numeros_excluidos:
        excl_str = ", ".join(f"{n:02d}" for n in sorted(numeros_excluidos))
        print(f"   🚫 Exclusão GLOBAL: {excl_str}")
    
    if exclusoes_posicionais:
        print(f"   🎯 Exclusões POSICIONAIS:")
        for pos in sorted(exclusoes_posicionais.keys()):
            nums = exclusoes_posicionais[pos]
            nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
            print(f"      N{pos:2}: [{nums_str}]")
    
    if quantidade > 0:
        custo = len(combinacoes_selecionadas) * 3.50
        print(f"   💰 Custo estimado: R$ {custo:,.2f}")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
