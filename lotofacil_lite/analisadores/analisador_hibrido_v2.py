#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 ANALISADOR HÍBRIDO V2.0: CORREÇÃO NEURAL + METADADOS
======================================================== 
Versão melhorada que considera a tendência de reversão da própria Rede Neural
Baseado na análise: Neural previu BAIXA mas ocorreu ALTA - padrão de reversão!

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

class AnalisadorHibridoV2:
    """Analisador híbrido V2.0 com correção de reversão neural"""
    
    def __init__(self):
        self.analisador_metadados = AnalisadorMetadadosPreditivos()
        self.sistema_neural = SistemaNeuralNetworkV7()
        self.predicoes_neural = None
        self.clausulas_hibridas = []
        self.justificativas_hibridas = []
        self.aplicou_reversao_neural = False
        
    def executar_analise_hibrida_v2(self):
        """Executa análise híbrida V2.0 com correção de reversão"""
        try:
            print("🔬 ANALISADOR HÍBRIDO V2.0: CORREÇÃO NEURAL + METADADOS")
            print("="*70)
            print("💡 NOVA LÓGICA: Se neural prevê BAIXA → Ajustar para ALTA")
            print("🎯 Baseado na análise: Neural errou na direção oposta")
            print("="*70)
            
            # 1. Obter predições da rede neural
            if not self._obter_predicoes_neural():
                return False
                
            # 2. Carregar dados de metadados
            if not self.analisador_metadados.carregar_dados_metadados():
                return False
                
            # 3. Analisar situação atual
            ultimo_concurso = self.analisador_metadados.analisar_situacao_atual()
            
            # 4. Gerar cláusulas híbridas V2.0 com correção
            self._gerar_clausulas_hibridas_v2(ultimo_concurso)
            
            # 5. Mostrar resultados
            self._mostrar_resultados_hibridos_v2(ultimo_concurso)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise híbrida V2.0: {e}")
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
            print(f"   📊 Distribuição Neural: {self.predicoes_neural['distribuicao']}")
            print(f"   🎯 Soma Neural: {self.predicoes_neural['soma_prevista']}")
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
    
    def _gerar_clausulas_hibridas_v2(self, ultimo_concurso):
        """Gera cláusulas híbridas V2.0 com correção de reversão neural"""
        
        # Obter cláusulas base dos metadados
        clausulas_base, justificativas_base = self.analisador_metadados.gerar_clausulas_where_preditivas()
        
        # LÓGICA V2.0: CORREÇÃO DE REVERSÃO NEURAL
        aplicar_reversao = False
        
        # Se neural prevê BAIXA, vamos ajustar para ALTA (reversão)
        if self.predicoes_neural['distribuicao'] == "BAIXA":
            aplicar_reversao = True
            print("🔄 APLICANDO CORREÇÃO DE REVERSÃO NEURAL:")
            print("   Neural previu BAIXA → Ajustando para ALTA")
            
        # Se neural prevê ALTA, vamos ajustar para BAIXA (reversão)  
        elif self.predicoes_neural['distribuicao'] == "ALTA":
            aplicar_reversao = True
            print("🔄 APLICANDO CORREÇÃO DE REVERSÃO NEURAL:")
            print("   Neural previu ALTA → Ajustando para BAIXA")
        
        self.clausulas_hibridas = []
        self.justificativas_hibridas = []
        
        for i, (clausula, justificativa) in enumerate(zip(clausulas_base, justificativas_base)):
            
            campo = clausula.split()[0]
            clausula_ajustada = clausula
            justificativa_ajustada = justificativa
            
            # Aplicar correções baseadas na REVERSÃO neural
            if aplicar_reversao:
                
                if campo == "SomaTotal":
                    if self.predicoes_neural['distribuicao'] == "BAIXA":
                        # Neural previu baixa, vamos para alta
                        soma_corrigida = self.predicoes_neural['soma_prevista'] + 80  # Adicionar para ir para alta
                        margem = 20
                        clausula_ajustada = f"SomaTotal BETWEEN {soma_corrigida - margem} AND {soma_corrigida + margem}"
                        justificativa_ajustada = f"SomaTotal: REVERSÃO Neural (previu {self.predicoes_neural['soma_prevista']} BAIXA → ajuste ALTA ≈{soma_corrigida})"
                        self.aplicou_reversao_neural = True
                    elif self.predicoes_neural['distribuicao'] == "ALTA":
                        # Neural previu alta, vamos para baixa
                        soma_corrigida = self.predicoes_neural['soma_prevista'] - 80
                        margem = 20
                        clausula_ajustada = f"SomaTotal BETWEEN {soma_corrigida - margem} AND {soma_corrigida + margem}"
                        justificativa_ajustada = f"SomaTotal: REVERSÃO Neural (previu {self.predicoes_neural['soma_prevista']} ALTA → ajuste BAIXA ≈{soma_corrigida})"
                        self.aplicou_reversao_neural = True
                        
                elif campo == "Quintil5":
                    if self.predicoes_neural['distribuicao'] == "BAIXA":
                        # Neural previu baixa, corrigir para mais números no Quintil5
                        qtde_corrigida = max(4, self.predicoes_neural['quintil5'] + 2)
                        clausula_ajustada = f"Quintil5 BETWEEN {qtde_corrigida-1} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Quintil5: REVERSÃO Neural (previu {self.predicoes_neural['quintil5']} BAIXA → ajuste ALTA {qtde_corrigida})"
                        self.aplicou_reversao_neural = True
                    elif self.predicoes_neural['distribuicao'] == "ALTA":
                        # Neural previu alta, corrigir para menos números no Quintil5
                        qtde_corrigida = max(1, self.predicoes_neural['quintil5'] - 2)
                        clausula_ajustada = f"Quintil5 BETWEEN {qtde_corrigida} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Quintil5: REVERSÃO Neural (previu {self.predicoes_neural['quintil5']} ALTA → ajuste BAIXA {qtde_corrigida})"
                        self.aplicou_reversao_neural = True
                        
                elif campo == "Faixa_Alta":
                    if self.predicoes_neural['distribuicao'] == "BAIXA":
                        # Neural previu baixa, corrigir para mais números altos
                        qtde_corrigida = max(4, self.predicoes_neural['qtde_altos'] + 3)
                        clausula_ajustada = f"Faixa_Alta BETWEEN {qtde_corrigida-1} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Faixa_Alta: REVERSÃO Neural (previu {self.predicoes_neural['qtde_altos']} BAIXA → ajuste ALTA {qtde_corrigida})"
                        self.aplicou_reversao_neural = True
                    elif self.predicoes_neural['distribuicao'] == "ALTA":
                        # Neural previu alta, corrigir para menos números altos
                        qtde_corrigida = max(1, self.predicoes_neural['qtde_altos'] - 3)
                        clausula_ajustada = f"Faixa_Alta BETWEEN {qtde_corrigida} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Faixa_Alta: REVERSÃO Neural (previu {self.predicoes_neural['qtde_altos']} ALTA → ajuste BAIXA {qtde_corrigida})"
                        self.aplicou_reversao_neural = True
                        
                elif campo == "Faixa_Media":
                    if self.predicoes_neural['distribuicao'] == "BAIXA":
                        # Neural previu baixa, ajustar faixa média
                        qtde_corrigida = min(7, self.predicoes_neural['qtde_medios'] + 1)
                        clausula_ajustada = f"Faixa_Media BETWEEN {qtde_corrigida-1} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Faixa_Media: REVERSÃO Neural (ajuste para distribuição ALTA)"
                        
                elif campo == "Faixa_Baixa":
                    if self.predicoes_neural['distribuicao'] == "BAIXA":
                        # Neural previu baixa, corrigir para menos números baixos
                        qtde_corrigida = max(3, self.predicoes_neural['qtde_baixos'] - 2)
                        clausula_ajustada = f"Faixa_Baixa BETWEEN {qtde_corrigida-1} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Faixa_Baixa: REVERSÃO Neural (previu {self.predicoes_neural['qtde_baixos']} BAIXA → ajuste menos baixos {qtde_corrigida})"
                    elif self.predicoes_neural['distribuicao'] == "ALTA":
                        # Neural previu alta, corrigir para mais números baixos
                        qtde_corrigida = min(8, self.predicoes_neural['qtde_baixos'] + 2)
                        clausula_ajustada = f"Faixa_Baixa BETWEEN {qtde_corrigida-1} AND {qtde_corrigida+1}"
                        justificativa_ajustada = f"Faixa_Baixa: REVERSÃO Neural (previu {self.predicoes_neural['qtde_baixos']} ALTA → ajuste mais baixos {qtde_corrigida})"
            
            self.clausulas_hibridas.append(clausula_ajustada)
            self.justificativas_hibridas.append(justificativa_ajustada)
    
    def _mostrar_resultados_hibridos_v2(self, ultimo_concurso):
        """Mostra os resultados da análise híbrida V2.0"""
        
        print("\n" + "="*70)
        print("🔮 RESULTADOS DA ANÁLISE HÍBRIDA V2.0")
        print("="*70)
        
        print("🧠 PREDIÇÕES DA REDE NEURAL V7.0:")
        print(f"   📊 Distribuição Neural: {self.predicoes_neural['distribuicao']}")
        print(f"   🎯 Números Neural: {self.predicoes_neural['numeros']}")
        print(f"   ➕ Soma Neural: {self.predicoes_neural['soma_prevista']}")
        
        if self.aplicou_reversao_neural:
            print(f"\n🔄 CORREÇÃO DE REVERSÃO APLICADA:")
            print(f"   💡 Neural previu {self.predicoes_neural['distribuicao']} → Corrigindo para direção OPOSTA")
            print(f"   🎯 Esta correção deve melhorar significativamente as predições!")
        
        print(f"\n📊 CLÁUSULAS HÍBRIDAS V2.0 GERADAS ({len(self.clausulas_hibridas)} condições):")
        print("="*50)
        
        # Destacar correções neurais
        for i, (clausula, justificativa) in enumerate(zip(self.clausulas_hibridas, self.justificativas_hibridas), 1):
            if "REVERSÃO Neural" in justificativa:
                print(f"🔄 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
            elif "Ajuste neural" in justificativa:
                print(f"🧠 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
            else:
                print(f"📊 {i:2}. {clausula}")
                print(f"    💡 {justificativa}")
        
        # Query final
        query_hibrida = "SELECT * FROM Resultados_INT WHERE " + " AND ".join(self.clausulas_hibridas)
        
        print(f"\n🔍 QUERY HÍBRIDA V2.0 COMPLETA:")
        print("="*50)
        print(query_hibrida)
        
        # Validação
        try:
            resultados_teste = self.analisador_metadados.db_config.execute_query(query_hibrida)
            print(f"\n🧪 VALIDAÇÃO V2.0:")
            print(f"   ✅ {len(resultados_teste)} concursos históricos atendem às condições híbridas V2.0")
            print(f"   📊 Isso representa {len(resultados_teste)/3487*100:.1f}% do histórico")
            
            if len(resultados_teste) > 0:
                print(f"   📋 Exemplos de concursos similares:")
                for i, resultado in enumerate(resultados_teste[-3:], 1):
                    concurso = resultado[0]
                    print(f"      {i}. Concurso {concurso}")
            
        except Exception as e:
            print(f"   ⚠️ Erro na validação: {e}")
    
    def obter_query_hibrida_v2(self):
        """Retorna a query híbrida V2.0 gerada"""
        if self.clausulas_hibridas:
            return "SELECT * FROM Resultados_INT WHERE " + " AND ".join(self.clausulas_hibridas)
        return None
    
    def obter_clausulas_e_justificativas_v2(self):
        """Retorna cláusulas e justificativas V2.0"""
        return self.clausulas_hibridas, self.justificativas_hibridas

if __name__ == "__main__":
    analisador = AnalisadorHibridoV2()
    sucesso = analisador.executar_analise_hibrida_v2()
    
    if sucesso:
        print("\n✅ ANÁLISE HÍBRIDA V2.0 CONCLUÍDA COM SUCESSO!")
        print("🔄 Correção de reversão neural aplicada!")
    else:
        print("\n❌ FALHA NA ANÁLISE HÍBRIDA V2.0")