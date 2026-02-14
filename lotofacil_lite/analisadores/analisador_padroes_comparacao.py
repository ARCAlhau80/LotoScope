"""
Analisador de Padrões dos Campos de Comparação
Analisa os campos menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
para identificar padrões cíclicos e desenvolver capacidade preditiva
"""

import os
import sys
import pandas as pd
import numpy as np
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

class AnalisadorPadroesComparacao:
    def __init__(self):
        self.dados = None
        self.padroes_encontrados = {}
        self.regras_predicao = {}
        
    def extrair_dados_comparacao(self):
        """Extrai dados dos campos de comparação da base"""
        print("\n🔍 EXTRAINDO DADOS DOS CAMPOS DE COMPARAÇÃO")
        print("-" * 60)
        
        query = """
        SELECT 
            concurso,
            data_sorteio,
            menor_que_ultimo,
            maior_que_ultimo,
            igual_ao_ultimo,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT 
        WHERE menor_que_ultimo IS NOT NULL 
        AND maior_que_ultimo IS NOT NULL 
        AND igual_ao_ultimo IS NOT NULL
        ORDER BY concurso
        """
        
        try:
            resultados = db_config.execute_query(query)
            if resultados:
                colunas = ['concurso', 'data_sorteio', 'menor_que_ultimo', 'maior_que_ultimo', 
                          'igual_ao_ultimo', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                          'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']
                
                self.dados = pd.DataFrame(resultados, columns=colunas)
                print(f"✅ {len(self.dados)} concursos extraídos")
                print(f"📊 Período: {self.dados['data_sorteio'].min()} a {self.dados['data_sorteio'].max()}")
                
                # Verificar se soma sempre 15
                soma_campos = self.dados['menor_que_ultimo'] + self.dados['maior_que_ultimo'] + self.dados['igual_ao_ultimo']
                somas_unicas = soma_campos.unique()
                print(f"🔢 Somas únicas encontradas: {somas_unicas}")
                
                return True
            else:
                print("❌ Nenhum dado encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao extrair dados: {e}")
            return False
    
    def analisar_distribuicoes_basicas(self):
        """Analisa distribuições básicas dos campos"""
        print("\n📊 ANÁLISE DE DISTRIBUIÇÕES BÁSICAS")
        print("-" * 60)
        
        for campo in ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']:
            distribuicao = self.dados[campo].value_counts().sort_index()
            print(f"\n{campo.upper()}:")
            print(f"Min: {self.dados[campo].min()}, Max: {self.dados[campo].max()}")
            print(f"Média: {self.dados[campo].mean():.2f}, Mediana: {self.dados[campo].median()}")
            print("Distribuição:")
            for valor, freq in distribuicao.items():
                perc = (freq / len(self.dados)) * 100
                print(f"  {valor}: {freq} vezes ({perc:.1f}%)")
    
    def identificar_padroes_sequenciais(self):
        """Identifica padrões sequenciais nos campos"""
        print("\n🔄 IDENTIFICANDO PADRÕES SEQUENCIAIS")
        print("-" * 60)
        
        # Criar sequências de 3 concursos consecutivos
        sequencias_3 = []
        for i in range(len(self.dados) - 2):
            seq = tuple([
                (self.dados.iloc[i]['menor_que_ultimo'], 
                 self.dados.iloc[i]['maior_que_ultimo'], 
                 self.dados.iloc[i]['igual_ao_ultimo']),
                (self.dados.iloc[i+1]['menor_que_ultimo'], 
                 self.dados.iloc[i+1]['maior_que_ultimo'], 
                 self.dados.iloc[i+1]['igual_ao_ultimo']),
                (self.dados.iloc[i+2]['menor_que_ultimo'], 
                 self.dados.iloc[i+2]['maior_que_ultimo'], 
                 self.dados.iloc[i+2]['igual_ao_ultimo'])
            ])
            sequencias_3.append(seq)
        
        # Contar frequências das sequências
        contador_seq = Counter(sequencias_3)
        sequencias_frequentes = contador_seq.most_common(10)
        
        print("🔝 TOP 10 SEQUÊNCIAS MAIS FREQUENTES (3 concursos):")
        for i, (seq, freq) in enumerate(sequencias_frequentes):
            perc = (freq / len(sequencias_3)) * 100
            print(f"{i+1:2d}. {seq} - {freq} vezes ({perc:.1f}%)")
        
        self.padroes_encontrados['sequencias_3'] = sequencias_frequentes
        return sequencias_frequentes
    
    def analisar_transicoes(self):
        """Analisa transições entre estados consecutivos"""
        print("\n🔀 ANÁLISE DE TRANSIÇÕES ENTRE ESTADOS")
        print("-" * 60)
        
        transicoes = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(self.dados) - 1):
            estado_atual = (self.dados.iloc[i]['menor_que_ultimo'], 
                           self.dados.iloc[i]['maior_que_ultimo'], 
                           self.dados.iloc[i]['igual_ao_ultimo'])
            
            estado_proximo = (self.dados.iloc[i+1]['menor_que_ultimo'], 
                             self.dados.iloc[i+1]['maior_que_ultimo'], 
                             self.dados.iloc[i+1]['igual_ao_ultimo'])
            
            transicoes[estado_atual][estado_proximo] += 1
        
        # Encontrar transições mais prováveis
        print("🎯 TRANSIÇÕES MAIS PROVÁVEIS:")
        for estado_origem in transicoes:
            total_transicoes = sum(transicoes[estado_origem].values())
            if total_transicoes >= 5:  # Apenas estados com pelo menos 5 ocorrências
                print(f"\nDe {estado_origem} ({total_transicoes} vezes):")
                transicoes_ordenadas = sorted(transicoes[estado_origem].items(), 
                                            key=lambda x: x[1], reverse=True)
                
                for estado_destino, freq in transicoes_ordenadas[:3]:
                    prob = (freq / total_transicoes) * 100
                    print(f"  → {estado_destino}: {freq} vezes ({prob:.1f}%)")
        
        self.padroes_encontrados['transicoes'] = dict(transicoes)
        return transicoes
    
    def buscar_ciclos_repetitivos(self):
        """Busca ciclos repetitivos nos padrões"""
        print("\n🔄 BUSCANDO CICLOS REPETITIVOS")
        print("-" * 60)
        
        # Criar string de estados para buscar padrões
        estados_str = []
        for i in range(len(self.dados)):
            estado = f"{self.dados.iloc[i]['menor_que_ultimo']}-{self.dados.iloc[i]['maior_que_ultimo']}-{self.dados.iloc[i]['igual_ao_ultimo']}"
            estados_str.append(estado)
        
        # Buscar ciclos de diferentes tamanhos
        ciclos_encontrados = {}
        
        for tamanho_ciclo in range(2, 8):  # Ciclos de 2 a 7 concursos
            print(f"\n🔍 Buscando ciclos de tamanho {tamanho_ciclo}:")
            
            ciclos = {}
            for i in range(len(estados_str) - tamanho_ciclo * 2):
                padrao = tuple(estados_str[i:i + tamanho_ciclo])
                
                # Verificar se o padrão se repete imediatamente após
                if i + tamanho_ciclo * 2 <= len(estados_str):
                    proxima_sequencia = tuple(estados_str[i + tamanho_ciclo:i + tamanho_ciclo * 2])
                    
                    if padrao == proxima_sequencia:
                        if padrao not in ciclos:
                            ciclos[padrao] = []
                        ciclos[padrao].append(i)
            
            # Mostrar ciclos encontrados
            if ciclos:
                for padrao, posicoes in ciclos.items():
                    if len(posicoes) >= 2:  # Pelo menos 2 repetições
                        print(f"  Ciclo: {' → '.join(padrao)} (repetiu {len(posicoes)} vezes)")
                        ciclos_encontrados[tamanho_ciclo] = ciclos
            else:
                print(f"  Nenhum ciclo perfeito de tamanho {tamanho_ciclo} encontrado")
        
        self.padroes_encontrados['ciclos'] = ciclos_encontrados
        return ciclos_encontrados
    
    def calcular_correlacoes_numeros(self):
        """Calcula correlações entre campos de comparação e números sorteados"""
        print("\n🔢 CORRELAÇÕES COM NÚMEROS SORTEADOS")
        print("-" * 60)
        
        # Calcular algumas estatísticas dos números
        colunas_numeros = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10', 
                          'N11', 'N12', 'N13', 'N14', 'N15']
        
        self.dados['soma_numeros'] = self.dados[colunas_numeros].sum(axis=1)
        self.dados['media_numeros'] = self.dados[colunas_numeros].mean(axis=1)
        self.dados['amplitude'] = self.dados[colunas_numeros].max(axis=1) - self.dados[colunas_numeros].min(axis=1)
        
        # Correlações
        correlacoes = {}
        campos_comparacao = ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']
        campos_estatisticos = ['soma_numeros', 'media_numeros', 'amplitude']
        
        for campo_comp in campos_comparacao:
            print(f"\n{campo_comp.upper()}:")
            correlacoes[campo_comp] = {}
            
            for campo_stat in campos_estatisticos:
                corr = self.dados[campo_comp].corr(self.dados[campo_stat])
                correlacoes[campo_comp][campo_stat] = corr
                print(f"  vs {campo_stat}: {corr:.3f}")
        
        self.padroes_encontrados['correlacoes'] = correlacoes
        return correlacoes
    
    def criar_modelo_preditivo_simples(self):
        """Cria modelo preditivo baseado nos padrões encontrados"""
        print("\n🎯 CRIANDO MODELO PREDITIVO")
        print("-" * 60)
        
        # Usar as transições mais prováveis para predição
        transicoes = self.padroes_encontrados.get('transicoes', {})
        
        regras_predicao = {}
        
        for estado_origem, destinos in transicoes.items():
            total = sum(destinos.values())
            if total >= 10:  # Apenas estados com pelo menos 10 ocorrências
                # Encontrar o destino mais provável
                destino_mais_provavel = max(destinos.items(), key=lambda x: x[1])
                probabilidade = (destino_mais_provavel[1] / total) * 100
                
                if probabilidade >= 15:  # Reduzir threshold para 15%
                    regras_predicao[estado_origem] = {
                        'destino_previsto': destino_mais_provavel[0],
                        'probabilidade': probabilidade,
                        'ocorrencias': destino_mais_provavel[1],
                        'total_amostras': total
                    }
        
        print(f"✅ {len(regras_predicao)} regras preditivas criadas")
        
        for estado, regra in regras_predicao.items():
            print(f"\n🔮 {estado} → {regra['destino_previsto']}")
            print(f"   Probabilidade: {regra['probabilidade']:.1f}%")
            print(f"   Base: {regra['ocorrencias']}/{regra['total_amostras']} casos")
        
        self.regras_predicao = regras_predicao
        return regras_predicao
    
    def testar_acuracia_modelo(self):
        """Testa a acurácia do modelo com dados históricos"""
        print("\n🧪 TESTANDO ACURÁCIA DO MODELO")
        print("-" * 60)
        
        if not self.regras_predicao:
            print("❌ Nenhuma regra de predição disponível")
            return None
        
        # Usar últimos 30% dos dados para teste
        total_dados = len(self.dados)
        inicio_teste = int(total_dados * 0.7)
        
        dados_teste = self.dados.iloc[inicio_teste:]
        
        predicoes_corretas = 0
        total_predicoes = 0
        
        for i in range(len(dados_teste) - 1):
            estado_atual = (dados_teste.iloc[i]['menor_que_ultimo'], 
                           dados_teste.iloc[i]['maior_que_ultimo'], 
                           dados_teste.iloc[i]['igual_ao_ultimo'])
            
            estado_real_proximo = (dados_teste.iloc[i+1]['menor_que_ultimo'], 
                                  dados_teste.iloc[i+1]['maior_que_ultimo'], 
                                  dados_teste.iloc[i+1]['igual_ao_ultimo'])
            
            if estado_atual in self.regras_predicao:
                predicao = self.regras_predicao[estado_atual]['destino_previsto']
                total_predicoes += 1
                
                if predicao == estado_real_proximo:
                    predicoes_corretas += 1
        
        if total_predicoes > 0:
            acuracia = (predicoes_corretas / total_predicoes) * 100
            print(f"📊 RESULTADOS DO TESTE:")
            print(f"   Predições testadas: {total_predicoes}")
            print(f"   Predições corretas: {predicoes_corretas}")
            print(f"   Acurácia: {acuracia:.1f}%")
            
            if acuracia >= 50:
                print("✅ Modelo apresenta capacidade preditiva significativa!")
            elif acuracia >= 35:
                print("🟡 Modelo apresenta alguma capacidade preditiva")
            else:
                print("❌ Modelo não apresenta capacidade preditiva suficiente")
        else:
            print("❌ Nenhuma predição pôde ser testada")
        
        return acuracia if total_predicoes > 0 else 0
    
    def prever_proximo_estado(self, ultimo_estado=None):
        """Prevê o próximo estado baseado no modelo"""
        if ultimo_estado is None:
            # Usar o último estado da base
            ultimo_estado = (self.dados.iloc[-1]['menor_que_ultimo'], 
                           self.dados.iloc[-1]['maior_que_ultimo'], 
                           self.dados.iloc[-1]['igual_ao_ultimo'])
        
        print(f"\n🔮 PREDIÇÃO PARA O PRÓXIMO CONCURSO")
        print("-" * 60)
        print(f"Estado atual: {ultimo_estado}")
        
        if ultimo_estado in self.regras_predicao:
            regra = self.regras_predicao[ultimo_estado]
            print(f"\n✅ PREDIÇÃO ENCONTRADA:")
            print(f"Estado previsto: {regra['destino_previsto']}")
            print(f"Probabilidade: {regra['probabilidade']:.1f}%")
            print(f"Confiança: {regra['ocorrencias']}/{regra['total_amostras']} casos históricos")
            
            return regra['destino_previsto'], regra['probabilidade']
        else:
            print("❌ Nenhuma regra preditiva encontrada para este estado")
            return None, 0
    
    def executar_analise_completa(self):
        """Executa análise completa dos padrões"""
        print("🚀 INICIANDO ANÁLISE COMPLETA DOS PADRÕES DE COMPARAÇÃO")
        print("=" * 80)
        
        # Passo 1: Extrair dados
        if not self.extrair_dados_comparacao():
            return False
        
        # Passo 2: Análises básicas
        self.analisar_distribuicoes_basicas()
        
        # Passo 3: Padrões sequenciais
        self.identificar_padroes_sequenciais()
        
        # Passo 4: Transições
        self.analisar_transicoes()
        
        # Passo 5: Ciclos
        self.buscar_ciclos_repetitivos()
        
        # Passo 6: Correlações
        self.calcular_correlacoes_numeros()
        
        # Passo 7: Modelo preditivo
        self.criar_modelo_preditivo_simples()
        
        # Passo 8: Teste de acurácia
        acuracia = self.testar_acuracia_modelo()
        
        # Passo 9: Predição próximo estado
        self.prever_proximo_estado()
        
        print(f"\n🎉 ANÁLISE COMPLETA FINALIZADA!")
        if acuracia is not None:
            print(f"📈 Acurácia do modelo: {acuracia:.1f}%")
        else:
            print(f"📈 Modelo não pôde ser testado - necessário mais dados")
        
        return True

def main():
    """Função principal"""
    analisador = AnalisadorPadroesComparacao()
    analisador.executar_analise_completa()

if __name__ == "__main__":
    main()