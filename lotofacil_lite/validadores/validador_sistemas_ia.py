#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 VALIDADOR DE SISTEMAS IA - DADOS REAIS
Verifica quais sistemas estão configurados para usar dados reais

Autor: AR CALHAU
Data: 17 de Setembro de 2025
"""

import os
import re
from typing import Dict, List, Tuple

def analisar_arquivo_python(caminho_arquivo: str) -> Dict:
    """Analisa um arquivo Python para verificar uso de dados reais"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        analise = {
            'arquivo': os.path.basename(caminho_arquivo),
            'usa_database_config': 'from database_config import' in conteudo or 'import database_config' in conteudo,
            'usa_resultados_int': 'Resultados_INT' in conteudo,
            'usa_colunas_corretas': re.search(r'N1.*N2.*N3.*N4.*N5', conteudo) is not None,
            'usa_colunas_incorretas': re.search(r'Bola1.*Bola2.*Bola3', conteudo) is not None,
            'usa_tabelas_incorretas': any(tab in conteudo for tab in ['Sorteios', 'lotofacil_numeros_sorteados', 'Resultados_LotofacilFechado']),
            'tem_fallback_simulado': 'dados simulados' in conteudo.lower() or 'fallback' in conteudo.lower(),
            'tem_ia': any(termo in conteudo.lower() for termo in ['neural', 'tensorflow', 'sklearn', 'machine learning', 'ia', 'inteligencia']),
        }
        
        return analise
        
    except Exception as e:
        return {
            'arquivo': os.path.basename(caminho_arquivo),
            'erro': str(e)
        }

def obter_sistemas_ia() -> List[str]:
    """Obtém lista dos principais sistemas com IA"""
    diretorio = r"c:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite"
    
    sistemas_ia = [
        'ia_numeros_repetidos.py',
        'super_gerador_ia.py', 
        'gerador_academico_dinamico.py',
        'gerador_zona_conforto.py',
        'piramide_invertida_dinamica.py',
        'sistema_feedback_resultados.py',
        'sistema_neural_network_v6.py',
        'sistema_inteligencia_preditiva.py',
        'sistema_rede_neural_insights.py',
        'gerador_complementacao_inteligente.py',
        'adaptador_geradores.py',
        'super_combinacao_ia.py',
        'sistema_ultra_precisao_v4.py',
        'sistema_assimetrico_premium.py'
    ]
    
    # Verifica quais arquivos existem
    sistemas_existentes = []
    for sistema in sistemas_ia:
        caminho = os.path.join(diretorio, sistema)
        if os.path.exists(caminho):
            sistemas_existentes.append(caminho)
    
    return sistemas_existentes

def validar_sistemas_ia():
    """Valida todos os sistemas com IA"""
    print("🔍 VALIDAÇÃO DE SISTEMAS IA - USO DE DADOS REAIS")
    print("=" * 70)
    
    sistemas = obter_sistemas_ia()
    resultados = []
    
    for sistema in sistemas:
        analise = analisar_arquivo_python(sistema)
        resultados.append(analise)
    
    # Mostra resultados
    sistemas_ok = 0
    sistemas_problema = 0
    
    for resultado in resultados:
        nome = resultado['arquivo']
        
        if 'erro' in resultado:
            print(f"❌ {nome}: ERRO - {resultado['erro']}")
            sistemas_problema += 1
            continue
        
        # Determina status
        status_items = []
        
        if resultado['usa_database_config']:
            status_items.append("✅ database_config")
        else:
            status_items.append("⚠️ sem database_config")
            
        if resultado['usa_resultados_int']:
            status_items.append("✅ Resultados_INT")
        else:
            status_items.append("⚠️ sem Resultados_INT")
            
        if resultado['usa_colunas_corretas']:
            status_items.append("✅ colunas N1-N15")
        elif resultado['usa_colunas_incorretas']:
            status_items.append("❌ colunas Bola1-Bola15")
        else:
            status_items.append("⚠️ sem queries diretas")
            
        if resultado['usa_tabelas_incorretas']:
            status_items.append("❌ tabelas incorretas")
            
        if resultado['tem_fallback_simulado']:
            status_items.append("⚠️ tem fallback")
        
        # Determina status geral
        tem_problemas = (
            resultado['usa_colunas_incorretas'] or 
            resultado['usa_tabelas_incorretas'] or
            not resultado['usa_database_config']
        )
        
        if tem_problemas:
            print(f"❌ {nome}: {' | '.join(status_items)}")
            sistemas_problema += 1
        else:
            print(f"✅ {nome}: {' | '.join(status_items)}")
            sistemas_ok += 1
    
    # Resumo
    print("\n📊 RESUMO DA VALIDAÇÃO:")
    print("=" * 40)
    print(f"✅ Sistemas OK: {sistemas_ok}")
    print(f"❌ Sistemas com problemas: {sistemas_problema}")
    print(f"📁 Total analisado: {len(resultados)}")
    
    if sistemas_problema > 0:
        print(f"\n🔧 AÇÕES NECESSÁRIAS:")
        print("1. Corrigir sistemas que usam colunas Bola1-Bola15")
        print("2. Atualizar sistemas que usam tabelas incorretas")
        print("3. Implementar database_config nos sistemas sem ele")
        print("4. Testar sistemas corrigidos")
    else:
        print(f"\n🎉 TODOS OS SISTEMAS ESTÃO USANDO DADOS REAIS!")
    
    return resultados

def mostrar_sistemas_detalhados():
    """Mostra análise detalhada de cada sistema"""
    print("\n🔍 ANÁLISE DETALHADA POR SISTEMA:")
    print("=" * 50)
    
    sistemas = obter_sistemas_ia()
    
    for sistema in sistemas:
        analise = analisar_arquivo_python(sistema)
        nome = analise['arquivo']
        
        print(f"\n📁 {nome}")
        print("-" * 30)
        
        if 'erro' in analise:
            print(f"❌ Erro: {analise['erro']}")
            continue
        
        for chave, valor in analise.items():
            if chave == 'arquivo':
                continue
            
            emoji = "✅" if valor else "❌"
            descricao = chave.replace('_', ' ').title()
            print(f"{emoji} {descricao}: {valor}")

if __name__ == "__main__":
    # Executa validação completa
    resultados = validar_sistemas_ia()
    
    # Mostra detalhes se solicitado
    mostrar_detalhes = input("\n🔍 Mostrar análise detalhada? (s/n): ").lower().startswith('s')
    if mostrar_detalhes:
        mostrar_sistemas_detalhados()