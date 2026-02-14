#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔮 SISTEMA DE PREVISÃO ADAPTATIVA TEMPORAL
Análise temporal com machine learning simples
Autor: AR CALHAU
Data: 13 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque, defaultdict
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

import json
from typing import Dict, List, Tuple, Optional

class SistemaPrevisaoAdaptativa:
    """Sistema de previsão que aprende e se adapta"""
    
    def __init__(self):
        self.historico_previsoes = {}
        self.taxa_acerto_por_filtro = defaultdict(list)
        self.pesos_adaptativos = {}
        self.memoria_padroes = deque(maxlen=100)  # Últimos 100 padrões
        
        # Configurações adaptativas
        self.janela_aprendizado = 20
        self.threshold_confianca = 0.75
        self.fator_decaimento = 0.95  # Para dar mais peso a dados recentes
        
        # Inicializa pesos neutros
        self.filtros_monitorados = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'SEQ', 'DistanciaExtremos', 'ParesSequencia',
            'QtdeMultiplos3', 'ParesSaltados', 'Faixa_Baixa', 'Faixa_Media', 
            'Faixa_Alta', 'QtdeRepetidos', 'RepetidosMesmaPosicao'
        ]
        
        for filtro in self.filtros_monitorados:
            self.pesos_adaptativos[filtro] = 1.0

    def carregar_historico_aprendizado(self) -> bool:
        """Carrega histórico de previsões para aprendizado"""
        arquivo_historico = "historico_previsoes_adaptativas.json"
        
        try:
            if os.path.exists(arquivo_historico):
                with open(arquivo_historico, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.historico_previsoes = dados.get('previsoes', {})
                    self.taxa_acerto_por_filtro = defaultdict(list, dados.get('taxas_acerto', {}))
                    self.pesos_adaptativos = dados.get('pesos_adaptativos', self.pesos_adaptativos)
                
                print(f"✅ Histórico carregado: {len(self.historico_previsoes)} previsões")
                return True
            else:
                print("📝 Iniciando novo histórico de aprendizado")
                return True
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar histórico: {e}")
            return True  # Continua mesmo sem histórico

    def salvar_historico_aprendizado(self) -> bool:
        """Salva histórico para preservar aprendizado"""
        arquivo_historico = "historico_previsoes_adaptativas.json"
        
        try:
            dados = {
                'previsoes': self.historico_previsoes,
                'taxas_acerto': dict(self.taxa_acerto_por_filtro),
                'pesos_adaptativos': self.pesos_adaptativos,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            with open(arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar histórico: {e}")
            return False

    def analisar_padroes_temporais(self, concursos_base: int = 50) -> Dict:
        """Analisa padrões temporais sofisticados"""
        print(f"\n⏰ ANÁLISE TEMPORAL ADAPTATIVA")
        print(f"📊 Base de análise: {concursos_base} concursos")
        print("=" * 40)
        
        try:
            with db_config.get_connection() as conn:
                query = f"""
                SELECT TOP {concursos_base}
                    Concurso, Data_Sorteio,
                    {', '.join(self.filtros_monitorados)}
                FROM Resultados_INT 
                WHERE Concurso IS NOT NULL
                ORDER BY Concurso DESC
                """
                
                dados = pd.read_sql(query, conn)
                
                if len(dados) == 0:
                    return {}
                
                padroes_temporais = {}
                
                # Análise por tipo de padrão
                for filtro in self.filtros_monitorados:
                    if filtro not in dados.columns:
                        continue
                    
                    valores = dados[filtro].tolist()
                    
                    # 1. Análise de ciclos
                    ciclos = self._detectar_ciclos(valores)
                    
                    # 2. Análise de tendência
                    tendencia = self._calcular_tendencia_robusta(valores)
                    
                    # 3. Análise de volatilidade
                    volatilidade = self._calcular_volatilidade_adaptativa(valores)
                    
                    # 4. Detecção de pontos de inflexão
                    inflexoes = self._detectar_inflexoes(valores)
                    
                    # 5. Análise de sazonalidade
                    sazonalidade = self._analisar_sazonalidade(valores)
                    
                    padroes_temporais[filtro] = {
                        'ciclos_detectados': ciclos,
                        'tendencia': tendencia,
                        'volatilidade': volatilidade,
                        'pontos_inflexao': inflexoes,
                        'sazonalidade': sazonalidade,
                        'peso_adaptativo': self.pesos_adaptativos.get(filtro, 1.0)
                    }
                
                return padroes_temporais
                
        except Exception as e:
            print(f"❌ Erro na análise temporal: {e}")
            return {}

    def _detectar_ciclos(self, valores: List[float]) -> Dict:
        """Detecta ciclos nos dados"""
        if len(valores) < 8:
            return {'ciclo_detectado': False}
        
        # Busca por ciclos de diferentes tamanhos
        melhor_ciclo = {'tamanho': 0, 'confianca': 0, 'detectado': False}
        
        for tamanho_ciclo in range(3, int(int(min(len(valores)) // 3, 15):
            correlacoes = []
            
            for inicio in range(int(int(int(len(valores)) - 2 * tamanho_ciclo):
                ciclo1 = valores[inicio:inicio + tamanho_ciclo]
                ciclo2 = valores[inicio + tamanho_ciclo:inicio + 2 * tamanho_ciclo]
                
                # Calcula correlação entre ciclos
                if len(ciclo1) == len(ciclo2):
                    correlacao = np.corrcoef(ciclo1)), int(int(ciclo2))[0), int(1]
                    if not np.isnan(correlacao):
                        correlacoes.append(abs(correlacao))
            
            if correlacoes:
                confianca_ciclo = np.mean(correlacoes)
                if confianca_ciclo > melhor_ciclo['confianca']:
                    melhor_ciclo = {
                        'tamanho': tamanho_ciclo,
                        'confianca': confianca_ciclo,
                        'detectado': confianca_ciclo > 0.6
                    }
        
        return melhor_ciclo

    def _calcular_tendencia_robusta(self, valores: List[float]) -> Dict:
        """Calcula tendência usando múltiplos métodos"""
        if len(valores) < 3:
            return {'direcao': 'ESTAVEL', 'intensidade': 0}
        
        # Método 1: Regressão linear
        x = np.arange(int(int(int(len(valores)))
        coef_linear = np.polyfit(x)), int(int(valores, 1))[0]
        
        # Método 2: Diferenças médias ponderadas
        diferencas = []
        pesos = []
        for i in range(1, int(int(len(valores)):
            diff = valores[i] - valores[i-1]
            peso = i / len(valores)  # Mais peso para dados recentes
            diferencas.append(diff)
            pesos.append(peso)
        
        diff_ponderada = np.average(diferencas, weights=pesos) if diferencas else 0
        
        # Método 3: Análise de extremos recentes
        if len(valores) >= 5:
            recentes = valores[:5]
            anteriores = valores[5:]
            media_recente = np.mean(recentes)
            media_anterior = np.mean(anteriores) if anteriores else media_recente
            tendencia_extremos = media_recente - media_anterior
        else:
            tendencia_extremos = 0
        
        # Combina métodos
        tendencia_final = (coef_linear * 0.4 + diff_ponderada * 0.4 + tendencia_extremos * 0.2)
        
        # Classifica direção
        if tendencia_final > 0.1:
            direcao = 'CRESCENTE'
        elif tendencia_final < -0.1:
            direcao = 'DECRESCENTE'
        else:
            direcao = 'ESTAVEL'
        
        return {
            'direcao': direcao,
            'intensidade': abs(tendencia_final),
            'confianca': min(1.0, 1 - abs(coef_linear - diff_ponderada) / (abs(coef_linear) + abs(diff_ponderada) + 0.1))
        }

    def _calcular_volatilidade_adaptativa(self, valores: List[float]) -> Dict:
        """Calcula volatilidade com adaptação temporal"""
        if len(valores) < 3:
            return {'nivel': 'BAIXA', 'valor': 0}
        
        # Volatilidade clássica (desvio padrão)
        volatilidade_classica = np.std(valores)
        
        # Volatilidade adaptativa (mais peso nos dados recentes)
        pesos = np.exp(np.arange(int(int(int(len(valores))) * 0.1)  # Crescimento exponencial
        pesos = pesos / np.sum(pesos)  # Normaliza
        
        media_ponderada = np.average(valores)), int(int(weights=pesos))
        var_ponderada = np.average((np.array(valores) - media_ponderada) ** 2, weights=pesos)
        volatilidade_adaptativa = np.sqrt(var_ponderada)
        
        # Classifica nível
        if volatilidade_adaptativa < 1.0:
            nivel = 'BAIXA'
        elif volatilidade_adaptativa < 2.5:
            nivel = 'MEDIA'
        else:
            nivel = 'ALTA'
        
        return {
            'nivel': nivel,
            'valor': volatilidade_adaptativa,
            'classica': volatilidade_classica,
            'adaptativa': volatilidade_adaptativa
        }

    def _detectar_inflexoes(self, valores: List[float]) -> List[int]:
        """Detecta pontos de inflexão (mudanças de direção)"""
        if len(valores) < 5:
            return []
        
        inflexoes = []
        
        for i in range(2, int(int(len(valores)) - 2):
            # Analisa janela de 5 pontos centrada em i
            janela = valores[i-2:i+3]
            
            # Verifica se i é um pico ou vale
            if (janela[2] > janela[1] and janela[2] > janela[3] and 
                janela[2] > janela[0] and janela[2] > janela[4]):
                inflexoes.append(i)  # Pico
            elif (janela[2] < janela[1] and janela[2] < janela[3] and 
                  janela[2] < janela[0] and janela[2] < janela[4]):
                inflexoes.append(i)  # Vale
        
        return inflexoes

    def _analisar_sazonalidade(self, int(valores: List[float])) -> Dict:
        """Analisa padrões sazonais"""
        if len(valores) < 12:
            return {'detectada': False}
        
        # Testa diferentes períodos sazonais
        periodos_teste = [3, 4, 5, 6, 7, 10, 12]
        melhor_periodo = {'periodo': 0, 'correlacao': 0, 'detectada': False}
        
        for periodo in periodos_teste:
            if len(valores) >= 2 * periodo:
                # Calcula autocorrelação com lag igual ao período
                correlacao = self._calcular_autocorrelacao(valores, periodo)
                
                if correlacao > melhor_periodo['correlacao']:
                    melhor_periodo = {
                        'periodo': periodo,
                        'correlacao': correlacao,
                        'detectada': correlacao > 0.5
                    }
        
        return melhor_periodo

    def _calcular_autocorrelacao(self, valores: List[float], lag: int) -> float:
        """Calcula autocorrelação com lag específico"""
        if len(valores) <= lag:
            return 0
        
        serie1 = valores[:-lag]
        serie2 = valores[lag:]
        
        if len(serie1) != len(serie2) or len(serie1) == 0:
            return 0
        
        correlacao = np.corrcoef(serie1, serie2)[0, 1]
        return 0 if np.isnan(correlacao) else abs(correlacao)

    def prever_proximo_concurso_adaptativo(self) -> Dict:
        """Faz previsão adaptativa para próximo concurso"""
        print("\n🔮 PREVISÃO ADAPTATIVA - PRÓXIMO CONCURSO")
        print("=" * 45)
        
        # Analisa padrões temporais
        padroes = self.analisar_padroes_temporais()
        
        previsoes_adaptativas = {}
        confiancas_globais = []
        
        for filtro, analise in padroes.items():
            # Peso adaptativo baseado em performance histórica
            peso_adaptativo = self.pesos_adaptativos.get(filtro, 1.0)
            
            # Previsão baseada em múltiplos fatores
            previsao_base = self._calcular_previsao_base(filtro, analise)
            
            # Ajustes baseados em padrões detectados
            ajuste_ciclo = self._ajustar_por_ciclo(analise['ciclos_detectados'])
            ajuste_tendencia = self._ajustar_por_tendencia(analise['tendencia'])
            ajuste_sazonalidade = self._ajustar_por_sazonalidade(analise['sazonalidade'])
            
            # Previsão final ponderada
            previsao_final = (
                previsao_base * 0.5 +
                (previsao_base + ajuste_ciclo) * 0.2 +
                (previsao_base + ajuste_tendencia) * 0.2 +
                (previsao_base + ajuste_sazonalidade) * 0.1
            ) * peso_adaptativo
            
            previsao_final = max(0, round(previsao_final))
            
            # Calcula confiança combinada
            confianca_ciclo = analise['ciclos_detectados'].get('confianca', 0.5)
            confianca_tendencia = analise['tendencia'].get('confianca', 0.5)
            confianca_sazonalidade = analise['sazonalidade'].get('correlacao', 0.5)
            
            confianca_final = (confianca_ciclo + confianca_tendencia + confianca_sazonalidade) / 3
            confianca_final *= peso_adaptativo  # Ajusta pela performance histórica
            
            confiancas_globais.append(confianca_final)
            
            previsoes_adaptativas[filtro] = {
                'valor_previsto': previsao_final,
                'confianca': round(min(1.0, max(0.1, confianca_final)), 3),
                'peso_adaptativo': peso_adaptativo,
                'componentes': {
                    'base': previsao_base,
                    'ajuste_ciclo': ajuste_ciclo,
                    'ajuste_tendencia': ajuste_tendencia,
                    'ajuste_sazonalidade': ajuste_sazonalidade
                }
            }
        
        # Estatísticas globais
        confianca_global = np.mean(confiancas_globais) if confiancas_globais else 0.5
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'previsoes': previsoes_adaptativas,
            'confianca_global': round(confianca_global, 3),
            'metodo': 'ADAPTATIVO_TEMPORAL',
            'padroes_base': len(padroes)
        }
        
        # Salva para aprendizado futuro
        self._salvar_previsao_para_aprendizado(resultado)
        
        return resultado

    def _calcular_previsao_base(self, filtro: str, analise: Dict) -> float:
        """Calcula previsão base usando dados históricos"""
        try:
            with db_config.get_connection() as conn:
                query = f"""
                SELECT TOP 10 {filtro}
                FROM Resultados_INT 
                WHERE {filtro} IS NOT NULL
                ORDER BY Concurso DESC
                """
                
                cursor = conn.cursor()
                cursor.execute(query)
                valores = [row[0] for row in cursor.fetchall()]
                
                if not valores:
                    return 5.0  # Valor neutro padrão
                
                # Média ponderada com decaimento exponencial
                pesos = [self.fator_decaimento ** i for i in range(int(int(int(len(valores)))]
                pesos_normalizados = [p / sum(pesos) for p in pesos]
                
                previsao = sum(v * p for v)), int(int(p in zip(valores), int(pesos_normalizados))))
                return previsao
                
        except Exception:
            return 5.0

    def _ajustar_por_ciclo(self, ciclo_info: Dict) -> float:
        """Ajusta previsão baseado em ciclos detectados"""
        if not ciclo_info.get('detectado', False):
            return 0
        
        confianca = ciclo_info.get('confianca', 0)
        tamanho = ciclo_info.get('tamanho', 5)
        
        # Ajuste proporcional à confiança do ciclo
        ajuste = (confianca - 0.5) * 2  # Normaliza para -1 a 1
        return ajuste

    def _ajustar_por_tendencia(self, tendencia_info: Dict) -> float:
        """Ajusta previsão baseado em tendência"""
        direcao = tendencia_info.get('direcao', 'ESTAVEL')
        intensidade = tendencia_info.get('intensidade', 0)
        
        if direcao == 'CRESCENTE':
            return intensidade * 2
        elif direcao == 'DECRESCENTE':
            return -intensidade * 2
        else:
            return 0

    def _ajustar_por_sazonalidade(self, sazonalidade_info: Dict) -> float:
        """Ajusta previsão baseado em sazonalidade"""
        if not sazonalidade_info.get('detectada', False):
            return 0
        
        correlacao = sazonalidade_info.get('correlacao', 0.5)
        periodo = sazonalidade_info.get('periodo', 5)
        
        # Ajuste leve baseado na força da sazonalidade
        ajuste = (correlacao - 0.5) * 1.5
        return ajuste

    def _salvar_previsao_para_aprendizado(self, previsao: Dict):
        """Salva previsão para aprendizado futuro"""
        concurso_previsto = self._obter_proximo_numero_concurso()
        self.historico_previsoes[str(concurso_previsto)] = previsao

    def _obter_proximo_numero_concurso(self) -> int:
        """Obtém número do próximo concurso"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
                ultimo = cursor.fetchone()[0]
                return ultimo + 1 if ultimo else 1
        except:
            return 1

    def gerar_arquivo_previsao(self, previsoes: Dict) -> str:
        """Gera arquivo com previsões adaptativas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"previsao_adaptativa_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("🔮 PREVISÃO ADAPTATIVA TEMPORAL\n")
                f.write("=" * 40 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Confiança global: {previsoes['confianca_global']*100:.1f}%\n\n")
                
                f.write("📊 PREVISÕES POR FILTRO:\n")
                f.write("-" * 30 + "\n")
                
                for filtro, dados in previsoes['previsoes'].items():
                    valor = dados['valor_previsto']
                    confianca = dados['confianca'] * 100
                    peso = dados['peso_adaptativo']
                    
                    f.write(f"{filtro}:\n")
                    f.write(f"   Valor: {valor}\n")
                    f.write(f"   Confiança: {confianca:.1f}%\n")
                    f.write(f"   Peso adaptativo: {peso:.3f}\n\n")
                
                f.write("🧠 DETALHES TÉCNICOS:\n")
                f.write("-" * 25 + "\n")
                f.write(f"Método: {previsoes['metodo']}\n")
                f.write(f"Padrões analisados: {previsoes['padroes_base']}\n")
                f.write(f"Timestamp: {previsoes['timestamp']}\n")
            
            print(f"📄 Arquivo de previsão salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return ""


def main():
    """Função principal"""
    print("🔮 SISTEMA DE PREVISÃO ADAPTATIVA TEMPORAL")
    print("=" * 50)
    
    sistema = SistemaPrevisaoAdaptativa()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco")
        return
    
    try:
        # Carrega histórico de aprendizado
        sistema.carregar_historico_aprendizado()
        
        # Executa previsão adaptativa
        previsoes = sistema.prever_proximo_concurso_adaptativo()
        
        if previsoes:
            # Salva resultados
            arquivo = sistema.gerar_arquivo_previsao(previsoes)
            sistema.salvar_historico_aprendizado()
            
            print(f"\n✅ PREVISÃO ADAPTATIVA CONCLUÍDA!")
            print(f"📊 Confiança global: {previsoes['confianca_global']*100:.1f}%")
            print(f"📄 Arquivo gerado: {arquivo}")
        else:
            print("❌ Erro na geração de previsões")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
