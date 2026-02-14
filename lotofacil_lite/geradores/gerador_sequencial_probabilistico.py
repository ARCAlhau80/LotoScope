#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR SEQUENCIAL PROBABILÍSTICO
Sistema avançado de geração baseado em probabilidades condicionais
P(Ni | N1, N2, ..., Ni-1) - Cada posição influencia as próximas

Conceito: Gera combinações considerando que a escolha de cada número
afeta a probabilidade dos números subsequentes, criando um modelo
de dependência sequencial baseado nos padrões históricos.

Autor: AR CALHAU
Data: 14 de Agosto de 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import random
import math
from collections import defaultdict, Counter
from datetime import datetime
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class GeradorSequencialProbabilistico:
    """
    Gerador que utiliza probabilidades condicionais sequenciais
    para criar combinações baseadas em interdependências posicionais
    """
    
    def __init__(self):
        self.conexao_db = None
        self.dados_historicos = []
        self.matrizes_condicionais = {}  # P(Ni | N1...Ni-1) para cada posição
        self.padroes_sequenciais = {}
        self.probabilidades_posicao = {}
        self.historico_geracoes = []
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos para análise de padrões sequenciais"""
        try:
            print("📊 Carregando dados históricos para análise sequencial...")
            
            query = """
            SELECT TOP 500 
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                SomaTotal, QtdePrimos, QtdeImpares, Concurso
            FROM Resultados_INT 
            ORDER BY Concurso DESC
            """
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                self.dados_historicos = []
                for row in cursor.fetchall():
                    numeros = list(row[:15])
                    dados = {
                        'numeros': numeros,
                        'soma_total': row[15],
                        'qtde_primos': row[16],
                        'qtde_impares': row[17],
                        'concurso': row[18]
                    }
                    self.dados_historicos.append(dados)
                
                print(f"✅ {len(self.dados_historicos)} concursos carregados para análise")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados históricos: {e}")
            return False
    
    def calcular_matrizes_condicionais(self):
        """
        Calcula as matrizes de probabilidade condicional P(Ni | N1...Ni-1)
        para cada posição da combinação
        """
        print("🧠 Calculando matrizes de probabilidade condicional...")
        
        # Inicializa estruturas para cada posição (1-15)
        for posicao in range(1, 16):
            self.matrizes_condicionais[posicao] = defaultdict(lambda: defaultdict(int))
            self.probabilidades_posicao[posicao] = defaultdict(float)
        
        # Análise sequencial dos dados históricos
        for concurso in self.dados_historicos:
            numeros = concurso['numeros']
            
            for posicao in range(15):
                numero_atual = numeros[posicao]
                posicao_key = posicao + 1  # 1-15
                
                # Para primeira posição, apenas conta frequência
                if posicao == 0:
                    self.matrizes_condicionais[1]['independente'][numero_atual] += 1
                else:
                    # Para posições subsequentes, considera números anteriores
                    contexto_anterior = tuple(sorted(numeros[:posicao]))
                    self.matrizes_condicionais[posicao_key][contexto_anterior][numero_atual] += 1
        
        # Converte contagens em probabilidades
        self._normalizar_probabilidades()
        
        print("✅ Matrizes condicionais calculadas para todas as posições")
    
    def _normalizar_probabilidades(self):
        """Normaliza as contagens em probabilidades condicionais"""
        for posicao in range(1, 16):
            matriz = self.matrizes_condicionais[posicao]
            
            for contexto, numeros_dict in matriz.items():
                total_contexto = sum(numeros_dict.values())
                
                if total_contexto > 0:
                    for numero in numeros_dict:
                        prob = numeros_dict[numero] / total_contexto
                        self.probabilidades_posicao[posicao][(contexto, numero)] = prob
    
    def analisar_padroes_sequenciais(self):
        """Analisa padrões de dependência sequencial"""
        print("🔍 Analisando padrões de dependência sequencial...")
        
        # Análise de correlações entre posições consecutivas
        correlacoes = defaultdict(list)
        
        for concurso in self.dados_historicos:
            numeros = concurso['numeros']
            
            for i in range(14):  # 0-13 (posições 1-14)
                for j in range(i + 1, 15):  # Posições subsequentes
                    diferenca = abs(numeros[j] - numeros[i])
                    correlacoes[f"pos_{i+1}_to_{j+1}"].append(diferenca)
        
        # Calcula estatísticas das correlações
        self.padroes_sequenciais = {}
        for chave, diferencas in correlacoes.items():
            media = sum(diferencas) / len(diferencas) if diferencas else 0
            variancia = sum((x - media) ** 2 for x in diferencas) / len(diferencas) if diferencas else 0
            desvio = math.sqrt(variancia)
            
            self.padroes_sequenciais[chave] = {
                'media': media,
                'desvio': desvio,
                'min': min(diferencas) if diferencas else 0,
                'max': max(diferencas) if diferencas else 0
            }
        
        print("✅ Padrões sequenciais analisados")
    
    def gerar_numero_posicao(self, posicao: int, numeros_anteriores: list) -> int:
        """
        Gera um número para uma posição específica baseado na probabilidade condicional
        
        Args:
            posicao: Posição atual (1-15)
            numeros_anteriores: Lista dos números já escolhidos
            
        Returns:
            int: Número escolhido para a posição
        """
        if posicao == 1:
            # Primeira posição: usa distribuição histórica independente
            candidatos = list(range(1, 26))
            pesos = []
            
            matriz_pos1 = self.matrizes_condicionais[1]['independente']
            for numero in candidatos:
                peso = matriz_pos1.get(numero, 1)  # Peso mínimo 1
                pesos.append(peso)
            
            return random.choices(candidatos, weights=pesos)[0]
        
        else:
            # Posições subsequentes: usa probabilidade condicional
            contexto = tuple(sorted(numeros_anteriores))
            numeros_disponiveis = [n for n in range(1, 26) if n not in numeros_anteriores]
            
            # Busca probabilidades condicionais para este contexto
            prob_matrix = self.matrizes_condicionais[posicao]
            
            # Se contexto exato não existe, usa contexto parcial
            melhor_contexto = self._encontrar_melhor_contexto(contexto, prob_matrix)
            
            if melhor_contexto and melhor_contexto in prob_matrix:
                # Usa probabilidades condicionais
                pesos = []
                for numero in numeros_disponiveis:
                    peso = prob_matrix[melhor_contexto].get(numero, 0.1)  # Peso mínimo
                    pesos.append(peso)
                
                if sum(pesos) > 0:
                    return random.choices(numeros_disponiveis, weights=pesos)[0]
            
            # Fallback: escolha com base em padrões gerais
            return self._escolha_fallback(posicao, numeros_anteriores, numeros_disponiveis)
    
    def _encontrar_melhor_contexto(self, contexto_target, prob_matrix):
        """Encontra o melhor contexto disponível na matriz"""
        # Tenta contexto completo primeiro
        if contexto_target in prob_matrix:
            return contexto_target
        
        # Tenta contextos parciais (subconjuntos)
        melhor_match = None
        melhor_score = 0
        
        for contexto_existente in prob_matrix.keys():
            if contexto_existente == 'independente':
                continue
                
            # Calcula overlap entre contextos
            if isinstance(contexto_existente, tuple):
                overlap = len(set(contexto_target) & set(contexto_existente))
                score = overlap / max(len(contexto_target), len(contexto_existente))
                
                if score > melhor_score:
                    melhor_score = score
                    melhor_match = contexto_existente
        
        return melhor_match
    
    def _escolha_fallback(self, posicao: int, numeros_anteriores: list, disponiveis: list) -> int:
        """Estratégia de fallback para escolha de números"""
        # Analisa tendências da posição específica
        numeros_posicao = []
        for concurso in self.dados_historicos:
            if posicao <= 15:
                numeros_posicao.append(concurso['numeros'][posicao - 1])
        
        # Calcula preferências da posição
        contador = Counter(numeros_posicao)
        
        pesos = []
        for numero in disponiveis:
            peso = contador.get(numero, 1)
            
            # Ajusta peso baseado em padrões sequenciais
            if numeros_anteriores:
                ultimo_numero = max(numeros_anteriores)
                diferenca_ideal = self.padroes_sequenciais.get(f"pos_{len(numeros_anteriores)}_to_{posicao}", {}).get('media', 5)
                diferenca_real = abs(numero - ultimo_numero)
                
                # Penaliza diferenças muito distantes do padrão
                fator_ajuste = 1.0 / (1.0 + abs(diferenca_real - diferenca_ideal) * 0.1)
                peso *= fator_ajuste
            
            pesos.append(peso)
        
        return random.choices(disponiveis, weights=pesos)[0]
    
    def gerar_combinacao_sequencial(self) -> list:
        """
        Gera uma combinação completa usando probabilidades condicionais sequenciais
        
        Returns:
            list: Combinação de 15 números gerada sequencialmente
        """
        combinacao = []
        
        for posicao in range(1, 16):
            numero = self.gerar_numero_posicao(posicao, combinacao)
            combinacao.append(numero)
        
        # Garante que a combinação está ordenada e válida
        combinacao = sorted(list(set(combinacao)))
        
        # Se perdeu números por duplicação, completa
        while len(combinacao) < 15:
            disponiveis = [n for n in range(1, 26) if n not in combinacao]
            if disponiveis:
                numero_extra = random.choice(disponiveis)
                combinacao.append(numero_extra)
                combinacao = sorted(combinacao)
        
        return combinacao[:15]  # Garante exatamente 15 números
    
    def avaliar_qualidade_combinacao(self, combinacao: list) -> dict:
        """Avalia a qualidade de uma combinação gerada"""
        soma = sum(combinacao)
        primos = len([n for n in combinacao if n in {2, 3, 5, 7, 11, 13, 17, 19, 23}])
        impares = len([n for n in combinacao if n % 2 == 1])
        
        # Análise de gaps
        gaps = 0
        for i in range(14):
            if combinacao[i + 1] - combinacao[i] > 1:
                gaps += 1
        
        # Análise de distribuição por quintis
        quintis = [0, 0, 0, 0, 0]
        for num in combinacao:
            if 1 <= num <= 5: quintis[0] += 1
            elif 6 <= num <= 10: quintis[1] += 1
            elif 11 <= num <= 15: quintis[2] += 1
            elif 16 <= num <= 20: quintis[3] += 1
            elif 21 <= num <= 25: quintis[4] += 1
        
        return {
            'soma': soma,
            'primos': primos,
            'impares': impares,
            'gaps': gaps,
            'quintis': quintis,
            'amplitude': max(combinacao) - min(combinacao)
        }
    
    def gerar_lote_combinacoes(self, quantidade: int = 1000) -> list:
        """
        Gera um lote de combinações usando o método sequencial probabilístico
        
        Args:
            quantidade: Número de combinações a gerar
            
        Returns:
            list: Lista de combinações geradas
        """
        print(f"🎯 Gerando {quantidade} combinações sequenciais probabilísticas...")
        
        combinacoes = []
        combinacoes_set = set()  # Para evitar duplicatas
        tentativas = 0
        max_tentativas = quantidade * 3
        
        while len(combinacoes) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            
            combinacao = self.gerar_combinacao_sequencial()
            combinacao_tuple = tuple(combinacao)
            
            if combinacao_tuple not in combinacoes_set:
                combinacoes_set.add(combinacao_tuple)
                
                # Avalia qualidade
                qualidade = self.avaliar_qualidade_combinacao(combinacao)
                
                combinacoes.append({
                    'numeros': combinacao,
                    'qualidade': qualidade
                })
                
                if len(combinacoes) % 100 == 0:
                    print(f"   📊 {len(combinacoes)} combinações geradas...")
        
        print(f"✅ {len(combinacoes)} combinações únicas geradas em {tentativas} tentativas")
        return combinacoes
    
    def salvar_combinacoes(self, combinacoes: list, nome_arquivo: str = None):
        """Salva as combinações geradas em arquivo"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_sequencial_probabilistico_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("# COMBINAÇÕES GERADAS - SISTEMA SEQUENCIAL PROBABILÍSTICO\n")
                f.write(f"# Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"# Total: {len(combinacoes)} combinações\n")
                f.write(f"# Método: Probabilidades Condicionais P(Ni | N1...Ni-1)\n")
                f.write("#" + "=" * 70 + "\n\n")
                
                for i, comb_data in enumerate(combinacoes, 1):
                    numeros = comb_data['numeros']
                    qualidade = comb_data['qualidade']
                    
                    # Linha principal da combinação
                    linha_numeros = ' '.join(f"{n:2d}" for n in numeros)
                    f.write(f"{linha_numeros}\n")
                    
                    # Comentário com estatísticas (a cada 10 combinações)
                    if i % 10 == 0:
                        f.write(f"# Bloco {i//10}: Soma={qualidade['soma']}, "
                               f"Primos={qualidade['primos']}, "
                               f"Ímpares={qualidade['impares']}\n\n")
            
            print(f"💾 Combinações salvas em: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def executar_analise_completa(self):
        """Executa análise completa e geração de combinações"""
        print("\n" + "="*80)
        print("🎯 GERADOR SEQUENCIAL PROBABILÍSTICO")
        print("   Análise de Dependências Posicionais P(Ni | N1...Ni-1)")
        print("="*80)
        
        # Etapa 1: Carregamento de dados
        if not self.carregar_dados_historicos():
            return False
        
        # Etapa 2: Cálculo das matrizes condicionais
        self.calcular_matrizes_condicionais()
        
        # Etapa 3: Análise de padrões sequenciais
        self.analisar_padroes_sequenciais()
        
        # Etapa 4: Geração de combinações
        print("\n📊 CONFIGURAÇÃO DA GERAÇÃO:")
        try:
            qtd = int(input("Digite a quantidade de combinações (padrão 2000): ") or "2000")
        except ValueError:
            qtd = 2000
        
        combinacoes = self.gerar_lote_combinacoes(qtd)
        
        if combinacoes:
            # Etapa 5: Análise estatística do lote
            self._analisar_estatisticas_lote(combinacoes)
            
            # Etapa 6: Salvamento
            nome_arquivo = self.salvar_combinacoes(combinacoes)
            
            if nome_arquivo:
                print(f"\n🎉 PROCESSO CONCLUÍDO!")
                print(f"📁 Arquivo gerado: {nome_arquivo}")
                print(f"📊 {len(combinacoes)} combinações sequenciais probabilísticas")
                return True
        
        return False
    
    def _analisar_estatisticas_lote(self, combinacoes: list):
        """Analisa estatísticas do lote gerado"""
        print("\n📈 ANÁLISE ESTATÍSTICA DO LOTE:")
        
        somas = [c['qualidade']['soma'] for c in combinacoes]
        primos = [c['qualidade']['primos'] for c in combinacoes]
        impares = [c['qualidade']['impares'] for c in combinacoes]
        
        # Calcula médias usando Python puro
        soma_media = sum(somas) / len(somas) if somas else 0
        primos_medio = sum(primos) / len(primos) if primos else 0
        impares_medio = sum(impares) / len(impares) if impares else 0
        
        print(f"   • Soma média: {soma_media:.1f} (min: {min(somas)}, max: {max(somas)})")
        print(f"   • Primos médio: {primos_medio:.1f}")
        print(f"   • Ímpares médio: {impares_medio:.1f}")
        
        # Análise de distribuição por números
        contador_numeros = Counter()
        for comb in combinacoes:
            contador_numeros.update(comb['numeros'])
        
        mais_frequentes = contador_numeros.most_common(5)
        menos_frequentes = contador_numeros.most_common()[-5:]
        
        print(f"   • Números mais frequentes: {[f'{n}({f})' for n, f in mais_frequentes]}")
        print(f"   • Números menos frequentes: {[f'{n}({f})' for n, f in menos_frequentes]}")

def main():
    """Função principal"""
    gerador = GeradorSequencialProbabilistico()
    
    # Testa conexão com banco
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    # Executa análise completa
    sucesso = gerador.executar_analise_completa()
    
    if sucesso:
        print("\n✅ Geração sequencial probabilística concluída com sucesso!")
    else:
        print("\n❌ Erro durante a geração")

if __name__ == "__main__":
    main()
