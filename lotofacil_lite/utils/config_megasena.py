#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CONFIGURAÇÕES DO GERADOR ACADÊMICO MEGA-SENA
===========================================
Arquivo de configuração centralizada para facilitar adaptações
"""

# Configurações da Mega-Sena
MEGASENA_CONFIG = {
    'nome_jogo': 'Mega-Sena',
    'total_numeros': 60,
    'numeros_por_jogo': 6,
    'numero_minimo': 1,
    'numero_maximo': 60,
    
    # Faixas de números
    'faixas': {
        'baixa': {'inicio': 1, 'fim': 20, 'nome': 'Baixa (1-20)'},
        'media': {'inicio': 21, 'fim': 40, 'nome': 'Média (21-40)'},
        'alta': {'inicio': 41, 'fim': 60, 'nome': 'Alta (41-60)'}
    },
    
    # Distribuições típicas
    'distribuicoes_tipicas': [
        {'baixa': 2, 'media': 2, 'alta': 2, 'nome': 'Equilibrada', 'peso': 0.3},
        {'baixa': 3, 'media': 2, 'alta': 1, 'nome': 'Mais Baixos', 'peso': 0.2},
        {'baixa': 1, 'media': 2, 'alta': 3, 'nome': 'Mais Altos', 'peso': 0.2},
        {'baixa': 2, 'media': 3, 'alta': 1, 'nome': 'Mais Médios', 'peso': 0.15},
        {'baixa': 1, 'media': 3, 'alta': 2, 'nome': 'Variação 1', 'peso': 0.1},
        {'baixa': 2, 'media': 1, 'alta': 3, 'nome': 'Variação 2', 'peso': 0.05}
    ],
    
    # Parâmetros estatísticos típicos
    'parametros_estatisticos': {
        'soma_minima': 21,     # 1+2+3+4+5+6
        'soma_maxima': 345,    # 55+56+57+58+59+60
        'soma_media_esperada': 183,  # Aproximadamente
        'soma_desvio_padrao': 45,
        'consecutivos_max_comum': 2,
        'pares_mais_comum': 3,
        'impares_mais_comum': 3
    },
    
    # Estratégias disponíveis
    'estrategias': {
        'equilibrada': {
            'nome': 'Equilibrada',
            'descricao': 'Distribuição uniforme por faixas',
            'peso_quentes': 0.4,
            'peso_frios': 0.2,
            'peso_aleatorio': 0.4
        },
        'quentes': {
            'nome': 'Números Quentes',
            'descricao': 'Prioriza números mais frequentes',
            'peso_quentes': 0.7,
            'peso_frios': 0.1,
            'peso_aleatorio': 0.2
        },
        'frios': {
            'nome': 'Números Frios',
            'descricao': 'Prioriza números menos frequentes',
            'peso_quentes': 0.1,
            'peso_frios': 0.7,
            'peso_aleatorio': 0.2
        },
        'contrarian': {
            'nome': 'Contrária',
            'descricao': 'Mix de quentes e frios',
            'peso_quentes': 0.3,
            'peso_frios': 0.3,
            'peso_aleatorio': 0.4
        }
    }
}

# Configurações de arquivo
ARQUIVO_CONFIG = {
    'encoding': 'utf-8',
    'prefixo_nome': 'combinacoes_megasena',
    'formato_data': '%Y%m%d_%H%M%S',
    'formato_display_data': '%d/%m/%Y %H:%M:%S',
    'separador_numeros': ' - ',
    'formato_numero': '{:02d}',
    'extensao': '.txt'
}

# Configurações de análise
ANALISE_CONFIG = {
    'min_concursos_analise': 50,
    'top_numeros_quentes': 15,
    'top_numeros_frios': 15,
    'janela_analise_tendencia': 20,
    'limite_consecutivos_alerta': 3,
    'percentil_soma_baixa': 25,
    'percentil_soma_alta': 75
}

# Mensagens do sistema
MENSAGENS = {
    'inicializacao': '🎰 Gerador Acadêmico Mega-Sena inicializado',
    'carregamento_dados': '📂 Carregando dados históricos da Mega-Sena...',
    'analise_padroes': '🧠 Analisando padrões de frequência...',
    'geracao_combinacoes': '🤖 Gerando combinações com estratégia',
    'salvamento': '💾 Combinações salvas em:',
    'erro_dados': '⚠️ Carregue os dados históricos primeiro!',
    'erro_analise': '⚠️ Execute a análise de padrões primeiro!',
    'sucesso': '✅',
    'erro': '❌',
    'aviso': '⚠️',
    'info': 'ℹ️'
}

def get_configuracao_megasena():
    """Retorna configuração completa da Mega-Sena"""
    return MEGASENA_CONFIG

def get_configuracao_arquivo():
    """Retorna configuração de arquivos"""
    return ARQUIVO_CONFIG

def get_configuracao_analise():
    """Retorna configuração de análise"""
    return ANALISE_CONFIG

def get_mensagens():
    """Retorna dicionário de mensagens"""
    return MENSAGENS

# Validações
def validar_numero_megasena(numero):
    """Valida se o número está na faixa da Mega-Sena"""
    config = get_configuracao_megasena()
    return config['numero_minimo'] <= numero <= config['numero_maximo']

def validar_combinacao_megasena(combinacao):
    """Valida uma combinação para Mega-Sena"""
    config = get_configuracao_megasena()
    
    if len(combinacao) != config['numeros_por_jogo']:
        return False, f"Deve ter exatamente {config['numeros_por_jogo']} números"
    
    if len(set(combinacao)) != len(combinacao):
        return False, "Não pode ter números repetidos"
    
    for num in combinacao:
        if not validar_numero_megasena(num):
            return False, f"Número {num} fora da faixa válida"
    
    return True, "Combinação válida"

def get_faixa_numero(numero):
    """Retorna a faixa de um número"""
    config = get_configuracao_megasena()
    
    for nome, faixa in config['faixas'].items():
        if faixa['inicio'] <= numero <= faixa['fim']:
            return nome
    
    return 'indefinida'

def analisar_distribuicao_combinacao(combinacao):
    """Analisa a distribuição de uma combinação por faixas"""
    distribuicao = {'baixa': 0, 'media': 0, 'alta': 0}
    
    for numero in combinacao:
        faixa = get_faixa_numero(numero)
        if faixa in distribuicao:
            distribuicao[faixa] += 1
    
    return distribuicao

if __name__ == "__main__":
    # Teste das configurações
    print("🧪 TESTE DAS CONFIGURAÇÕES:")
    print("-" * 40)
    
    config = get_configuracao_megasena()
    print(f"✅ Jogo: {config['nome_jogo']}")
    print(f"✅ Números: {config['numeros_por_jogo']} de {config['numero_minimo']}-{config['numero_maximo']}")
    
    # Teste de validação
    combinacao_teste = [7, 15, 23, 31, 45, 52]
    valida, msg = validar_combinacao_megasena(combinacao_teste)
    print(f"✅ Teste combinação {combinacao_teste}: {msg}")
    
    # Teste de distribuição
    distribuicao = analisar_distribuicao_combinacao(combinacao_teste)
    print(f"✅ Distribuição: {distribuicao}")
    
    print("\n🎯 Configurações carregadas com sucesso!")
