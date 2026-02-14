#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 SISTEMA DE FEEDBACK LOOP INTELIGENTE
=======================================
Sistema que distribui aprendizado de validações reais para TODOS os geradores,
permitindo evolução contínua e melhoria automática dos algoritmos.

FUNCIONALIDADES:
• Analisa padrões de acerto/erro de cada gerador
• Identifica pontos fortes e fracos algorítmicos  
• Gera recomendações específicas para cada método
• Aplica otimizações automáticas nos parâmetros
• Evolução contínua baseada em resultados reais

Autor: AR CALHAU
Data: 21/09/2025
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import statistics

class AnalisadorPadroes:
    """Analisa padrões nos resultados de validação"""
    
    def __init__(self):
        self.historico_analises = []
    
    def analisar_performance_gerador(self, historico_gerador: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa performance histórica de um gerador com nova métrica de sucesso"""
        if not historico_gerador:
            return {'erro': 'Histórico vazio'}
        
        # Extrai métricas antigas para compatibilidade
        precisoes = [h['precisao_geral'] for h in historico_gerador]
        melhores_acertos = [h['melhor_acerto'] for h in historico_gerador]
        medias_acertos = [h['media_acertos'] for h in historico_gerador]
        
        # NOVA MÉTRICA PRINCIPAL: Extrai percentuais de combinações com 11+ acertos
        percentuais_11_plus = []
        combinacoes_11_plus = []
        classificacoes_sucesso = []
        
        for h in historico_gerador:
            # Se tem a nova métrica, usa ela
            if 'percentual_11_plus' in h:
                percentuais_11_plus.append(h['percentual_11_plus'])
                combinacoes_11_plus.append(h['combinacoes_11_plus'])
                classificacoes_sucesso.append(h['classificacao_sucesso'])
            else:
                # Fallback: estima baseado na precisão antiga
                # Aproximação: se precisão > 73%, provavelmente tem 50%+ com 11+ acertos
                estimativa = max(0, (h['precisao_geral'] - 60) * 1.5)  # Conversão aproximada
                percentuais_11_plus.append(min(100, estimativa))
                combinacoes_11_plus.append(0)  # Não temos o dado
                
                if estimativa >= 70:
                    classificacoes_sucesso.append("EXCELENTE")
                elif estimativa >= 50:
                    classificacoes_sucesso.append("SUCESSO")
                elif estimativa >= 30:
                    classificacoes_sucesso.append("BOM")
                else:
                    classificacoes_sucesso.append("INSUFICIENTE")
        
        # Análise de tendência com nova métrica
        tendencia_11_plus = self._calcular_tendencia(percentuais_11_plus)
        tendencia_precisao = self._calcular_tendencia(precisoes)
        tendencia_acertos = self._calcular_tendencia(melhores_acertos)
        
        # Análise de consistência
        desvio_11_plus = statistics.stdev(percentuais_11_plus) if len(percentuais_11_plus) > 1 else 0
        desvio_precisao = statistics.stdev(precisoes) if len(precisoes) > 1 else 0
        
        # Nova definição de consistência baseada na métrica 11+
        consistencia = 'Alta' if desvio_11_plus < 10 else 'Média' if desvio_11_plus < 20 else 'Baixa'
        
        # Identifica padrões
        padroes = self._identificar_padroes_comportamento(historico_gerador)
        
        # Conta sucessos e excelências
        sucessos = classificacoes_sucesso.count("SUCESSO") + classificacoes_sucesso.count("EXCELENTE")
        excelencias = classificacoes_sucesso.count("EXCELENTE")
        taxa_sucesso = (sucessos / len(classificacoes_sucesso)) * 100 if classificacoes_sucesso else 0
        
        return {
            'resumo': {
                'total_validacoes': len(historico_gerador),
                # NOVA MÉTRICA PRINCIPAL
                'percentual_11_plus_medio': statistics.mean(percentuais_11_plus) if percentuais_11_plus else 0,
                'percentual_11_plus_maximo': max(percentuais_11_plus) if percentuais_11_plus else 0,
                'taxa_sucesso': taxa_sucesso,
                'total_sucessos': sucessos,
                'total_excelencias': excelencias,
                # Métricas antigas para compatibilidade
                'precisao_media': statistics.mean(precisoes),
                'precisao_maxima': max(precisoes),
                'precisao_minima': min(precisoes),
                'melhor_acerto_medio': statistics.mean(melhores_acertos),
                'consistencia': consistencia,
                'desvio_padrao_11_plus': desvio_11_plus,
                'desvio_padrao': desvio_precisao
            },
            'tendencias': {
                'percentual_11_plus': tendencia_11_plus,  # NOVA MÉTRICA PRINCIPAL
                'precisao': tendencia_precisao,
                'acertos': tendencia_acertos,
                'direcao_evolucao': 'Melhorando' if tendencia_11_plus > 0 else 'Degradando' if tendencia_11_plus < 0 else 'Estável'
            },
            'padroes': padroes,
            'recomendacoes': self._gerar_recomendacoes_v2(percentuais_11_plus, classificacoes_sucesso, padroes)
        }
    
    def _calcular_tendencia(self, valores: List[float]) -> float:
        """Calcula tendência linear dos valores"""
        if len(valores) < 2:
            return 0
        
        # Cálculo manual de regressão linear simples
        n = len(valores)
        x = list(range(n))
        
        # Médias
        x_media = sum(x) / n
        y_media = sum(valores) / n
        
        # Cálculo do coeficiente angular (slope)
        numerador = sum((x[i] - x_media) * (valores[i] - y_media) for i in range(n))
        denominador = sum((x[i] - x_media) ** 2 for i in range(n))
        
        if denominador == 0:
            return 0
            
        coeficiente = numerador / denominador
        return float(coeficiente)
    
    def _identificar_padroes_comportamento(self, historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identifica padrões específicos no comportamento do gerador"""
        padroes = {
            'volatilidade': 'Normal',
            'picos_performance': [],
            'quedas_performance': [],
            'comportamento_recente': 'Estável'
        }
        
        if len(historico) < 3:
            return padroes
        
        precisoes = [h['precisao_geral'] for h in historico]
        
        # Detecta volatilidade
        variacao_media = statistics.mean([abs(precisoes[i] - precisoes[i-1]) for i in range(1, len(precisoes))])
        if variacao_media > 10:
            padroes['volatilidade'] = 'Alta'
        elif variacao_media < 3:
            padroes['volatilidade'] = 'Baixa'
        
        # Detecta picos e quedas (mudanças > 15%)
        for i in range(1, len(precisoes)):
            mudanca = precisoes[i] - precisoes[i-1]
            if mudanca > 15:
                padroes['picos_performance'].append({
                    'concurso': historico[i]['concurso'],
                    'melhoria': mudanca
                })
            elif mudanca < -15:
                padroes['quedas_performance'].append({
                    'concurso': historico[i]['concurso'],
                    'queda': abs(mudanca)
                })
        
        # Analisa comportamento recente (últimas 3 validações)
        if len(precisoes) >= 3:
            recentes = precisoes[-3:]
            if all(recentes[i] > recentes[i-1] for i in range(1, len(recentes))):
                padroes['comportamento_recente'] = 'Ascendente'
            elif all(recentes[i] < recentes[i-1] for i in range(1, len(recentes))):
                padroes['comportamento_recente'] = 'Descendente'
        
        return padroes
    
    def _gerar_recomendacoes(self, precisoes: List[float], acertos: List[int], padroes: Dict[str, Any]) -> List[str]:
        """Gera recomendações específicas baseadas na análise"""
        recomendacoes = []
        
        precisao_media = statistics.mean(precisoes)
        
        # Recomendações baseadas em performance
        if precisao_media < 50:
            recomendacoes.append("🔧 CRÍTICO: Revisar algoritmo base - performance muito baixa")
            recomendacoes.append("💡 Considerar usar dados históricos mais amplos")
        elif precisao_media < 65:
            recomendacoes.append("⚡ Otimizar parâmetros - há potencial de melhoria")
            recomendacoes.append("🎯 Ajustar pesos dos fatores de decisão")
        elif precisao_media > 80:
            recomendacoes.append("🏆 Excelente performance - manter configuração atual")
            recomendacoes.append("🔍 Investigar fatores de sucesso para replicar")
        
        # Recomendações baseadas em volatilidade
        if padroes['volatilidade'] == 'Alta':
            recomendacoes.append("📊 Reduzir volatilidade - adicionar mais estabilidade")
            recomendacoes.append("⚖️ Implementar médias móveis nos parâmetros")
        
        # Recomendações baseadas em tendência
        if padroes['comportamento_recente'] == 'Descendente':
            recomendacoes.append("📉 Performance em queda - investigar causas")
            recomendacoes.append("🔄 Considerar rollback para configuração anterior")
        elif padroes['comportamento_recente'] == 'Ascendente':
            recomendacoes.append("📈 Tendência positiva - manter direção atual")
        
        # Recomendações baseadas em picos
        if padroes['picos_performance']:
            recomendacoes.append("🎯 Analisar condições dos picos de performance")
            recomendacoes.append("🔬 Identificar fatores que causaram melhores resultados")
        
        return recomendacoes
    
    def _gerar_recomendacoes_v2(self, percentuais_11_plus: List[float], classificacoes: List[str], padroes: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na nova métrica de 11+ acertos"""
        recomendacoes = []
        
        if not percentuais_11_plus:
            recomendacoes.append("⚠️ Histórico insuficiente para recomendações")
            return recomendacoes
        
        percentual_medio = statistics.mean(percentuais_11_plus)
        
        # Recomendações baseadas na nova métrica de sucesso
        if percentual_medio < 30:
            recomendacoes.append("🚨 CRÍTICO: Menos de 30% das combinações atingem 11+ acertos")
            recomendacoes.append("🔧 Revisar completamente a estratégia de seleção de números")
            recomendacoes.append("💡 Considerar usar padrões históricos mais rigorosos")
        elif percentual_medio < 50:
            recomendacoes.append("⚠️ ATENÇÃO: Abaixo da meta de 50% com 11+ acertos")
            recomendacoes.append("🎯 Ajustar critérios para priorizar combinações de maior qualidade")
            recomendacoes.append("📊 Analisar padrões das combinações que atingem 11+ acertos")
        elif percentual_medio < 70:
            recomendacoes.append("✅ SUCESSO: Meta de 50% atingida - buscar excelência (70%)")
            recomendacoes.append("⚡ Otimizar parâmetros para aumentar % de combinações 11+")
            recomendacoes.append("🔍 Identificar fatores que geram combinações de alta qualidade")
        else:
            recomendacoes.append("🏆 EXCELENTE: Meta de excelência atingida (70%+)")
            recomendacoes.append("🔒 Manter configuração atual - performance excepcional")
            recomendacoes.append("📈 Focar em manter consistência nos resultados")
        
        # Recomendações baseadas em tendência
        if padroes['comportamento_recente'] == 'Descendente':
            recomendacoes.append("📉 Tendência de queda detectada - revisar mudanças recentes")
        elif padroes['comportamento_recente'] == 'Ascendente':
            recomendacoes.append("📈 Tendência de melhoria - manter direção atual")
        
        # Recomendações baseadas em volatilidade
        if padroes['volatilidade'] == 'Alta':
            recomendacoes.append("🔄 Alta volatilidade - estabilizar parâmetros")
        
        # Recomendações baseadas na classificação mais recente
        if classificacoes:
            ultima_classificacao = classificacoes[-1]
            if ultima_classificacao == "INSUFICIENTE":
                recomendacoes.append("🔴 Última performance INSUFICIENTE - ação urgente necessária")
            elif ultima_classificacao == "EXCELENTE":
                recomendacoes.append("🟢 Última performance EXCELENTE - replicar estratégia")
        
        return recomendacoes

class GeradorOtimizacoes:
    """Gera otimizações específicas para cada tipo de gerador"""
    
    def __init__(self):
        self.otimizacoes_aplicadas = defaultdict(list)
    
    def gerar_otimizacoes_especificas(self, nome_gerador: str, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Gera otimizações específicas para um gerador"""
        
        # Mapeamento de geradores para estratégias específicas
        estrategias_gerador = {
            'ia_numeros_repetidos': self._otimizar_ia_neural,
            'gerador_academico_dinamico': self._otimizar_academico,
            'super_gerador_ia': self._otimizar_super_gerador,
            'sistema_modelo_temporal_79': self._otimizar_temporal,
            'piramide_invertida_dinamica': self._otimizar_piramide,
            'sistema_neural_v7': self._otimizar_neural_v7,
            'sistema_hibrido_v3': self._otimizar_hibrido,
            'gerador_complementacao': self._otimizar_complementacao,
            'sistema_escalonado_v4': self._otimizar_escalonado,
            'gerador_zona_conforto': self._otimizar_zona_conforto
        }
        
        if nome_gerador in estrategias_gerador:
            otimizacoes = estrategias_gerador[nome_gerador](analise)
        else:
            otimizacoes = self._otimizar_generico(analise)
        
        # Registra otimizações aplicadas
        self.otimizacoes_aplicadas[nome_gerador].append({
            'timestamp': datetime.now().isoformat(),
            'otimizacoes': otimizacoes,
            'analise_base': analise['resumo']
        })
        
        return otimizacoes
    
    def _otimizar_ia_neural(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações específicas para IA de números repetidos"""
        precisao = analise['resumo']['precisao_media']
        
        otimizacoes = {
            'tipo': 'neural_ia',
            'parametros': {},
            'acoes': []
        }
        
        if precisao < 60:
            otimizacoes['parametros']['epochs'] = 200  # Mais treinamento
            otimizacoes['parametros']['learning_rate'] = 0.001  # Taxa menor
            otimizacoes['acoes'].append("Aumentar épocas de treinamento")
            otimizacoes['acoes'].append("Reduzir taxa de aprendizado")
        
        if analise['padroes']['volatilidade'] == 'Alta':
            otimizacoes['parametros']['dropout'] = 0.3  # Mais regularização
            otimizacoes['acoes'].append("Adicionar dropout para estabilidade")
        
        otimizacoes['acoes'].append("Revisar arquitetura da rede neural")
        return otimizacoes
    
    def _otimizar_academico(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para gerador acadêmico"""
        return {
            'tipo': 'academico',
            'parametros': {
                'janela_temporal': 150 if analise['resumo']['precisao_media'] < 65 else 100,
                'peso_frequencia': 0.4,
                'peso_ciclos': 0.3,
                'peso_tendencias': 0.3
            },
            'acoes': [
                "Ajustar janela temporal baseada em performance",
                "Rebalancear pesos dos fatores acadêmicos",
                "Incorporar mais dados históricos"
            ]
        }
    
    def _otimizar_super_gerador(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para super gerador IA"""
        return {
            'tipo': 'super_integrado',
            'parametros': {
                'peso_ia': 0.5,
                'peso_academico': 0.3,
                'peso_heuristico': 0.2,
                'diversidade_minima': 8
            },
            'acoes': [
                "Rebalancear componentes IA vs Acadêmico",
                "Aumentar diversidade se volatilidade alta",
                "Otimizar integração entre módulos"
            ]
        }
    
    def _otimizar_temporal(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para modelo temporal 79.9%"""
        return {
            'tipo': 'temporal_avancado',
            'parametros': {
                'janela_otima': 110,  # Já otimizada
                'peso_recencia': 0.6,
                'peso_sazonalidade': 0.4,
                'suavizacao': 0.1
            },
            'acoes': [
                "Manter configuração vencedora (79.9%)",
                "Ajustar apenas se performance degradar",
                "Monitorar sazonalidade dos padrões"
            ]
        }
    
    def _otimizar_piramide(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para pirâmide invertida"""
        return {
            'tipo': 'piramide_dinamica',
            'parametros': {
                'sensibilidade_transicao': 0.3,
                'peso_faixas_baixas': 0.7,
                'peso_faixas_altas': 0.3
            },
            'acoes': [
                "Ajustar sensibilidade às transições",
                "Priorizar números saindo de faixas baixas",
                "Calibrar detecção de sequências dominantes"
            ]
        }
    
    def _otimizar_neural_v7(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para sistema neural V7"""
        return {
            'tipo': 'neural_v7',
            'parametros': {
                'enfase_altos_baixos': 0.8,
                'threshold_reversao': 0.75,
                'ensemble_size': 5
            },
            'acoes': [
                "Calibrar detecção de reversão Altos/Baixos",
                "Ajustar threshold de confiança",
                "Otimizar ensemble de modelos"
            ]
        }
    
    def _otimizar_hibrido(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para sistema híbrido V3"""
        return {
            'tipo': 'hibrido_adaptativo',
            'parametros': {
                'peso_neural': 0.6,
                'peso_metadados': 0.4,
                'threshold_extremo': 0.8,
                'threshold_medio': 0.2
            },
            'acoes': [
                "Ajustar equilíbrio neural vs metadados",
                "Calibrar detecção de valores extremos",
                "Refinar lógica adaptativa"
            ]
        }
    
    def _otimizar_complementacao(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para complementação inteligente"""
        return {
            'tipo': 'complementacao_matematica',
            'parametros': {
                'criterio_selecao_20': 'frequencia_balanceada',
                'peso_historico': 0.7,
                'peso_tendencia': 0.3
            },
            'acoes': [
                "Otimizar seleção dos 20 números base",
                "Melhorar critérios de complementação",
                "Validar cobertura matemática C(5,3)"
            ]
        }
    
    def _otimizar_escalonado(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para sistema escalonado V4"""
        return {
            'tipo': 'escalonado_filtrado',
            'parametros': {
                'niveis_filtro': 8,
                'peso_neural_ranking': 0.6,
                'peso_matematico': 0.4
            },
            'acoes': [
                "Ajustar níveis de filtro redutor",
                "Calibrar peso do ranking neural",
                "Otimizar seleção TOP combinações"
            ]
        }
    
    def _otimizar_zona_conforto(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações para zona de conforto"""
        return {
            'tipo': 'zona_conforto',
            'parametros': {
                'percentual_zona_1_17': 0.8,
                'max_sequencia': 12,
                'diversidade_restante': 0.6
            },
            'acoes': [
                "Ajustar percentual da zona 1-17",
                "Calibrar tamanho máximo de sequências",
                "Equilibrar números restantes (18-25)"
            ]
        }
    
    def _otimizar_generico(self, analise: Dict[str, Any]) -> Dict[str, Any]:
        """Otimizações genéricas para geradores não mapeados"""
        return {
            'tipo': 'generico',
            'parametros': {
                'diversidade': 0.5,
                'estabilidade': 0.3,
                'inovacao': 0.2
            },
            'acoes': [
                "Implementar sistema de feedback básico",
                "Adicionar mecanismos de auto-ajuste",
                "Monitorar performance continuamente"
            ]
        }

class DistribuidorFeedback:
    """Distribui feedback e otimizações para os geradores"""
    
    def __init__(self):
        self.analisador = AnalisadorPadroes()
        self.otimizador = GeradorOtimizacoes()
        self.historico_distribuicao = []
    
    def processar_feedback_completo(self, resultado_validacao: Dict[str, Any]) -> Dict[str, Any]:
        """Processa feedback completo de uma validação"""
        print(f"\n🔄 PROCESSANDO FEEDBACK PARA {len(resultado_validacao['validacoes'])} GERADORES...")
        
        feedback_processado = {
            'concurso': resultado_validacao['concurso_alvo'],
            'timestamp': datetime.now().isoformat(),
            'geradores_processados': {},
            'resumo_otimizacoes': {},
            'impacto_estimado': {}
        }
        
        for nome_gerador, validacao in resultado_validacao['validacoes'].items():
            print(f"    🔧 Processando {nome_gerador}...")
            
            # Carrega histórico do gerador
            historico = self._carregar_historico_gerador(nome_gerador)
            
            # Adiciona validação atual ao histórico
            historico.append({
                'concurso': resultado_validacao['concurso_alvo'],
                'timestamp': resultado_validacao['timestamp'],
                'precisao_geral': validacao['precisao_geral'],
                'melhor_acerto': validacao['melhor_acerto'],
                'media_acertos': validacao['media_acertos']
            })
            
            # Analisa padrões
            analise = self.analisador.analisar_performance_gerador(historico)
            
            if 'erro' not in analise:
                # Gera otimizações
                otimizacoes = self.otimizador.gerar_otimizacoes_especificas(nome_gerador, analise)
                
                # Salva feedback processado
                feedback_processado['geradores_processados'][nome_gerador] = {
                    'analise': analise,
                    'otimizacoes': otimizacoes,
                    'historico_size': len(historico)
                }
                
                # Aplica otimizações
                sucesso_aplicacao = self._aplicar_otimizacoes_gerador(nome_gerador, otimizacoes)
                feedback_processado['geradores_processados'][nome_gerador]['aplicacao_sucesso'] = sucesso_aplicacao
                
                # Estima impacto
                impacto = self._estimar_impacto_otimizacoes(analise, otimizacoes)
                feedback_processado['impacto_estimado'][nome_gerador] = impacto
                
                print(f"        ✅ Análise concluída | Tendência: {analise['tendencias']['direcao_evolucao']}")
                print(f"        🎯 Otimizações: {len(otimizacoes['acoes'])} ações sugeridas")
                print(f"        📈 Impacto estimado: {impacto['melhoria_esperada']:.1f}%")
            else:
                print(f"        ❌ Erro na análise: {analise['erro']}")
            
            # Salva histórico atualizado
            self._salvar_historico_gerador(nome_gerador, historico)
        
        # Gera resumo de otimizações
        feedback_processado['resumo_otimizacoes'] = self._gerar_resumo_otimizacoes(feedback_processado)
        
        # Salva no histórico de distribuição
        self.historico_distribuicao.append(feedback_processado)
        self._salvar_historico_distribuicao()
        
        print(f"✅ Feedback processado para {len(feedback_processado['geradores_processados'])} geradores")
        return feedback_processado
    
    def _carregar_historico_gerador(self, nome_gerador: str) -> List[Dict[str, Any]]:
        """Carrega histórico específico de um gerador"""
        arquivo_historico = f"historico_performance_{nome_gerador}.json"
        
        try:
            if os.path.exists(arquivo_historico):
                with open(arquivo_historico, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar histórico de {nome_gerador}: {e}")
        
        return []
    
    def _salvar_historico_gerador(self, nome_gerador: str, historico: List[Dict[str, Any]]):
        """Salva histórico específico de um gerador"""
        arquivo_historico = f"historico_performance_{nome_gerador}.json"
        
        try:
            with open(arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(historico, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar histórico de {nome_gerador}: {e}")
    
    def _aplicar_otimizacoes_gerador(self, nome_gerador: str, otimizacoes: Dict[str, Any]) -> bool:
        """Aplica otimizações específicas a um gerador"""
        arquivo_config = f"config_otimizada_{nome_gerador}.json"
        
        try:
            # Salva configuração otimizada
            config_otimizada = {
                'timestamp': datetime.now().isoformat(),
                'parametros': otimizacoes['parametros'],
                'acoes_sugeridas': otimizacoes['acoes'],
                'tipo_otimizacao': otimizacoes['tipo'],
                'aplicado': False,  # Flag para controlar aplicação
                'versao': 1
            }
            
            with open(arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config_otimizada, f, indent=2, ensure_ascii=False)
            
            # Marca configuração como pronta para aplicação na próxima execução
            self._marcar_otimizacao_pendente(nome_gerador, config_otimizada)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar otimizações para {nome_gerador}: {e}")
            return False
    
    def _marcar_otimizacao_pendente(self, nome_gerador: str, config: Dict[str, Any]):
        """Marca otimização como pendente para próxima execução"""
        arquivo_pendentes = "otimizacoes_pendentes.json"
        
        try:
            # Carrega otimizações pendentes existentes
            pendentes = {}
            if os.path.exists(arquivo_pendentes):
                with open(arquivo_pendentes, 'r', encoding='utf-8') as f:
                    pendentes = json.load(f)
            
            # Adiciona nova otimização
            pendentes[nome_gerador] = {
                'config': config,
                'criado_em': datetime.now().isoformat(),
                'status': 'pendente'
            }
            
            # Salva arquivo atualizado
            with open(arquivo_pendentes, 'w', encoding='utf-8') as f:
                json.dump(pendentes, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao marcar otimização pendente: {e}")
    
    def carregar_otimizacoes_pendentes(self, nome_gerador: str) -> Optional[Dict[str, Any]]:
        """Carrega otimizações pendentes para um gerador específico"""
        arquivo_pendentes = "otimizacoes_pendentes.json"
        
        try:
            if os.path.exists(arquivo_pendentes):
                with open(arquivo_pendentes, 'r', encoding='utf-8') as f:
                    pendentes = json.load(f)
                
                if nome_gerador in pendentes:
                    config = pendentes[nome_gerador]
                    if config['status'] == 'pendente':
                        # Marca como aplicada
                        pendentes[nome_gerador]['status'] = 'aplicada'
                        pendentes[nome_gerador]['aplicado_em'] = datetime.now().isoformat()
                        
                        # Salva arquivo atualizado
                        with open(arquivo_pendentes, 'w', encoding='utf-8') as f:
                            json.dump(pendentes, f, indent=2, ensure_ascii=False)
                        
                        return config['config']
        except Exception as e:
            print(f"⚠️ Erro ao carregar otimizações pendentes: {e}")
        
        return None
    
    def _estimar_impacto_otimizacoes(self, analise: Dict[str, Any], otimizacoes: Dict[str, Any]) -> Dict[str, Any]:
        """Estima impacto das otimizações na performance"""
        precisao_atual = analise['resumo']['precisao_media']
        
        # Estimativa baseada no tipo de otimização e situação atual
        if precisao_atual < 50:
            melhoria_esperada = 15  # Muito potencial para melhoria
        elif precisao_atual < 65:
            melhoria_esperada = 8   # Bom potencial
        elif precisao_atual < 75:
            melhoria_esperada = 4   # Algum potencial
        else:
            melhoria_esperada = 2   # Pouco potencial (já boa)
        
        # Ajusta baseado no número de ações
        fator_acoes = min(len(otimizacoes['acoes']) * 0.5, 2.0)
        melhoria_ajustada = melhoria_esperada * fator_acoes
        
        return {
            'melhoria_esperada': melhoria_ajustada,
            'confianca_estimativa': 0.7,
            'prazo_esperado': '1-2 validações',
            'tipo_impacto': 'Gradual' if melhoria_ajustada < 5 else 'Moderado' if melhoria_ajustada < 10 else 'Significativo'
        }
    
    def _gerar_resumo_otimizacoes(self, feedback_processado: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo das otimizações aplicadas"""
        total_geradores = len(feedback_processado['geradores_processados'])
        
        tipos_otimizacao = defaultdict(int)
        total_acoes = 0
        melhoria_media_esperada = 0
        
        for dados in feedback_processado['geradores_processados'].values():
            tipo = dados['otimizacoes']['tipo']
            tipos_otimizacao[tipo] += 1
            total_acoes += len(dados['otimizacoes']['acoes'])
        
        if feedback_processado['impacto_estimado']:
            impactos = [imp['melhoria_esperada'] for imp in feedback_processado['impacto_estimado'].values()]
            melhoria_media_esperada = statistics.mean(impactos)
        
        return {
            'total_geradores_otimizados': total_geradores,
            'tipos_otimizacao': dict(tipos_otimizacao),
            'total_acoes_sugeridas': total_acoes,
            'melhoria_media_esperada': melhoria_media_esperada,
            'geradores_com_maior_potencial': self._identificar_maior_potencial(feedback_processado)
        }
    
    def _identificar_maior_potencial(self, feedback_processado: Dict[str, Any]) -> List[str]:
        """Identifica geradores com maior potencial de melhoria"""
        if not feedback_processado['impacto_estimado']:
            return []
        
        # Ordena por melhoria esperada
        geradores_ordenados = sorted(
            feedback_processado['impacto_estimado'].items(),
            key=lambda x: x[1]['melhoria_esperada'],
            reverse=True
        )
        
        return [nome for nome, _ in geradores_ordenados[:3]]
    
    def _salvar_historico_distribuicao(self):
        """Salva histórico de distribuição de feedback"""
        arquivo = "historico_distribuicao_feedback.json"
        
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.historico_distribuicao, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar histórico de distribuição: {e}")
    
    def gerar_relatorio_evolucao(self) -> str:
        """Gera relatório de evolução dos geradores"""
        if not self.historico_distribuicao:
            return "📊 Nenhum histórico de evolução disponível"
        
        relatorio = []
        relatorio.append("📈 RELATÓRIO DE EVOLUÇÃO DOS GERADORES")
        relatorio.append("=" * 60)
        
        # Analisa evolução geral
        total_sessoes = len(self.historico_distribuicao)
        ultima_sessao = self.historico_distribuicao[-1]
        
        relatorio.append(f"📊 Total de sessões de feedback: {total_sessoes}")
        relatorio.append(f"📅 Última atualização: {ultima_sessao['timestamp']}")
        relatorio.append(f"🤖 Geradores ativos: {len(ultima_sessao['geradores_processados'])}")
        relatorio.append("")
        
        # Top geradores com evolução
        if total_sessoes >= 2:
            evolucoes = self._calcular_evolucoes_geradores()
            
            relatorio.append("🏆 TOP EVOLUÇÕES:")
            relatorio.append("-" * 30)
            for nome, evolucao in evolucoes[:5]:
                relatorio.append(f"   📈 {nome}: +{evolucao:.1f}% de melhoria")
            relatorio.append("")
        
        # Resumo da última sessão
        resumo = ultima_sessao['resumo_otimizacoes']
        relatorio.append("📋 ÚLTIMA SESSÃO DE OTIMIZAÇÃO:")
        relatorio.append("-" * 40)
        relatorio.append(f"   🎯 Geradores otimizados: {resumo['total_geradores_otimizados']}")
        relatorio.append(f"   🔧 Total de ações: {resumo['total_acoes_sugeridas']}")
        relatorio.append(f"   📊 Melhoria esperada: {resumo['melhoria_media_esperada']:.1f}%")
        
        if resumo['geradores_com_maior_potencial']:
            relatorio.append(f"   🚀 Maior potencial: {', '.join(resumo['geradores_com_maior_potencial'])}")
        
        return "\n".join(relatorio)
    
    def _calcular_evolucoes_geradores(self) -> List[Tuple[str, float]]:
        """Calcula evolução de performance dos geradores"""
        evolucoes = []
        
        if len(self.historico_distribuicao) < 2:
            return evolucoes
        
        primeira_sessao = self.historico_distribuicao[0]
        ultima_sessao = self.historico_distribuicao[-1]
        
        geradores_comuns = set(primeira_sessao['geradores_processados'].keys()) & \
                          set(ultima_sessao['geradores_processados'].keys())
        
        for gerador in geradores_comuns:
            try:
                primeiro_impacto = primeira_sessao['impacto_estimado'][gerador]['melhoria_esperada']
                ultimo_impacto = ultima_sessao['impacto_estimado'][gerador]['melhoria_esperada']
                
                evolucao = ultimo_impacto - primeiro_impacto
                evolucoes.append((gerador, evolucao))
            except KeyError:
                continue
        
        return sorted(evolucoes, key=lambda x: x[1], reverse=True)

def main():
    """Função principal para teste do sistema"""
    distribuidor = DistribuidorFeedback()
    
    print("🔄 SISTEMA DE FEEDBACK LOOP INTELIGENTE")
    print("=" * 50)
    print("📊 Sistema ready para processar validações")
    print("🎯 Aguardando dados de validação...")
    
    # Mostra relatório de evolução se disponível
    relatorio = distribuidor.gerar_relatorio_evolucao()
    print(f"\n{relatorio}")

if __name__ == "__main__":
    main()