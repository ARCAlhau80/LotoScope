#!/usr/bin/env python3
"""
🎯 SISTEMA LOTOSCOPE INTEGRADO - VERSÃO FINAL PRODUÇÃO
===========================================================
Sistema completo: Treinamento → Predição → Geração de Combinações
Objetivo: Reduzir de 3.268.760 para algumas centenas de combinações
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional

# Importar módulos locais
try:
    from analisador_preditivo_especializado import AnalisadorPreditivoEspecializado
    from treinador_otimizado import TreinadorOtimizado  
    from gerador_combinacoes_otimizado import GeradorCombinacoesOtimizado
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Certifique-se de que todos os arquivos estão no mesmo diretório")
    sys.exit(1)

class LotoScopeIntegrado:
    """Sistema LotoScope integrado - Versão Final de Produção"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.analisador = None
        self.treinador = None
        self.gerador = None
        self.modelos_treinados = {}
        
        self.logger.info("🎯 LotoScope Integrado inicializado")
    
    def _setup_logger(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'lotoscope_{datetime.now().strftime("%Y%m%d_%H%M")}.log')
            ]
        )
        return logging.getLogger('LotoScopeIntegrado')
    
    def inicializar_componentes(self):
        """Inicializar todos os componentes do sistema"""
        self.logger.info("🔧 Inicializando componentes do sistema...")
        
        try:
            # Inicializar analisador
            self.analisador = AnalisadorPreditivoEspecializado()
            self.logger.info("✅ Analisador inicializado")
            
            # Inicializar treinador
            self.treinador = TreinadorOtimizado()
            self.logger.info("✅ Treinador inicializado")
            
            # Inicializar gerador
            self.gerador = GeradorCombinacoesOtimizado()
            self.logger.info("✅ Gerador inicializado")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar componentes: {e}")
            return False
    
    def executar_treinamento_completo(self, forcar_retreino: bool = False) -> bool:
        """
        Executar treinamento completo do sistema
        
        Args:
            forcar_retreino: Se True, força novo treinamento mesmo com modelos existentes
            
        Returns:
            True se treinamento foi bem-sucedido
        """
        self.logger.info("🎓 Iniciando treinamento completo do sistema...")
        
        try:
            # Carregar dados históricos
            self.logger.info("📊 Carregando dados históricos...")
            dados_historicos = self.analisador.carregar_dados_historicos()
            
            if not dados_historicos:
                self.logger.error("❌ Falha ao carregar dados históricos")
                return False
            
            self.logger.info(f"✅ {len(dados_historicos)} registros carregados")
            
            # Executar treinamento otimizado
            self.logger.info("🤖 Executando treinamento com otimização...")
            self.modelos_treinados = self.treinador.executar_treinamento_completo(dados_historicos)
            
            if not self.modelos_treinados:
                self.logger.error("❌ Falha no treinamento dos modelos")
                return False
            
            # Salvar modelos treinados
            self._salvar_modelos()
            
            self.logger.info("🎉 Treinamento completo finalizado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante treinamento: {e}")
            return False
    
    def gerar_predicao_proximo_concurso(self, numero_concurso: Optional[int] = None) -> Dict:
        """
        Gerar predição para o próximo concurso
        
        Args:
            numero_concurso: Número do concurso (opcional)
            
        Returns:
            Dicionário com predições dos 8 parâmetros
        """
        self.logger.info("🔮 Gerando predição para próximo concurso...")
        
        try:
            if not self.modelos_treinados:
                self.logger.info("📂 Carregando modelos treinados...")
                self._carregar_modelos()
            
            # Obter dados para predição
            dados_recentes = self.analisador.carregar_dados_historicos()[-50:]  # Últimos 50 concursos
            
            # Gerar predições usando os modelos otimizados
            predicoes = {}
            
            # Lista dos 8 parâmetros-chave
            parametros = [
                'maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo',
                'n1', 'n15', 'faixa_6a25', 'faixa_6a20', 'acertos_combinacao_fixa'
            ]
            
            for parametro in parametros:
                if parametro in self.modelos_treinados:
                    modelo = self.modelos_treinados[parametro]
                    
                    # Preparar features para predição
                    features = self._preparar_features_predicao(dados_recentes, parametro)
                    
                    # Fazer predição
                    predicao = modelo['modelo'].predict(features.reshape(1, -1))[0]
                    predicao = max(0, min(25, round(predicao)))  # Garantir range válido
                    
                    predicoes[parametro] = predicao
                    
                    self.logger.info(f"   {parametro}: {predicao} (confiança: {modelo.get('score', 0):.3f})")
            
            # Ajustar predições para garantir consistência
            predicoes = self._ajustar_predicoes_consistencia(predicoes)
            
            # Adicionar metadados
            predicoes['timestamp'] = datetime.now().isoformat()
            predicoes['concurso_previsto'] = numero_concurso or (max([d.numero_concurso for d in dados_recentes]) + 1)
            predicoes['confianca_geral'] = np.mean([self.modelos_treinados[p].get('score', 0) for p in parametros if p in self.modelos_treinados])
            
            self.logger.info(f"🎯 Predição concluída - Confiança geral: {predicoes['confianca_geral']:.3f}")
            
            return predicoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar predição: {e}")
            return {}
    
    def gerar_combinacoes_otimizadas(self, predicoes: Dict, max_combinacoes: int = 500) -> List[Dict]:
        """
        Gerar combinações otimizadas baseadas nas predições
        
        Args:
            predicoes: Dicionário com predições dos parâmetros
            max_combinacoes: Número máximo de combinações a gerar
            
        Returns:
            Lista de combinações avaliadas e classificadas
        """
        self.logger.info("🎲 Gerando combinações otimizadas...")
        
        try:
            # Gerar combinações baseadas nos parâmetros previstos
            combinacoes = self.gerador.gerar_combinacoes_por_parametros(predicoes)
            
            # Limitar número de combinações se necessário
            if len(combinacoes) > max_combinacoes:
                combinacoes = combinacoes[:max_combinacoes]
                self.logger.info(f"⚠️ Limitado a {max_combinacoes} combinações")
            
            # Avaliar e classificar combinações
            avaliacoes = self.gerador.avaliar_combinacoes(combinacoes, predicoes)
            
            # Adicionar probabilidades estimadas
            for i, avaliacao in enumerate(avaliacoes):
                # Probabilidade baseada no score e posição
                prob_base = avaliacao['score'] / 50.0  # Normalizar score
                prob_posicao = (len(avaliacoes) - i) / len(avaliacoes)  # Bonus por posição
                avaliacao['probabilidade_estimada'] = (prob_base + prob_posicao) / 2
            
            self.logger.info(f"🎯 {len(avaliacoes)} combinações geradas e avaliadas")
            
            return avaliacoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar combinações: {e}")
            return []
    
    def executar_predicao_completa(self, numero_concurso: Optional[int] = None, max_combinacoes: int = 300) -> Dict:
        """
        Executar processo completo de predição
        
        Args:
            numero_concurso: Número do concurso a prever (opcional)
            max_combinacoes: Máximo de combinações a gerar
            
        Returns:
            Dicionário completo com predições e combinações
        """
        self.logger.info("🚀 Executando predição completa...")
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'concurso': numero_concurso,
            'predicoes': {},
            'combinacoes': [],
            'estatisticas': {},
            'sucesso': False
        }
        
        try:
            # 1. Gerar predições dos parâmetros
            predicoes = self.gerar_predicao_proximo_concurso(numero_concurso)
            
            if not predicoes:
                self.logger.error("❌ Falha ao gerar predições")
                return resultado
            
            resultado['predicoes'] = predicoes
            
            # 2. Gerar combinações otimizadas
            combinacoes = self.gerar_combinacoes_otimizadas(predicoes, max_combinacoes)
            
            if not combinacoes:
                self.logger.error("❌ Falha ao gerar combinações")
                return resultado
            
            resultado['combinacoes'] = combinacoes
            
            # 3. Calcular estatísticas
            estatisticas = {
                'total_combinacoes': len(combinacoes),
                'reducao_percentual': (1 - len(combinacoes) / 3268760) * 100,
                'fator_reducao': 3268760 // len(combinacoes) if len(combinacoes) > 0 else 0,
                'confianca_media': predicoes.get('confianca_geral', 0),
                'score_medio': np.mean([c['score'] for c in combinacoes]),
                'top_10_scores': [c['score'] for c in combinacoes[:10]]
            }
            
            resultado['estatisticas'] = estatisticas
            resultado['sucesso'] = True
            
            # 4. Exibir resumo
            self._exibir_resumo_predicao(resultado)
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Erro na predição completa: {e}")
            resultado['erro'] = str(e)
            return resultado
    
    def _preparar_features_predicao(self, dados_recentes: List, parametro: str) -> np.array:
        """Preparar features para predição de um parâmetro específico"""
        features = []
        
        # Usar últimos 10 valores do parâmetro como features básicas
        valores_param = []
        for d in dados_recentes[-10:]:
            if hasattr(d, parametro):
                valores_param.append(getattr(d, parametro))
            else:
                valores_param.append(0)
        
        features.extend(valores_param)
        
        # Adicionar features estatísticas
        if valores_param:
            features.extend([
                np.mean(valores_param),
                np.std(valores_param),
                np.max(valores_param),
                np.min(valores_param)
            ])
        
        # Padding para garantir tamanho fixo
        while len(features) < 20:
            features.append(0)
        
        return np.array(features[:20])
    
    def _ajustar_predicoes_consistencia(self, predicoes: Dict) -> Dict:
        """Ajustar predições para garantir consistência matemática"""
        # Garantir que maior + menor + igual = 15
        if all(k in predicoes for k in ['maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo']):
            total = predicoes['maior_que_ultimo'] + predicoes['menor_que_ultimo'] + predicoes['igual_ao_ultimo']
            
            if total != 15:
                # Ajustar proporcionalmente
                fator = 15 / total if total > 0 else 1
                predicoes['maior_que_ultimo'] = round(predicoes['maior_que_ultimo'] * fator)
                predicoes['menor_que_ultimo'] = round(predicoes['menor_que_ultimo'] * fator)
                predicoes['igual_ao_ultimo'] = 15 - predicoes['maior_que_ultimo'] - predicoes['menor_que_ultimo']
        
        # Garantir ranges válidos
        predicoes['n1'] = max(1, min(25, predicoes.get('n1', 1)))
        predicoes['n15'] = max(1, min(25, predicoes.get('n15', 25)))
        predicoes['faixa_6a25'] = max(0, min(15, predicoes.get('faixa_6a25', 12)))
        predicoes['faixa_6a20'] = max(0, min(15, predicoes.get('faixa_6a20', 9)))
        predicoes['acertos_combinacao_fixa'] = max(0, min(15, predicoes.get('acertos_combinacao_fixa', 9)))
        
        return predicoes
    
    def _salvar_modelos(self):
        """Salvar modelos treinados"""
        try:
            import pickle
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"modelos_lotoscope_{timestamp}.pkl"
            
            with open(filename, 'wb') as f:
                pickle.dump(self.modelos_treinados, f)
            
            self.logger.info(f"💾 Modelos salvos em: {filename}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao salvar modelos: {e}")
    
    def _carregar_modelos(self):
        """Carregar modelos treinados"""
        try:
            import pickle
            import glob
            
            # Encontrar arquivo mais recente
            arquivos = glob.glob("modelos_lotoscope_*.pkl")
            if arquivos:
                arquivo_mais_recente = max(arquivos, key=os.path.getctime)
                
                with open(arquivo_mais_recente, 'rb') as f:
                    self.modelos_treinados = pickle.load(f)
                
                self.logger.info(f"📂 Modelos carregados de: {arquivo_mais_recente}")
                return True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao carregar modelos: {e}")
        
        return False
    
    def _exibir_resumo_predicao(self, resultado: Dict):
        """Exibir resumo da predição"""
        print("\n" + "="*60)
        print("🎯 LOTOSCOPE - RESUMO DA PREDIÇÃO")
        print("="*60)
        
        predicoes = resultado['predicoes']
        estatisticas = resultado['estatisticas']
        
        print(f"📅 Data/Hora: {resultado['timestamp']}")
        print(f"🎲 Concurso previsto: {resultado['concurso']}")
        print(f"📊 Confiança geral: {predicoes.get('confianca_geral', 0):.1%}")
        
        print(f"\n🎯 PARÂMETROS PREVISTOS:")
        print(f"   N1 (menor número): {predicoes.get('n1', 0)}")
        print(f"   N15 (maior número): {predicoes.get('n15', 0)}")
        print(f"   Maior que último: {predicoes.get('maior_que_ultimo', 0)}")
        print(f"   Menor que último: {predicoes.get('menor_que_ultimo', 0)}")
        print(f"   Igual ao último: {predicoes.get('igual_ao_ultimo', 0)}")
        print(f"   Números 6-25: {predicoes.get('faixa_6a25', 0)}")
        print(f"   Números 6-20: {predicoes.get('faixa_6a20', 0)}")
        print(f"   Acertos comb. fixa: {predicoes.get('acertos_combinacao_fixa', 0)}")
        
        print(f"\n📈 ESTATÍSTICAS DA REDUÇÃO:")
        print(f"   Combinações totais possíveis: 3.268.760")
        print(f"   Combinações geradas: {estatisticas['total_combinacoes']:,}")
        print(f"   Redução: {estatisticas['reducao_percentual']:.4f}%")
        print(f"   Fator de redução: {estatisticas['fator_reducao']:,}x")
        
        print(f"\n🏆 TOP 5 COMBINAÇÕES:")
        for i, combo in enumerate(resultado['combinacoes'][:5]):
            print(f"   {i+1}. {combo['combinacao']} (Score: {combo['score']:.1f})")
        
        print("="*60)

