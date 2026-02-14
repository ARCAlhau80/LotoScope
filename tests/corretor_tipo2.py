#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CORRETOR DE PADRÕES CORROMPIDOS
Corrige arquivos que tiveram substituições regex mal feitas
"""

import re
import os
import ast
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent / 'lotofacil_lite'

def verificar_sintaxe(conteudo):
    """Verifica se o código tem erro de sintaxe"""
    try:
        ast.parse(conteudo)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def corrigir_padroes_corrompidos(conteudo):
    """
    Corrige padrões que foram corrompidos por substituições regex mal feitas.
    
    Padrões identificados:
    - int(int(N)) -> N
    - ), int( -> , 
    - ))), int(int(' -> ), '
    - self), int(...) -> self, ...
    - ): None -> : None
    """
    
    original = conteudo
    
    # Padrão 1: int(int(N)) -> N
    conteudo = re.sub(r'int\(int\((\d+)\)\)', r'\1', conteudo)
    
    # Padrão 2: int(int(N)) -> N (com variáveis)
    # int(int(variavel)) -> variavel
    # Cuidado para não quebrar int(variavel) legítimo
    
    # Padrão 3: ), int(valor) -> , valor
    # Mas cuidado com chamadas legítimas de função
    conteudo = re.sub(r'\), int\((\d+)\)', r', \1', conteudo)
    
    # Padrão 4: int(int('texto')) -> 'texto'
    conteudo = re.sub(r"int\(int\('([^']+)'\)\)", r"'\1'", conteudo)
    conteudo = re.sub(r'int\(int\("([^"]+)"\)\)', r'"\1"', conteudo)
    
    # Padrão 5: self), int(parametro=valor)) -> self, parametro=valor)
    conteudo = re.sub(r'\bself\), int\(([a-zA-Z_][a-zA-Z0-9_]*=)', r'self, \1', conteudo)
    
    # Padrão 6: ), int(parametro=valor)) -> , parametro=valor)
    conteudo = re.sub(r'\), int\(([a-zA-Z_][a-zA-Z0-9_]*=[^)]+)\)\)', r', \1)', conteudo)
    
    # Padrão 7: )): -> ):
    conteudo = re.sub(r'\)\):', r'):', conteudo)
    
    # Padrão 8: ): None -> : None (em parâmetros de função)
    conteudo = re.sub(r'\): None', r'=None', conteudo)
    
    # Padrão 9: Limpar parênteses extras em ranges
    # range(int(1), int(26)) -> range(1, 26)
    conteudo = re.sub(r'range\(int\((\d+)\), int\((\d+)\)\)', r'range(\1, \2)', conteudo)
    
    # Padrão 10: Parênteses duplos no final ))))
    # Cuidado para não quebrar código legítimo
    
    # Padrão 11: self), -> self,
    conteudo = re.sub(r'\bself\), ', r'self, ', conteudo)
    
    # Padrão 12: int( no início de parâmetro sem fechar
    # Detectar e remover int( não balanceados
    
    return conteudo, conteudo != original

def corrigir_arquivo(caminho):
    """Corrige um arquivo específico"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except UnicodeDecodeError:
        try:
            with open(caminho, 'r', encoding='latin-1') as f:
                conteudo = f.read()
        except:
            return False, "Erro de encoding"
    
    # Verificar sintaxe original
    ok_original, erro_original = verificar_sintaxe(conteudo)
    if ok_original:
        return True, "Já está OK"
    
    # Tentar correção
    conteudo_corrigido, modificado = corrigir_padroes_corrompidos(conteudo)
    
    if modificado:
        ok_corrigido, erro_corrigido = verificar_sintaxe(conteudo_corrigido)
        if ok_corrigido:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            return True, "Corrigido padrões corrompidos"
        else:
            # Ainda tem erro, mas salvamos para ver o progresso
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            return False, f"Parcialmente corrigido, ainda tem: {erro_corrigido[:50]}"
    
    return False, erro_original

def main():
    print("=" * 70)
    print("CORRETOR DE PADRÕES CORROMPIDOS - LotoScope")
    print("=" * 70)
    
    # Lista de arquivos conhecidos com problemas do TIPO 2
    arquivos_tipo2 = [
        'geradores/gerador_academico_megasena.py',
        'geradores/gerador_dataset_historico.py',
        'geradores/gerador_dinamico_megasena.py',
        'geradores/gerador_estrutura_completa.py',
        'geradores/gerador_inteligente_ciclos_ajustado.py',
        'geradores/gerador_posicional.py',
        'geradores/gerador_posicional_n12.py',
        'geradores/piramide_invertida_dinamica_n12.py',
        'geradores/super_combinacao_ia.py',
        'geradores/super_combinacao_ia_n12.py',
        'analisadores/analisador_preditivo_avancado.py',
        'analisadores/analise_janelas_deslizantes_novo.py',
        'analisadores/analise_janela_treinamento.py',
        'sistemas/sistema_inteligencia_preditiva.py',
        'sistemas/sistema_otimizacao_probabilistica.py',
        'sistemas/sistema_previsao_adaptativa.py',
        'sistemas/sistema_rede_neural_insights.py',
        'utils/conector_megasena_db.py',
        'ia/inteligencia_primos_fibonacci.py',
    ]
    
    print(f"\n📋 Tentando corrigir {len(arquivos_tipo2)} arquivos com padrões corrompidos...\n")
    
    corrigidos = 0
    parciais = 0
    falhas = []
    
    for arquivo_rel in arquivos_tipo2:
        caminho = ROOT_DIR / arquivo_rel
        
        if not caminho.exists():
            print(f"  ⚠️ Arquivo não encontrado: {arquivo_rel}")
            continue
        
        print(f"  → {arquivo_rel}")
        
        sucesso, msg = corrigir_arquivo(caminho)
        
        if sucesso:
            print(f"    ✅ {msg}")
            corrigidos += 1
        elif "Parcialmente" in msg:
            print(f"    🔄 {msg}")
            parciais += 1
        else:
            print(f"    ❌ {msg[:60]}")
            falhas.append((arquivo_rel, msg))
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTADO:")
    print(f"   ✅ Corrigidos: {corrigidos}")
    print(f"   🔄 Parciais: {parciais}")
    print(f"   ❌ Falhas: {len(falhas)}")
    print("=" * 70)
    
    return len(falhas)

if __name__ == "__main__":
    import sys
    sys.exit(main())
