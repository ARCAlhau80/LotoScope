"""
🌐 LotoScope Web Backend
Aplicação Flask para geração interativa de combinações da Lotofácil
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Adicionar o diretório do database ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

# Importação do serviço de banco de dados
try:
    from lotofacil_service import LotofacilDatabaseService
    db_service = LotofacilDatabaseService()
    DB_SERVICE_AVAILABLE = True
    print("✅ Serviço LotofacilDatabaseService carregado")
except ImportError as e:
    DB_SERVICE_AVAILABLE = False
    db_service = None
    print(f"⚠️ Serviço de banco não disponível: {e}")
except Exception as e:
    DB_SERVICE_AVAILABLE = False
    db_service = None
    print(f"⚠️ Erro ao carregar serviço de banco: {e}")

app = Flask(__name__, 
           template_folder='../frontend/templates',
           static_folder='../frontend/static')
CORS(app)  # Habilitar CORS para requisições do frontend

# Configuração global
app.config['SECRET_KEY'] = 'lotoscope-web-2025'

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Verificação de saúde da API"""
    return jsonify({
        'status': 'ok',
        'message': 'LotoScope Web API funcionando',
        'version': '1.0.0',
        'db_available': DB_SERVICE_AVAILABLE
    })

@app.route('/api/calculate-probability', methods=['POST'])
def calculate_probability():
    """
    Calcula probabilidade baseada nos números fixos e configuração
    """
    try:
        data = request.get_json()
        
        # Parâmetros do novo sistema de 4 estados
        selected_numbers = data.get('selected_numbers', [])
        mandatory_numbers = data.get('mandatory_numbers', [])
        excluded_numbers = data.get('excluded_numbers', [])
        
        # Compatibilidade com sistema antigo
        fixed_numbers = data.get('fixed_numbers', [])
        
        game_size = data.get('game_size', 15)
        quantity = data.get('quantity', 1)
        dynamic_filters = data.get('dynamic_filters', {})
        risk_profile = data.get('risk_profile', 'moderado')
        
        print(f"🎯 Probabilidade - Perfil: {risk_profile}")
        print(f"� Números selecionados: {selected_numbers}")
        print(f"🟡 Números obrigatórios: {mandatory_numbers}")
        print(f"�📌 Números fixos (compat.): {fixed_numbers}")
        if excluded_numbers:
            print(f"🚫 Números excluídos: {excluded_numbers}")
        if dynamic_filters:
            print(f"📊 Filtros dinâmicos recebidos: {dynamic_filters}")
        
        if DB_SERVICE_AVAILABLE and db_service:
            try:
                # Usar cálculo real do banco de dados com novo sistema de 4 estados
                result = db_service.calculate_probability(
                    fixed_numbers=fixed_numbers, 
                    game_size=game_size, 
                    quantity=quantity,
                    dynamic_filters=dynamic_filters, 
                    risk_profile=risk_profile,
                    excluded_numbers=excluded_numbers,
                    selected_numbers=selected_numbers,
                    mandatory_numbers=mandatory_numbers
                )
                return jsonify({
                    'success': True,
                    'total_combinations': result['total_combinations'],
                    'probability': result['probability'],
                    'fixed_count': result['fixed_count'],
                    'excluded_count': result.get('excluded_count', 0),
                    'remaining_slots': result['remaining_slots'],
                    'db_mode': 'connected'
                })
            except Exception as e:
                print(f"❌ Erro no serviço de banco: {e}")
                # Fallback para cálculo local
        
        # Cálculo melhorado de probabilidade (fallback)
        remaining_slots = game_size - len(fixed_numbers)
        available_numbers = 25 - len(fixed_numbers) - len(excluded_numbers)
        
        # Usar combinações para cálculo mais preciso
        if remaining_slots > 0 and available_numbers >= remaining_slots:
            # Cálculo C(available_numbers, remaining_slots)
            total_combinations = 1
            for i in range(remaining_slots):
                total_combinations *= (available_numbers - i)
                total_combinations //= (i + 1)
        else:
            total_combinations = 1
        
        # Ajustar para base realística da Lotofácil
        base_combinations = 3268760  # Total de combinações C(25,15)
        if len(fixed_numbers) > 0 or len(excluded_numbers) > 0:
            # Reduzir baseado nos números fixos e excluídos
            reduction_factor = 1.0
            for _ in fixed_numbers:
                reduction_factor *= 0.75  # Cada número fixo reduz ~25%
            for _ in excluded_numbers:
                reduction_factor *= 0.85  # Cada número excluído reduz ~15%
            total_combinations = int(base_combinations * reduction_factor)
        else:
            total_combinations = base_combinations
            
        total_combinations = max(total_combinations, quantity)
        probability = f"1 em {total_combinations // quantity:,}"
        
        return jsonify({
            'success': True,
            'total_combinations': total_combinations,
            'probability': probability,
            'fixed_count': len(fixed_numbers),
            'excluded_count': len(excluded_numbers),
            'remaining_slots': remaining_slots,
            'db_mode': 'simulation'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-combinations', methods=['POST'])
def generate_combinations():
    """
    Gera combinações baseadas na configuração com suporte a 4 estados de números
    """
    try:
        data = request.get_json()
        
        # Novos parâmetros para os 4 estados
        selected_numbers = data.get('selected_numbers', [])
        mandatory_numbers = data.get('mandatory_numbers', []) 
        excluded_numbers = data.get('excluded_numbers', [])
        
        # Compatibilidade com versão antiga
        fixed_numbers = data.get('fixed_numbers', [])
        if fixed_numbers and not selected_numbers and not mandatory_numbers:
            selected_numbers = fixed_numbers
            print("⚠️ Modo compatibilidade: fixed_numbers → selected_numbers")
        
        game_size = data.get('game_size', 15)
        quantity = data.get('quantity', 1)
        risk_profile = data.get('risk_profile', 'moderado')
        dynamic_filters = data.get('dynamic_filters', {})
        
        print(f"🎯 Perfil de risco: {risk_profile}")
        print(f"� Números SELECIONADOS: {selected_numbers}")
        print(f"🔒 Números OBRIGATÓRIOS: {mandatory_numbers}")
        print(f"🚫 Números EXCLUÍDOS: {excluded_numbers}")
        if dynamic_filters:
            print(f"� Filtros dinâmicos recebidos: {dynamic_filters}")
        
        # Tratar quantidade vazia ou zero como "todas"
        if quantity == "" or quantity is None or quantity == 0:
            quantity = None  # Indica que deve retornar todas
            print(f"🎯 Gerando TODAS as combinações que atendem os critérios")
        else:
            quantity = int(quantity)
            print(f"🎲 Gerando {quantity} combinações")
        
        if DB_SERVICE_AVAILABLE and db_service:
            try:
                # Usar geração real do banco de dados com nova lógica
                result = db_service.generate_combinations(
                    fixed_numbers=None,  # Deprecated
                    selected_numbers=selected_numbers,
                    mandatory_numbers=mandatory_numbers,
                    excluded_numbers=excluded_numbers,
                    game_size=game_size, 
                    quantity=quantity, 
                    dynamic_filters=dynamic_filters,
                    risk_profile=risk_profile
                )
                return jsonify({
                    'success': True,
                    'combinations': result['combinations'],
                    'count': result['count'],
                    'requested': quantity if quantity is not None else "todas",
                    'db_mode': 'connected',
                    'source': result['source']
                })
            except Exception as e:
                print(f"❌ Erro no serviço de banco: {e}")
                # Fallback para geração local
        
        # Limitar quantidade para evitar sobrecarga no fallback
        fallback_quantity = quantity if quantity is not None else 50
        fallback_quantity = min(fallback_quantity, 100)
        
        # Gerar combinações inteligentes (fallback)
        combinations = generate_smart_combinations(fixed_numbers, excluded_numbers, game_size, fallback_quantity)
        
        return jsonify({
            'success': True,
            'combinations': combinations,
            'count': len(combinations),
            'requested': quantity if quantity is not None else "todas",
            'db_mode': 'simulation',
            'source': 'fallback'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_smart_combinations(fixed_numbers, excluded_numbers, game_size, quantity):
    """
    Gera combinações inteligentes baseadas nos números fixos e excluídos (fallback)
    """
    combinations = []
    # Excluir números fixos e excluídos da lista de disponíveis
    excluded_set = set(fixed_numbers + excluded_numbers)
    available_numbers = [n for n in range(1, 26) if n not in excluded_set]
    needed_numbers = game_size - len(fixed_numbers)
    
    # Usar distribuição inteligente baseada em faixas posicionais
    position_ranges = {
        1: [1, 2, 3], 2: [2, 3, 4, 5], 3: [3, 4, 5, 6, 7],
        4: [4, 5, 6, 7, 8, 9], 5: [6, 7, 8, 9, 10, 11],
        6: [7, 8, 9, 10, 11, 12], 7: [9, 10, 11, 12, 13, 14],
        8: [10, 11, 12, 13, 14, 15, 16], 9: [12, 13, 14, 15, 16, 17],
        10: [14, 15, 16, 17, 18, 19], 11: [15, 16, 17, 18, 19, 20],
        12: [17, 18, 19, 20, 21, 22], 13: [19, 20, 21, 22, 23],
        14: [21, 22, 23, 24], 15: [23, 24, 25]
    }
    
    import random
    for _ in range(quantity):
        combination = fixed_numbers.copy()
        remaining_to_add = needed_numbers
        
        # Adicionar números baseado nas faixas posicionais
        attempts = 0
        while len(combination) < game_size and attempts < 100:
            # Selecionar posição aleatória que ainda precisa de número
            position = len(combination) + 1
            if position <= 15:
                # Escolher número da faixa apropriada, excluindo os proibidos
                valid_numbers = [n for n in position_ranges.get(position, available_numbers) 
                               if n not in combination and n in available_numbers]
                if valid_numbers:
                    number = random.choice(valid_numbers)
                    combination.append(number)
                else:
                    # Fallback: escolher qualquer número disponível
                    remaining = [n for n in available_numbers if n not in combination]
                    if remaining:
                        combination.append(random.choice(remaining))
            attempts += 1
        
        # Completar se necessário
        while len(combination) < game_size:
            remaining = [n for n in available_numbers if n not in combination]
            if remaining:
                combination.append(random.choice(remaining))
            else:
                break
        
        # Ordenar e adicionar se válida
        if len(combination) == game_size:
            combination.sort()
            if combination not in combinations:
                combinations.append(combination)
    
    return combinations

@app.route('/api/trend-info')
def get_trend_info():
    """
    Retorna informações das tendências preditivas e dados do concurso
    """
    try:
        if DB_SERVICE_AVAILABLE and db_service:
            try:
                # Obter informações de tendência
                filtros = db_service.get_dynamic_trend_filters()
                
                # Tentar obter informações do concurso
                concurso_info = {}
                try:
                    from lotofacil_lite.relatorio_tendencias_preditivas import RelatorioTendenciasPreditivas
                    relatorio = RelatorioTendenciasPreditivas()
                    if relatorio.obter_ultimo_concurso():
                        ultimo_concurso = relatorio.ultimo_concurso.get('concurso', 'N/A')
                        proximo_concurso = ultimo_concurso + 1 if isinstance(ultimo_concurso, int) else 'N/A'
                        concurso_info = {
                            'ultimo_concurso': ultimo_concurso,
                            'proximo_concurso': proximo_concurso,
                            'data_ultima_analise': relatorio.ultimo_concurso.get('data', 'N/A')
                        }
                except Exception as e:
                    print(f"⚠️ Erro ao obter info do concurso: {e}")
                    concurso_info = {
                        'ultimo_concurso': 'N/A',
                        'proximo_concurso': 'N/A',
                        'data_ultima_analise': 'N/A'
                    }
                
                # Obter dados REAIS do último concurso para inversão de tendências
                dados_reais_ultimo_concurso = {}
                try:
                    # Tentar obter dados reais via análise sequencial
                    from analise_sequencial import AnaliseSequencial
                    analise = AnaliseSequencial()
                    dados_ultimo = analise.obter_dados_ultimo_concurso()
                    
                    if dados_ultimo:
                        dados_reais_ultimo_concurso = {
                            'menor_que_ultimo': dados_ultimo.get('menor_que_ultimo'),
                            'maior_que_ultimo': dados_ultimo.get('maior_que_ultimo'), 
                            'igual_ao_ultimo': dados_ultimo.get('igual_ao_ultimo'),
                            'soma_total': dados_ultimo.get('soma_total')
                        }
                        print(f"✅ Dados REAIS do último concurso obtidos: {dados_reais_ultimo_concurso}")
                    else:
                        print("⚠️ Dados do último concurso não disponíveis")
                except Exception as e:
                    print(f"⚠️ Erro ao obter dados reais do último concurso: {e}")
                
                return jsonify({
                    'success': True,
                    'contest_info': concurso_info,
                    'trend_info': {
                        'resumo': filtros.get('resumo', 'N/A'),
                        'confianca': filtros.get('confianca', 0),
                        'fonte': filtros.get('fonte', 'padrao'),
                        'soma_esperada': {
                            'min': filtros.get('soma_total_min', 180),
                            'max': filtros.get('soma_total_max', 219)
                        },
                        'filtros_aplicados': {
                            'menor_que_ultimo': filtros.get('menor_que_ultimo', []),
                            'maior_que_ultimo': filtros.get('maior_que_ultimo', []),
                            'igual_ao_ultimo': filtros.get('igual_ao_ultimo', []),
                            'repetidos_mesma_posicao': filtros.get('repetidos_mesma_posicao', [])
                        },
                        # DADOS REAIS do último concurso para inversão de tendências
                        'ultimo_concurso_real': dados_reais_ultimo_concurso
                    },
                    'db_mode': 'connected'
                })
            except Exception as e:
                print(f"❌ Erro ao obter tendências: {e}")
        
        # Fallback quando não há acesso às tendências
        return jsonify({
            'success': True,
            'trend_info': {
                'resumo': 'Filtros padrão - Tendências não disponíveis',
                'confianca': 50.0,
                'fonte': 'padrao',
                'soma_esperada': {
                    'min': 180,
                    'max': 219
                },
                'filtros_aplicados': {
                    'menor_que_ultimo': [11, 12, 13, 14],
                    'maior_que_ultimo': [1, 2, 3, 4],
                    'igual_ao_ultimo': [0, 1, 2, 3, 4],
                    'repetidos_mesma_posicao': [0, 1, 2, 3, 4]
                }
            },
            'db_mode': 'simulation'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/base-stats')
def get_base_stats():
    """
    Retorna estatísticas da base de dados
    """
    try:
        if DB_SERVICE_AVAILABLE and db_service:
            try:
                # Aqui implementar get_stats no serviço se necessário
                pass
            except Exception as e:
                print(f"❌ Erro no serviço de banco: {e}")
        
        # Simulação de estatísticas realísticas
        return jsonify({
            'success': True,
            'stats': {
                'total_combinations_15': 3268760,
                'total_combinations_16': 2042975,
                'total_combinations_17': 1081575,
                'total_combinations_18': 480700,
                'total_combinations_19': 177100,
                'total_combinations_20': 53130,
                'most_frequent_numbers': [13, 5, 4, 16, 20, 18, 19, 10, 25, 14],
                'least_frequent_numbers': [26, 1, 2, 24, 23, 22, 21, 11, 7, 8],
                'db_mode': 'connected' if DB_SERVICE_AVAILABLE else 'simulation'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate-selection', methods=['POST'])
def validate_selection():
    """
    Valida se a seleção atual é válida
    """
    try:
        data = request.get_json()
        fixed_numbers = data.get('fixed_numbers', [])
        excluded_numbers = data.get('excluded_numbers', [])
        game_size = data.get('game_size', 15)
        
        # Validações
        errors = []
        warnings = []
        
        # Verificar conflitos entre fixos e excluídos
        conflitos = set(fixed_numbers) & set(excluded_numbers)
        if conflitos:
            errors.append(f"Números não podem ser fixos E excluídos: {list(conflitos)}")
        
        if len(fixed_numbers) >= game_size:
            errors.append("Números fixos não podem ser >= tamanho do jogo")
        
        # Verificar se há números suficientes disponíveis
        total_excluded = len(set(fixed_numbers + excluded_numbers))
        available_numbers = 25 - total_excluded
        if available_numbers < (game_size - len(fixed_numbers)):
            errors.append("Muitos números excluídos - insuficientes para completar o jogo")
        
        if len(set(fixed_numbers)) != len(fixed_numbers):
            errors.append("Números fixos duplicados")
            
        if len(set(excluded_numbers)) != len(excluded_numbers):
            errors.append("Números excluídos duplicados")
        
        # Validar range de números
        all_numbers = fixed_numbers + excluded_numbers
        if any(n < 1 or n > 25 for n in all_numbers):
            errors.append("Números devem estar entre 1 e 25")
        
        # Avisos para seleções extremas
        if len(fixed_numbers) > game_size * 0.8:
            warnings.append("Muitos números fixos podem limitar demais as combinações")
            
        if len(excluded_numbers) > 10:
            warnings.append("Muitos números excluídos podem reduzir drasticamente as opções")
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """
    🗑️ Limpa o cache de filtros dinâmicos para forçar nova análise
    """
    try:
        if DB_SERVICE_AVAILABLE and db_service:
            db_service.clear_cache()
            return jsonify({
                'success': True,
                'message': 'Cache limpo com sucesso - próxima análise será atualizada'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Serviço de banco não disponível'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export-combinations', methods=['POST'])
def export_combinations():
    """
    Exporta combinações em formato TXT
    """
    try:
        data = request.get_json()
        combinations = data.get('combinations', [])
        
        if not combinations:
            return jsonify({
                'success': False,
                'error': 'Nenhuma combinação fornecida'
            }), 400
        
        # Formatar combinações separadas por ponto e vírgula
        txt_content = []
        for i, combo in enumerate(combinations, 1):
            combo_str = ';'.join(map(str, combo))
            txt_content.append(f"{combo_str}")
        
        # Adicionar cabeçalho
        header = f"# LotoScope - Combinações Geradas\n"
        header += f"# Total: {len(combinations)} combinações\n"
        header += f"# Formato: números separados por ;\n\n"
        
        final_content = header + '\n'.join(txt_content)
        
        return jsonify({
            'success': True,
            'content': final_content,
            'filename': f'lotoscope_combinacoes_{len(combinations)}.txt'
        })
        
    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analise-sequencial', methods=['GET', 'POST'])
def analise_sequencial():
    """
    Endpoint para análise sequencial de padrões
    Analisa comportamento histórico dos valores menor_que, maior_que e igual_ao_ultimo
    """
    try:
        # Importar o módulo de análise sequencial
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
        from analise_sequencial import executar_analise_sequencial
        
        print("🔍 Executando análise sequencial de padrões...")
        resultado = executar_analise_sequencial()
        
        if resultado['success']:
            print(f"✅ Análise concluída - Concurso {resultado['concurso_analisado']}")
            return jsonify(resultado)
        else:
            print(f"❌ Erro na análise: {resultado.get('error', 'Erro desconhecido')}")
            return jsonify(resultado), 500
            
    except Exception as e:
        print(f"❌ Erro ao executar análise sequencial: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """
    🧪 Endpoint de teste
    """
    return jsonify({
        'message': 'Endpoint funcionando!',
        'success': True,
        'timestamp': str(datetime.now())
    })

@app.route('/api/last-draw', methods=['GET'])
def get_last_draw():
    """
    🎯 Busca os números do último sorteio da Lotofácil
    """
    try:
        print("🔍 Endpoint /api/last-draw chamado")
        if DB_SERVICE_AVAILABLE and db_service:
            print("✅ Banco disponível, buscando números do último sorteio...")
            result = db_service.get_last_draw_numbers()
            print(f"📊 Resultado do banco: {result}")
            return jsonify(result)
        else:
            print("⚠️ Banco não disponível, usando fallback")
            # Fallback quando banco não está disponível
            fallback_data = {
                'concurso': 3512,
                'numbers': [1, 2, 4, 5, 6, 8, 9, 11, 12, 14, 16, 17, 19, 23, 25],
                'success': True,
                'source': 'fallback'
            }
            print(f"📊 Dados fallback: {fallback_data}")
            return jsonify(fallback_data)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando LotoScope Web Backend...")
    print(f"📍 Acesse: http://localhost:5000")
    db_status = 'Conectado' if DB_SERVICE_AVAILABLE else 'Simulação'
    print(f"💾 Modo banco: {db_status}")
    app.run(debug=True, host='0.0.0.0', port=5000)