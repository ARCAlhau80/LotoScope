#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔺🎯 COMPARAÇÃO ENTRE GERADORES COM FILTRO VALIDADO
Compara o desempenho do filtro entre o Gerador Acadêmico Dinâmico e a Pirâmide Invertida

Autor: AR CALHAU
Data: 24 de Agosto de 2025
"""

import time
from gerador_academico_dinamico import GeradorAcademicoDinamico
from piramide_invertida_dinamica import PiramideInvertidaDinamica

def comparar_geradores_com_filtro():
    """Compara os dois sistemas com filtro validado"""
    print("🔺🎯 COMPARAÇÃO DE GERADORES COM FILTRO VALIDADO")
    print("=" * 65)
    
    resultados = {
        'academico': {'tempo': 0, 'combinacoes': [], 'validas': 0},
        'piramide': {'tempo': 0, 'combinacoes': [], 'validas': 0}
    }
    
    # 🎯 TESTE DO GERADOR ACADÊMICO DINÂMICO
    print("\n🎯 TESTE 1: GERADOR ACADÊMICO DINÂMICO")
    print("-" * 45)
    
    gerador_academico = GeradorAcademicoDinamico()
    gerador_academico.configurar_filtro_validado(usar_filtro=True, min_acertos=11, max_acertos=13)
    
    print("📊 Calculando insights acadêmicos...")
    if gerador_academico.calcular_insights_dinamicos():
        print("✅ Insights carregados com sucesso")
        
        inicio = time.time()
        try:
            combinacoes_academico = gerador_academico.gerar_multiplas_combinacoes(quantidade=10, qtd_numeros=15)
            fim = time.time()
            
            resultados['academico']['tempo'] = fim - inicio
            resultados['academico']['combinacoes'] = combinacoes_academico
            
            # Valida combinações
            for comb in combinacoes_academico:
                if gerador_academico.validar_combinacao_filtro(comb):
                    resultados['academico']['validas'] += 1
            
            print(f"⏱️ Tempo: {resultados['academico']['tempo']:.3f}s")
            print(f"🎯 Combinações: {len(combinacoes_academico)}")
            print(f"✅ Válidas: {resultados['academico']['validas']}/{len(combinacoes_academico)}")
            
        except Exception as e:
            print(f"❌ Erro no gerador acadêmico: {e}")
            return False
    else:
        print("❌ Falha ao carregar dados do gerador acadêmico")
        return False
    
    # 🔺 TESTE DA PIRÂMIDE INVERTIDA
    print("\n🔺 TESTE 2: PIRÂMIDE INVERTIDA DINÂMICA")
    print("-" * 45)
    
    piramide = PiramideInvertidaDinamica()
    piramide.configurar_filtro_validado(usar_filtro=True, min_acertos=11, max_acertos=13)
    
    print("📊 Carregando dados históricos da pirâmide...")
    if piramide.carregar_dados_historicos():
        print("✅ Dados carregados com sucesso")
        
        inicio = time.time()
        try:
            combinacoes_piramide = piramide.gerar_baseado_transicoes(qtd_numeros=15, quantidade=10)
            fim = time.time()
            
            resultados['piramide']['tempo'] = fim - inicio
            resultados['piramide']['combinacoes'] = combinacoes_piramide
            
            # Valida combinações
            for comb in combinacoes_piramide:
                if piramide.validar_combinacao_filtro(comb):
                    resultados['piramide']['validas'] += 1
            
            print(f"⏱️ Tempo: {resultados['piramide']['tempo']:.3f}s")
            print(f"🎯 Combinações: {len(combinacoes_piramide)}")
            print(f"✅ Válidas: {resultados['piramide']['validas']}/{len(combinacoes_piramide)}")
            
        except Exception as e:
            print(f"❌ Erro na pirâmide: {e}")
            return False
    else:
        print("❌ Falha ao carregar dados da pirâmide")
        return False
    
    # 📊 ANÁLISE COMPARATIVA
    print(f"\n📊 ANÁLISE COMPARATIVA:")
    print("=" * 40)
    
    # Performance
    print(f"⏱️ PERFORMANCE:")
    print(f"   Acadêmico: {resultados['academico']['tempo']:.3f}s")
    print(f"   Pirâmide:  {resultados['piramide']['tempo']:.3f}s")
    
    if resultados['academico']['tempo'] > 0 and resultados['piramide']['tempo'] > 0:
        if resultados['academico']['tempo'] < resultados['piramide']['tempo']:
            mais_rapido = "Acadêmico"
            diferenca = resultados['piramide']['tempo'] / resultados['academico']['tempo']
        else:
            mais_rapido = "Pirâmide"
            diferenca = resultados['academico']['tempo'] / resultados['piramide']['tempo']
        
        print(f"   🏆 Mais rápido: {mais_rapido} ({diferenca:.2f}x)")
    
    # Taxa de validade
    taxa_academico = (resultados['academico']['validas'] / len(resultados['academico']['combinacoes']) * 100) if resultados['academico']['combinacoes'] else 0
    taxa_piramide = (resultados['piramide']['validas'] / len(resultados['piramide']['combinacoes']) * 100) if resultados['piramide']['combinacoes'] else 0
    
    print(f"\n✅ TAXA DE VALIDADE:")
    print(f"   Acadêmico: {taxa_academico:.1f}%")
    print(f"   Pirâmide:  {taxa_piramide:.1f}%")
    
    # Análise de sobreposição
    if resultados['academico']['combinacoes'] and resultados['piramide']['combinacoes']:
        comb_academico_set = set(tuple(sorted(comb)) for comb in resultados['academico']['combinacoes'])
        comb_piramide_set = set(tuple(sorted(comb)) for comb in resultados['piramide']['combinacoes'])
        
        sobreposicao = len(comb_academico_set.intersection(comb_piramide_set))
        total_unicas = len(comb_academico_set.union(comb_piramide_set))
        
        print(f"\n🔄 SOBREPOSIÇÃO:")
        print(f"   Combinações idênticas: {sobreposicao}")
        print(f"   Total de combinações únicas: {total_unicas}")
        print(f"   Diversidade: {((total_unicas - sobreposicao) / total_unicas * 100):.1f}%")
    
    # Análise de números mais utilizados
    print(f"\n🔥 NÚMEROS MAIS UTILIZADOS:")
    
    # Conta números do acadêmico
    contador_academico = {}
    for comb in resultados['academico']['combinacoes']:
        for num in comb:
            contador_academico[num] = contador_academico.get(num, 0) + 1
    
    # Conta números da pirâmide
    contador_piramide = {}
    for comb in resultados['piramide']['combinacoes']:
        for num in comb:
            contador_piramide[num] = contador_piramide.get(num, 0) + 1
    
    # Top 5 de cada
    top_academico = sorted(contador_academico.items(), key=lambda x: x[1], reverse=True)[:5]
    top_piramide = sorted(contador_piramide.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"   Acadêmico: {[f'{n}({c}x)' for n, c in top_academico]}")
    print(f"   Pirâmide:  {[f'{n}({c}x)' for n, c in top_piramide]}")
    
    # Verifica se os números favoritos estão nos jogos validados
    jogos_validados = gerador_academico.filtros_validados
    
    print(f"\n🎮 ALINHAMENTO COM JOGOS VALIDADOS:")
    for nome, contador in [("Acadêmico", contador_academico), ("Pirâmide", contador_piramide)]:
        numeros_j1 = sum(1 for num in contador.keys() if num in jogos_validados['jogo_1'])
        numeros_j2 = sum(1 for num in contador.keys() if num in jogos_validados['jogo_2'])
        
        print(f"   {nome}: J1={numeros_j1}/20, J2={numeros_j2}/20")
    
    print(f"\n🎯 CONCLUSÃO:")
    print("-" * 20)
    
    if taxa_academico >= 95 and taxa_piramide >= 95:
        print("✅ AMBOS os sistemas estão funcionando perfeitamente com o filtro!")
        print("🏆 Taxa de validade excelente em ambos")
        
        if abs(resultados['academico']['tempo'] - resultados['piramide']['tempo']) < 1.0:
            print("⚡ Performance similar entre os sistemas")
        
        if sobreposicao < len(resultados['academico']['combinacoes']) // 2:
            print("🎲 Boa diversidade entre os sistemas")
        
        return True
    else:
        print("⚠️ Um ou ambos sistemas apresentaram problemas")
        return False

def main():
    """Execução principal da comparação"""
    try:
        sucesso = comparar_geradores_com_filtro()
        
        if sucesso:
            print(f"\n🎊 IMPLEMENTAÇÃO DO FILTRO COMPLETAMENTE VALIDADA!")
            print(f"   ✅ Gerador Acadêmico Dinâmico: OK")
            print(f"   ✅ Pirâmide Invertida Dinâmica: OK")
            print(f"   🎯 Filtro validado funcionando em ambos sistemas!")
        else:
            print(f"\n⚠️ Alguns problemas foram detectados na implementação")
        
        return sucesso
        
    except Exception as e:
        print(f"❌ Erro durante comparação: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Comparação cancelada pelo usuário")
        sys.exit(1)
