#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 GERADOR RÁPIDO COM INTELIGÊNCIA POSICIONAL
==============================================
⚡ O MELHOR DOS DOIS MUNDOS! ⚡

Combina a velocidade do combinations(25,15) com a inteligência posicional!

COMO FUNCIONA:
1. Gera 3.268.760 combinações únicas de 15 números
2. Verifica se cada combinação "encaixa" nas restrições posicionais
3. Mantém apenas as que são posicionalmente válidas

VANTAGENS:
- RÁPIDO: segundos/minutos em vez de horas
- INTELIGENTE: respeita probabilidades por posição
- PRECISO: mesmo resultado do Trator, muito mais rápido

Autor: LotoScope AI
Data: Janeiro 2026
"""

import sys
import os
import glob
from datetime import datetime
from itertools import combinations
from typing import List, Set, Dict
import random
import multiprocessing as mp

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerador_posicional_probabilistico import GeradorPosicionalProbabilistico


def calcular_score_combinacao(combo: List[int]) -> Dict:
    """
    Calcula score de qualidade de uma combinação baseado em múltiplos critérios.
    
    Critérios:
    - Equilíbrio par/ímpar (ideal: 7/8 ou 8/7)
    - Soma total (ideal: entre 170 e 220)
    - Distribuição por faixas (1-5, 6-10, 11-15, 16-20, 21-25)
    - Sequências (evitar muitas consecutivas)
    
    Returns:
        Dict com score total e componentes
    """
    # 1. Equilíbrio par/ímpar (0-25 pontos)
    pares = sum(1 for n in combo if n % 2 == 0)
    impares = 15 - pares
    # Ideal: 7/8 ou 8/7 = 25 pontos, 6/9 ou 9/6 = 20, etc
    desvio_paridade = abs(pares - 7.5)
    score_paridade = max(0, 25 - (desvio_paridade * 5))
    
    # 2. Soma total (0-25 pontos)
    soma = sum(combo)
    # Ideal: 195 (média histórica ~195), range bom: 170-220
    if 180 <= soma <= 210:
        score_soma = 25
    elif 170 <= soma <= 220:
        score_soma = 20
    elif 160 <= soma <= 230:
        score_soma = 15
    else:
        score_soma = max(0, 25 - abs(soma - 195) / 5)
    
    # 3. Distribuição por faixas (0-25 pontos)
    # Ideal: 3 números de cada faixa de 5
    faixas = [0, 0, 0, 0, 0]
    for n in combo:
        faixa = min(4, (n - 1) // 5)
        faixas[faixa] += 1
    
    # Cada faixa deve ter entre 2 e 4 números
    score_faixas = 25
    for qtd in faixas:
        if qtd < 1 or qtd > 5:
            score_faixas -= 8
        elif qtd < 2 or qtd > 4:
            score_faixas -= 3
    score_faixas = max(0, score_faixas)
    
    # 4. Sequências consecutivas (0-25 pontos)
    # Penalizar excesso de números consecutivos
    sequencias = 0
    for i in range(len(combo) - 1):
        if combo[i + 1] == combo[i] + 1:
            sequencias += 1
    
    # Até 4 consecutivos é normal, acima penaliza
    if sequencias <= 4:
        score_sequencias = 25
    elif sequencias <= 6:
        score_sequencias = 20
    elif sequencias <= 8:
        score_sequencias = 15
    else:
        score_sequencias = max(0, 25 - (sequencias - 4) * 3)
    
    # Score total (0-100)
    score_total = score_paridade + score_soma + score_faixas + score_sequencias
    
    return {
        'total': score_total,
        'paridade': score_paridade,
        'soma': score_soma,
        'faixas': score_faixas,
        'sequencias': score_sequencias,
        'pares': pares,
        'soma_valor': soma,
        'dist_faixas': faixas
    }


def selecionar_inteligente(combinacoes: List[List[int]], quantidade: int, 
                           numeros_obrigatorios: List[int] = None) -> List[List[int]]:
    """
    Seleção inteligente de combinações baseada em qualidade e diversidade.
    
    Estratégia:
    1. Calcula score de qualidade para todas as combinações
    2. Divide em faixas de qualidade (excelente, bom, médio)
    3. Seleciona proporcionalmente de cada faixa
    4. Garante diversidade (evita combinações muito similares)
    
    Args:
        combinacoes: Lista de todas as combinações válidas
        quantidade: Quantas selecionar
        numeros_obrigatorios: Números fixos para priorizar
    
    Returns:
        Lista de combinações selecionadas ordenadas
    """
    if quantidade >= len(combinacoes):
        return sorted(combinacoes)
    
    print(f"\n🧠 SELEÇÃO INTELIGENTE (não aleatória)")
    print(f"   Calculando scores de {len(combinacoes):,} combinações...")
    
    # Calcular scores
    scored = []
    for i, combo in enumerate(combinacoes):
        if i % 100000 == 0 and i > 0:
            print(f"   Scoring... {i:,}/{len(combinacoes):,}")
        
        score_info = calcular_score_combinacao(combo)
        scored.append((combo, score_info['total'], score_info))
    
    # Ordenar por score (maior primeiro)
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Estatísticas de qualidade
    scores = [s[1] for s in scored]
    media_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    print(f"\n   📊 ESTATÍSTICAS DE QUALIDADE:")
    print(f"      Score máximo: {max_score:.1f}")
    print(f"      Score médio:  {media_score:.1f}")
    print(f"      Score mínimo: {min_score:.1f}")
    
    # Dividir em faixas de qualidade
    # Top 20% = Excelente, 20-60% = Bom, 60-100% = Médio
    n_total = len(scored)
    faixa_excelente = scored[:int(n_total * 0.20)]
    faixa_bom = scored[int(n_total * 0.20):int(n_total * 0.60)]
    faixa_medio = scored[int(n_total * 0.60):]
    
    print(f"\n   📈 DISTRIBUIÇÃO POR QUALIDADE:")
    print(f"      ⭐ Excelente (top 20%): {len(faixa_excelente):,} combinações")
    print(f"      ✓ Bom (20-60%):        {len(faixa_bom):,} combinações")
    print(f"      • Médio (60-100%):     {len(faixa_medio):,} combinações")
    
    # Selecionar proporcionalmente: 50% excelente, 35% bom, 15% médio
    qtd_excelente = max(1, int(quantidade * 0.50))
    qtd_bom = max(1, int(quantidade * 0.35))
    qtd_medio = quantidade - qtd_excelente - qtd_bom
    
    # Ajustar se faixa não tiver suficiente
    if len(faixa_excelente) < qtd_excelente:
        excesso = qtd_excelente - len(faixa_excelente)
        qtd_excelente = len(faixa_excelente)
        qtd_bom += excesso
    
    if len(faixa_bom) < qtd_bom:
        excesso = qtd_bom - len(faixa_bom)
        qtd_bom = len(faixa_bom)
        qtd_medio += excesso
    
    print(f"\n   🎯 SELEÇÃO PROPORCIONAL:")
    print(f"      ⭐ Excelentes: {qtd_excelente}")
    print(f"      ✓ Bons:       {qtd_bom}")
    print(f"      • Médios:     {qtd_medio}")
    
    selecionadas = []
    
    # Selecionar de cada faixa com diversidade
    def selecionar_com_diversidade(faixa, qtd, ja_selecionadas):
        """Seleciona evitando combinações muito similares."""
        if qtd <= 0 or not faixa:
            return []
        
        resultado = []
        
        # Primeiro, pegar distribuídos pela faixa
        if qtd >= len(faixa):
            return [c[0] for c in faixa]
        
        # Pegar distribuídos (não apenas os primeiros)
        step = len(faixa) // qtd
        indices = [i * step for i in range(qtd)]
        
        for idx in indices:
            if idx < len(faixa):
                combo = faixa[idx][0]
                
                # Verificar similaridade com já selecionadas
                muito_similar = False
                for sel in ja_selecionadas + resultado:
                    # Considerar muito similar se compartilhar 13+ números
                    comum = len(set(combo) & set(sel))
                    if comum >= 13:
                        muito_similar = True
                        break
                
                if not muito_similar:
                    resultado.append(combo)
                elif len(faixa) > idx + 1:
                    # Tentar próximo
                    for alt_idx in range(idx + 1, min(idx + 10, len(faixa))):
                        alt_combo = faixa[alt_idx][0]
                        alt_similar = False
                        for sel in ja_selecionadas + resultado:
                            if len(set(alt_combo) & set(sel)) >= 13:
                                alt_similar = True
                                break
                        if not alt_similar:
                            resultado.append(alt_combo)
                            break
        
        return resultado
    
    # Selecionar de cada faixa
    sel_excelente = selecionar_com_diversidade(faixa_excelente, qtd_excelente, [])
    sel_bom = selecionar_com_diversidade(faixa_bom, qtd_bom, sel_excelente)
    sel_medio = selecionar_com_diversidade(faixa_medio, qtd_medio, sel_excelente + sel_bom)
    
    selecionadas = sel_excelente + sel_bom + sel_medio
    
    # Se não conseguiu quantidade suficiente, completar com aleatórias
    if len(selecionadas) < quantidade:
        faltam = quantidade - len(selecionadas)
        disponiveis = [c[0] for c in scored if c[0] not in selecionadas]
        if disponiveis:
            extras = random.sample(disponiveis, min(faltam, len(disponiveis)))
            selecionadas.extend(extras)
    
    print(f"\n   ✅ Selecionadas: {len(selecionadas)} combinações diversificadas")
    
    # Mostrar scores das selecionadas
    scores_sel = [calcular_score_combinacao(c)['total'] for c in selecionadas]
    print(f"   📊 Score médio selecionadas: {sum(scores_sel)/len(scores_sel):.1f}")
    print(f"   📊 Score médio geral:        {media_score:.1f}")
    
    return sorted(selecionadas)


def limpar_arquivos_anteriores():
    """Remove arquivos TXT de combinações anteriores."""
    padrao = "combinacoes_hibrido_*.txt"
    arquivos = glob.glob(padrao)
    
    if arquivos:
        print(f"\n🗑️ Encontrados {len(arquivos)} arquivo(s) anterior(es):")
        for arq in arquivos:
            print(f"   • {arq}")
            os.remove(arq)
        print(f"   ✅ Arquivos removidos!")
    else:
        print("\n✅ Nenhum arquivo anterior encontrado.")


def verificar_combinacao_posicional(combo: tuple, numeros_por_posicao: List[Set[int]]) -> bool:
    """
    Verifica se uma combinação ordenada é válida posicionalmente.
    
    Para ser válida, o número na posição i da combinação deve estar
    disponível na posição N(i+1) do gerador.
    
    Args:
        combo: Tupla de 15 números ordenados
        numeros_por_posicao: Lista de sets com números válidos para cada posição
    
    Returns:
        True se a combinação é posicionalmente válida
    """
    for i, num in enumerate(combo):
        if num not in numeros_por_posicao[i]:
            return False
    return True


def processar_bloco(args):
    """
    Processa um bloco de combinações em paralelo.
    
    Args:
        args: (lista_combos, numeros_por_posicao, obrigatorios_set, obrig_min, obrig_max)
    
    Returns:
        Lista de combinações válidas
    """
    combos, numeros_por_posicao, obrigatorios_set, obrig_min, obrig_max = args
    
    validas = []
    
    for combo in combos:
        # Verificar obrigatórios com range (min/max)
        if obrigatorios_set:
            combo_set = set(combo)
            qtd_obrig_na_combo = len(obrigatorios_set & combo_set)
            
            # Verificar se está dentro do range permitido
            if qtd_obrig_na_combo < obrig_min or qtd_obrig_na_combo > obrig_max:
                continue
        
        # Verificar se é posicionalmente válida
        if verificar_combinacao_posicional(combo, numeros_por_posicao):
            validas.append(list(combo))
    
    return validas


def gerar_combinacoes_hibrido(
    limite_encalhado: int = 10,
    numeros_obrigatorios: List[int] = None,
    numeros_excluidos: List[int] = None,
    exclusoes_posicionais: dict = None,
    usar_paralelo: bool = True,
    obrigatorios_min: int = None,
    obrigatorios_max: int = None
) -> List[List[int]]:
    """
    Gera combinações usando abordagem híbrida:
    - Velocidade do combinations
    - Inteligência do posicional
    
    Args:
        limite_encalhado: 0 = desativado, >0 = exclui encalhados
        numeros_obrigatorios: Pool de números para o filtro de obrigatórios
        numeros_excluidos: NÃO devem aparecer
        exclusoes_posicionais: Exclusões por posição
        usar_paralelo: Usar multiprocessing
        obrigatorios_min: Mínimo de obrigatórios que devem aparecer (None = todos)
        obrigatorios_max: Máximo de obrigatórios que podem aparecer (None = todos)
    
    Returns:
        Lista de combinações válidas
    """
    numeros_obrigatorios = numeros_obrigatorios or []
    obrigatorios_set = set(numeros_obrigatorios)
    
    # Configurar range de obrigatórios
    # Se não especificado, usa o comportamento padrão (todos obrigatórios)
    total_obrigatorios = len(numeros_obrigatorios)
    if obrigatorios_min is None:
        obrigatorios_min = total_obrigatorios  # Padrão: todos são obrigatórios
    if obrigatorios_max is None:
        obrigatorios_max = total_obrigatorios  # Padrão: todos são obrigatórios
    
    # Validar range
    obrigatorios_min = max(0, min(obrigatorios_min, total_obrigatorios))
    obrigatorios_max = max(obrigatorios_min, min(obrigatorios_max, total_obrigatorios))
    
    # Criar gerador posicional para obter as restrições
    remover_encalhados = limite_encalhado > 0
    
    g = GeradorPosicionalProbabilistico(
        limite_encalhado=limite_encalhado if limite_encalhado > 0 else 999,
        remover_encalhados=remover_encalhados,
        numeros_excluidos=numeros_excluidos,
        exclusoes_posicionais=exclusoes_posicionais
    )
    
    # Obter números disponíveis para cada posição (como sets para busca O(1))
    numeros_por_posicao = []
    numeros_globais = set()
    
    print("\n📊 NÚMEROS DISPONÍVEIS POR POSIÇÃO:")
    print("-" * 60)
    
    for pos in range(1, 16):
        probs_filtradas = g.get_probabilidades_filtradas(pos)
        nums = set([n for n, p in probs_filtradas])
        numeros_por_posicao.append(nums)
        numeros_globais.update(nums)
        
        nums_sorted = sorted(nums)
        if numeros_obrigatorios:
            obrig_na_pos = [n for n in nums_sorted if n in obrigatorios_set]
            if obrig_na_pos:
                print(f"   N{pos:2}: {len(nums)} números: {nums_sorted} ⭐ Obrig: {obrig_na_pos}")
            else:
                print(f"   N{pos:2}: {len(nums)} números: {nums_sorted}")
        else:
            print(f"   N{pos:2}: {len(nums)} números: {nums_sorted}")
    
    print("-" * 60)
    
    # Verificar obrigatórios
    if numeros_obrigatorios:
        print(f"   ⭐ Pool de OBRIGATÓRIOS: {sorted(numeros_obrigatorios)}")
        print(f"   📊 Range: mínimo {obrigatorios_min}, máximo {obrigatorios_max}")
        
        # Validar que cada obrigatório aparece em pelo menos uma posição
        for num in numeros_obrigatorios:
            posicoes_validas = [i+1 for i, nums in enumerate(numeros_por_posicao) if num in nums]
            if not posicoes_validas:
                print(f"   ⚠️ Número {num} não está disponível em nenhuma posição (pode ser filtrado)")
    
    # Números globais disponíveis (união de todas as posições)
    print(f"\n   Números disponíveis globalmente: {sorted(numeros_globais)}")
    print(f"   Total: {len(numeros_globais)} números")
    
    # Calcular total de combinações a verificar
    from math import comb
    
    # Com obrigatórios flexíveis: precisamos verificar TODAS as combinações
    # pois qualquer combinação pode ter entre min e max obrigatórios
    total_combos = comb(len(numeros_globais), 15)
    print(f"\n   Total a verificar: C({len(numeros_globais)},15) = {total_combos:,}")
    
    # Estimar tempo
    combos_por_segundo = 500_000  # estimativa conservadora
    tempo_est = total_combos / combos_por_segundo
    if tempo_est > 60:
        print(f"   ⏱️ Tempo estimado: ~{tempo_est/60:.1f} minutos")
    else:
        print(f"   ⏱️ Tempo estimado: ~{tempo_est:.0f} segundos")
    
    # Gerar combinações
    print(f"\n🔄 Gerando e verificando combinações...")
    inicio = datetime.now()
    
    combinacoes_validas = []
    contador = 0
    validas_count = 0
    
    # Gerar todas as combinações e filtrar por range de obrigatórios
    numeros_lista = sorted(numeros_globais)
    gerador = combinations(numeros_lista, 15)
    
    for combo in gerador:
        contador += 1
        
        if contador % 500000 == 0:
            tempo_decorrido = (datetime.now() - inicio).total_seconds()
            pct = contador / total_combos * 100
            eta = (tempo_decorrido / contador) * (total_combos - contador)
            if eta > 60:
                eta_str = f"~{eta/60:.1f}min"
            else:
                eta_str = f"~{eta:.0f}s"
            print(f"   Verificando... {contador:,}/{total_combos:,} ({pct:.1f}%) "
                  f"| Válidas: {validas_count:,} | ETA: {eta_str}")
        
        # Verificar filtro de obrigatórios com range
        if obrigatorios_set:
            combo_set = set(combo)
            qtd_obrig_na_combo = len(obrigatorios_set & combo_set)
            
            # Verificar se está dentro do range permitido
            if qtd_obrig_na_combo < obrigatorios_min or qtd_obrig_na_combo > obrigatorios_max:
                continue
        
        # Verificar se é posicionalmente válida
        if verificar_combinacao_posicional(combo, numeros_por_posicao):
            combinacoes_validas.append(list(combo))
            validas_count += 1
    
    duracao = (datetime.now() - inicio).total_seconds()
    
    taxa_validas = (len(combinacoes_validas) / contador * 100) if contador > 0 else 0
    
    print(f"\n✅ Verificadas {contador:,} combinações em {duracao:.2f} segundos")
    print(f"   Válidas posicionalmente: {len(combinacoes_validas):,} ({taxa_validas:.2f}%)")
    
    return combinacoes_validas


def salvar_combinacoes(combinacoes, quantidade_solicitada):
    """Salva as combinações em arquivo TXT na pasta lotofacil_lite."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar na pasta lotofacil_lite (um nível acima de geradores)
    pasta_destino = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if quantidade_solicitada == 0:
        nome_arquivo = f"combinacoes_hibrido_{timestamp}_TODAS_{len(combinacoes)}.txt"
    else:
        nome_arquivo = f"combinacoes_hibrido_{timestamp}_{len(combinacoes)}.txt"
    
    arquivo = os.path.join(pasta_destino, nome_arquivo)
    
    print(f"\n💾 Salvando em: {arquivo}")
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        for comb in combinacoes:
            linha = ",".join(f"{n:02d}" for n in comb)
            f.write(linha + "\n")
    
    print(f"✅ Arquivo salvo!")
    print(f"   • {len(combinacoes):,} combinações")
    
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
    print("🎯 GERADOR HÍBRIDO - RÁPIDO COM INTELIGÊNCIA POSICIONAL")
    print("⚡ O MELHOR DOS DOIS MUNDOS! ⚡")
    print("=" * 70)
    print()
    print("✅ RÁPIDO: Usa combinations(25,15) - muito mais eficiente")
    print("✅ INTELIGENTE: Mantém restrições posicionais do Trator")
    print("✅ RESULTADO: Mesmas combinações do Trator, muito mais rápido!")
    print("=" * 70)
    
    # Limpar arquivos anteriores
    limpar_arquivos_anteriores()
    
    # Prompt de entrada
    print("\n📝 CONFIGURAÇÃO:")
    print("   • Digite 0 para gerar TODAS as combinações válidas")
    print("   • Digite um número para selecionar aleatoriamente")
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
    print("   • Números que não saem há X concursos são excluídos")
    print("   • Padrão: 10 concursos")
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
                print("   ⚠️ Usando 50 (máximo)")
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
    print("   • Digite 0 para não usar obrigatórios")
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
                print("   ❌ Digite entre 0 e 14")
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
                    print(f"   ❌ Informe exatamente {qtd_obrigatorios}")
                    continue
                
                invalidos = [n for n in nums if n < 1 or n > 25]
                if invalidos:
                    print(f"   ❌ Fora do range 1-25: {invalidos}")
                    continue
                
                if len(nums) != len(set(nums)):
                    print("   ❌ Duplicados não permitidos")
                    continue
                
                numeros_obrigatorios = nums
                break
            except ValueError:
                print("   ❌ Formato inválido!")
        
        print(f"\n   ✅ Pool de Obrigatórios: {sorted(numeros_obrigatorios)}")
        
        # ========== RANGE DE OBRIGATÓRIOS (NOVO) ==========
        print("\n" + "-" * 50)
        print("   📊 RANGE DE OBRIGATÓRIOS FLEXÍVEIS:")
        print("-" * 50)
        print(f"   Você informou {qtd_obrigatorios} números no pool.")
        print("   Quantos desses DEVEM aparecer em cada combinação?")
        print()
        print(f"   • Mínimo possível: 1 (pelo menos 1 dos {qtd_obrigatorios})")
        print(f"   • Máximo possível: {qtd_obrigatorios} (todos os {qtd_obrigatorios})")
        print(f"   • Padrão: min={qtd_obrigatorios}, max={qtd_obrigatorios} (todos obrigatórios)")
        print()
        
        # Perguntar mínimo
        while True:
            try:
                entrada = input(f"   Mínimo de obrigatórios [Enter={qtd_obrigatorios}]: ").strip()
                if entrada == "":
                    obrigatorios_min = qtd_obrigatorios
                else:
                    obrigatorios_min = int(entrada)
                
                if obrigatorios_min < 1 or obrigatorios_min > qtd_obrigatorios:
                    print(f"   ❌ Digite entre 1 e {qtd_obrigatorios}")
                    continue
                break
            except ValueError:
                print("   ❌ Digite um número válido!")
        
        # Perguntar máximo
        while True:
            try:
                entrada = input(f"   Máximo de obrigatórios [Enter={qtd_obrigatorios}]: ").strip()
                if entrada == "":
                    obrigatorios_max = qtd_obrigatorios
                else:
                    obrigatorios_max = int(entrada)
                
                if obrigatorios_max < obrigatorios_min or obrigatorios_max > qtd_obrigatorios:
                    print(f"   ❌ Digite entre {obrigatorios_min} e {qtd_obrigatorios}")
                    continue
                break
            except ValueError:
                print("   ❌ Digite um número válido!")
        
        if obrigatorios_min == obrigatorios_max == qtd_obrigatorios:
            print(f"\n   ✅ TODOS os {qtd_obrigatorios} obrigatórios em cada combinação")
        elif obrigatorios_min == obrigatorios_max:
            print(f"\n   ✅ Exatamente {obrigatorios_min} dos {qtd_obrigatorios} em cada combinação")
        else:
            print(f"\n   ✅ Entre {obrigatorios_min} e {obrigatorios_max} dos {qtd_obrigatorios} em cada combinação")
    else:
        obrigatorios_min = 0
        obrigatorios_max = 0
    
    # ========== EXCLUSÃO GLOBAL ==========
    print("\n" + "=" * 70)
    print("🚫 EXCLUSÃO GLOBAL (números que NÃO aparecem)")
    print("=" * 70)
    
    numeros_excluidos = []
    entrada = input("   Números a EXCLUIR [Enter=nenhum]: ").strip()
    
    if entrada:
        try:
            entrada = entrada.replace(",", " ")
            partes = entrada.split()
            nums = [int(p.strip()) for p in partes if p.strip()]
            nums = [n for n in nums if 1 <= n <= 25][:9]
            
            conflito = set(nums) & set(numeros_obrigatorios)
            if conflito:
                print(f"   ⚠️ {list(conflito)} são obrigatórios, ignorados!")
                nums = [n for n in nums if n not in numeros_obrigatorios]
            
            if nums:
                numeros_excluidos = nums
                print(f"   ✅ Excluídos: {sorted(numeros_excluidos)}")
        except:
            print("   ⚠️ Formato inválido")
    
    # ========== GERAR ==========
    inicio = datetime.now()
    
    print("\n" + "=" * 70)
    print("🎯 GERANDO COMBINAÇÕES (modo híbrido)...")
    print("=" * 70)
    
    todas_combinacoes = gerar_combinacoes_hibrido(
        limite_encalhado=limite_encalhado,
        numeros_obrigatorios=numeros_obrigatorios,
        numeros_excluidos=numeros_excluidos if numeros_excluidos else None,
        obrigatorios_min=obrigatorios_min if numeros_obrigatorios else None,
        obrigatorios_max=obrigatorios_max if numeros_obrigatorios else None
    )
    
    if not todas_combinacoes:
        print("\n❌ Nenhuma combinação gerada!")
        return
    
    # Selecionar quantidade
    if quantidade == 0:
        combinacoes_selecionadas = todas_combinacoes
        print(f"\n🎯 Total: {len(combinacoes_selecionadas):,} combinações!")
    else:
        if quantidade > len(todas_combinacoes):
            print(f"\n⚠️ Solicitado {quantidade:,}, existem {len(todas_combinacoes):,}")
            quantidade = len(todas_combinacoes)
        
        # ⭐ SELEÇÃO INTELIGENTE (não mais aleatória!)
        combinacoes_selecionadas = selecionar_inteligente(
            todas_combinacoes, 
            quantidade,
            numeros_obrigatorios
        )
        print(f"\n🎯 Selecionadas {len(combinacoes_selecionadas):,} com SELEÇÃO INTELIGENTE!")
    
    # Salvar
    arquivo = salvar_combinacoes(combinacoes_selecionadas, quantidade)
    
    # Mostrar amostra
    mostrar_amostra(combinacoes_selecionadas)
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print("\n" + "=" * 70)
    print("🎯 PROCESSO CONCLUÍDO - MODO HÍBRIDO!")
    print("=" * 70)
    print(f"   ⏱️ Tempo total: {duracao:.2f} segundos")
    print(f"   📁 Arquivo: {arquivo}")
    print(f"   🎰 Combinações: {len(combinacoes_selecionadas):,}")
    
    if numeros_obrigatorios:
        print(f"   ⭐ Pool de Obrigatórios: {sorted(numeros_obrigatorios)}")
        if obrigatorios_min == obrigatorios_max:
            print(f"   📊 Usando exatamente {obrigatorios_min} desses números")
        else:
            print(f"   📊 Usando entre {obrigatorios_min} e {obrigatorios_max} desses números")
    
    if numeros_excluidos:
        print(f"   🚫 Excluídos: {sorted(numeros_excluidos)}")
    
    if quantidade > 0:
        custo = len(combinacoes_selecionadas) * 3.50
        print(f"   💰 Custo estimado: R$ {custo:,.2f}")
    
    print("\n✅ Este gerador mantém a inteligência posicional!")
    print("=" * 70)


if __name__ == "__main__":
    main()
