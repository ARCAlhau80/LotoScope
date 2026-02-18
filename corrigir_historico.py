"""
Script para remover o último backtest incorreto do histórico de aprendizado.
O usuário validou com o concurso 3614 em vez do 3615 (futuro).
"""

import json
import os

HISTORICO_PATH = r'C:\Users\AR CALHAU\source\repos\LotoScope\dados\historico_aprendizado.json'

def main():
    # Carregar histórico
    with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
        historico = json.load(f)
    
    print('=' * 70)
    print('CORREÇÃO DO HISTÓRICO DE APRENDIZADO')
    print('=' * 70)
    
    print('\n=== ANTES DA CORREÇÃO ===')
    print(f"Total backtests: {historico['total_backtests']}")
    print(f"Exclusão correta: {historico['exclusao_correta']}")
    print(f"Exclusão errada: {historico['exclusao_errada']}")
    print(f"Níveis jackpot: {historico['niveis_jackpot']}")
    
    ultimo = historico['historico_detalhado'][-1]
    print(f"\nÚltimo registro (A SER REMOVIDO):")
    print(f"  Data: {ultimo['data']}")
    print(f"  Resultado: {ultimo['resultado']}")
    print(f"  Excluídos: {ultimo['excluidos']}")
    print(f"  Exclusão correta? {ultimo['exclusao_correta']}")
    print(f"  Último nível jackpot: {ultimo['ultimo_nivel_jackpot']}")
    
    # Reverter contadores baseado no último registro
    historico['total_backtests'] -= 1
    
    if ultimo['exclusao_correta']:
        historico['exclusao_correta'] -= 1
    else:
        historico['exclusao_errada'] -= 1
    
    # Reverter nível jackpot se houve
    nivel_jackpot = ultimo.get('ultimo_nivel_jackpot', -1)
    if nivel_jackpot >= 0:
        nivel_key = str(nivel_jackpot)
        if nivel_key in historico['niveis_jackpot']:
            historico['niveis_jackpot'][nivel_key] -= 1
    
    # Remover evento atípico se existir com a mesma data
    eventos_atipicos = historico.get('eventos_atipicos', [])
    eventos_atipicos = [e for e in eventos_atipicos if e.get('data') != ultimo['data']]
    historico['eventos_atipicos'] = eventos_atipicos
    
    # Remover último registro
    historico['historico_detalhado'].pop()
    
    print('\n=== APÓS A CORREÇÃO ===')
    print(f"Total backtests: {historico['total_backtests']}")
    print(f"Exclusão correta: {historico['exclusao_correta']}")
    print(f"Exclusão errada: {historico['exclusao_errada']}")
    print(f"Níveis jackpot: {historico['niveis_jackpot']}")
    
    if historico['historico_detalhado']:
        novo_ultimo = historico['historico_detalhado'][-1]
        print(f"\nNovo último registro:")
        print(f"  Data: {novo_ultimo['data']}")
        print(f"  Excluídos: {novo_ultimo['excluidos']}")
    
    # Criar backup
    backup_path = HISTORICO_PATH.replace('.json', '_backup_antes_correcao.json')
    with open(backup_path, 'w', encoding='utf-8') as f:
        with open(HISTORICO_PATH, 'r', encoding='utf-8') as original:
            f.write(original.read())
    print(f"\n✅ Backup criado: {backup_path}")
    
    # Salvar histórico corrigido
    with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Histórico corrigido salvo!")
    print('\n' + '=' * 70)
    print('CORREÇÃO CONCLUÍDA - O último backtest incorreto foi removido.')
    print('=' * 70)

if __name__ == '__main__':
    main()
