"""
Modelo Preditivo Avançado para Campos de Comparação
Combina correlações numéricas com padrões de transição
para prever próximos estados com alta acertabilidade
"""

import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import db_config
    print("✅ Módulo database_config importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar database_config: {e}")

class ModeloPreditivoAvancado:
    def __init__(self):
        self.dados = None
        self.regras_transicao = {}
        self.correlacoes = {}
        self.modelo_hibrido = {}
        
    def carregar_dados(self):
        """Carrega dados da análise anterior"""
        print("\n🔍 CARREGANDO DADOS PARA MODELO AVANÇADO")
        print("-" * 60)
        
        query = """
        SELECT 
            concurso,
            menor_que_ultimo,
            maior_que_ultimo,
            igual_ao_ultimo,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT 
        WHERE menor_que_ultimo IS NOT NULL 
        ORDER BY concurso
        """
        
        try:
            resultados = db_config.execute_query(query)
            if resultados:
                colunas = ['concurso', 'menor_que_ultimo', 'maior_que_ultimo', 
                          'igual_ao_ultimo', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                          'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
                
                # Converter para estrutura de dados simples (lista de dicionários)
                self.dados = []
                for row in resultados:
                    row_dict = {}
                    for i, col in enumerate(colunas):
                        row_dict[col] = row[i]
                    self.dados.append(row_dict)
                
                # Calcular estatísticas dos números
                colunas_numeros = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10', 
                                  'N11', 'N12', 'N13', 'N14', 'N15']
                
                for row in self.dados:
                    numeros = [row[col] for col in colunas_numeros]
                    row['soma_numeros'] = sum(numeros)
                    row['media_numeros'] = sum(numeros) / len(numeros)
                    row['amplitude'] = max(numeros) - min(numeros)
                
                print(f"✅ {len(self.dados)} concursos carregados")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def calcular_correlacoes_avancadas(self):
        """Calcula correlações detalhadas para predição"""
        print("\n🔢 ANÁLISE AVANÇADA DE CORRELAÇÕES")
        print("-" * 60)
        
        # Extrair listas para cálculo de correlação
        menor_que_ultimo = [row['menor_que_ultimo'] for row in self.dados]
        maior_que_ultimo = [row['maior_que_ultimo'] for row in self.dados]
        igual_ao_ultimo = [row['igual_ao_ultimo'] for row in self.dados]
        soma_numeros = [row['soma_numeros'] for row in self.dados]
        amplitude = [row['amplitude'] for row in self.dados]
        
        # Calcular correlações manualmente
        corr_menor_soma = self.calcular_correlacao(menor_que_ultimo, soma_numeros)
        corr_maior_soma = self.calcular_correlacao(maior_que_ultimo, soma_numeros)
        corr_igual_amplitude = self.calcular_correlacao(igual_ao_ultimo, amplitude)
        
        print(f"🎯 CORRELAÇÕES CONFIRMADAS:")
        print(f"   menor_que_ultimo vs soma: {corr_menor_soma:.3f}")
        print(f"   maior_que_ultimo vs soma: {corr_maior_soma:.3f}")
        print(f"   igual_ao_ultimo vs amplitude: {corr_igual_amplitude:.3f}")
        
        # Criar modelo de predição baseado em correlações
        self.correlacoes = {
            'menor_soma': corr_menor_soma,
            'maior_soma': corr_maior_soma,
            'igual_amplitude': corr_igual_amplitude
        }
        
        # Análise de faixas
        print(f"\n📊 ANÁLISE POR FAIXAS:")
        
        # Faixas de soma
        dados_baixa = [row for row in self.dados if row['soma_numeros'] <= 240]
        dados_alta = [row for row in self.dados if row['soma_numeros'] >= 300]
        
        print(f"📈 SOMA BAIXA (≤240): {len(dados_baixa)} casos")
        if dados_baixa:
            menor_medio = sum(row['menor_que_ultimo'] for row in dados_baixa) / len(dados_baixa)
            maior_medio = sum(row['maior_que_ultimo'] for row in dados_baixa) / len(dados_baixa)
            igual_medio = sum(row['igual_ao_ultimo'] for row in dados_baixa) / len(dados_baixa)
            print(f"   menor_que_ultimo médio: {menor_medio:.1f}")
            print(f"   maior_que_ultimo médio: {maior_medio:.1f}")
            print(f"   igual_ao_ultimo médio: {igual_medio:.1f}")
        
        print(f"📈 SOMA ALTA (≥300): {len(dados_alta)} casos")
        if dados_alta:
            menor_medio = sum(row['menor_que_ultimo'] for row in dados_alta) / len(dados_alta)
            maior_medio = sum(row['maior_que_ultimo'] for row in dados_alta) / len(dados_alta)
            igual_medio = sum(row['igual_ao_ultimo'] for row in dados_alta) / len(dados_alta)
            print(f"   menor_que_ultimo médio: {menor_medio:.1f}")
            print(f"   maior_que_ultimo médio: {maior_medio:.1f}")
            print(f"   igual_ao_ultimo médio: {igual_medio:.1f}")
        
        return True
    
    def calcular_correlacao(self, x, y):
        """Calcula correlação de Pearson manualmente"""
        if len(x) != len(y) or len(x) == 0:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def identificar_padroes_de_inversao(self):
        """Identifica padrões de inversão nos campos"""
        print("\n🔄 IDENTIFICANDO PADRÕES DE INVERSÃO")
        print("-" * 60)
        
        inversoes = []
        
        for i in range(len(self.dados) - 1):
            atual = (self.dados[i]['menor_que_ultimo'], 
                    self.dados[i]['maior_que_ultimo'], 
                    self.dados[i]['igual_ao_ultimo'])
            
            proximo = (self.dados[i+1]['menor_que_ultimo'], 
                      self.dados[i+1]['maior_que_ultimo'], 
                      self.dados[i+1]['igual_ao_ultimo'])
            
            # Detectar inversões (menor vira maior, maior vira menor)
            if atual[0] > 10 and proximo[1] > 10:  # menor alto -> maior alto
                inversoes.append(('menor_para_maior', atual, proximo))
            elif atual[1] > 10 and proximo[0] > 10:  # maior alto -> menor alto  
                inversoes.append(('maior_para_menor', atual, proximo))
        
        # Contar tipos de inversão
        contador_inversoes = Counter([inv[0] for inv in inversoes])
        
        print(f"🔀 INVERSÕES ENCONTRADAS:")
        for tipo, freq in contador_inversoes.items():
            print(f"   {tipo}: {freq} vezes ({freq/len(self.dados)*100:.1f}%)")
        
        # Padrões mais comuns de inversão
        if inversoes:
            print(f"\n🎯 PADRÕES DE INVERSÃO MAIS COMUNS:")
            padroes_inversao = Counter([(inv[1], inv[2]) for inv in inversoes])
            
            for (estado_antes, estado_depois), freq in padroes_inversao.most_common(5):
                print(f"   {estado_antes} → {estado_depois}: {freq} vezes")
        
        return inversoes
    
    def criar_modelo_hibrido(self):
        """Cria modelo híbrido combinando correlações e transições"""
        print("\n🧠 CRIANDO MODELO HÍBRIDO AVANÇADO")
        print("-" * 60)
        
        # Primeiro, criar regras baseadas em transições (da análise anterior)
        transicoes = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(self.dados) - 1):
            estado_atual = (self.dados[i]['menor_que_ultimo'], 
                           self.dados[i]['maior_que_ultimo'], 
                           self.dados[i]['igual_ao_ultimo'])
            
            estado_proximo = (self.dados[i+1]['menor_que_ultimo'], 
                             self.dados[i+1]['maior_que_ultimo'], 
                             self.dados[i+1]['igual_ao_ultimo'])
            
            transicoes[estado_atual][estado_proximo] += 1
        
        # Criar regras híbridas
        regras_hibridas = {}
        
        for estado_origem, destinos in transicoes.items():
            total = sum(destinos.values())
            if total >= 8:  # Estados com pelo menos 8 ocorrências
                
                # Calcular probabilidade da transição mais comum
                destino_mais_provavel = max(destinos.items(), key=lambda x: x[1])
                probabilidade_transicao = (destino_mais_provavel[1] / total) * 100
                
                # Calcular score baseado em correlações
                soma_atual = self.estimar_soma_por_estado(estado_origem)
                soma_prevista = self.estimar_soma_por_estado(destino_mais_provavel[0])
                
                # Score de correlação (quão bem a mudança se alinha com as correlações)
                score_correlacao = self.calcular_score_correlacao(estado_origem, destino_mais_provavel[0])
                
                # Score híbrido combinado
                score_hibrido = (probabilidade_transicao * 0.7) + (score_correlacao * 0.3)
                
                if score_hibrido >= 15:  # Threshold para regras híbridas
                    regras_hibridas[estado_origem] = {
                        'destino_previsto': destino_mais_provavel[0],
                        'prob_transicao': probabilidade_transicao,
                        'score_correlacao': score_correlacao,
                        'score_hibrido': score_hibrido,
                        'ocorrencias': destino_mais_provavel[1],
                        'total_amostras': total,
                        'soma_atual_est': soma_atual,
                        'soma_prevista_est': soma_prevista
                    }
        
        self.modelo_hibrido = regras_hibridas
        
        print(f"✅ {len(regras_hibridas)} regras híbridas criadas")
        
        # Mostrar melhores regras
        regras_ordenadas = sorted(regras_hibridas.items(), 
                                 key=lambda x: x[1]['score_hibrido'], reverse=True)
        
        print(f"\n🏆 TOP 10 REGRAS HÍBRIDAS:")
        for i, (estado, regra) in enumerate(regras_ordenadas[:10]):
            print(f"{i+1:2d}. {estado} → {regra['destino_previsto']}")
            print(f"    Score Híbrido: {regra['score_hibrido']:.1f}%")
            print(f"    Transição: {regra['prob_transicao']:.1f}% | Correlação: {regra['score_correlacao']:.1f}%")
            print(f"    Base: {regra['ocorrencias']}/{regra['total_amostras']} casos")
            print()
        
        return regras_hibridas
    
    def estimar_soma_por_estado(self, estado):
        """Estima a soma média dos números para um estado específico"""
        menor, maior, igual = estado
        
        # Usar correlações para estimar
        # Correlação menor_que_ultimo vs soma: -0.652
        # Correlação maior_que_ultimo vs soma: +0.648
        
        # Valores médios da base
        soma_total = sum(row['soma_numeros'] for row in self.dados)
        soma_media = soma_total / len(self.dados)  # ~270
        
        # Ajustar baseado no estado
        ajuste_menor = (menor - 5.9) * -8  # Factor baseado na correlação
        ajuste_maior = (maior - 5.94) * 8   # Factor baseado na correlação
        
        soma_estimada = soma_media + ajuste_menor + ajuste_maior
        
        return max(150, min(400, soma_estimada))  # Limitar a faixa realista
    
    def calcular_score_correlacao(self, estado_atual, estado_proximo):
        """Calcula score baseado em quão bem a transição se alinha com correlações"""
        soma_atual = self.estimar_soma_por_estado(estado_atual)
        soma_proxima = self.estimar_soma_por_estado(estado_proximo)
        
        # Mudança esperada na soma
        mudanca_soma = soma_proxima - soma_atual
        
        # Mudanças nos campos
        mudanca_menor = estado_proximo[0] - estado_atual[0]
        mudanca_maior = estado_proximo[1] - estado_atual[1]
        
        # Score baseado em alinhamento com correlações
        score = 50  # Base score
        
        # Se menor_que_ultimo aumenta, soma deveria diminuir (correlação negativa)
        if mudanca_menor > 0 and mudanca_soma < 0:
            score += 20
        elif mudanca_menor < 0 and mudanca_soma > 0:
            score += 20
        elif mudanca_menor == 0:
            score += 10
        
        # Se maior_que_ultimo aumenta, soma deveria aumentar (correlação positiva)
        if mudanca_maior > 0 and mudanca_soma > 0:
            score += 20
        elif mudanca_maior < 0 and mudanca_soma < 0:
            score += 20
        elif mudanca_maior == 0:
            score += 10
        
        return min(100, max(0, score))
    
    def testar_modelo_hibrido(self):
        """Testa a acurácia do modelo híbrido"""
        print("\n🧪 TESTANDO MODELO HÍBRIDO")
        print("-" * 60)
        
        if not self.modelo_hibrido:
            print("❌ Modelo híbrido não disponível")
            return 0
        
        # Usar últimos 30% dos dados para teste
        total_dados = len(self.dados)
        inicio_teste = int(total_dados * 0.7)
        
        dados_teste = self.dados[inicio_teste:]
        
        predicoes_corretas = 0
        total_predicoes = 0
        predicoes_detalhadas = []
        
        for i in range(len(dados_teste) - 1):
            estado_atual = (dados_teste[i]['menor_que_ultimo'], 
                           dados_teste[i]['maior_que_ultimo'], 
                           dados_teste[i]['igual_ao_ultimo'])
            
            estado_real_proximo = (dados_teste[i+1]['menor_que_ultimo'], 
                                  dados_teste[i+1]['maior_que_ultimo'], 
                                  dados_teste[i+1]['igual_ao_ultimo'])
            
            if estado_atual in self.modelo_hibrido:
                regra = self.modelo_hibrido[estado_atual]
                predicao = regra['destino_previsto']
                total_predicoes += 1
                
                acertou = predicao == estado_real_proximo
                if acertou:
                    predicoes_corretas += 1
                
                predicoes_detalhadas.append({
                    'estado_atual': estado_atual,
                    'predicao': predicao,
                    'real': estado_real_proximo,
                    'acertou': acertou,
                    'score_hibrido': regra['score_hibrido']
                })
        
        if total_predicoes > 0:
            acuracia = (predicoes_corretas / total_predicoes) * 100
            
            print(f"📊 RESULTADOS DO TESTE HÍBRIDO:")
            print(f"   Predições testadas: {total_predicoes}")
            print(f"   Predições corretas: {predicoes_corretas}")
            print(f"   Acurácia: {acuracia:.1f}%")
            
            # Análise por faixa de score
            predicoes_alto_score = [p for p in predicoes_detalhadas if p['score_hibrido'] >= 25]
            if predicoes_alto_score:
                acertos_alto_score = sum(1 for p in predicoes_alto_score if p['acertou'])
                acuracia_alto_score = (acertos_alto_score / len(predicoes_alto_score)) * 100
                print(f"   Acurácia (score ≥25): {acuracia_alto_score:.1f}% ({acertos_alto_score}/{len(predicoes_alto_score)})")
            
            if acuracia >= 35:
                print("✅ Modelo híbrido apresenta boa capacidade preditiva!")
            elif acuracia >= 25:
                print("🟡 Modelo híbrido apresenta capacidade preditiva moderada")
            else:
                print("❌ Modelo híbrido precisa de mais otimização")
            
            return acuracia
        else:
            print("❌ Nenhuma predição pôde ser testada")
            return 0
    
    def prever_proximo_estado_hibrido(self, ultimo_estado=None):
        """Faz predição usando modelo híbrido"""
        if ultimo_estado is None:
            ultimo_estado = (self.dados[-1]['menor_que_ultimo'], 
                           self.dados[-1]['maior_que_ultimo'], 
                           self.dados[-1]['igual_ao_ultimo'])
        
        print(f"\n🔮 PREDIÇÃO HÍBRIDA PARA PRÓXIMO CONCURSO")
        print("-" * 60)
        print(f"Estado atual: {ultimo_estado}")
        
        if ultimo_estado in self.modelo_hibrido:
            regra = self.modelo_hibrido[ultimo_estado]
            print(f"\n✅ PREDIÇÃO HÍBRIDA ENCONTRADA:")
            print(f"Estado previsto: {regra['destino_previsto']}")
            print(f"Score híbrido: {regra['score_hibrido']:.1f}%")
            print(f"Probabilidade transição: {regra['prob_transicao']:.1f}%")
            print(f"Score correlação: {regra['score_correlacao']:.1f}%")
            print(f"Base histórica: {regra['ocorrencias']}/{regra['total_amostras']} casos")
            print(f"Soma atual estimada: {regra['soma_atual_est']:.0f}")
            print(f"Soma prevista: {regra['soma_prevista_est']:.0f}")
            
            return regra['destino_previsto'], regra['score_hibrido']
        else:
            print("❌ Nenhuma regra híbrida encontrada para este estado")
            
            # Tentar predição baseada apenas em correlações
            print(f"\n🔍 TENTANDO PREDIÇÃO POR CORRELAÇÕES:")
            soma_estimada = self.estimar_soma_por_estado(ultimo_estado)
            print(f"Soma atual estimada: {soma_estimada:.0f}")
            
            # Sugerir tendência baseada na soma
            if soma_estimada < 240:
                print("📈 Tendência: Números devem subir (maior_que_ultimo deve aumentar)")
                estado_sugerido = (max(0, ultimo_estado[0] - 2), 
                                 min(15, ultimo_estado[1] + 3), 
                                 ultimo_estado[2])
            elif soma_estimada > 300:
                print("📉 Tendência: Números devem descer (menor_que_ultimo deve aumentar)")
                estado_sugerido = (min(15, ultimo_estado[0] + 3), 
                                 max(0, ultimo_estado[1] - 2), 
                                 ultimo_estado[2])
            else:
                print("➡️ Tendência: Estabilidade relativa esperada")
                estado_sugerido = ultimo_estado
            
            print(f"Estado sugerido por correlação: {estado_sugerido}")
            return estado_sugerido, 15.0  # Score baixo para predições por correlação
    
    def executar_analise_completa(self):
        """Executa análise completa do modelo avançado"""
        print("🚀 INICIANDO MODELO PREDITIVO AVANÇADO")
        print("=" * 80)
        
        if not self.carregar_dados():
            return False
        
        self.calcular_correlacoes_avancadas()
        inversoes = self.identificar_padroes_de_inversao()
        self.criar_modelo_hibrido()
        acuracia = self.testar_modelo_hibrido()
        self.prever_proximo_estado_hibrido()
        
        print(f"\n🎉 MODELO AVANÇADO FINALIZADO!")
        print(f"📈 Acurácia do modelo híbrido: {acuracia:.1f}%")
        
        return True

def main():
    """Função principal"""
    modelo = ModeloPreditivoAvancado()
    modelo.executar_analise_completa()

if __name__ == "__main__":
    main()