#!/usr/bin/env python3
"""
SISTEMA LOTOSCOPE - EXECUTAR E SALVAR COMBINAÇÕES
===============================================
Sistema final que gera e salva combinações em arquivo TXT
"""

from lotoscope_final import LotoScopeIntegrado
from datetime import datetime
import os

def salvar_combinacoes_txt(combinacoes, predicoes, filename=None):
    """Salva combinações em arquivo TXT no formato solicitado"""
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"combinacoes_lotoscope_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("=" * 60 + "\n")
            f.write("COMBINAÇÕES LOTOSCOPE - SISTEMA DE PREDIÇÃO\n")
            f.write("=" * 60 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de combinações: {len(combinacoes)}\n")
            
            # Parâmetros usados
            f.write(f"\nParâmetros previstos:\n")
            f.write(f"- N1 (menor): {predicoes.get('n1', 0)}\n")
            f.write(f"- N15 (maior): {predicoes.get('n15', 0)}\n")
            f.write(f"- Maior que último: {predicoes.get('maior_que_ultimo', 0)}\n")
            f.write(f"- Menor que último: {predicoes.get('menor_que_ultimo', 0)}\n")
            f.write(f"- Igual ao último: {predicoes.get('igual_ao_ultimo', 0)}\n")
            f.write(f"- Faixa 6-25: {predicoes.get('faixa_6a25', 0)}\n")
            f.write(f"- Faixa 6-20: {predicoes.get('faixa_6a20', 0)}\n")
            f.write(f"- Acertos comb. fixa: {predicoes.get('acertos_combinacao_fixa', 0)}\n")
            
            f.write(f"\nRedução: de 3.268.760 para {len(combinacoes)} combinações\n")
            f.write("=" * 60 + "\n\n")
            
            # Combinações (apenas números separados por vírgula)
            f.write("COMBINAÇÕES:\n\n")
            for i, combo_data in enumerate(combinacoes, 1):
                # Extrair apenas os números da combinação
                combinacao = combo_data['combinacao']
                
                # Converter numpy.int64 para int normal e ordenar
                numeros = [int(num) for num in combinacao]
                numeros.sort()
                
                # Formatar como string separada por vírgulas
                linha_combo = ",".join(map(str, numeros))
                f.write(f"{linha_combo}\n")
            
            f.write(f"\n" + "=" * 60 + "\n")
            f.write(f"Total: {len(combinacoes)} combinações salvas\n")
        
        print(f"✅ Combinações salvas em: {filename}")
        print(f"📁 Localização: {os.path.abspath(filename)}")
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return None

def executar_sistema_e_salvar():
    """Executa o sistema completo e salva as combinações"""
    print("LOTOSCOPE - EXECUTAR E SALVAR COMBINAÇÕES")
    print("=" * 50)
    
    # Inicializar sistema
    print("1. Inicializando sistema...")
    lotoscope = LotoScopeIntegrado()
    
    if not lotoscope.inicializar_componentes():
        print("❌ ERRO na inicialização")
        return False
    
    print("✅ Sistema inicializado com sucesso!")
    
    # Executar predição completa
    print("\n2. Gerando predições e combinações...")
    resultado = lotoscope.executar_predicao_completa()
    
    if not resultado['sucesso']:
        print("❌ ERRO na geração das predições")
        return False
    
    # Mostrar estatísticas
    stats = resultado['estatisticas']
    print(f"✅ Predição executada com sucesso!")
    print(f"   - Combinações geradas: {stats['total_combinacoes']}")
    print(f"   - Redução: {stats['fator_reducao']:,}x")
    
    # Salvar combinações
    print("\n3. Salvando combinações em arquivo...")
    arquivo = salvar_combinacoes_txt(
        resultado['combinacoes'], 
        resultado['predicoes']
    )
    
    if arquivo:
        print(f"✅ Arquivo salvo com sucesso!")
        print(f"\n📋 RESUMO FINAL:")
        print(f"   - Arquivo: {arquivo}")
        print(f"   - Combinações: {len(resultado['combinacoes'])}")
        print(f"   - Redução: de 3.268.760 para {len(resultado['combinacoes'])}")
        return True
    else:
        print("❌ ERRO ao salvar arquivo")
        return False

if __name__ == "__main__":
    sucesso = executar_sistema_e_salvar()
    
    print(f"\n{'='*50}")
    if sucesso:
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    else:
        print("❌ PROCESSO FALHOU")
    print("="*50)