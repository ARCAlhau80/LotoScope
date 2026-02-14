"""
🎯 Database Service para LotoScope Web
Implementa a lógica exata baseada na tabela COMBINACOES_LOTOFACIL
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lotofacil_lite'))

from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import random

# Importar o relatório de tendências
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lotofacil_lite'))
    from relatorio_tendencias_preditivas import RelatorioTendenciasPreditivas
    print("✅ Módulo relatorio_tendencias_preditivas importado com sucesso")
    TENDENCIAS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erro ao importar relatorio_tendencias_preditivas: {e}")
    RelatorioTendenciasPreditivas = None
    TENDENCIAS_AVAILABLE = False

class LotofacilDatabaseService:
    def __init__(self):
        self.config = DatabaseConfig()
        self._cache_tendencias = None
        self._cache_timestamp = None
        
    def get_connection(self):
        """Obtém conexão com banco"""
        return self.config.get_connection()
    
    def get_dynamic_trend_filters(self):
        """
        Obtém filtros dinâmicos baseados na análise sequencial SEMPRE
        """
        import time
        
        # Cache por 5 minutos (300 segundos) - mais frequente para análise sequencial
        current_time = time.time()
        if (self._cache_tendencias and self._cache_timestamp and 
            current_time - self._cache_timestamp < 300):
            print("🔄 Usando filtros dinâmicos do cache")
            return self._cache_tendencias
        
        try:
            # SEMPRE tentar usar análise sequencial primeiro
            print("🔍 Tentando obter filtros via análise sequencial...")
            filtros_sequenciais = self._get_filters_from_sequential_analysis()
            
            if filtros_sequenciais:
                print("✅ Filtros da análise sequencial obtidos com sucesso")
                # Cachear resultado
                self._cache_tendencias = filtros_sequenciais
                self._cache_timestamp = current_time
                return filtros_sequenciais
            
            print("⚠️ Análise sequencial não disponível, tentando tendências preditivas...")
            
            # Fallback para tendências preditivas
            if TENDENCIAS_AVAILABLE:
                # Instanciar relatório de tendências
                relatorio = RelatorioTendenciasPreditivas()
                
                # Obter último concurso
                if not relatorio.obter_ultimo_concurso():
                    print("⚠️ Não foi possível obter último concurso")
                    return self._get_default_filters()
                
                # Carregar dados históricos
                if not relatorio.carregar_dados_historicos():
                    print("⚠️ Não foi possível carregar dados históricos")
                    return self._get_default_filters()
                
                # Analisar tendência da soma
                tendencia_soma = relatorio.analisar_tendencia_soma()
                
                # Verificar estado extremo
                estado_extremo = relatorio.verificar_estado_extremo()
                
                # Construir filtros baseados nas tendências
                filtros = self._build_trend_filters(tendencia_soma, estado_extremo, relatorio.ultimo_concurso)
                
                # Cachear resultado
                self._cache_tendencias = filtros
                self._cache_timestamp = current_time
                
                print(f"🔮 Filtros de tendência dinâmicos obtidos: {filtros['resumo']}")
                return filtros
            else:
                print("❌ Módulo de tendências também não disponível")
                return self._get_default_filters()
            
        except Exception as e:
            print(f"❌ Erro ao obter filtros dinâmicos: {e}")
            return self._get_default_filters()
    
    def clear_cache(self):
        """
        🗑️ Limpa o cache de filtros dinâmicos forçando nova análise
        """
        print("🗑️ Limpando cache de filtros dinâmicos...")
        self._cache_tendencias = None
        self._cache_timestamp = None
        print("✅ Cache limpo - próxima consulta fará nova análise")
    
    def _get_filters_from_sequential_analysis(self):
        """
        Obtém filtros dinâmicos da análise sequencial de padrões
        """
        try:
            from analise_sequencial import AnaliseSequencial
            
            # Executar análise sequencial
            analise = AnaliseSequencial()
            
            # Carregar dados completos
            if not analise.carregar_dados_completos():
                print("❌ Falha ao carregar dados para análise sequencial")
                return None
            
            # Obter dados do último concurso
            ultimo_concurso = analise.ultimo_concurso
            if not ultimo_concurso:
                print("❌ Dados do último concurso não disponíveis")
                return None
            
            concurso_analisado = ultimo_concurso.get('concurso', 'N/A')
            print(f"🔍 Análise sequencial do concurso {concurso_analisado}")
            
            # Usar lógica baseada na análise sequencial
            # Valores atuais do último concurso
            menor_atual = ultimo_concurso.get('menor_que_ultimo', 7)
            maior_atual = ultimo_concurso.get('maior_que_ultimo', 7)
            igual_atual = ultimo_concurso.get('igual_ao_ultimo', 3)
            
            print(f"📊 Valores atuais - menor: {menor_atual}, maior: {maior_atual}, igual: {igual_atual}")
            
            # Construir filtros dinâmicos baseados na análise dos padrões
            filtros = {
                'resumo': f"Análise sequencial - Concurso {concurso_analisado} (menor:{menor_atual}, maior:{maior_atual}, igual:{igual_atual})",
                'fonte': 'analise_sequencial',
                'confianca': 85.0
            }
            
            # LÓGICA DE ANÁLISE SEQUENCIAL SIMPLIFICADA:
            # Com base no histórico, definir faixas para o próximo sorteio
            
            # 1. MENOR_QUE_ULTIMO: Se está muito alto (14), tende a corrigir para baixo
            if menor_atual >= 12:
                filtros['menor_que_ultimo'] = [0, 1, 2, 3, 4, 5, 6]  # Correção para baixo
                print("📉 menor_que_ultimo: Correção intensa para baixo (atual muito alto)")
            elif menor_atual <= 3:
                filtros['menor_que_ultimo'] = [5, 6, 7, 8, 9, 10, 11] # Correção para cima
                print("📈 menor_que_ultimo: Correção para cima (atual muito baixo)")
            else:
                filtros['menor_que_ultimo'] = [menor_atual-2, menor_atual-1, menor_atual, menor_atual+1, menor_atual+2]
                print("🔄 menor_que_ultimo: Oscilação próxima ao atual")
            
            # 2. MAIOR_QUE_ULTIMO: Se está muito baixo (0), tende a corrigir para cima
            if maior_atual <= 2:
                filtros['maior_que_ultimo'] = [8, 9, 10, 11, 12, 13, 14, 15] # Correção para cima
                print("📈 maior_que_ultimo: Correção intensa para cima (atual muito baixo)")
            elif maior_atual >= 12:
                filtros['maior_que_ultimo'] = [0, 1, 2, 3, 4, 5, 6] # Correção para baixo
                print("📉 maior_que_ultimo: Correção para baixo (atual muito alto)")
            else:
                filtros['maior_que_ultimo'] = [maior_atual-2, maior_atual-1, maior_atual, maior_atual+1, maior_atual+2]
                print("🔄 maior_que_ultimo: Oscilação próxima ao atual")
            
            # 3. IGUAL_AO_ULTIMO: Baseado em padrões médios
            if igual_atual <= 1:
                filtros['igual_ao_ultimo'] = [1, 2, 3, 4, 5] # Tende a subir um pouco
                print("📈 igual_ao_ultimo: Correção leve para cima")
            elif igual_atual >= 6:
                filtros['igual_ao_ultimo'] = [0, 1, 2, 3] # Tende a descer
                print("📉 igual_ao_ultimo: Correção para baixo")
            else:
                filtros['igual_ao_ultimo'] = [0, 1, 2, 3, 4, 5] # Padrão normal
                print("🔄 igual_ao_ultimo: Faixa padrão")
            
            # Garantir que todos os valores estão no range correto (0-15)
            for campo in ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']:
                if campo in filtros:
                    filtros[campo] = [v for v in filtros[campo] if 0 <= v <= 15]
                    print(f"✅ {campo}: {filtros[campo]}")
            
            # Definir soma total baseada nos padrões históricos (conservador)
            filtros['soma_total_min'] = 175
            filtros['soma_total_max'] = 225
            
            # Repetidos na mesma posição (conservador)
            filtros['repetidos_mesma_posicao'] = [0, 1, 2, 3, 4]
            
            # Validar se todos os campos necessários estão presentes
            campos_obrigatorios = ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']
            for campo in campos_obrigatorios:
                if campo not in filtros or not filtros[campo]:
                    print(f"❌ Campo obrigatório {campo} não foi calculado corretamente")
                    return None
            
            print(f"🎯 Filtros da análise sequencial: {filtros}")
            return filtros
            
        except ImportError as e:
            print(f"❌ Módulo de análise sequencial não disponível: {e}")
            return None
        except Exception as e:
            print(f"❌ Erro na análise sequencial: {e}")
            return None
    
    def _get_default_filters(self):
        """Filtros padrão quando tendências não estão disponíveis"""
        print("⚠️ Usando filtros padrão (análise dinâmica não disponível)")
        return {
            'menor_que_ultimo': [11, 12, 13, 14, 15],
            'maior_que_ultimo': [1, 2, 3, 4, 5],
            'igual_ao_ultimo': [0, 1, 2, 3, 4, 5, 6, 7],
            'repetidos_mesma_posicao': [0, 1, 2, 3, 4],
            'soma_total_min': 180,
            'soma_total_max': 219,
            'resumo': 'Filtros padrão (análise dinâmica não disponível)',
            'fonte': 'padrao',
            'confianca': 50.0
        }
    
    def _build_trend_filters(self, tendencia_soma, estado_extremo, ultimo_concurso):
        """
        Constrói filtros dinâmicos baseados nas tendências - REGRA FUNDAMENTAL CORRIGIDA
        REGRA: menor_que_ultimo + maior_que_ultimo + igual_ao_ultimo = 15 (SEMPRE!)
        """
        filtros = {}
        
        # 1. Filtros baseados na tendência da soma
        faixa_esperada = tendencia_soma.get('faixa_esperada', (180, 219))
        filtros['soma_total_min'] = max(160, int(faixa_esperada[0] * 0.9))  # Margem de segurança
        filtros['soma_total_max'] = min(250, int(faixa_esperada[1] * 1.1))  # Margem de segurança
        
        # 2. Obter dados do último concurso para análise contextual
        menor_atual = ultimo_concurso.get('menor_que_ultimo', 7)
        maior_atual = ultimo_concurso.get('maior_que_ultimo', 7)
        
        # 3. Filtros baseados no estado extremo
        if estado_extremo.get('eh_extremo', False):
            # Em estados extremos, aplicar correção mais intensa - RESPEITANDO SOMA = 15
            # Se espera correção: menor alto (números baixos) + maior baixo + igual balanceado
            filtros['menor_que_ultimo'] = [8, 9, 10, 11, 12]      # 5 opções
            filtros['maior_que_ultimo'] = [0, 1, 2, 3, 4]         # 5 opções 
            filtros['igual_ao_ultimo'] = [0, 1, 2]                # 3 opções (8+3+1=15, 9+4+0=15, etc.)
            resumo = f"Estado extremo detectado - Correção intensa esperada"
        else:
            # Baseado na tendência da soma - NOVA LÓGICA COM SOMA = 15
            tendencia = tendencia_soma.get('tendencia', 'ESTABILIDADE')
            
            if tendencia == 'ALTA':
                # Esperamos mais números maiores que o último - LÓGICA CORRIGIDA
                # Para ter mais números maiores: menor_que baixo + maior_que alto
                filtros['menor_que_ultimo'] = [3, 4, 5]         # BAIXO (poucos números menores)
                filtros['maior_que_ultimo'] = [9, 10, 11]       # ALTO (muitos números maiores)
                filtros['igual_ao_ultimo'] = [1, 2, 3]          # Balanceado
                resumo = f"Tendência ALTA - Soma esperada: {faixa_esperada[0]}-{faixa_esperada[1]}"
                
            elif tendencia == 'BAIXA':
                # Esperamos mais números menores que o último - LÓGICA CORRIGIDA
                # Para ter mais números menores: menor_que alto + maior_que baixo
                filtros['menor_que_ultimo'] = [9, 10, 11]       # ALTO (muitos números menores)
                filtros['maior_que_ultimo'] = [2, 3, 4]         # BAIXO (poucos números maiores)
                filtros['igual_ao_ultimo'] = [1, 2, 3]          # Balanceado
                resumo = f"Tendência BAIXA - Soma esperada: {faixa_esperada[0]}-{faixa_esperada[1]}"
                
            elif tendencia == 'ESTABILIDADE_ALTA':
                # Estabilidade mantendo patamar alto - LÓGICA CORRIGIDA
                if menor_atual >= 11:
                    # Menor atual é ALTO (11) = muitos números menores que o último
                    # CORREÇÃO: próximo sorteio deve ter POUCOS números menores (menor_que baixo)
                    # e MUITOS números maiores (maior_que alto)
                    filtros['menor_que_ultimo'] = [3, 4, 5]        # BAIXO (poucos números menores)
                    filtros['maior_que_ultimo'] = [9, 10, 11]      # ALTO (muitos números maiores)
                    filtros['igual_ao_ultimo'] = [1, 2, 3]         # Balanceado
                    resumo = f"Estabilidade ALTA - Menor atual alto ({menor_atual}): correção para baixo"
                else:
                    # Padrão alto normal: manter equilíbrio elevado
                    filtros['menor_que_ultimo'] = [4, 5, 6]        # Médio-baixo
                    filtros['maior_que_ultimo'] = [7, 8, 9]        # Médio-alto  
                    filtros['igual_ao_ultimo'] = [1, 2, 3]         # Balanceado
                    resumo = f"Estabilidade ALTA - Padrão elevado mantido"
                
            elif tendencia == 'ESTABILIDADE_BAIXA':
                # Estabilidade com correção ascendente - LÓGICA CORRIGIDA
                # Se estamos baixo, queremos subir: menor_que baixo + maior_que alto
                filtros['menor_que_ultimo'] = [3, 4, 5]          # BAIXO (correção ascendente)
                filtros['maior_que_ultimo'] = [9, 10, 11]        # ALTO (correção ascendente)
                filtros['igual_ao_ultimo'] = [1, 2, 3]           # Médio
                resumo = f"Estabilidade BAIXA (menor:{menor_atual}, maior:{maior_atual}) - Correção ascendente"
                
            else:  # ESTABILIDADE normal
                # Estabilidade - LÓGICA CORRIGIDA CONTEXTUAL
                # Análise contextual baseada no estado atual
                if menor_atual >= 10:
                    # Se menor atual está alto: corrigir para baixo
                    filtros['menor_que_ultimo'] = [3, 4, 5]        # BAIXO (correção)
                    filtros['maior_que_ultimo'] = [9, 10, 11]      # ALTO (correção)
                    filtros['igual_ao_ultimo'] = [1, 2, 3]         # Médio
                elif menor_atual <= 5:
                    # Se menor atual está baixo: permitir subida
                    filtros['menor_que_ultimo'] = [7, 8, 9]        # ALTO (permitir subida)
                    filtros['maior_que_ultimo'] = [4, 5, 6]        # BAIXO (permitir subida)
                    filtros['igual_ao_ultimo'] = [1, 2, 3]         # Médio
                else:
                    # Estado realmente equilibrado: manter balanço
                    filtros['menor_que_ultimo'] = [5, 6, 7]        # Médio
                    filtros['maior_que_ultimo'] = [6, 7, 8]        # Médio
                    filtros['igual_ao_ultimo'] = [1, 2, 3]         # Baixo-médio
                resumo = f"Estabilidade contextual (menor:{menor_atual}, maior:{maior_atual}) - Lógica corrigida"
        
        # 4. Filtros para repetidos na mesma posição (conservador)
        filtros['repetidos_mesma_posicao'] = [0, 1, 2, 3, 4]
        
        # 5. Adicionar resumo
        filtros['resumo'] = resumo
        filtros['confianca'] = tendencia_soma.get('confianca', 60.0)
        filtros['fonte'] = 'tendencias_dinamicas'
        
        return filtros
    
    def calculate_probability(self, fixed_numbers=None, game_size=15, quantity=1, 
                            dynamic_filters=None, risk_profile='moderado', excluded_numbers=None,
                            selected_numbers=None, mandatory_numbers=None):
        """
        Calcula probabilidade real baseada nos filtros da tabela COMBINACOES_LOTOFACIL
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Converter para novo sistema se ainda usando o antigo
            if selected_numbers is None and mandatory_numbers is None:
                # Modo compatibilidade: usar fixed_numbers como selected_numbers
                selected_numbers = fixed_numbers or []
                mandatory_numbers = []
            else:
                # Modo novo: usar os parâmetros específicos
                selected_numbers = selected_numbers or []
                mandatory_numbers = mandatory_numbers or []
            
            # Montar query de contagem
            where_clause = self._build_where_clause(
                selected_numbers, mandatory_numbers, game_size, 
                dynamic_filters=dynamic_filters, 
                risk_profile=risk_profile,
                excluded_numbers=excluded_numbers or []
            )
            
            count_query = f"""
                SELECT COUNT_BIG(*) as total
                FROM COMBINACOES_LOTOFACIL
                WHERE {where_clause}
            """
            
            print(f"🔍 Query de probabilidade: {count_query}")
            cursor.execute(count_query)
            result = cursor.fetchone()
            total_combinations = result[0] if result else 0
            
            cursor.close()
            conn.close()
            
            # Garantir que quantity é inteiro
            qty = 1 if quantity in [None, '', 0] else int(quantity)
            
            # Calcular contagens para retorno
            total_selected = len(selected_numbers) + len(mandatory_numbers)
            fixed_count = len(fixed_numbers or []) if fixed_numbers else total_selected
            
            return {
                'total_combinations': total_combinations,
                'probability': f"1 em {max(1, total_combinations // qty):,}",
                'fixed_count': fixed_count,
                'selected_count': len(selected_numbers),
                'mandatory_count': len(mandatory_numbers),
                'excluded_count': len(excluded_numbers or []),
                'remaining_slots': game_size - total_selected
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular probabilidade: {e}")
            # Usar fixed_numbers se disponível, caso contrário usar selected+mandatory
            fallback_numbers = fixed_numbers or (selected_numbers + mandatory_numbers)
            return self._fallback_probability(fallback_numbers, game_size, quantity)
    
    def generate_combinations(self, fixed_numbers=None, game_size=15, quantity=1, 
                            dynamic_filters=None, risk_profile='moderado', excluded_numbers=None,
                            selected_numbers=None, mandatory_numbers=None):
        """
        Gera combinações reais da tabela COMBINACOES_LOTOFACIL
        
        Args:
            fixed_numbers: DEPRECATED - usar selected_numbers e mandatory_numbers
            selected_numbers: Números que devem aparecer em X% das combinações  
            mandatory_numbers: Números que DEVEM aparecer em TODAS as combinações
            excluded_numbers: Números que NÃO podem aparecer
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Compatibilidade: se usar fixed_numbers (modo antigo), tratar como selected
            if fixed_numbers and not selected_numbers and not mandatory_numbers:
                selected_numbers = fixed_numbers
                print("⚠️ Modo compatibilidade: fixed_numbers tratado como selected_numbers")
            
            # Montar query de seleção
            where_clause = self._build_where_clause(
                selected_numbers or [], mandatory_numbers or [], game_size,
                dynamic_filters=dynamic_filters,
                risk_profile=risk_profile,
                excluded_numbers=excluded_numbers or []
            )
            
            # Verificar se deve retornar todas as combinações
            if quantity is None or quantity == 0 or quantity == "":
                # Gerar TODAS as combinações que atendem os critérios
                select_query = f"""
                    SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
                    FROM COMBINACOES_LOTOFACIL
                    WHERE {where_clause}
                    ORDER BY CRYPT_GEN_RANDOM(4)
                """
                print(f"🎯 Query de geração (TODAS): {select_query}")
            else:
                # Converter quantity para inteiro e limitar quantidade para performance
                quantity = int(quantity) if quantity else 1
                quantity = min(quantity, 10000)  # Aumentei o limite máximo
                
                select_query = f"""
                    SELECT TOP {quantity} N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
                    FROM COMBINACOES_LOTOFACIL
                    WHERE {where_clause}
                    ORDER BY CRYPT_GEN_RANDOM(4)
                """
                print(f"🎲 Query de geração: {select_query}")
            
            print(f"🎲 Query de geração: {select_query}")
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute(select_query)
            results = cursor.fetchall()
            
            # Converter para lista de listas
            combinations = []
            for row in results:
                combo = list(row[:game_size])  # Pegar apenas os números necessários
                combinations.append(combo)
            
            cursor.close()
            conn.close()
            
            return {
                'combinations': combinations,
                'count': len(combinations),
                'source': 'database'
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar combinações: {e}")
            return self._fallback_combinations(fixed_numbers or [], game_size, quantity)
    
    def _build_where_clause(self, selected_numbers, mandatory_numbers, game_size, dynamic_filters=None, risk_profile='moderado', excluded_numbers=None):
        """
        Constrói a cláusula WHERE baseada na nova lógica de 4 estados
        
        Args:
            selected_numbers: Números selecionados (estratégia percentual)
            mandatory_numbers: Números obrigatórios (devem estar em todas)
            excluded_numbers: Números excluídos (não podem aparecer)
        """
        conditions = []
        
        # 1. FILTROS FIXOS (sempre aplicados para TODOS os perfis)
        fixed_filters = [
            "QtdePrimos in (2,3,4,5,6,7,8)",
            "QtdeFibonacci in (2,3,4,5,6)", 
            "QtdeImpares in (6,7,8,9,10)",
            "QtdeRepetidos in (7,8,9,10)",
            "Quintil1 in (1,2,3,4,5)",
            "Quintil2 in (1,2,3,4,5)", 
            "Quintil3 in (1,2,3,4,5)",
            "Quintil4 in (1,2,3,4,5)",
            "Quintil5 in (1,2,3,4,5)",
            "seq in (6,7,8,9,10,11,12,13,14)",
            "qtdeMultiplos3 in (3,4,5,6)",
            "distanciaExtremos in (19,20,21,22,23,24)"
        ]
        conditions.extend(fixed_filters)
        print(f"🔧 Aplicando filtros FIXOS para perfil: {risk_profile}")
        
        # 2. FILTROS DINÂMICOS (baseados em análise sequencial ou tendências)
        # NOVO PERFIL: SEM_PERFIL - Não aplica filtros dinâmicos
        if risk_profile == 'sem_perfil':
            print("🔓 SEM PERFIL: Pulando TODOS os filtros dinâmicos (retorna todas as combinações)")
        else:
            try:
                # Se filtros dinâmicos foram fornecidos, usar eles
                # Verificar se há filtros com valores válidos (não None e não vazios)
                has_valid_filters = False
                if dynamic_filters:
                    for key, value in dynamic_filters.items():
                        if value is not None and value != [] and value != '':
                            has_valid_filters = True
                            break
                
                if has_valid_filters:
                    print(f"🎯 Usando filtros dinâmicos fornecidos (perfil: {risk_profile})")
                    print(f"🔍 Filtros recebidos: {dynamic_filters}")
                    filtros_dinamicos = self._process_dynamic_filters(dynamic_filters)
                else:
                    # Usar filtros padrão do sistema
                    print("📊 Usando filtros padrão do sistema")
                    filtros_dinamicos = self.get_dynamic_trend_filters()
            
                # Aplicar filtros dinâmicos - CONSERVADOR usa apenas 3 filtros principais
                if filtros_dinamicos.get('menor_que_ultimo'):
                    menor_values = ','.join(map(str, filtros_dinamicos['menor_que_ultimo']))
                    conditions.append(f"menor_que_ultimo in ({menor_values})")
                    print(f"🔧 Aplicado menor_que_ultimo: {menor_values}")
                
                if filtros_dinamicos.get('maior_que_ultimo'):
                    maior_values = ','.join(map(str, filtros_dinamicos['maior_que_ultimo']))
                    conditions.append(f"maior_que_ultimo in ({maior_values})")
                    print(f"🔧 Aplicado maior_que_ultimo: {maior_values}")
                
                if filtros_dinamicos.get('igual_ao_ultimo'):
                    igual_values = ','.join(map(str, filtros_dinamicos['igual_ao_ultimo']))
                    conditions.append(f"igual_ao_ultimo in ({igual_values})")
                    print(f"🔧 Aplicado igual_ao_ultimo: {igual_values}")
                
                # CONSERVADOR: aplicar APENAS os 3 filtros principais (menor, maior, igual)
                if risk_profile != 'conservador':
                    # Para AGRESSIVO e MODERADO: aplicar todos os filtros
                    if filtros_dinamicos.get('repetidos_mesma_posicao'):
                        repetidos_values = ','.join(map(str, filtros_dinamicos['repetidos_mesma_posicao']))
                        conditions.append(f"repetidosMesmaPosicao in ({repetidos_values})")
                        print(f"🔧 Aplicado repetidos_mesma_posicao: {repetidos_values}")
                    
                    if filtros_dinamicos.get('soma_total_min') and filtros_dinamicos.get('soma_total_max'):
                        soma_min = filtros_dinamicos['soma_total_min']
                        soma_max = filtros_dinamicos['soma_total_max']
                        conditions.append(f"SomaTotal between {soma_min} and {soma_max}")
                        print(f"🔧 Aplicado SomaTotal: {soma_min} - {soma_max}")
                else:
                    print(f"🛡️ CONSERVADOR: Pulando filtros adicionais (repetidos_mesma_posicao, soma_total)")
                    print(f"🛡️ CONSERVADOR: Usando APENAS 3 filtros dinâmicos principais")
                
                if filtros_dinamicos.get('resumo'):
                    print(f"🔮 Filtros aplicados: {filtros_dinamicos['resumo']}")
                else:
                    print(f"🔮 Filtros dinâmicos aplicados com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao aplicar filtros dinâmicos, usando padrão: {e}")
                # Fallback para filtros estáticos
                dynamic_filters = [
                    "menor_que_ultimo in (11,12,13,14,15)",
                    "maior_que_ultimo in (1,2,3,4,5)", 
                    "igual_ao_ultimo in (0,1,2,3,4,5,6,7)",
                    "repetidosMesmaPosicao in (0,1,2,3,4)",
                    "SomaTotal between 180 and 219"
                ]
                conditions.extend(dynamic_filters)
        
        # 3. RANGES POSICIONAIS ESPECÍFICOS 
        if risk_profile == 'sem_perfil':
            print("🔓 SEM PERFIL: Pulando filtros posicionais")
        elif risk_profile != 'conservador':
            # AGRESSIVO e MODERADO: usar ranges específicos
            position_ranges = self._get_specific_position_ranges()
            for pos, values in position_ranges.items():
                if values:
                    values_str = ','.join(map(str, values))
                    conditions.append(f"{pos} in ({values_str})")
            print(f"🎯 Aplicando filtros POSICIONAIS para perfil: {risk_profile}")
        else:
            # CONSERVADOR: usar ranges amplos para permitir números fixos funcionarem
            wide_position_ranges = self._get_wide_position_ranges()
            for pos, values in wide_position_ranges.items():
                if values:
                    values_str = ','.join(map(str, values))
                    conditions.append(f"{pos} in ({values_str})")
            print(f"🛡️ CONSERVADOR: Aplicando filtros posicionais AMPLOS (para suportar números fixos)")
        
        # 4. NÚMEROS DO USUÁRIO (nova lógica com 4 estados)
        print(f"🎯 Processando números do usuário para perfil: {risk_profile}")
        
        # 4A. NÚMEROS OBRIGATÓRIOS (devem aparecer em TODAS as combinações)
        if mandatory_numbers:
            mandatory_constraints = self._build_mandatory_numbers_constraints(mandatory_numbers)
            conditions.extend(mandatory_constraints)
            print(f"🔒 Números OBRIGATÓRIOS: {mandatory_numbers}")
        
        # 4B. NÚMEROS SELECIONADOS (estratégia percentual)
        if selected_numbers:
            selected_constraints = self._build_selected_numbers_constraints(selected_numbers, mandatory_numbers)
            conditions.extend(selected_constraints)
            print(f"� Números SELECIONADOS: {selected_numbers}")
        
        # 4C. NÚMEROS EXCLUÍDOS (não podem aparecer)
        if excluded_numbers:
            excluded_constraints = self._build_excluded_numbers_constraints(excluded_numbers)
            conditions.extend(excluded_constraints)
            print(f"🚫 Números EXCLUÍDOS: {excluded_numbers}")
        
        return " AND ".join(conditions)
    
    def _process_dynamic_filters(self, dynamic_filters):
        """
        Processa filtros dinâmicos recebidos do frontend
        """
        processed = {}
        
        # Processar cada filtro se não for None e não estiver vazio
        for key, value in dynamic_filters.items():
            if value is not None and value != [] and value != '':
                if isinstance(value, list) and len(value) > 0:
                    processed[key] = value
                    print(f"✅ Filtro {key}: {value}")
                elif isinstance(value, (int, float)):
                    processed[key] = value
                    print(f"✅ Filtro {key}: {value}")
                else:
                    print(f"⚠️ Filtro {key} ignorado - valor inválido: {value}")
            else:
                print(f"🔍 Filtro {key} ignorado - valor vazio: {value}")
                    
        print(f"🎯 Filtros processados finais: {processed}")
        return processed
    
    def _get_specific_position_ranges(self):
        """
        Retorna os ranges posicionais específicos (da análise de tendências)
        """
        return {
            'n1': [1, 2],
            'n2': [2, 3], 
            'n3': [3, 4, 5],
            'n4': [5, 6, 7],
            'n5': [6, 7, 8],
            'n6': [8, 9, 10],
            'n7': [10, 11, 12],
            'n8': [11, 12, 13, 14],
            'n9': [14, 15, 16],
            'n10': [15, 16, 17],
            'n11': [17, 18, 19],
            'n12': [19, 20, 21],
            'n13': [20, 21, 22],
            # n14 e n15 não aparecem no exemplo específico
        }
    
    def _get_wide_position_ranges(self):
        """
        Retorna ranges posicionais MUITO amplos para CONSERVADOR (máxima flexibilidade + inversão menor/maior)
        Ranges especificados pelo usuário para maior amplitude mantendo a lógica posicional
        """
        return {
            'n1': [1, 2, 3, 4, 5],
            'n2': [2, 3, 4, 5, 6, 7], 
            'n3': [3, 4, 5, 6, 7, 8],
            'n4': [4, 5, 6, 7, 8, 9, 10],
            'n5': [5, 6, 7, 8, 9, 10, 11],
            'n6': [6, 7, 8, 9, 10, 11, 12, 13],
            'n7': [8, 9, 10, 11, 12, 13, 14, 15],
            'n8': [9, 10, 11, 12, 13, 14, 15, 16, 17],
            'n9': [11, 12, 13, 14, 15, 16, 17, 18],
            'n10': [12, 13, 14, 15, 16, 17, 18, 19, 20],
            'n11': [14, 15, 16, 17, 18, 19, 20, 21],
            'n12': [16, 17, 18, 19, 20, 21, 22],
            'n13': [18, 19, 20, 21, 22, 23],
            'n14': [20, 21, 22, 23, 24],
            'n15': [22, 23, 24, 25]
        }
    
    def _build_mandatory_numbers_constraints(self, mandatory_numbers):
        """
        Constrói constraints para números OBRIGATÓRIOS (devem aparecer em TODAS as combinações)
        Cada número deve estar presente obrigatoriamente
        """
        constraints = []
        
        if not mandatory_numbers:
            return constraints
            
        print(f"🔒 Processando {len(mandatory_numbers)} números OBRIGATÓRIOS: {mandatory_numbers}")
        
        # Para cada número obrigatório, adicionar constraint de presença (abordagem simplificada)
        for number in mandatory_numbers:
            constraint = f"{number} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)"
            constraints.append(constraint)
            print(f"🔒 Número {number} OBRIGATÓRIO em qualquer posição")
        
        print(f"✅ Geradas {len(constraints)} constraints para números OBRIGATÓRIOS")
        return constraints

    def _build_selected_numbers_constraints(self, selected_numbers, mandatory_numbers=None):
        """
        Constrói constraints para números SELECIONADOS (estratégia percentual CASE)
        
        REGRA CLARA:
        - Até 15 selecionados: TODOS devem estar presentes
        - Mais de 15 selecionados: SEMPRE 15 números desse grupo (ou 15-obrigatórios se houver fixos)
        """
        constraints = []
        
        if not selected_numbers:
            return constraints
        
        print(f"📊 Processando {len(selected_numbers)} números SELECIONADOS")
        
        # REGRA CLARA IMPLEMENTADA:
        # Até 15 selecionados: TODOS devem estar presentes
        # Mais de 15 selecionados: SEMPRE 15 números desse grupo (ajustado por obrigatórios)
        if len(selected_numbers) <= 15:
            print(f"🔢 ≤15 números: TODOS devem estar presentes")
            # Para poucos números: todos devem estar presentes (abordagem simplificada)
            for number in selected_numbers:
                constraint = f"{number} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15)"
                constraints.append(constraint)
                print(f"🔢 Número {number} OBRIGATÓRIO em qualquer posição")
            
            return constraints
        
        # Para muitos números (>15): usar estratégia CASE
        # Ajustar pela quantidade de números obrigatórios
        num_mandatory = len(mandatory_numbers) if mandatory_numbers else 0
        min_required = 15 - num_mandatory  # 15 total menos os obrigatórios
        
        print(f"🧮 >15 números: {min_required} números dos selecionados (15 total - {num_mandatory} obrigatórios)")
        
        if min_required <= 0:
            print("⚠️ Todos os slots já ocupados por números obrigatórios")
            return constraints
        
        # ABORDAGEM SIMPLIFICADA: usar IN com todas as colunas
        case_conditions = []
        print(f"📋 Gerando CASE WHEN IN para números: {selected_numbers}")
        
        for num in selected_numbers:
            case_condition = f"CASE WHEN {num} IN (N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15) THEN 1 ELSE 0 END"
            case_conditions.append(case_condition)
            print(f"  ✅ Número {num}: pode aparecer em qualquer posição")
        
        print(f"📊 Total de CASE WHEN gerados: {len(case_conditions)}")
        
        # Criar constraint que soma todos os CASE e exige EXATAMENTE
        if case_conditions:
            sum_case = " + ".join(case_conditions)
            constraint = f"({sum_case}) = {min_required}"
            constraints.append(constraint)
            print(f"✅ Constraint CASE criada: EXATAMENTE {min_required} números devem estar presentes")
            print(f"🔍 Constraint SQL: {constraint[:200]}..." if len(constraint) > 200 else f"🔍 Constraint SQL: {constraint}")
        
        return constraints

    def _build_fixed_numbers_constraints(self, fixed_numbers):
        """
        Constrói constraints para números fixos escolhidos pelo usuário
        
        LÓGICA INTELIGENTE:
        - Até 15 números: TODOS devem estar presentes (lógica atual)
        - Mais de 15 números: Pelo menos 12 dos números escolhidos devem estar presentes
        """
        constraints = []
        
        if not fixed_numbers:
            return constraints
            
        print(f"🔢 Processando {len(fixed_numbers)} números fixos: {fixed_numbers}")
        
        # ESTRATÉGIA 1: ATÉ 15 NÚMEROS - TODOS DEVEM ESTAR PRESENTES
        if len(fixed_numbers) <= 15:
            print("📌 Usando estratégia: TODOS os números devem estar presentes")
            
            # Mapeamento de qual número pode aparecer em quais posições
            number_position_map = {
                1: ['n1'], 2: ['n1', 'n2'], 3: ['n1', 'n2', 'n3'], 4: ['n2', 'n3', 'n4'], 
                5: ['n1', 'n2', 'n3', 'n4'], 6: ['n3', 'n4', 'n5'], 7: ['n3', 'n4', 'n5', 'n6'],
                8: ['n4', 'n5', 'n6'], 9: ['n4', 'n5', 'n6', 'n7'], 10: ['n5', 'n6', 'n7', 'n8'],
                11: ['n5', 'n6', 'n7', 'n8'], 12: ['n6', 'n7', 'n8', 'n9'], 
                13: ['n6', 'n7', 'n8', 'n9', 'n10'], 14: ['n7', 'n8', 'n9', 'n10'],
                15: ['n8', 'n9', 'n10', 'n11'], 16: ['n8', 'n9', 'n10', 'n11'],
                17: ['n9', 'n10', 'n11', 'n12'], 18: ['n10', 'n11', 'n12'],
                19: ['n10', 'n11', 'n12', 'n13'], 20: ['n11', 'n12', 'n13'],
                21: ['n12', 'n13', 'n14'], 22: ['n12', 'n13', 'n14'],
                23: ['n13', 'n14', 'n15'], 24: ['n14', 'n15'], 25: ['n15']
            }
            
            # Para cada número fixo, adicionar constraint
            for number in fixed_numbers:
                if number in number_position_map:
                    positions = number_position_map[number]
                    position_list = ','.join(positions)
                    constraints.append(f"{number} in ({position_list})")
        
        # ESTRATÉGIA 2: MAIS DE 15 NÚMEROS - PELO MENOS X DEVEM ESTAR PRESENTES  
        else:
            print("🎯 Usando estratégia: PELO MENOS 12 dos números escolhidos devem estar presentes")
            
            # Calcular quantos números devem estar presentes (mínimo 80% ou 12, o que for maior)
            min_required = max(12, int(len(fixed_numbers) * 0.8))
            min_required = min(min_required, 15)  # Máximo 15 (tamanho da combinação)
            
            print(f"📊 Exigindo pelo menos {min_required} números dos {len(fixed_numbers)} escolhidos")
            
            # Usar função de contagem para verificar quantos números escolhidos estão presentes
            numbers_str = ','.join(map(str, fixed_numbers))
            
            # Constraint que conta quantos dos números escolhidos estão na combinação
            count_constraint = f"""
            (
                (CASE WHEN n1 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n2 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n3 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n4 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n5 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n6 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n7 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n8 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n9 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n10 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n11 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n12 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n13 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n14 IN ({numbers_str}) THEN 1 ELSE 0 END) +
                (CASE WHEN n15 IN ({numbers_str}) THEN 1 ELSE 0 END)
            ) >= {min_required}
            """
            
            constraints.append(count_constraint)
        
        print(f"✅ Geradas {len(constraints)} constraints para números fixos")
        return constraints
    
    def _build_excluded_numbers_constraints(self, excluded_numbers):
        """
        Constrói constraints para números EXCLUÍDOS escolhidos pelo usuário
        Usa NOT IN para garantir que os números não apareçam em nenhuma posição
        """
        constraints = []
        
        # Para cada número excluído, criar constraint NOT IN para todas as posições
        for number in excluded_numbers:
            if 1 <= number <= 25:  # Validar range
                # Criar constraint NOT IN para todas as 15 posições
                all_positions = ','.join([f'n{i}' for i in range(1, 16)])
                constraints.append(f"{number} not in ({all_positions})")
                print(f"🚫 Número {number} excluído de todas as posições")
        
        return constraints
    
    def _fallback_probability(self, fixed_numbers, game_size, quantity):
        """Fallback quando banco não está disponível"""
        base = 3268760  # Total combinações C(25,15)
        reduction = 0.8 ** len(fixed_numbers)
        total = int(base * reduction)
        
        # Garantir que quantity é inteiro
        qty = 1 if quantity in [None, '', 0] else int(quantity)
        
        return {
            'total_combinations': total,
            'probability': f"1 em {max(1, total // qty):,}",
            'fixed_count': len(fixed_numbers),
            'remaining_slots': game_size - len(fixed_numbers)
        }
    
    def _fallback_combinations(self, fixed_numbers, game_size, quantity):
        """Fallback quando banco não está disponível"""
        combinations = []
        # Garantir que quantity é inteiro
        qty = 1 if quantity in [None, '', 0] else int(quantity)
        
        for _ in range(min(qty, 10)):
            combo = fixed_numbers.copy()
            available = [n for n in range(1, 26) if n not in fixed_numbers]
            while len(combo) < game_size and available:
                combo.append(available.pop(random.randint(0, len(available)-1)))
            combinations.append(sorted(combo))
        
        return {
            'combinations': combinations,
            'count': len(combinations),
            'source': 'fallback'
        }

    def get_last_draw_numbers(self):
        """
        Busca os números do último sorteio da Lotofácil na tabela resultados_int
        """
        try:
            print("🔍 Buscando último resultado na tabela resultados_int...")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query simples na tabela resultados_int
            query = """
            SELECT TOP 1 concurso, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15
            FROM resultados_int
            ORDER BY concurso DESC
            """
            
            print(f"🔍 Executando query: {query}")
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result:
                concurso = result[0]
                numbers = sorted([result[i] for i in range(1, 16)])  # n1 até n15
                
                print(f"✅ Último sorteio encontrado - Concurso: {concurso}, Números: {numbers}")
                
                cursor.close()
                conn.close()
                
                return {
                    'concurso': concurso,
                    'numbers': numbers,
                    'success': True,
                    'source': 'resultados_int'
                }
            else:
                print("❌ Nenhum resultado encontrado na tabela resultados_int")
                cursor.close()
                conn.close()
                
                return {
                    'concurso': None,
                    'numbers': [],
                    'success': False,
                    'error': 'Nenhum resultado encontrado'
                }
                
        except Exception as e:
            print(f"❌ Erro ao buscar na tabela resultados_int: {e}")
            return {
                'concurso': None,
                'numbers': [],
                'success': False,
                'error': str(e)
            }