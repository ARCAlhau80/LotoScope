#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 ANALISADOR HÍBRIDO V3.0: LÓGICA ADAPTATIVA INTELIGENTE
=========================================================
Versão com lógica adaptativa que escolhe entre:
1. Seguir predição neural (quando próxima)
2. Aplicar reversão neural (quando extrema)
3. Manter metadados puros (quando neural inconclusa)

Baseado na correção: SomaTotal real = 218 (não 318)

Autor: AR CALHAU
Data: 18/09/2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'analisadores'))
sys.path.insert(0, str(_BASE_DIR / 'sistemas'))

from analisador_metadados_preditivos import AnalisadorMetadadosPreditivos
from sistema_neural_network_v7 import SistemaNeuralNetworkV7

class AnalisadorHibridoV3:
    """Analisador híbrido V3.0 com lógica adaptativa inteligente"""
    
    def __init__(self):
        self.analisador_metadados = AnalisadorMetadadosPreditivos()
        self.sistema_neural = SistemaNeuralNetworkV7()
        self.predicoes_neural = None
        self.clausulas_hibridas = []
        self.justificativas_hibridas = []
        self.estrategia_aplicada = ""
        
    def executar_analise_hibrida_v3(self):
        """Executa análise híbrida V3.0 com lógica adaptativa"""
        try:
            print("🔬 ANALISADOR HÍBRIDO V3.0: LÓGICA ADAPTATIVA INTELIGENTE")
            print("="*70)
            print("🧠 ESTRATÉGIAS ADAPTATIVAS:")
            print("   1. NEURAL PRÓXIMA → Seguir predição neural")
            print("   2. NEURAL EXTREMA → Aplicar reversão")
            print("   3. NEURAL NEUTRA → Manter metadados puros")
            print("💡 Baseado na correção: SomaTotal real = 218")
            print("="*70)
            
            # 1. Obter predições da rede neural
            if not self._obter_predicoes_neural():
                return False
                
            # 2. Carregar dados de metadados
            if not self.analisador_metadados.carregar_dados_metadados():
                return False
                
            # 3. Analisar situação atual
            ultimo_concurso = self.analisador_metadados.analisar_situacao_atual()
            
            # 4. Determinar estratégia adaptativa
            self._determinar_estrategia_adaptativa()
            
            # 5. Gerar cláusulas híbridas V3.0 com lógica adaptativa
            self._gerar_clausulas_hibridas_v3(ultimo_concurso)
            
            # 6. Mostrar resultados
            self._mostrar_resultados_hibridos_v3(ultimo_concurso)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise híbrida V3.0: {e}")
            return False
    
    def _obter_predicoes_neural(self):
        """Obtém predições da Rede Neural V7.0"""
        try:
            print("🧠 Executando Sistema Neural V7.0...")
            resultado_neural = self.sistema_neural.executar_sistema_completo()
            
            if not resultado_neural:
                print("❌ Sistema neural não retornou predições")
                return False
            
            # Extrair números preditos
            numeros_preditos = resultado_neural.get('numeros', [])
            
            if not numeros_preditos or len(numeros_preditos) == 0:
                print("❌ Nenhuma predição neural gerada")
                return False
            
            # Analisar distribuição dos números preditos
            self.predicoes_neural = self._analisar_distribuicao_neural(numeros_preditos)
            
            print(f"✅ Predições neurais obtidas:")
            print(f"   📊 Distribuição: {self.predicoes_neural['distribuicao']}")
            print(f"   🎯 Soma: {self.predicoes_neural['soma_prevista']}")
            print(f"   📈 Altos: {self.predicoes_neural['qtde_altos']}")
            print(f"   📉 Baixos: {self.predicoes_neural['qtde_baixos']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao obter predições neurais: {e}")
            return False
    
    def _analisar_distribuicao_neural(self, numeros_preditos):
        """Analisa a distribuição dos números preditos pela rede neural"""
        numeros = sorted(numeros_preditos)
        
        # Análise de distribuição
        baixos = [n for n in numeros if n <= 12]  # 1-12
        medios = [n for n in numeros if 13 <= n <= 19]  # 13-19  
        altos = [n for n in numeros if n >= 20]  # 20-25
        
        # Quintis
        quintil1 = [n for n in numeros if 1 <= n <= 5]
        quintil2 = [n for n in numeros if 6 <= n <= 10] 
        quintil3 = [n for n in numeros if 11 <= n <= 15]
        quintil4 = [n for n in numeros if 16 <= n <= 20]
        quintil5 = [n for n in numeros if 21 <= n <= 25]
        
        soma_total = sum(numeros)
        
        distribuicao = "EQUILIBRADA"
        if len(altos) > len(baixos) + 2:
            distribuicao = "ALTA"
        elif len(baixos) > len(altos) + 2:
            distribuicao = "BAIXA"
        
        return {
            'numeros': numeros,
            'distribuicao': distribuicao,
            'soma_prevista': soma_total,
            'qtde_baixos': len(baixos),
            'qtde_medios': len(medios), 
            'qtde_altos': len(altos),
            'quintil1': len(quintil1),
            'quintil2': len(quintil2),
            'quintil3': len(quintil3), 
            'quintil4': len(quintil4),
            'quintil5': len(quintil5),
            'faixa_baixa': len(baixos),
            'faixa_media': len(medios),
            'faixa_alta': len(altos)
        }
    
    def _determinar_estrategia_adaptativa(self):
        """Determina a estratégia adaptativa baseada na predição neural"""
        
        soma_neural = self.predicoes_neural['soma_prevista']
        
        # Faixas de referência histórica
        soma_media_historica = 195  # Aproximada
        margem_normal = 30
        
        print(f"\n🤔 DETERMINANDO ESTRATÉGIA ADAPTATIVA:")
        print(f"   🎯 Soma Neural: {soma_neural}")
        print(f"   📊 Soma Média Histórica: {soma_media_historica}")
        
        # ESTRATÉGIA 1: NEURAL PRÓXIMA (dentro da margem normal)
        if abs(soma_neural - soma_media_historica) <= margem_normal:
            self.estrategia_aplicada = "NEURAL_PROXIMA"
            print(f"   ✅ ESTRATÉGIA: SEGUIR NEURAL (diferença {abs(soma_neural - soma_media_historica)} ≤ {margem_normal})")
            
        # ESTRATÉGIA 2: NEURAL MUITO BAIXA (reversão para cima)
        elif soma_neural < (soma_media_historica - margem_normal):
            self.estrategia_aplicada = "REVERSAO_PARA_CIMA"
            print(f"   🔄 ESTRATÉGIA: REVERSÃO PARA CIMA (neural muito baixa: {soma_neural})")
            
        # ESTRATÉGIA 3: NEURAL MUITO ALTA (reversão para baixo)
        elif soma_neural > (soma_media_historica + margem_normal):
            self.estrategia_aplicada = "REVERSAO_PARA_BAIXO"
            print(f"   🔄 ESTRATÉGIA: REVERSÃO PARA BAIXO (neural muito alta: {soma_neural})")
            
        else:
            # ESTRATÉGIA 4: MANTER METADADOS (quando incerto)
            self.estrategia_aplicada = "METADADOS_PUROS"
            print(f"   📊 ESTRATÉGIA: MANTER METADADOS PUROS (neural incerta)")
    
    def _gerar_clausulas_hibridas_v3(self, ultimo_concurso):
        """Gera cláusulas híbridas V3.0 com lógica adaptativa"""
        
        # Obter cláusulas base dos metadados
        clausulas_base, justificativas_base = self.analisador_metadados.gerar_clausulas_where_preditivas()
        
        self.clausulas_hibridas = []
        self.justificativas_hibridas = []
        
        for i, (clausula, justificativa) in enumerate(zip(clausulas_base, justificativas_base)):
            
            campo = clausula.split()[0]
            clausula_ajustada = clausula
            justificativa_ajustada = justificativa
            
            # Aplicar estratégia adaptativa
            if campo == "SomaTotal":
                
                if self.estrategia_aplicada == "NEURAL_PROXIMA":
                    # Seguir predição neural (com margem)
                    soma_neural = self.predicoes_neural['soma_prevista']
                    margem = 15
                    clausula_ajustada = f"SomaTotal BETWEEN {soma_neural - margem} AND {soma_neural + margem}"
                    justificativa_ajustada = f"SomaTotal: SEGUIR NEURAL (soma neural {soma_neural} próxima da média)"
                    
                elif self.estrategia_aplicada == "REVERSAO_PARA_CIMA":
                    # Neural muito baixa, ajustar para cima moderadamente
                    soma_base = self.predicoes_neural['soma_prevista']
                    ajuste = 30  # Ajuste moderado (não extremo como V2.0)
                    soma_ajustada = soma_base + ajuste
                    margem = 15
                    clausula_ajustada = f"SomaTotal BETWEEN {soma_ajustada - margem} AND {soma_ajustada + margem}"
                    justificativa_ajustada = f"SomaTotal: REVERSÃO MODERADA (neural {soma_base} baixa → ajuste {soma_ajustada})"
                    
                elif self.estrategia_aplicada == "REVERSAO_PARA_BAIXO":
                    # Neural muito alta, ajustar para baixo moderadamente
                    soma_base = self.predicoes_neural['soma_prevista']
                    ajuste = 30  # Ajuste moderado
                    soma_ajustada = soma_base - ajuste
                    margem = 15
                    clausula_ajustada = f"SomaTotal BETWEEN {soma_ajustada - margem} AND {soma_ajustada + margem}"
                    justificativa_ajustada = f"SomaTotal: REVERSÃO MODERADA (neural {soma_base} alta → ajuste {soma_ajustada})"
                    
                # Se METADADOS_PUROS, mantém clausula original
                
            elif campo == "Quintil5":
                
                if self.estrategia_aplicada in ["NEURAL_PROXIMA", "REVERSAO_PARA_CIMA"]:
                    # Ajustar baseado na predição/correção neural
                    qtde_neural = self.predicoes_neural['quintil5']
                    if self.estrategia_aplicada == "REVERSAO_PARA_CIMA":
                        qtde_ajustada = min(5, qtde_neural + 2)
                    else:
                        qtde_ajustada = qtde_neural
                    
                    clausula_ajustada = f"Quintil5 BETWEEN {max(1, qtde_ajustada-1)} AND {min(5, qtde_ajustada+1)}"
                    justificativa_ajustada = f"Quintil5: {self.estrategia_aplicada} (neural {qtde_neural} → ajuste {qtde_ajustada})"
                    
            elif campo in ["Faixa_Alta", "Faixa_Baixa", "Faixa_Media"]:
                
                if self.estrategia_aplicada != "METADADOS_PUROS":
                    # Aplicar ajustes baseados na estratégia
                    if campo == "Faixa_Alta":
                        qtde_neural = self.predicoes_neural['qtde_altos']
                        if self.estrategia_aplicada == "REVERSAO_PARA_CIMA":
                            qtde_ajustada = min(7, qtde_neural + 2)
                        elif self.estrategia_aplicada == "REVERSAO_PARA_BAIXO":
                            qtde_ajustada = max(1, qtde_neural - 1)
                        else:
                            qtde_ajustada = qtde_neural
                            
                        clausula_ajustada = f"Faixa_Alta BETWEEN {max(1, qtde_ajustada-1)} AND {min(7, qtde_ajustada+1)}"
                        justificativa_ajustada = f"Faixa_Alta: {self.estrategia_aplicada} (neural {qtde_neural} → {qtde_ajustada})"
            
            self.clausulas_hibridas.append(clausula_ajustada)
            self.justificativas_hibridas.append(justificativa_ajustada)
    
    def _mostrar_resultados_hibridos_v3(self, ultimo_concurso):
        """Mostra os resultados da análise híbrida V3.0"""
        
        print("\n" + "="*70)
        print("🔮 RESULTADOS DA ANÁLISE HÍBRIDA V3.0")
        print("="*70)
        
        print("🧠 PREDIÇÕES DA REDE NEURAL V7.0:")
        print(f"   📊 Distribuição: {self.predicoes_neural['distribuicao']}")
        print(f"   🎯 Soma: {self.predicoes_neural['soma_prevista']}")
        print(f"   🔄 Estratégia Aplicada: {self.estrategia_aplicada}")
        
        print(f"\n💡 LÓGICA V3.0 APLICADA:")
        if self.estrategia_aplicada == "NEURAL_PROXIMA":
            print("   ✅ Neural próxima da média → SEGUIR predições neurais")
        elif self.estrategia_aplicada == "REVERSAO_PARA_CIMA":
            print("   🔄 Neural muito baixa → REVERSÃO MODERADA para cima")
        elif self.estrategia_aplicada == "REVERSAO_PARA_BAIXO":
            print("   🔄 Neural muito alta → REVERSÃO MODERADA para baixo")
        else:
            print("   📊 Neural incerta → MANTER metadados puros")
        
        print(f"\n📊 CLÁUSULAS HÍBRIDAS V3.0 GERADAS ({len(self.clausulas_hibridas)} condições):")
        print("="*50)
        
        # Destacar estratégias aplicadas
        for i, (clausula, justificativa) in enumerate(zip(self.clausulas_hibridas, self.justificativas_hibridas), 1):
            if self.estrategia_aplicada in justificativa:
                print(f"🎯 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
            else:
                print(f"📊 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
        
        # Query final
        query_hibrida = "SELECT * FROM Resultados_INT WHERE " + " AND ".join(self.clausulas_hibridas)
        
        print(f"\n🔍 QUERY HÍBRIDA V3.0 COMPLETA:")
        print("="*50)
        print(query_hibrida)
        
        # Validação
        try:
            resultados_teste = self.analisador_metadados.db_config.execute_query(query_hibrida)
            print(f"\n🧪 VALIDAÇÃO V3.0:")
            print(f"   ✅ {len(resultados_teste)} concursos históricos atendem às condições")
            print(f"   📊 Representa {len(resultados_teste)/3487*100:.1f}% do histórico")
            
        except Exception as e:
            print(f"   ⚠️ Erro na validação: {e}")
    
    def obter_query_hibrida_v3(self):
        """Retorna a query híbrida V3.0 gerada"""
        if self.clausulas_hibridas:
            return "SELECT * FROM Resultados_INT WHERE " + " AND ".join(self.clausulas_hibridas)
        return None
    
    def obter_clausulas_e_justificativas_v3(self):
        """Retorna cláusulas e justificativas V3.0"""
        return self.clausulas_hibridas, self.justificativas_hibridas

if __name__ == "__main__":
    analisador = AnalisadorHibridoV3()
    sucesso = analisador.executar_analise_hibrida_v3()
    
    if sucesso:
        print("\n✅ ANÁLISE HÍBRIDA V3.0 CONCLUÍDA!")
        print("🧠 Lógica adaptativa inteligente aplicada!")
    else:
        print("\n❌ FALHA NA ANÁLISE HÍBRIDA V3.0")