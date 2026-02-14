#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ANÁLISE COMPARATIVA DE COMBINAÇÕES ACADÊMICAS
Analisando divergências e similaridades entre 7 gerações
"""

import os
from collections import Counter, defaultdict
from datetime import datetime

def extrair_combinacoes(arquivo):
    """Extrai as combinações de um arquivo"""
    combinacoes = []
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        
    # Procura pela seção das combinações
    linhas = conteudo.split('\n')
    capturando = False
    
    for linha in linhas:
        if 'Jogo ' in linha and ':' in linha:
            # Extrai números após o ":"
            numeros_str = linha.split(':')[1].strip()
            numeros = [int(n.strip()) for n in numeros_str.split(',')]
            combinacoes.append(sorted(numeros))
        elif linha.startswith('1,') and ',' in linha:
            # Linha de combinação no formato compacto
            numeros = [int(n.strip()) for n in linha.split(',')]
            combinacoes.append(sorted(numeros))
    
    return combinacoes

def analisar_frequencias(todas_combinacoes):
    """Analisa frequência dos números"""
    contador_numeros = Counter()
    
    for arquivo, combinacoes in todas_combinacoes.items():
        for comb in combinacoes:
            contador_numeros.update(comb)
    
    return contador_numeros

def calcular_sobreposicao(comb1, comb2):
    """Calcula sobreposição entre duas combinações"""
    return len(set(comb1).intersection(set(comb2)))

def analisar_similaridades(todas_combinacoes):
    """Analisa similaridades entre arquivos"""
    arquivos = list(todas_combinacoes.keys())
    similaridades = {}
    
    for i, arq1 in enumerate(arquivos):
        for j, arq2 in enumerate(arquivos[i+1:], i+1):
            combs1 = todas_combinacoes[arq1]
            combs2 = todas_combinacoes[arq2]
            
            # Combinações idênticas
            identicas = 0
            sobreposicoes = []
            
            for c1 in combs1:
                for c2 in combs2:
                    if c1 == c2:
                        identicas += 1
                    else:
                        sobreposicao = calcular_sobreposicao(c1, c2)
                        sobreposicoes.append(sobreposicao)
            
            similaridades[(arq1, arq2)] = {
                'combinacoes_identicas': identicas,
                'sobreposicao_media': sum(sobreposicoes) / len(sobreposicoes) if sobreposicoes else 0,
                'sobreposicao_maxima': max(sobreposicoes) if sobreposicoes else 0,
                'sobreposicao_minima': min(sobreposicoes) if sobreposicoes else 0
            }
    
    return similaridades

def main():
    print("🔍 ANÁLISE COMPARATIVA - COMBINAÇÕES ACADÊMICAS")
    print("="*60)
    print()
    
    # Lista dos arquivos
    arquivos = [
        'combinacoes_academico_alta_16nums_20250905_131120.txt',
        'combinacoes_academico_alta_16nums_20250905_141345.txt', 
        'combinacoes_academico_alta_16nums_20250905_132003.txt',
        'combinacoes_academico_alta_16nums_20250905_131812.txt',
        'combinacoes_academico_alta_16nums_20250905_131749.txt',
        'combinacoes_academico_alta_16nums_20250905_131732.txt',
        'combinacoes_academico_alta_16nums_20250905_131248.txt'
    ]
    
    todas_combinacoes = {}
    
    # Extrai combinações de cada arquivo
    print("📂 CARREGANDO ARQUIVOS:")
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            combinacoes = extrair_combinacoes(arquivo)
            todas_combinacoes[arquivo] = combinacoes
            timestamp = arquivo.split('_')[-1].replace('.txt', '')
            print(f"   ✅ {timestamp}: {len(combinacoes)} combinações")
        else:
            print(f"   ❌ {arquivo}: Não encontrado")
    
    print(f"\n📊 TOTAL: {len(todas_combinacoes)} arquivos carregados")
    print()
    
    # Análise de frequências
    print("🎯 ANÁLISE DE FREQUÊNCIAS:")
    print("-" * 40)
    contador_numeros = analisar_frequencias(todas_combinacoes)
    
    print("🔥 NÚMEROS MAIS FREQUENTES:")
    for numero, freq in contador_numeros.most_common(10):
        print(f"   {numero:2d}: {freq:3d} aparições ({freq/len(todas_combinacoes)/13*100:.1f}%)")
    
    print("\n❄️ NÚMEROS MENOS FREQUENTES:")
    for numero, freq in contador_numeros.most_common()[-10:]:
        print(f"   {numero:2d}: {freq:3d} aparições ({freq/len(todas_combinacoes)/13*100:.1f}%)")
    
    print()
    
    # Análise de similaridades
    print("🔄 ANÁLISE DE SIMILARIDADES:")
    print("-" * 40)
    similaridades = analisar_similaridades(todas_combinacoes)
    
    print("📈 COMPARAÇÕES ENTRE ARQUIVOS:")
    for (arq1, arq2), dados in similaridades.items():
        t1 = arq1.split('_')[-1].replace('.txt', '')
        t2 = arq2.split('_')[-1].replace('.txt', '')
        
        print(f"\n🔗 {t1} ↔ {t2}:")
        print(f"   • Combinações idênticas: {dados['combinacoes_identicas']}")
        print(f"   • Sobreposição média: {dados['sobreposicao_media']:.1f} números")
        print(f"   • Sobreposição máxima: {dados['sobreposicao_maxima']} números")
        print(f"   • Sobreposição mínima: {dados['sobreposicao_minima']} números")
    
    # Estatísticas gerais
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print("-" * 40)
    
    total_combinacoes = sum(len(combs) for combs in todas_combinacoes.values())
    combinacoes_unicas = set()
    for combs in todas_combinacoes.values():
        for comb in combs:
            combinacoes_unicas.add(tuple(comb))
    
    print(f"   📦 Total de combinações: {total_combinacoes}")
    print(f"   🎯 Combinações únicas: {len(combinacoes_unicas)}")
    print(f"   🔄 Taxa de repetição: {(1 - len(combinacoes_unicas)/total_combinacoes)*100:.1f}%")
    
    # Números sempre presentes
    numeros_sempre_presentes = set(range(1, 26))
    for combs in todas_combinacoes.values():
        numeros_arquivo = set()
        for comb in combs:
            numeros_arquivo.update(comb)
        numeros_sempre_presentes.intersection_update(numeros_arquivo)
    
    if numeros_sempre_presentes:
        print(f"\n🎯 NÚMEROS SEMPRE PRESENTES: {sorted(numeros_sempre_presentes)}")
    else:
        print(f"\n🎯 NÚMEROS SEMPRE PRESENTES: Nenhum")
    
    # Análise de padrões temporais
    print(f"\n⏰ ANÁLISE TEMPORAL:")
    print("-" * 40)
    timestamps = []
    for arquivo in todas_combinacoes.keys():
        timestamp_str = arquivo.split('_')[-1].replace('.txt', '')
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            timestamps.append((timestamp, arquivo))
        except:
            pass
    
    timestamps.sort()
    
    if len(timestamps) >= 2:
        primeiro = timestamps[0][0]
        ultimo = timestamps[-1][0]
        duracao = ultimo - primeiro
        print(f"   📅 Primeiro arquivo: {primeiro.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   📅 Último arquivo: {ultimo.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   ⏱️ Período total: {duracao}")
    
    print(f"\n✅ ANÁLISE CONCLUÍDA!")

if __name__ == "__main__":
    main()
