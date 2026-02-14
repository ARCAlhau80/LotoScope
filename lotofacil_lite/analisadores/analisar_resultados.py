#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise rápida dos resultados do teste histórico
"""

import json
import glob
from datetime import datetime

def analisar_resultados():
    # Encontrar arquivo mais recente
    arquivos = glob.glob("teste_performance_*.json")
    if not arquivos:
        print("❌ Nenhum arquivo de resultado encontrado!")
        return
    
    arquivo_mais_recente = max(arquivos, key=lambda x: datetime.strptime(x.split('_')[-1].replace('.json', ''), '%Y%m%d_%H%M%S'))
    
    print(f"🔍 Analisando: {arquivo_mais_recente}")
    print("=" * 60)
    
    with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Verificar estrutura do arquivo
    if 'metrica_principal' in dados:
        # Arquivo do testador_performance_historica.py
        media = dados['metrica_principal']['media_acertos']
        total_testes = dados['metrica_principal']['total_testes']
        taxa_sucesso = dados['metrica_principal']['taxa_sucesso']
        min_acertos = dados['metrica_principal']['min_acertos']
        max_acertos = dados['metrica_principal']['max_acertos']
        desvio = dados['metrica_principal']['desvio_padrao']
        
        print(f"🎯 RESULTADOS DO TESTE HISTÓRICO")
        print(f"📊 Testes Realizados: {total_testes}")
        print(f"🔥 MÉDIA DE ACERTOS: {media:.2f}/20 = {(media/20)*100:.1f}%")
        print(f"📈 Taxa de Sucesso: {taxa_sucesso:.2f}%")
        print(f"⚡ Min: {min_acertos} | Max: {max_acertos} | DP: {desvio:.2f}")
        
        # Análise por formato
        if 'analise_por_formato' in dados:
            print("\n📋 ANÁLISE POR FORMATO:")
            for formato, stats in dados['analise_por_formato'].items():
                print(f"   {formato}: {stats['media_acertos']:.2f} acertos médios")
    
    else:
        print("❌ Estrutura do arquivo não reconhecida!")
        print("Chaves disponíveis:", list(dados.keys())[:5], "...")

if __name__ == "__main__":
    analisar_resultados()
