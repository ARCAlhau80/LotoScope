"""
🔍 Análise Sequencial de Padrões - LotoScope Web
Analisa comportamento histórico dos valores menor_que, maior_que e igual_ao_ultimo
"""
import sys
import os

# Adicionar o diretório do database ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lotofacil_lite'))

try:
    from database_config import DatabaseConfig

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

    db_config = DatabaseConfig()
    print("✅ Módulo DatabaseConfig importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar DatabaseConfig: {e}")
    db_config = None

from collections import defaultdict, Counter
import statistics

class AnaliseSequencial:
    def __init__(self):
        self.dados_historicos = []
        self.ultimo_concurso = None
        
    def carregar_dados_completos(self):
        """Carrega todos os dados históricos para análise sequencial"""
        query = """
        SELECT 
            concurso,
            menor_que_ultimo,
            maior_que_ultimo,
            igual_ao_ultimo,
            SomaTotal
        FROM RESULTADOS_INT 
        WHERE menor_que_ultimo IS NOT NULL 
            AND maior_que_ultimo IS NOT NULL 
            AND igual_ao_ultimo IS NOT NULL
        ORDER BY concurso ASC
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                # Converter para lista de dicionários
                colunas = [desc[0] for desc in cursor.description]
                self.dados_historicos = [dict(zip(colunas, row)) for row in resultados]
                
                # Último concurso
                self.ultimo_concurso = self.dados_historicos[-1]
                
                cursor.close()
                conn.close()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_padrao_sequencial(self, campo, valor_atual):
        """
        Analisa o comportamento sequencial de um campo específico
        
        Args:
            campo: 'menor_que_ultimo', 'maior_que_ultimo' ou 'igual_ao_ultimo'
            valor_atual: valor do campo no último sorteio
        """
        # Encontrar todas as ocorrências do valor atual
        ocorrencias = []
        proximos_valores = []
        
        for i in range(len(self.dados_historicos) - 1):  # -1 porque precisamos do próximo
            concurso_atual = self.dados_historicos[i]
            proximo_concurso = self.dados_historicos[i + 1]
            
            if concurso_atual[campo] == valor_atual:
                ocorrencias.append({
                    'concurso': concurso_atual['concurso'],
                    'valor_atual': concurso_atual[campo],
                    'proximo_valor': proximo_concurso[campo],
                    'proximo_concurso': proximo_concurso['concurso']
                })
                proximos_valores.append(proximo_concurso[campo])
        
        if not ocorrencias:
            return None
        
        # Análise estatística
        contador = Counter(proximos_valores)
        total_ocorrencias = len(proximos_valores)
        
        # Calcular estatísticas
        media = statistics.mean(proximos_valores)
        mediana = statistics.median(proximos_valores)
        
        # Criar distribuição de probabilidades
        distribuicao = {}
        for valor in range(0, 16):  # 0 a 15 possíveis
            count = contador.get(valor, 0)
            percentual = (count / total_ocorrencias) * 100 if total_ocorrencias > 0 else 0
            distribuicao[valor] = {
                'count': count,
                'percentual': percentual
            }
        
        # Encontrar faixa mais provável (valores com maior probabilidade)
        valores_ordenados = sorted(contador.items(), key=lambda x: x[1], reverse=True)
        
        # Calcular intervalo de confiança (80% dos casos)
        valores_acumulados = 0
        faixa_80_porcento = []
        
        for valor, count in valores_ordenados:
            valores_acumulados += count
            faixa_80_porcento.append(valor)
            if valores_acumulados >= total_ocorrencias * 0.8:
                break
        
        faixa_80_porcento.sort()
        
        resultado = {
            'campo': campo,
            'valor_atual': valor_atual,
            'total_ocorrencias': total_ocorrencias,
            'ocorrencias_detalhadas': ocorrencias,
            'proximos_valores': proximos_valores,
            'distribuicao': distribuicao,
            'estatisticas': {
                'media': round(media, 2),
                'mediana': mediana,
                'minimo': min(proximos_valores),
                'maximo': max(proximos_valores)
            },
            'mais_frequentes': valores_ordenados[:5],  # Top 5
            'faixa_80_porcento': {
                'valores': faixa_80_porcento,
                'minimo': min(faixa_80_porcento),
                'maximo': max(faixa_80_porcento)
            }
        }
        
        return resultado
    
    def analise_completa_ultimo_sorteio(self):
        """Executa análise completa baseada no último sorteio - Para API Web"""
        if not self.ultimo_concurso:
            return None
        
        ultimo = self.ultimo_concurso
        
        # Analisar cada campo
        resultados = {
            'concurso_analisado': ultimo['concurso'],
            'valores_atuais': {
                'menor_que_ultimo': ultimo['menor_que_ultimo'],
                'maior_que_ultimo': ultimo['maior_que_ultimo'],
                'igual_ao_ultimo': ultimo['igual_ao_ultimo']
            },
            'analises': {}
        }
        
        for campo in ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']:
            valor_atual = ultimo[campo]
            resultado = self.analisar_padrao_sequencial(campo, valor_atual)
            if resultado:
                resultados['analises'][campo] = resultado
        
        return resultados
    
    def calcular_perfis_risco(self, analise):
        """
        Calcula as faixas para os diferentes perfis de risco
        
        Args:
            analise: resultado da análise de um campo
            
        Returns:
            dict: perfis conservador, moderado e agressivo
        """
        faixa_80 = analise['faixa_80_porcento']
        minimo = faixa_80['minimo']
        maximo = faixa_80['maximo']
        centro = (minimo + maximo) / 2
        amplitude = maximo - minimo
        
        # Calcular perfis
        perfis = {
            'moderado': {
                'min': minimo,
                'max': maximo,
                'descricao': 'Usar previsões exatas da análise'
            },
            'conservador': {
                'min': max(0, int(minimo - amplitude * 0.3)),  # Amplia 30% para baixo
                'max': min(15, int(maximo + amplitude * 0.3)), # Amplia 30% para cima (max 15 para lotofácil)
                'descricao': 'Faixas ampliadas para maior segurança'
            },
            'agressivo': {
                'min': max(minimo, int(centro - amplitude * 0.25)),  # 25% em torno do centro
                'max': min(maximo, int(centro + amplitude * 0.25)),  # 25% em torno do centro
                'descricao': 'Foco na região mais provável'
            }
        }
        
        return perfis
    
    def gerar_relatorio_web(self):
        """Gera relatório formatado para exibição web"""
        if not self.carregar_dados_completos():
            return {'success': False, 'error': 'Falha ao carregar dados'}
        
        resultados = self.analise_completa_ultimo_sorteio()
        if not resultados:
            return {'success': False, 'error': 'Falha na análise'}
        
        # Formatar para web
        relatorio = {
            'success': True,
            'concurso_analisado': resultados['concurso_analisado'],
            'valores_atuais': resultados['valores_atuais'],
            'previsoes': {},
            'detalhes': resultados['analises'],
            'resumo_executivo': {}
        }
        
        # Gerar resumo executivo
        for campo, analise in resultados['analises'].items():
            faixa = analise['faixa_80_porcento']
            mais_freq = analise['mais_frequentes'][0]
            
            # Calcular perfis de risco
            perfis = self.calcular_perfis_risco(analise)
            
            relatorio['previsoes'][campo] = {
                'atual': analise['valor_atual'],
                'faixa_min': faixa['minimo'],
                'faixa_max': faixa['maximo'],
                'mais_provavel': mais_freq[0],
                'probabilidade': round((mais_freq[1]/analise['total_ocorrencias']*100), 1),
                'confianca': 80,
                'total_ocorrencias': analise['total_ocorrencias'],
                'perfis_risco': perfis
            }
            
            # Nome amigável do campo
            nome_campo = {
                'menor_que_ultimo': 'Menor que Último',
                'maior_que_ultimo': 'Maior que Último', 
                'igual_ao_ultimo': 'Igual ao Último'
            }.get(campo, campo)
            
            relatorio['resumo_executivo'][nome_campo] = {
                'atual': analise['valor_atual'],
                'previsao': f"{faixa['minimo']} a {faixa['maximo']}",
                'mais_provavel': f"{mais_freq[0]} ({round((mais_freq[1]/analise['total_ocorrencias']*100), 1)}%)",
                'historico': f"{analise['total_ocorrencias']} ocorrências"
            }
        
        return relatorio
        
    def obter_dados_ultimo_concurso(self):
        """
        Obtém os dados REAIS do último concurso para inversão de tendências
        """
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            
            # Buscar dados do último concurso da tabela de resultados históricos
            query = """
            SELECT TOP 1
                concurso,
                menor_que_ultimo,
                maior_que_ultimo,
                igual_ao_ultimo,
                repetidosMesmaPosicao,
                SomaTotal
            FROM RESULTADOS_INT
            ORDER BY concurso DESC
            """
            
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                dados_reais = {
                    'concurso': resultado[0],
                    'menor_que_ultimo': resultado[1],
                    'maior_que_ultimo': resultado[2], 
                    'igual_ao_ultimo': resultado[3],
                    'repetidos_mesma_posicao': resultado[4],
                    'soma_total': resultado[5]
                }
                
                print(f"✅ Dados REAIS obtidos do concurso {dados_reais['concurso']}: {dados_reais}")
                return dados_reais
            else:
                print("❌ Nenhum dado encontrado no banco")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter dados do último concurso: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

def executar_analise_sequencial():
    """Função wrapper para uso na API"""
    analise = AnaliseSequencial()
    return analise.gerar_relatorio_web()