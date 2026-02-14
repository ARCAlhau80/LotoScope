#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 ANALISADOR HÍBRIDO: NEURAL V7.0 + METADADOS PREDITIVOS
==========================================================
Combina a análise de metadados com as predições da Rede Neural V7.0
Melhora significativamente a precisão das predições

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

class AnalisadorHibridoNeuralMetadados:
    """Analisador híbrido que combina Rede Neural V7.0 com análise de metadados"""
    
    def __init__(self):
        self.analisador_metadados = AnalisadorMetadadosPreditivos()
        self.sistema_neural = SistemaNeuralNetworkV7()
        self.predicoes_neural = None
        self.clausulas_hibridas = []
        self.justificativas_hibridas = []
        
    def executar_analise_hibrida_completa(self):
        """Executa análise completa combinando neural + metadados"""
        try:
            print("🔬 ANALISADOR HÍBRIDO: NEURAL V7.0 + METADADOS")
            print("="*60)
            print("🧠 Fase 1: Carregando predições da Rede Neural V7.0...")
            
            # 1. Obter predições da rede neural
            if not self._obter_predicoes_neural():
                return False
                
            print("📊 Fase 2: Analisando metadados históricos...")
            
            # 2. Carregar dados de metadados
            if not self.analisador_metadados.carregar_dados_metadados():
                return False
                
            # 3. Analisar situação atual
            ultimo_concurso = self.analisador_metadados.analisar_situacao_atual()
            
            print("🔀 Fase 3: Integrando predições neurais com metadados...")
            
            # 4. Gerar cláusulas híbridas
            self._gerar_clausulas_hibridas(ultimo_concurso)
            
            # 5. Mostrar resultados
            self._mostrar_resultados_hibridos(ultimo_concurso)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise híbrida: {e}")
            return False
    
    def _obter_predicoes_neural(self):
        """Obtém predições da Rede Neural V7.0"""
        try:
            # Executar sistema neural completo
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
            print(f"   🎯 Soma prevista: {self.predicoes_neural['soma_prevista']}")
            print(f"   📈 Números altos: {self.predicoes_neural['qtde_altos']}")
            print(f"   📉 Números baixos: {self.predicoes_neural['qtde_baixos']}")
            
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
    
    def _gerar_clausulas_hibridas(self, ultimo_concurso):
        """Gera cláusulas WHERE híbridas combinando neural + metadados"""
        
        # Obter cláusulas base dos metadados
        clausulas_base, justificativas_base = self.analisador_metadados.gerar_clausulas_where_preditivas()
        
        # Ajustar com base nas predições neurais
        self.clausulas_hibridas = []
        self.justificativas_hibridas = []
        
        for i, (clausula, justificativa) in enumerate(zip(clausulas_base, justificativas_base)):
            
            campo = clausula.split()[0]
            clausula_ajustada = clausula
            justificativa_ajustada = justificativa
            
            # Ajustes baseados na predição neural
            if campo == "SomaTotal" and self.predicoes_neural['distribuicao'] == "ALTA":
                # Se neural prevê números altos, ajustar soma para cima
                soma_neural = self.predicoes_neural['soma_prevista']
                margem = 15
                clausula_ajustada = f"SomaTotal BETWEEN {soma_neural - margem} AND {soma_neural + margem}"
                justificativa_ajustada = f"SomaTotal: Ajuste neural - distribuição ALTA prevista (soma ≈{soma_neural})"
                
            elif campo == "Quintil5" and self.predicoes_neural['distribuicao'] == "ALTA":
                # Se neural prevê números altos, mais números no Quintil5
                qtde_q5 = self.predicoes_neural['quintil5']
                clausula_ajustada = f"Quintil5 BETWEEN {max(1, qtde_q5-1)} AND {qtde_q5+1}"
                justificativa_ajustada = f"Quintil5: Ajuste neural - {qtde_q5} números altos (21-25) previstos"
                
            elif campo == "Faixa_Alta" and self.predicoes_neural['distribuicao'] == "ALTA":
                # Ajustar faixa alta
                qtde_alta = self.predicoes_neural['qtde_altos']
                clausula_ajustada = f"Faixa_Alta BETWEEN {max(1, qtde_alta-1)} AND {qtde_alta+1}"
                justificativa_ajustada = f"Faixa_Alta: Ajuste neural - {qtde_alta} números altos (20-25) previstos"
                
            elif campo == "Faixa_Media" and self.predicoes_neural['distribuicao'] == "ALTA":
                # Ajustar faixa média baseado na predição
                qtde_media = self.predicoes_neural['qtde_medios']
                clausula_ajustada = f"Faixa_Media BETWEEN {max(1, qtde_media-1)} AND {qtde_media+1}"
                justificativa_ajustada = f"Faixa_Media: Ajuste neural - {qtde_media} números médios (13-19) previstos"
                
            elif campo == "Faixa_Baixa" and self.predicoes_neural['distribuicao'] == "ALTA":
                # Ajustar faixa baixa
                qtde_baixa = self.predicoes_neural['qtde_baixos']
                clausula_ajustada = f"Faixa_Baixa BETWEEN {max(1, qtde_baixa-1)} AND {qtde_baixa+1}"
                justificativa_ajustada = f"Faixa_Baixa: Ajuste neural - {qtde_baixa} números baixos (1-12) previstos"
            
            self.clausulas_hibridas.append(clausula_ajustada)
            self.justificativas_hibridas.append(justificativa_ajustada)
    
    def _mostrar_resultados_hibridos(self, ultimo_concurso):
        """Mostra os resultados da análise híbrida"""
        
        print("\n" + "="*70)
        print("🔮 RESULTADOS DA ANÁLISE HÍBRIDA")
        print("="*70)
        
        print("🧠 PREDIÇÕES DA REDE NEURAL V7.0:")
        print(f"   📊 Distribuição prevista: {self.predicoes_neural['distribuicao']}")
        print(f"   🎯 Números previstos: {self.predicoes_neural['numeros']}")
        print(f"   ➕ Soma prevista: {self.predicoes_neural['soma_prevista']}")
        print(f"   📈 Distribuição por faixas:")
        print(f"      • Baixa (1-12): {self.predicoes_neural['qtde_baixos']}")
        print(f"      • Média (13-19): {self.predicoes_neural['qtde_medios']}")
        print(f"      • Alta (20-25): {self.predicoes_neural['qtde_altos']}")
        
        print(f"\n📊 CLÁUSULAS HÍBRIDAS GERADAS ({len(self.clausulas_hibridas)} condições):")
        print("="*50)
        
        # Destacar ajustes neurais
        for i, (clausula, justificativa) in enumerate(zip(self.clausulas_hibridas, self.justificativas_hibridas), 1):
            if "Ajuste neural" in justificativa:
                print(f"🧠 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
            else:
                print(f"📊 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
        
        # Query final
        query_hibrida = "SELECT * FROM Resultados_INT WHERE " + " AND ".join(self.clausulas_hibridas)
        
        print(f"\n🔍 QUERY HÍBRIDA COMPLETA:")
        print("="*50)
        print(query_hibrida)
        
        # Validação
        try:
            resultados_teste = self.analisador_metadados.db_config.execute_query(query_hibrida)
            print(f"\n🧪 VALIDAÇÃO:")
            print(f"   ✅ {len(resultados_teste)} concursos históricos atendem às condições híbridas")
            print(f"   📊 Isso representa {len(resultados_teste)/3487*100:.1f}% do histórico")
            
        except Exception as e:
            print(f"   ⚠️ Erro na validação: {e}")
    
    def obter_query_hibrida(self):
        """Retorna a query híbrida gerada"""
        if self.clausulas_hibridas:
            return "SELECT * FROM Resultados_INT WHERE " + " AND ".join(self.clausulas_hibridas)
        return None
    
    def obter_clausulas_e_justificativas(self):
        """Retorna cláusulas e justificativas"""
        return self.clausulas_hibridas, self.justificativas_hibridas

if __name__ == "__main__":
    analisador = AnalisadorHibridoNeuralMetadados()
    sucesso = analisador.executar_analise_hibrida_completa()
    
    if sucesso:
        print("\n✅ ANÁLISE HÍBRIDA CONCLUÍDA COM SUCESSO!")
    else:
        print("\n❌ FALHA NA ANÁLISE HÍBRIDA")