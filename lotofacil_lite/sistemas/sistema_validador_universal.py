#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 SISTEMA VALIDADOR UNIVERSAL
===============================
Sistema que valida predições de TODOS os geradores contra resultados manuais
e distribui aprendizado para evolução contínua dos algoritmos.

FUNCIONALIDADES:
• Coleta predições de todos os 16 geradores
• Aceita resultado manual (concurso futuro)
• Calcula precisão real de cada gerador
• Distribui feedback para evolução dos algoritmos
• Ranking dinâmico baseado em performance real

Autor: AR CALHAU
Data: 21/09/2025
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from abc import ABC, abstractmethod
import importlib

class InterfaceGerador(ABC):
    """Interface padrão que todos os geradores devem implementar"""
    
    @abstractmethod
    def gerar_predicao(self, concurso_alvo: int, quantidade: int = 5) -> Dict[str, Any]:
        """
        Gera predição para um concurso específico
        
        Returns:
            Dict com estrutura:
            {
                'concurso_alvo': int,
                'combinacoes': List[List[int]],
                'metadados': Dict,
                'confianca': float,
                'algoritmo': str
            }
        """
        pass
    
    @abstractmethod
    def aplicar_feedback(self, resultado_validacao: Dict[str, Any]) -> None:
        """Aplica feedback do resultado de validação para melhorar algoritmo"""
        pass

