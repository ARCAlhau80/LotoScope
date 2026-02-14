#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 ADAPTADOR UNIVERSAL PARA GERADORES COM INTELIGÊNCIA N12
==========================================================
Sistema para aplicar automaticamente a inteligência N12 
em TODOS os geradores existentes do sistema.

OBJETIVO:
- Analisar situação atual (último N12 e distribuição)
- Prever próxima distribuição baseada na teoria N12
- Filtrar combinações dos geradores com base na previsão
- Otimizar resultados considerando oscilação pós-equilíbrio

Autor: AR CALHAU
Data: 19/09/2025
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'sistemas'))

from sistema_inteligencia_n12 import SistemaInteligenciaDistribuicaoN12
import importlib
import random
from itertools import combinations

class AdaptadorUniversalN12:
    def __init__(self):
        self.sistema_n12 = SistemaInteligenciaDistribuicaoN12()
        self.geradores_disponiveis = [
            'gerador_eficaz',
            'gerador_estrategico_melhores', 
            'gerador_nucleo_fixo',
            'gerador_posicional',
            'gerador_nucleo_comportamental',
            'super_combinacao_ia',
            'piramide_invertida_dinamica'
        ]
        
    def inicializar_inteligencia(self):
        """Inicializa e analisa a situação atual"""
        print("🚀 INICIALIZANDO ADAPTADOR UNIVERSAL N12")
        print("="*60)
        
        # Analisar situação atual considerando o concurso 3490
        success = self.analisar_situacao_atualizada()
        
        if success:
            self.sistema_n12.prever_proxima_distribuicao()
            return True
        return False
        
    def analisar_situacao_atualizada(self):
        """Analisa buscando o último concurso real da tabela"""
        print("🔍 ANALISANDO SITUAÇÃO ATUAL (DADOS REAIS DA TABELA)...")
        
        # Buscar dados reais do último concurso da tabela
        ultimo_concurso_data = self.sistema_n12.buscar_ultimo_concurso()
        if not ultimo_concurso_data:
            print("❌ Erro ao buscar último concurso!")
            return
            
        ultimo_concurso = ultimo_concurso_data['concurso']
        numeros_ultimo = ultimo_concurso_data['numeros']
        n12_ultimo = ultimo_concurso_data['n12']
        
        # Calcular distribuição real
        baixos = len([n for n in numeros_ultimo if 1 <= n <= 8])
        medios = len([n for n in numeros_ultimo if 9 <= n <= 17])  
        altos = len([n for n in numeros_ultimo if 18 <= n <= 25])
        
        # Determinar tipo de distribuição
        if baixos == medios == altos:
            distribuicao = "EQUILIBRADA"
        elif max(baixos, medios, altos) - min(baixos, medios, altos) <= 1:
            distribuicao = "QUASE_EQUILIBRADA"
        elif baixos > medios and baixos > altos:
            distribuicao = "BAIXA"
        elif medios > baixos and medios > altos:
            distribuicao = "MEDIA"
        else:
            distribuicao = "ALTA"
        
        self.sistema_n12.distribuicao_atual = distribuicao
        # Atualizar também os dados básicos
        self.sistema_n12.ultimo_concurso = ultimo_concurso
        self.sistema_n12.ultimo_n12 = n12_ultimo
        
        print(f"📊 SITUAÇÃO ATUAL (CONCURSO {ultimo_concurso}):")
        print(f"   🎯 Último concurso: {ultimo_concurso}")
        print(f"   📍 N12 atual: {n12_ultimo}")
        print(f"   📊 Distribuição: {distribuicao} ({baixos}-{medios}-{altos})")
        print(f"   ⚖️ PONTO CRÍTICO: Próximo pode oscilar!")
        
        return True
        
    def aplicar_estrategia_pos_equilibrio(self):
        """Estratégia baseada na teoria de oscilação contrária"""
        print(f"\n🎯 ESTRATÉGIA BASEADA EM OSCILAÇÃO CONTRÁRIA")
        print("-" * 50)
        print("💡 SITUAÇÃO DETECTADA:")
        print(f"   • Último concurso: {self.sistema_n12.ultimo_concurso}")
        print(f"   • Distribuição atual: {self.sistema_n12.distribuicao_atual}")
        print(f"   • N12 = {self.sistema_n12.ultimo_n12}")
        
        # Aplicar lógica de oscilação contrária
        if self.sistema_n12.distribuicao_atual == "ALTA":
            print("   • TEORIA: Após ALTA → Próximo tende BAIXA/MÉDIA!")
            estrategia = "PRIVILEGIAR_BAIXOS_MEDIOS"
            probabilidades = [45, 55, 0]  # Baixa=45%, Média=55%, Alta=0%
            n12_ideais = [14, 15, 16, 17, 18]  # N12 mais baixos
            distribuicoes_alvo = ['BAIXA', 'MEDIA']
        elif self.sistema_n12.distribuicao_atual == "BAIXA":
            print("   • TEORIA: Após BAIXA → Próximo tende MÉDIA/ALTA!")
            estrategia = "PRIVILEGIAR_MEDIOS_ALTOS"
            probabilidades = [0, 55, 45]  # Baixa=0%, Média=55%, Alta=45%
            n12_ideais = [19, 20, 21, 22, 23]  # N12 mais altos
            distribuicoes_alvo = ['MEDIA', 'ALTA']
        elif self.sistema_n12.distribuicao_atual == "MEDIA":
            print("   • TEORIA: Após MÉDIA → Próximo tende EXTREMOS!")
            estrategia = "PRIVILEGIAR_EXTREMOS"
            probabilidades = [50, 0, 50]  # Baixa=50%, Média=0%, Alta=50%
            n12_ideais = [15, 16, 17, 21, 22, 23]  # N12 extremos
            distribuicoes_alvo = ['BAIXA', 'ALTA']
        else:  # EQUILIBRADA
            print("   • TEORIA: Após EQUILÍBRIO → Oscilação livre!")
            estrategia = "DIVERSIFICAR_COM_ENFASE_EXTREMOS"
            probabilidades = [35, 30, 35]  # Baixa=35%, Média=30%, Alta=35%
            n12_ideais = [16, 17, 18, 20, 21, 22]
            distribuicoes_alvo = ['BAIXA', 'ALTA']
        
        # Definir estratégia específica
        self.sistema_n12.predicao_proxima = {
            'tipo': 'OSCILACAO_CONTRARIA',
            'opcoes': ['BAIXA', 'MEDIA', 'ALTA'],
            'probabilidades': probabilidades,
            'estrategia': estrategia,
            'n12_ideais': n12_ideais,
            'distribuicoes_alvo': distribuicoes_alvo,
            'especial': True
        }
        
        print(f"\n🔧 ESTRATÉGIA ESCOLHIDA: {estrategia}")
        if estrategia == "PRIVILEGIAR_BAIXOS_MEDIOS":
            print("   📈 Probabilidades: Baixa=45%, Média=55%")
        elif estrategia == "PRIVILEGIAR_MEDIOS_ALTOS":
            print("   📈 Probabilidades: Média=55%, Alta=45%")
        elif estrategia == "PRIVILEGIAR_EXTREMOS":
            print("   📈 Probabilidades: Baixa=50%, Alta=50%")
        else:
            print("   📈 Probabilidades: Baixa=35%, Média=30%, Alta=35%")
            
        print(f"   📍 N12 ideais: {n12_ideais}")
        print(f"   🎯 Focar em: {', '.join(distribuicoes_alvo)}")
        
    def gerar_combinacoes_inteligentes(self, quantidade=50):
        """Gera combinações inteligentes baseadas na estratégia N12"""
        print(f"\n🎲 GERANDO {quantidade} COMBINAÇÕES INTELIGENTES...")
        print("-" * 50)
        
        if not self.sistema_n12.predicao_proxima:
            self.aplicar_estrategia_pos_equilibrio()
            
        combinacoes_otimizadas = []
        tentativas = 0
        max_tentativas = quantidade * 10
        
        while len(combinacoes_otimizadas) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            
            # Gerar combinação baseada na estratégia
            combinacao = self.gerar_combinacao_estrategica()
            
            if combinacao and self.validar_combinacao(combinacao):
                combinacoes_otimizadas.append(combinacao)
                
        print(f"✅ Geradas {len(combinacoes_otimizadas)} combinações otimizadas")
        return combinacoes_otimizadas
        
    def gerar_combinacao_estrategica(self):
        """Gera uma combinação seguindo a estratégia N12"""
        estrategia = self.sistema_n12.predicao_proxima['estrategia']
        
        if estrategia == 'DIVERSIFICAR_COM_ENFASE_EXTREMOS':
            # Escolher distribuição alvo
            if random.random() < 0.7:  # 70% para extremos
                if random.random() < 0.5:
                    # Distribuição BAIXA
                    baixos = random.randint(int(6), int(8))
                    medios = random.randint(int(4), int(6)) 
                    altos = 15 - baixos - medios
                else:
                    # Distribuição ALTA
                    altos = random.randint(int(6), int(8))
                    medios = random.randint(int(4), int(6))
                    baixos = 15 - altos - medios
            else:
                # Distribuição MÉDIA (30%)
                medios = random.randint(int(6), int(8))
                baixos = random.randint(int(3), int(5))
                altos = 15 - medios - baixos
                
            # Garantir valores válidos
            if baixos < 0 or medios < 0 or altos < 0:
                return None
                
            # Gerar números
            nums_baixos = random.sample(range(1, 9), min(baixos, 8))
            nums_medios = random.sample(range(9, 18), min(medios, 9))
            nums_altos = random.sample(range(18, 26), min(altos, 8))
            
            combinacao = sorted(nums_baixos + nums_medios + nums_altos)
            
            # Verificar se tem 15 números
            if len(combinacao) == 15:
                return combinacao
                
        return None
        
    def validar_combinacao(self, combinacao):
        """Valida se a combinação segue os critérios N12"""
        if len(combinacao) != 15:
            return False
            
        n12 = combinacao[11]
        n12_ideais = self.sistema_n12.predicao_proxima.get('n12_ideais', [])
        
        # Verificar se N12 está nos valores ideais
        if n12_ideais and n12 not in n12_ideais:
            return False
            
        # Verificar distribuição
        baixos = len([n for n in combinacao if 1 <= n <= 8])
        medios = len([n for n in combinacao if 9 <= n <= 17])
        altos = len([n for n in combinacao if 18 <= n <= 25])
        
        # Para estratégia pós-equilíbrio, evitar equilíbrio perfeito
        if self.sistema_n12.predicao_proxima.get('especial'):
            if baixos == 5 and medios == 5 and altos == 5:
                return False  # Evitar repetir o equilíbrio perfeito
                
        return True
        
    def adaptar_gerador_existente(self, nome_gerador, params=None):
        """Adapta um gerador existente com inteligência N12"""
        print(f"\n🔧 ADAPTANDO GERADOR: {nome_gerador}")
        print("-" * 40)
        
        try:
            # Importar o gerador
            modulo = importlib.import_module(nome_gerador)
            
            # Gerar combinações originais (simulado)
            print(f"📦 Executando gerador original...")
            combinacoes_originais = self.simular_gerador_original()
            
            # Aplicar filtro N12
            combinacoes_otimizadas = self.sistema_n12.aplicar_filtro_inteligente_n12(combinacoes_originais)
            
            return combinacoes_otimizadas
            
        except ImportError:
            print(f"⚠️ Gerador {nome_gerador} não encontrado. Usando geração inteligente.")
            return self.gerar_combinacoes_inteligentes()
            
    def simular_gerador_original(self, quantidade=100):
        """Simula um gerador original para teste"""
        combinacoes = []
        for _ in range(quantidade):
            # Gerar combinação aleatória
            combinacao = sorted(random.sample(range(1, 26), 15))
            combinacoes.append(combinacao)
        return combinacoes
        
    def executar_adaptacao_completa(self):
        """Executa adaptação completa do sistema"""
        print("🎯 EXECUTANDO ADAPTAÇÃO COMPLETA")
        print("="*60)
        
        # 1. Inicializar
        if not self.inicializar_inteligencia():
            print("❌ Falha na inicialização")
            return
            
        # 2. Aplicar estratégia pós-equilíbrio
        self.aplicar_estrategia_pos_equilibrio()
        
        # 3. Gerar combinações inteligentes
        combinacoes_resultado = self.gerar_combinacoes_inteligentes(30)
        
        # 4. Mostrar resultados
        self.mostrar_resultados(combinacoes_resultado)
        
        return combinacoes_resultado
        
    def mostrar_resultados(self, combinacoes):
        """Mostra os resultados das combinações geradas"""
        print(f"\n📊 ANÁLISE DAS COMBINAÇÕES GERADAS")
        print("="*60)
        
        if not combinacoes:
            print("❌ Nenhuma combinação gerada")
            return
            
        # Analisar distribuições
        distribuicoes = {'BAIXA': 0, 'MEDIA': 0, 'ALTA': 0, 'EQUILIBRADA': 0}
        n12_valores = []
        
        for i, combinacao in enumerate(combinacoes[:10]):  # Mostrar primeiras 10
            baixos = len([n for n in combinacao if 1 <= n <= 8])
            medios = len([n for n in combinacao if 9 <= n <= 17])
            altos = len([n for n in combinacao if 18 <= n <= 25])
            
            if baixos > medios and baixos > altos:
                dist = "BAIXA"
            elif medios > baixos and medios > altos:
                dist = "MEDIA"
            elif altos > baixos and altos > medios:
                dist = "ALTA"
            else:
                dist = "EQUILIBRADA"
                
            distribuicoes[dist] += 1
            n12 = combinacao[11]
            n12_valores.append(n12)
            
            print(f"🎲 Jogo {i+1:2d}: {combinacao}")
            print(f"   📊 B={baixos}, M={medios}, A={altos} | N12={n12} | Dist={dist}")
            
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"   🔵 Baixa: {distribuicoes['BAIXA']} jogos")
        print(f"   🟡 Média: {distribuicoes['MEDIA']} jogos")
        print(f"   🔴 Alta: {distribuicoes['ALTA']} jogos")
        print(f"   ⚖️ Equilibrada: {distribuicoes['EQUILIBRADA']} jogos")
        print(f"   📍 N12 médio: {sum(n12_valores)/len(n12_valores):.1f}")

if __name__ == "__main__":
    adaptador = AdaptadorUniversalN12()
    adaptador.executar_adaptacao_completa()