def executar_sistema_completo():
    """Função principal para executar o sistema completo"""
    print("🎯 LOTOSCOPE INTEGRADO - SISTEMA DE PRODUÇÃO")
    print("=" * 50)
    
    # Inicializar sistema
    lotoscope = LotoScopeIntegrado()
    
    if not lotoscope.inicializar_componentes():
        print("❌ Falha na inicialização do sistema")
        return
    
    # Menu de opções
    while True:
        print(f"\n📋 OPÇÕES DISPONÍVEIS:")
        print("1. Executar treinamento completo")
        print("2. Gerar predição para próximo concurso")
        print("3. Executar predição completa (recomendado)")
        print("4. Sair")
        
        opcao = input("\n🎯 Escolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            print("\n🎓 Iniciando treinamento completo...")
            sucesso = lotoscope.executar_treinamento_completo()
            if sucesso:
                print("✅ Treinamento concluído com sucesso!")
            else:
                print("❌ Falha no treinamento")
                
        elif opcao == "2":
            print("\n🔮 Gerando predição...")
            predicoes = lotoscope.gerar_predicao_proximo_concurso()
            if predicoes:
                print("✅ Predição gerada:")
                for param, valor in predicoes.items():
                    if param not in ['timestamp', 'concurso_previsto', 'confianca_geral']:
                        print(f"   {param}: {valor}")
            else:
                print("❌ Falha na geração da predição")
                
        elif opcao == "3":
            print("\n🚀 Executando predição completa...")
            resultado = lotoscope.executar_predicao_completa()
            if resultado['sucesso']:
                print("✅ Predição completa executada com sucesso!")
            else:
                print("❌ Falha na predição completa")
                
        elif opcao == "4":
            print("👋 Encerrando LotoScope...")
            break
            
        else:
            print("⚠️ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    executar_sistema_completo()