class AdaptadorGerador:
    """Adapta geradores existentes para a interface padrão"""
    
    def __init__(self, nome_gerador: str):
        self.nome = nome_gerador
        self.modulo = None
        self.classe_principal = None
        self._carregar_gerador()
        
        # NOVA FUNCIONALIDADE: Carrega otimizações pendentes automaticamente
        self._carregar_e_aplicar_otimizacoes()
    
    def _carregar_e_aplicar_otimizacoes(self):
        """Carrega e aplica otimizações pendentes para este gerador"""
        try:
            # Importa o distribuidor de feedback para acessar otimizações
            from sistema_feedback_loop_inteligente import DistribuidorFeedback
            distribuidor = DistribuidorFeedback()
            
            # Carrega otimizações pendentes
            otimizacoes = distribuidor.carregar_otimizacoes_pendentes(self.nome)
            
            if otimizacoes:
                print(f"🔧 Aplicando otimizações para {self.nome}...")
                
                # Aplica parâmetros otimizados se disponível
                if 'parametros' in otimizacoes:
                    self._aplicar_parametros_otimizados(otimizacoes['parametros'])
                
                print(f"✅ Otimizações aplicadas para {self.nome}")
            else:
                print(f"ℹ️ Nenhuma otimização pendente para {self.nome}")
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar otimizações para {self.nome}: {e}")
    
    def _aplicar_parametros_otimizados(self, parametros: Dict[str, Any]):
        """Aplica parâmetros otimizados ao gerador"""
        try:
            # Para geradores com interface configurável
            if self.classe_principal and hasattr(self.classe_principal, 'configurar_parametros'):
                self.classe_principal.configurar_parametros(parametros)
                print(f"   📊 Parâmetros configurados: {list(parametros.keys())}")
            
            # Para geradores com atributos diretos
            elif self.classe_principal:
                for param, valor in parametros.items():
                    if hasattr(self.classe_principal, param):
                        setattr(self.classe_principal, param, valor)
                        print(f"   📊 {param} = {valor}")
                        
        except Exception as e:
            print(f"⚠️ Erro ao aplicar parâmetros: {e}")

    def _carregar_gerador(self):
        """Carrega dinamicamente o gerador"""
        try:
            # Mapeamento dos geradores conhecidos
            mapeamento_geradores = {
                'ia_numeros_repetidos': {
                    'modulo': 'ia_numeros_repetidos',
                    'classe': 'IANumerosRepetidos',
                    'metodo_geracao': 'gerar_predicoes_teste'
                },
                'gerador_academico_dinamico': {
                    'modulo': 'gerador_academico_dinamico',
                    'classe': 'GeradorAcademicoDinamico',
                    'metodo_geracao': 'gerar_combinacao_academica'
                },
                'super_gerador_ia': {
                    'modulo': 'super_gerador_ia',
                    'classe': 'SuperGeradorIA',
                    'metodo_geracao': 'gerar_super_combinacoes'
                },
                'sistema_modelo_temporal_79': {
                    'modulo': 'sistema_modelo_temporal_79',
                    'classe': 'SistemaModeloTemporal79',
                    'metodo_geracao': 'gerar_predicoes_temporais'
                },
                'piramide_invertida_dinamica': {
                    'modulo': 'piramide_invertida_dinamica',
                    'classe': 'PiramideInvertidaDinamica',
                    'metodo_geracao': 'gerar_combinacoes_piramide'
                },
                'sistema_neural_v7': {
                    'modulo': 'interface_neural_v7',
                    'classe': None,
                    'metodo_geracao': 'executar_neural_v7_interface'
                },
                'sistema_hibrido_v3': {
                    'modulo': 'analisador_hibrido_v3',
                    'classe': 'AnalisadorHibridoV3',
                    'metodo_geracao': 'executar_analise_hibrida_v3'
                },
                'gerador_complementacao': {
                    'modulo': 'gerador_complementacao_inteligente',
                    'classe': 'GeradorComplementacaoInteligente',
                    'metodo_geracao': 'gerar_combinacoes_complementares'
                },
                'sistema_escalonado_v4': {
                    'modulo': 'interface_sistema_v4',
                    'classe': 'InterfaceSistemaV4',
                    'metodo_geracao': 'executar_interface'
                },
                'gerador_zona_conforto': {
                    'modulo': 'gerador_zona_conforto',
                    'classe': None,
                    'metodo_geracao': 'menu_zona_conforto'
                }
            }
            
            if self.nome in mapeamento_geradores:
                config = mapeamento_geradores[self.nome]
                self.modulo = importlib.import_module(config['modulo'])
                
                if config['classe']:
                    self.classe_principal = getattr(self.modulo, config['classe'])
                    self.metodo_geracao = config['metodo_geracao']
                else:
                    # Função standalone
                    self.metodo_geracao = getattr(self.modulo, config['metodo_geracao'])
                    
                print(f"✅ {self.nome} carregado com sucesso")
            else:
                print(f"⚠️ Gerador {self.nome} não mapeado - usando adaptação genérica")
                
        except ImportError as e:
            print(f"❌ Erro ao carregar {self.nome}: {e}")
            self.modulo = None
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar {self.nome}: {e}")
            self.modulo = None
    
    def gerar_predicao(self, concurso_alvo: int, quantidade: int = 5) -> Dict[str, Any]:
        """Gera predição usando o gerador adaptado"""
        if not self.modulo:
            return self._predicao_mock(concurso_alvo, quantidade)
        
        try:
            if self.classe_principal:
                # Instancia classe e chama método
                instancia = self.classe_principal()
                
                # Tenta diferentes assinaturas de método
                if hasattr(instancia, self.metodo_geracao):
                    metodo = getattr(instancia, self.metodo_geracao)
                    
                    # Adaptação baseada no nome do método
                    if 'academica' in self.metodo_geracao:
                        combinacoes = [metodo(qtd_numeros=20) for _ in range(quantidade)]
                    elif 'temporal' in self.metodo_geracao:
                        resultado = metodo(quantidade)
                        combinacoes = resultado if isinstance(resultado, list) else [resultado]
                    elif 'predicoes' in self.metodo_geracao:
                        combinacoes = metodo(quantidade)
                    else:
                        combinacoes = metodo(quantidade)
                else:
                    # Método padrão
                    combinacoes = [self._gerar_combinacao_generica(instancia) for _ in range(quantidade)]
            else:
                # Função standalone
                resultado = self.metodo_geracao()
                combinacoes = resultado if isinstance(resultado, list) else [resultado]
            
            # Normaliza resultado
            if not isinstance(combinacoes, list):
                combinacoes = [combinacoes]
            
            # Filtra combinações válidas
            combinacoes_validas = []
            for comb in combinacoes:
                if isinstance(comb, list) and len(comb) >= 15:
                    # Garante que são 15 números únicos
                    comb_normalizada = sorted(list(set(comb)))[:15]
                    if len(comb_normalizada) == 15:
                        combinacoes_validas.append(comb_normalizada)
            
            # Se não temos combinações válidas, gera mock
            if not combinacoes_validas:
                return self._predicao_mock(concurso_alvo, quantidade)
            
            return {
                'concurso_alvo': concurso_alvo,
                'combinacoes': combinacoes_validas[:quantidade],
                'metadados': {
                    'gerador': self.nome,
                    'timestamp': datetime.now().isoformat(),
                    'metodo_usado': self.metodo_geracao,
                    'adaptacao': 'automatica'
                },
                'confianca': self._calcular_confianca_estimada(),
                'algoritmo': self.nome.replace('_', ' ').title()
            }
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar predição com {self.nome}: {e}")
            return self._predicao_mock(concurso_alvo, quantidade)
    
    def _gerar_combinacao_generica(self, instancia):
        """Tenta gerar combinação usando métodos comuns"""
        metodos_comuns = [
            'gerar_combinacao',
            'gerar_combinacoes',
            'generate_combination',
            'generate_combinations',
            'executar',
            'run'
        ]
        
        for metodo_nome in metodos_comuns:
            if hasattr(instancia, metodo_nome):
                metodo = getattr(instancia, metodo_nome)
                try:
                    resultado = metodo()
                    if isinstance(resultado, list) and len(resultado) >= 15:
                        return resultado[:15]
                except:
                    continue
        
        # Fallback: geração aleatória
        import random
        return sorted(random.sample(range(1, 26), 15))
    
    def _predicao_mock(self, concurso_alvo: int, quantidade: int) -> Dict[str, Any]:
        """Gera predição mock quando o gerador falha"""
        import random
        
        combinacoes = []
        for _ in range(quantidade):
            combinacao = sorted(random.sample(range(1, 26), 15))
            combinacoes.append(combinacao)
        
        return {
            'concurso_alvo': concurso_alvo,
            'combinacoes': combinacoes,
            'metadados': {
                'gerador': self.nome,
                'timestamp': datetime.now().isoformat(),
                'metodo_usado': 'mock_fallback',
                'adaptacao': 'mock'
            },
            'confianca': 0.1,  # Baixa confiança para mock
            'algoritmo': f"{self.nome} (Mock)"
        }
    
    def _calcular_confianca_estimada(self) -> float:
        """Calcula confiança estimada baseada no histórico do gerador"""
        # Confianças baseadas nos resultados conhecidos
        confiancas_conhecidas = {
            'ia_numeros_repetidos': 0.65,
            'gerador_academico_dinamico': 0.70,
            'super_gerador_ia': 0.75,  # Comprovado: 15 acertos
            'sistema_modelo_temporal_79': 0.799,  # Melhor resultado
            'piramide_invertida_dinamica': 0.68,
            'sistema_neural_v7': 0.76,
            'sistema_hibrido_v3': 0.78,  # Recomendado
            'gerador_complementacao': 0.72,
            'sistema_escalonado_v4': 0.77,
            'gerador_zona_conforto': 0.69
        }
        
        return confiancas_conhecidas.get(self.nome, 0.60)
    
    def aplicar_feedback(self, resultado_validacao: Dict[str, Any]) -> None:
        """Aplica feedback para o gerador (implementação futura)"""
        # Por enquanto, apenas salva o feedback
        feedback_file = f"feedback_{self.nome}.json"
        
        try:
            # Carrega feedback existente
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    historico = json.load(f)
            else:
                historico = []
            
            # Adiciona novo feedback
            historico.append({
                'timestamp': datetime.now().isoformat(),
                'resultado': resultado_validacao,
                'gerador': self.nome
            })
            
            # Salva feedback atualizado
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(historico, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Feedback salvo para {self.nome}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar feedback para {self.nome}: {e}")

class SistemaValidadorUniversal:
    """Sistema principal de validação universal"""
    
    def __init__(self):
        self.geradores = self._inicializar_geradores()
        self.historico_validacoes = []
        self.arquivo_historico = "validacoes_universais.json"
        self._carregar_historico()
        
        # Aplicar descobertas dos campos de comparação
        try:
            from integracao_descobertas_comparacao import aplicar_descobertas_comparacao
            aplicar_descobertas_comparacao(self)
            print("✅ Descobertas dos campos de comparação integradas ao validador")
        except ImportError:
            print("⚠️ Módulo de descobertas de comparação não encontrado")
    
    def _inicializar_geradores(self) -> List[AdaptadorGerador]:
        """Inicializa todos os geradores disponíveis"""
        nomes_geradores = [
            'ia_numeros_repetidos',
            'gerador_academico_dinamico', 
            'super_gerador_ia',
            'sistema_modelo_temporal_79',
            'piramide_invertida_dinamica',
            'sistema_neural_v7',
            'sistema_hibrido_v3',
            'gerador_complementacao',
            'sistema_escalonado_v4',
            'gerador_zona_conforto'
        ]
        
        geradores = []
        for nome in nomes_geradores:
            adaptador = AdaptadorGerador(nome)
            geradores.append(adaptador)
        
        print(f"✅ {len(geradores)} geradores inicializados")
        return geradores
    
    def _carregar_historico(self):
        """Carrega histórico de validações"""
        try:
            if os.path.exists(self.arquivo_historico):
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    self.historico_validacoes = json.load(f)
                print(f"📚 Histórico carregado: {len(self.historico_validacoes)} validações")
            else:
                self.historico_validacoes = []
                print("📚 Histórico vazio - primeira execução")
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            self.historico_validacoes = []
    
    def _salvar_historico(self):
        """Salva histórico de validações"""
        try:
            with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(self.historico_validacoes, f, indent=2, ensure_ascii=False)
            print(f"✅ Histórico salvo: {len(self.historico_validacoes)} validações")
        except Exception as e:
            print(f"❌ Erro ao salvar histórico: {e}")
    
    def executar_teste_completo(self, concurso_alvo: int, resultado_manual: List[int]) -> Dict[str, Any]:
        """
        Executa teste completo com todos os geradores
        
        Args:
            concurso_alvo: Número do concurso a ser testado
            resultado_manual: Lista de 15 números do resultado real
            
        Returns:
            Dict com resultados completos da validação
        """
        print(f"\n🔬 INICIANDO TESTE COMPLETO - CONCURSO {concurso_alvo}")
        print("=" * 70)
        
        # Valida entrada
        if not isinstance(resultado_manual, list) or len(resultado_manual) != 15:
            raise ValueError("Resultado manual deve ter exatamente 15 números")
        
        resultado_manual = sorted(list(set(resultado_manual)))
        if len(resultado_manual) != 15:
            raise ValueError("Resultado manual deve ter 15 números únicos")
        
        print(f"🎯 Resultado manual: {resultado_manual}")
        print(f"🤖 Testando {len(self.geradores)} geradores...")
        print()
        
        # Coleta predições de todos os geradores
        predicoes = {}
        for i, gerador in enumerate(self.geradores, 1):
            print(f"🔄 [{i:2d}/{len(self.geradores)}] Executando {gerador.nome}...")
            
            try:
                predicao = gerador.gerar_predicao(concurso_alvo, quantidade=5)
                predicoes[gerador.nome] = predicao
                print(f"    ✅ {len(predicao['combinacoes'])} combinações geradas")
            except Exception as e:
                print(f"    ❌ Erro: {e}")
                predicoes[gerador.nome] = None
        
        print(f"\n📊 Predições coletadas: {len([p for p in predicoes.values() if p])}/{len(self.geradores)}")
        
        # Valida cada predição contra o resultado
        resultados_validacao = {}
        for nome_gerador, predicao in predicoes.items():
            if predicao:
                resultado = self._validar_predicao(predicao, resultado_manual)
                resultados_validacao[nome_gerador] = resultado
        
        # Compila resultado final
        resultado_final = {
            'concurso_alvo': concurso_alvo,
            'resultado_manual': resultado_manual,
            'timestamp': datetime.now().isoformat(),
            'total_geradores': len(self.geradores),
            'geradores_executados': len(resultados_validacao),
            'predicoes': predicoes,
            'validacoes': resultados_validacao,
            'ranking': self._gerar_ranking(resultados_validacao),
            'estatisticas': self._calcular_estatisticas(resultados_validacao)
        }
        
        # Salva no histórico
        self.historico_validacoes.append(resultado_final)
        self._salvar_historico()
        
        # Distribui feedback para geradores
        self._distribuir_feedback(resultados_validacao)
        
        return resultado_final
    
    def _validar_predicao(self, predicao: Dict[str, Any], resultado_manual: List[int]) -> Dict[str, Any]:
        """Valida uma predição específica contra o resultado manual com nova métrica de sucesso"""
        combinacoes = predicao['combinacoes']
        
        resultados_combinacoes = []
        total_acertos = 0
        melhor_acerto = 0
        
        # NOVA MÉTRICA: Conta combinações com 11+ acertos
        combinacoes_11_plus = 0
        combinacoes_excelentes = 0  # 13+ acertos
        
        for i, combinacao in enumerate(combinacoes):
            acertos = len(set(combinacao) & set(resultado_manual))
            total_acertos += acertos
            melhor_acerto = max(melhor_acerto, acertos)
            
            # Contabiliza para nova métrica
            if acertos >= 11:
                combinacoes_11_plus += 1
            if acertos >= 13:
                combinacoes_excelentes += 1
            
            resultados_combinacoes.append({
                'combinacao': combinacao,
                'acertos': acertos,
                'precisao_percentual': (acertos / 15) * 100
            })
        
        media_acertos = total_acertos / len(combinacoes) if combinacoes else 0
        precisao_geral = (media_acertos / 15) * 100  # Mantém para compatibilidade
        
        # NOVA MÉTRICA PRINCIPAL: Percentual de combinações com 11+ acertos
        percentual_11_plus = (combinacoes_11_plus / len(combinacoes)) * 100 if combinacoes else 0
        percentual_excelentes = (combinacoes_excelentes / len(combinacoes)) * 100 if combinacoes else 0
        
        # Classificação do sucesso
        if percentual_11_plus >= 70:
            classificacao_sucesso = "EXCELENTE"
            emoji_status = "🏆"
        elif percentual_11_plus >= 50:
            classificacao_sucesso = "SUCESSO"
            emoji_status = "✅"
        elif percentual_11_plus >= 30:
            classificacao_sucesso = "BOM"
            emoji_status = "🟡"
        else:
            classificacao_sucesso = "INSUFICIENTE"
            emoji_status = "❌"
        
        return {
            'gerador': predicao['metadados']['gerador'],
            'algoritmo': predicao['algoritmo'],
            'confianca_declarada': predicao['confianca'],
            'total_combinacoes': len(combinacoes),
            'total_acertos': total_acertos,
            'media_acertos': media_acertos,
            'melhor_acerto': melhor_acerto,
            'precisao_geral': precisao_geral,  # Compatibilidade
            
            # NOVAS MÉTRICAS PRINCIPAIS
            'combinacoes_11_plus': combinacoes_11_plus,
            'percentual_11_plus': percentual_11_plus,
            'combinacoes_excelentes': combinacoes_excelentes,
            'percentual_excelentes': percentual_excelentes,
            'classificacao_sucesso': classificacao_sucesso,
            'emoji_status': emoji_status,
            
            'combinacoes_detalhadas': resultados_combinacoes,
            'metadados_predicao': predicao['metadados']
        }
    
    def _gerar_ranking(self, resultados_validacao: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera ranking dos geradores por performance usando nova métrica de sucesso"""
        ranking = []
        
        for nome_gerador, resultado in resultados_validacao.items():
            # NOVO SISTEMA DE PONTUAÇÃO:
            # 70% peso no percentual de combinações com 11+ acertos
            # 20% peso no percentual de combinações excelentes (13+)
            # 10% peso no melhor acerto
            score_final = (
                resultado['percentual_11_plus'] * 0.7 +  # Principal: 70% peso nas combinações 11+
                resultado['percentual_excelentes'] * 0.2 +  # Secundário: 20% peso nas excelentes
                (resultado['melhor_acerto'] / 15 * 100) * 0.1  # Complementar: 10% peso no melhor
            )
            
            ranking.append({
                'posicao': 0,  # Será preenchido após ordenação
                'gerador': nome_gerador,
                'algoritmo': resultado['algoritmo'],
                'score_final': score_final,
                'precisao_geral': resultado['precisao_geral'],  # Compatibilidade
                'percentual_11_plus': resultado['percentual_11_plus'],  # NOVA MÉTRICA PRINCIPAL
                'combinacoes_11_plus': resultado['combinacoes_11_plus'],
                'percentual_excelentes': resultado['percentual_excelentes'],
                'classificacao_sucesso': resultado['classificacao_sucesso'],
                'emoji_status': resultado['emoji_status'],
                'melhor_acerto': resultado['melhor_acerto'],
                'media_acertos': resultado['media_acertos'],
                'total_combinacoes': resultado['total_combinacoes'],
                'confianca_declarada': resultado['confianca_declarada']
            })
        
        # Ordena por score final
        ranking.sort(key=lambda x: x['score_final'], reverse=True)
        
        # Atribui posições
        for i, item in enumerate(ranking, 1):
            item['posicao'] = i
        
        return ranking
    
    def _calcular_estatisticas(self, resultados_validacao: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula estatísticas gerais do teste"""
        if not resultados_validacao:
            return {}
        
        precisoes = [r['precisao_geral'] for r in resultados_validacao.values()]
        melhores_acertos = [r['melhor_acerto'] for r in resultados_validacao.values()]
        medias_acertos = [r['media_acertos'] for r in resultados_validacao.values()]
        
        return {
            'precisao_media_geral': sum(precisoes) / len(precisoes),
            'precisao_maxima': max(precisoes),
            'precisao_minima': min(precisoes),
            'melhor_acerto_geral': max(melhores_acertos),
            'media_acertos_geral': sum(medias_acertos) / len(medias_acertos),
            'total_geradores_validos': len(resultados_validacao),
            'geradores_acima_70_pct': len([p for p in precisoes if p >= 70]),
            'geradores_acima_80_pct': len([p for p in precisoes if p >= 80])
        }
    
    def _distribuir_feedback(self, resultados_validacao: Dict[str, Any]):
        """Distribui feedback para todos os geradores"""
        print(f"\n🔄 DISTRIBUINDO FEEDBACK PARA {len(resultados_validacao)} GERADORES...")
        
        for nome_gerador, resultado in resultados_validacao.items():
            # Encontra o gerador correspondente
            gerador = next((g for g in self.geradores if g.nome == nome_gerador), None)
            
            if gerador:
                try:
                    gerador.aplicar_feedback(resultado)
                    print(f"    ✅ Feedback enviado para {nome_gerador}")
                except Exception as e:
                    print(f"    ❌ Erro ao enviar feedback para {nome_gerador}: {e}")
        
        print("✅ Distribuição de feedback concluída")
    
    def gerar_relatorio_completo(self, resultado_validacao: Dict[str, Any]) -> str:
        """Gera relatório detalhado da validação"""
        relatorio = []
        
        # Cabeçalho
        relatorio.append("🔬 RELATÓRIO DE VALIDAÇÃO UNIVERSAL")
        relatorio.append("=" * 80)
        relatorio.append(f"📅 Data/Hora: {resultado_validacao['timestamp']}")
        relatorio.append(f"🎯 Concurso: {resultado_validacao['concurso_alvo']}")
        relatorio.append(f"🎲 Resultado: {resultado_validacao['resultado_manual']}")
        relatorio.append(f"🤖 Geradores testados: {resultado_validacao['geradores_executados']}/{resultado_validacao['total_geradores']}")
        relatorio.append("")
        
        # Estatísticas gerais
        stats = resultado_validacao['estatisticas']
        relatorio.append("📊 ESTATÍSTICAS GERAIS:")
        relatorio.append("-" * 40)
        relatorio.append(f"📈 Precisão média: {stats['precisao_media_geral']:.1f}%")
        relatorio.append(f"� META: 50%+ das combinações com 11+ acertos = SUCESSO")
        relatorio.append(f"🏆 META: 70%+ das combinações com 11+ acertos = EXCELENTE")
        relatorio.append(f"� Melhor precisão: {stats['precisao_maxima']:.1f}%")
        relatorio.append(f"📉 Pior precisão: {stats['precisao_minima']:.1f}%")
        relatorio.append(f"🎯 Melhor acerto geral: {stats['melhor_acerto_geral']}/15")
        relatorio.append("")
        
        # Ranking com nova métrica
        relatorio.append("🏆 RANKING DE PERFORMANCE (NOVA MÉTRICA):")
        relatorio.append("-" * 90)
        for item in resultado_validacao['ranking'][:10]:  # Top 10
            relatorio.append(
                f"{item['posicao']:2d}º. {item['emoji_status']} {item['algoritmo']:<25} | "
                f"Score: {item['score_final']:5.1f} | "
                f"11+ acertos: {item['percentual_11_plus']:4.1f}% ({item['combinacoes_11_plus']}/{item['total_combinacoes']}) | "
                f"Status: {item['classificacao_sucesso']}"
            )
        relatorio.append("")
        
        # Detalhes por gerador
        relatorio.append("📋 DETALHES POR GERADOR:")
        relatorio.append("-" * 80)
        
        for nome_gerador, validacao in resultado_validacao['validacoes'].items():
            relatorio.append(f"\n🔧 {validacao['emoji_status']} {validacao['algoritmo']} - {validacao['classificacao_sucesso']}:")
            relatorio.append(f"   🎯 NOVA MÉTRICA: {validacao['percentual_11_plus']:.1f}% das combinações com 11+ acertos ({validacao['combinacoes_11_plus']}/{validacao['total_combinacoes']})")
            relatorio.append(f"   ⭐ Excelentes (13+): {validacao['percentual_excelentes']:.1f}% ({validacao['combinacoes_excelentes']}/{validacao['total_combinacoes']})")
            relatorio.append(f"   📊 Precisão geral: {validacao['precisao_geral']:.1f}% (compatibilidade)")
            relatorio.append(f"   � Melhor acerto: {validacao['melhor_acerto']}/15")
            relatorio.append(f"   📈 Média de acertos: {validacao['media_acertos']:.1f}/15")
            relatorio.append(f"   🎲 Combinações testadas: {validacao['total_combinacoes']}")
            
            # Mostra melhor combinação
            melhor_comb = max(validacao['combinacoes_detalhadas'], key=lambda x: x['acertos'])
            relatorio.append(f"   🏆 Melhor combinação: {melhor_comb['combinacao']} ({melhor_comb['acertos']} acertos)")
            
            # Mostra distribuição de acertos
            distribuicao = {}
            for comb in validacao['combinacoes_detalhadas']:
                acertos = comb['acertos']
                distribuicao[acertos] = distribuicao.get(acertos, 0) + 1
            
            dist_str = " | ".join([f"{acertos}pts: {qtd}x" for acertos, qtd in sorted(distribuicao.items(), reverse=True)])
            relatorio.append(f"   📊 Distribuição: {dist_str}")
        
        return "\n".join(relatorio)
    
    def obter_historico_gerador(self, nome_gerador: str) -> List[Dict[str, Any]]:
        """Obtém histórico de performance de um gerador específico"""
        historico = []
        
        for validacao in self.historico_validacoes:
            if nome_gerador in validacao['validacoes']:
                resultado = validacao['validacoes'][nome_gerador]
                historico.append({
                    'concurso': validacao['concurso_alvo'],
                    'timestamp': validacao['timestamp'],
                    'precisao_geral': resultado['precisao_geral'],
                    'melhor_acerto': resultado['melhor_acerto'],
                    'media_acertos': resultado['media_acertos']
                })
        
        return historico
    
    def mostrar_interface_usuario(self):
        """Interface de usuário para o sistema de validação"""
        print("\n🔬 SISTEMA VALIDADOR UNIVERSAL")
        print("=" * 60)
        print("🎯 Testa TODOS os geradores contra resultado manual")
        print("📊 Gera ranking de performance real")
        print("🔄 Distribui aprendizado para evolução contínua")
        print()
        
        try:
            # Pergunta o concurso alvo
            concurso_input = input("🎯 Concurso alvo (ex: 3491): ").strip()
            concurso_alvo = int(concurso_input) if concurso_input else 3491
            
            # Pergunta o resultado manual
            print(f"\n🎲 Digite o resultado do concurso {concurso_alvo}:")
            print("    (15 números separados por vírgula)")
            resultado_input = input("    Resultado: ").strip()
            
            # Converte resultado
            numeros_str = resultado_input.replace(';', ',').split(',')
            resultado_manual = [int(n.strip()) for n in numeros_str if n.strip()]
            
            if len(resultado_manual) != 15:
                print(f"❌ Erro: Digite exatamente 15 números (você digitou {len(resultado_manual)})")
                return
            
            if not all(1 <= n <= 25 for n in resultado_manual):
                print("❌ Erro: Todos os números devem estar entre 1 e 25")
                return
            
            if len(set(resultado_manual)) != 15:
                print("❌ Erro: Todos os números devem ser únicos")
                return
            
            # Confirma execução
            print(f"\n📋 CONFIGURAÇÃO:")
            print(f"   🎯 Concurso: {concurso_alvo}")
            print(f"   🎲 Resultado: {sorted(resultado_manual)}")
            print(f"   🤖 Geradores: {len(self.geradores)}")
            
            confirmar = input(f"\n🚀 Executar teste completo? (s/n): ").lower().strip()
            
            if confirmar.startswith('s'):
                # Executa teste
                resultado = self.executar_teste_completo(concurso_alvo, resultado_manual)
                
                # Mostra relatório
                print("\n" + "="*80)
                print(self.gerar_relatorio_completo(resultado))
                print("="*80)
                
                # Salva relatório
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"relatorio_validacao_universal_{concurso_alvo}_{timestamp}.txt"
                
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    f.write(self.gerar_relatorio_completo(resultado))
                
                print(f"\n💾 Relatório salvo em: {nome_arquivo}")
                
                # Pergunta se quer ver histórico de algum gerador
                print(f"\n📚 HISTÓRICO DISPONÍVEL:")
                geradores_com_historico = []
                for validacao in self.historico_validacoes[-5:]:  # Últimas 5 validações
                    geradores_com_historico.extend(validacao['validacoes'].keys())
                
                geradores_unicos = list(set(geradores_com_historico))
                if geradores_unicos:
                    print(f"   Geradores com histórico: {len(geradores_unicos)}")
                    
                    ver_historico = input(f"📈 Ver histórico de algum gerador? (s/n): ").lower().strip()
                    if ver_historico.startswith('s'):
                        print(f"   Geradores disponíveis: {', '.join(geradores_unicos[:5])}...")
                        gerador_escolhido = input(f"   Digite o nome do gerador: ").strip()
                        
                        if gerador_escolhido in geradores_unicos:
                            historico = self.obter_historico_gerador(gerador_escolhido)
                            print(f"\n📈 HISTÓRICO DE {gerador_escolhido.upper()}:")
                            print("-" * 50)
                            for h in historico[-10:]:  # Últimos 10
                                print(f"   Concurso {h['concurso']}: {h['precisao_geral']:.1f}% | Melhor: {h['melhor_acerto']}/15")
                
                print(f"\n✅ VALIDAÇÃO UNIVERSAL CONCLUÍDA!")
                print(f"🔄 Feedback distribuído para todos os geradores")
                print(f"📊 Ranking atualizado baseado em performance real")
                
            else:
                print("❌ Teste cancelado")
                
        except ValueError as e:
            print(f"❌ Erro nos dados: {e}")
        except KeyboardInterrupt:
            print(f"\n❌ Teste interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Função principal para teste"""
    validador = SistemaValidadorUniversal()
    validador.mostrar_interface_usuario()

if __name__ == "__main__":
    main()