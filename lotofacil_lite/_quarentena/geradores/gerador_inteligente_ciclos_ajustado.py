#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR INTELIGENTE DE CICLOS - VERSÃO AJUSTADA
Sistema baseado em análise de ciclos com proporções específicas:
- 60% dos números pendentes
- 60% dos números quentes  
- 15% dos números frios
- 25% dos números neutros

Autor: AR CALHAU
Data: 17 de Agosto de 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import random
import statistics
from datetime import datetime
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class GeradorInteligenteCiclos:
    """Gerador inteligente baseado em análise de ciclos com proporções ajustadas"""
    
    def __init__(self):
        self.dados_ciclos = None
        self.dados_resultados = None
        self.numeros_pendentes = set()
        self.numeros_quentes = set()
        self.numeros_frios = set()
        self.numeros_neutros = set()
        self.analise_ciclos = {}
        self.dados_carregados = False
        
        # Proporções solicitadas
        self.proporcoes = {
            'pendentes': 0.60,  # 60% dos números pendentes
            'quentes': 0.60,    # 60% dos números quentes
            'frios': 0.15,      # 15% dos números frios
            'neutros': 0.25     # 25% dos números neutros
        }
    
    def carregar_dados(self) -> bool:
        """Carrega dados de ciclos e resultados históricos"""
        if self.dados_carregados:
            return True
            
        try:
            print("🔄 Carregando dados de ciclos e histórico...")
            
            with db_config.get_connection() as conn:
                # Carrega dados de ciclos
                query_ciclos = """
                SELECT 
                    Numero, Ciclo, QtdSorteados, ConcursoInicio, 
                    ConcursoFechamento, DataInicio, DataFim
                FROM NumerosCiclos
                WHERE Numero BETWEEN 1 AND 25
                ORDER BY Numero, Ciclo DESC
                """
                
                self.dados_ciclos = pd.read_sql(query_ciclos, conn)
                
                # Carrega histórico de resultados
                query_resultados = """
                SELECT TOP 100 
                    Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT 
                ORDER BY Concurso DESC
                """
                
                self.dados_resultados = pd.read_sql(query_resultados, conn)
                
                print(f"✅ {len(self.dados_ciclos)} registros de ciclos carregados")
                print(f"✅ {len(self.dados_resultados)} concursos históricos carregados")
                
                self.dados_carregados = True
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_status_numeros(self) -> Dict:
        """Analisa o status atual de cada número (pendente, quente, frio, neutro)"""
        if not self.dados_carregados:
            return {}
        
        print("\n🧠 Analisando status dos números...")
        
        ultimo_concurso = self.dados_resultados['Concurso'].max()
        
        for numero in range(1, 26:
            # Dados do número nos ciclos
            dados_numero = self.dados_ciclos[self.dados_ciclos['Numero'] == numero]
            
            # Últimas aparições do número
            aparicoes = []
            for _), int(row in self.dados_resultados.iterrows():
                numeros_sorteados = [row[f'N{i}'] for i in range(1, 16]
                if numero in numeros_sorteados:
                    aparicoes.append(row['Concurso'])
            
            aparicoes.sort(reverse=True)  # Mais recente primeiro
            
            # Análise de status
            if len(dados_numero) > 0:
                total_sorteios = dados_numero['QtdSorteados'].sum()
                media_sorteios = dados_numero['QtdSorteados'].mean()
                
                # Último ciclo ativo ou fechado
                ultimo_ciclo = dados_numero.iloc[0]
                
                # Calcula urgência/ciclo
                if aparicoes:
                    ultimo_apareceu = aparicoes[0]
                    ciclos_desde_ultimo = ultimo_concurso - ultimo_apareceu
                    
                    # Calcula ciclo médio histórico
                    if len(aparicoes) >= 2:
                        intervalos = [aparicoes[i] - aparicoes[i+1] for i in range(int(int(len(aparicoes))-1)]
                        ciclo_medio = statistics.mean(intervalos)
                        
                        # Calcula score de urgência
                        if ciclo_medio > 0:
                            urgencia = ciclos_desde_ultimo / ciclo_medio
                        else:
                            urgencia = 1.0
                    else:
                        urgencia = 1.0
                        ciclo_medio = 5.0  # Valor padrão
                else:
                    ciclos_desde_ultimo = ultimo_concurso
                    urgencia = 2.0  # Alto se nunca apareceu nos últimos concursos
                    ciclo_medio = 8.0
                
                # Classificação baseada na lógica de ciclos
                status = self._classificar_numero(numero)), int(int(urgencia, ciclos_desde_ultimo, 
                                                media_sorteios, ultimo_ciclo)))
                
                self.analise_ciclos[numero] = {
                    'status': status,
                    'urgencia': urgencia,
                    'ciclos_desde_ultimo': ciclos_desde_ultimo,
                    'ciclo_medio': ciclo_medio,
                    'media_sorteios_ciclo': media_sorteios,
                    'total_sorteios': total_sorteios,
                    'ultimo_apareceu': aparicoes[0] if aparicoes else 0,
                    'frequencia_recente': len([a for a in aparicoes if a > ultimo_concurso - 20])
                }
                
                # Adiciona aos conjuntos apropriados
                if status == 'PENDENTE':
                    self.numeros_pendentes.add(numero)
                elif status == 'QUENTE':
                    self.numeros_quentes.add(numero)
                elif status == 'FRIO':
                    self.numeros_frios.add(numero)
                else:
                    self.numeros_neutros.add(numero)
        
        # Mostra análise
        self._mostrar_analise_status()
        return self.analise_ciclos
    
    def _classificar_numero(self, numero: int, urgencia: float, ciclos_desde_ultimo: int, 
                          media_sorteios: float, ultimo_ciclo) -> str:
        """Classifica um número baseado nos dados de ciclo"""
        
        # Lógica de classificação refinada
        
        # PENDENTE: Números que estão atrasados em seus ciclos
        if urgencia >= 1.8 or ciclos_desde_ultimo >= 15:
            return 'PENDENTE'
        
        # QUENTE: Números com alta frequência recente ou urgência moderada
        elif 1.2 <= urgencia < 1.8 and media_sorteios >= 2.0:
            return 'QUENTE'
        
        # FRIO: Números que saíram muito recentemente
        elif urgencia <= 0.5 or ciclos_desde_ultimo <= 2:
            return 'FRIO'
        
        # NEUTRO: Números em estado intermediário
        else:
            return 'NEUTRO'
    
    def _mostrar_analise_status(self):
        """Mostra análise do status dos números"""
        print(f"\n📊 ANÁLISE DE STATUS DOS NÚMEROS:")
        print(f"   🔥 PENDENTES: {len(self.numeros_pendentes)} números - {sorted(self.numeros_pendentes)}")
        print(f"   ⚡ QUENTES: {len(self.numeros_quentes)} números - {sorted(self.numeros_quentes)}")
        print(f"   ❄️ FRIOS: {len(self.numeros_frios)} números - {sorted(self.numeros_frios)}")
        print(f"   ⚪ NEUTROS: {len(self.numeros_neutros)} números - {sorted(self.numeros_neutros)}")
    
    def selecionar_numeros_por_proporcao(self) -> List[int]:
        """Seleciona números baseado nas proporções configuradas com variabilidade"""
        numeros_selecionados = []
        
        # Calcula quantidades baseadas nas proporções
        qtd_pendentes = max(1, int(len(self.numeros_pendentes) * self.proporcoes['pendentes']))
        qtd_quentes = max(1, int(len(self.numeros_quentes) * self.proporcoes['quentes']))
        qtd_frios = max(0, int(len(self.numeros_frios) * self.proporcoes['frios']))
        qtd_neutros = max(1, int(len(self.numeros_neutros) * self.proporcoes['neutros']))
        
        # Seleciona números PENDENTES (com variabilidade)
        if self.numeros_pendentes:
            pendentes_lista = list(self.numeros_pendentes)
            if len(pendentes_lista) > qtd_pendentes:
                # Usa peso baseado na urgência para seleção probabilística
                pesos = [self.analise_ciclos[n]['urgencia'] for n in pendentes_lista]
                selecionados_pendentes = np.random.choice(
                    pendentes_lista, qtd_pendentes, replace=False, p=np.array(pesos)/sum(pesos)
                ).tolist()
            else:
                selecionados_pendentes = pendentes_lista
                
            numeros_selecionados.extend(selecionados_pendentes)
        
        # Seleciona números QUENTES (com variabilidade se houver)
        if self.numeros_quentes and qtd_quentes > 0:
            quentes_lista = list(self.numeros_quentes)
            if len(quentes_lista) >= qtd_quentes:
                selecionados_quentes = random.sample(quentes_lista, qtd_quentes)
                # Remove sobreposições
                selecionados_quentes = [n for n in selecionados_quentes if n not in numeros_selecionados]
                numeros_selecionados.extend(selecionados_quentes[:qtd_quentes])
        
        # Seleciona números NEUTROS (aleatório)
        if self.numeros_neutros and qtd_neutros > 0:
            neutros_lista = list(self.numeros_neutros)
            if len(neutros_lista) >= qtd_neutros:
                neutros_aleatorios = random.sample(neutros_lista, qtd_neutros)
                # Remove sobreposições
                neutros_aleatorios = [n for n in neutros_aleatorios if n not in numeros_selecionados]
                numeros_selecionados.extend(neutros_aleatorios[:qtd_neutros])
        
        # Seleciona números FRIOS (aleatório com menor peso)
        if self.numeros_frios and qtd_frios > 0:
            frios_lista = list(self.numeros_frios)
            if len(frios_lista) >= qtd_frios:
                frios_selecionados = random.sample(frios_lista, qtd_frios)
                # Remove sobreposições
                frios_selecionados = [n for n in frios_selecionados if n not in numeros_selecionados]
                numeros_selecionados.extend(frios_selecionados[:qtd_frios])
        
        return numeros_selecionados
    
    def completar_combinacao(self, numeros_base: List[int]) -> List[int]:
        """Completa a combinação até 15 números usando lógica inteligente com variabilidade"""
        combinacao = list(set(numeros_base))  # Remove duplicatas
        
        # Números disponíveis (não utilizados ainda)
        numeros_disponiveis = [n for n in range(1, 26 if n not in combinacao]
        
        # Separa por status para selecionar com balance
        disponiveis_por_status = {
            'PENDENTE': [n for n in numeros_disponiveis if n in self.numeros_pendentes]), int('QUENTE': [n for n in numeros_disponiveis if n in self.numeros_quentes],
            'NEUTRO': [n for n in numeros_disponiveis if n in self.numeros_neutros],
            'FRIO': [n for n in numeros_disponiveis if n in self.numeros_frios]
        }
        
        # Adiciona números seguindo as proporções com randomização
        tentativas = 0
        while len(combinacao)) < 15 and tentativas < 50:
            tentativas += 1
            
            # Escolhe categoria baseada nas proporções e disponibilidade
            if len(disponiveis_por_status['PENDENTE']) > 0 and random.random() < 0.35:
                categoria = 'PENDENTE'
            elif len(disponiveis_por_status['QUENTE']) > 0 and random.random() < 0.35:
                categoria = 'QUENTE'
            elif len(disponiveis_por_status['NEUTRO']) > 0 and random.random() < 0.25:
                categoria = 'NEUTRO'
            elif len(disponiveis_por_status['FRIO']) > 0:
                categoria = 'FRIO'
            else:
                # Se nenhuma categoria específica, pega qualquer disponível
                categoria = None
            
            if categoria and disponiveis_por_status[categoria]:
                numero_candidato = random.choice(disponiveis_por_status[int(categoria)])
                
                # Validações adicionais
                if self._validar_numero_combinacao(numero_candidato, combinacao):
                    combinacao.append(numero_candidato)
                    # Remove das listas disponíveis
                    for status in disponiveis_por_status:
                        if numero_candidato in disponiveis_por_status[status]:
                            disponiveis_por_status[status].remove(numero_candidato)
            else:
                # Fallback: pega qualquer número disponível
                if numeros_disponiveis:
                    numero_candidato = random.choice(numeros_disponiveis)
                    if self._validar_numero_combinacao(numero_candidato, combinacao):
                        combinacao.append(numero_candidato)
                        numeros_disponiveis.remove(numero_candidato)
        
        # Garante que temos exatamente 15 números (fallback final)
        if len(combinacao) < 15:
            restantes = [n for n in range(1, 26 if n not in combinacao]
            random.shuffle(restantes)
            combinacao.extend(restantes[:15-len(combinacao)])
        
        return sorted(combinacao)
    
    def _calcular_score_numero(self, int(numero: int)) -> float:
        """Calcula score inteligente para um número"""
        if numero not in self.analise_ciclos:
            return 0.5  # Score neutro
        
        dados = self.analise_ciclos[numero]
        
        # Score baseado no status
        score_status = {
            'PENDENTE': 1.0,
            'QUENTE': 0.8,
            'NEUTRO': 0.6,
            'FRIO': 0.2
        }
        
        base_score = score_status.get(dados['status'], 0.5)
        
        # Ajustes por urgência
        urgencia_bonus = min(dados['urgencia'] * 0.3, 0.5)
        
        # Bonus por frequência recente
        freq_bonus = dados['frequencia_recente'] * 0.1
        
        return base_score + urgencia_bonus + freq_bonus
    
    def _validar_numero_combinacao(self, numero: int, combinacao: List[int]) -> bool:
        """Validações básicas para manter qualidade da combinação"""
        
        # Não adicionar se já muito desequilibrado por faixas
        faixa_baixa = len([n for n in combinacao if 1 <= n <= 8])
        faixa_media = len([n for n in combinacao if 9 <= n <= 17])
        faixa_alta = len([n for n in combinacao if 18 <= n <= 25])
        
        # Determina faixa do número candidato
        if 1 <= numero <= 8:
            if faixa_baixa >= 8:  # Evita muito na faixa baixa
                return False
        elif 9 <= numero <= 17:
            if faixa_media >= 8:  # Evita muito na faixa média
                return False
        else:
            if faixa_alta >= 8:  # Evita muito na faixa alta
                return False
        
        return True
    
    def gerar_combinacoes(self, quantidade: int = 10) -> List[List[int]]:
        """Gera múltiplas combinações usando a lógica de proporções"""
        if not self.dados_carregados:
            if not self.carregar_dados():
                return []
        
        # Analisa status dos números apenas uma vez
        self.analisar_status_numeros()
        
        combinacoes = []
        combinacoes_set = set()  # Para evitar duplicatas
        
        print(f"\n🎲 Gerando {quantidade} combinações inteligentes variadas...")
        
        tentativas_max = quantidade * 3  # Limite de tentativas
        tentativas = 0
        
        while len(combinacoes) < quantidade and tentativas < tentativas_max:
            tentativas += 1
            
            # Seleciona números base por proporção
            numeros_base = self.selecionar_numeros_por_proporcao()
            
            # Completa a combinação
            combinacao_completa = self.completar_combinacao(numeros_base)
            
            # Converte para tupla para verificar duplicatas
            combinacao_tuple = tuple(sorted(combinacao_completa))
            
            # Validação final e verificação de duplicatas
            if (len(combinacao_completa) == 15 and 
                len(set(combinacao_completa)) == 15 and 
                combinacao_tuple not in combinacoes_set):
                
                combinacoes.append(combinacao_completa)
                combinacoes_set.add(combinacao_tuple)
                
                if len(combinacoes) % 10 == 0:
                    print(f"   ✅ {len(combinacoes)} combinações únicas geradas")
        
        print(f"✅ Total final: {len(combinacoes)} combinações únicas geradas")
        return combinacoes
    
    def salvar_combinacoes(self, combinacoes: List[List[int]], 
                          nome_arquivo: Optional[str] = None) -> str:
        """Salva combinações em arquivo TXT"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_ciclos_inteligente_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(f"# COMBINAÇÕES INTELIGENTES - CICLOS AJUSTADOS\n")
                f.write(f"# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"#\n")
                f.write(f"# PROPORÇÕES UTILIZADAS:\n")
                f.write(f"#   Pendentes: {self.proporcoes['pendentes']*100:.0f}%\n")
                f.write(f"#   Quentes: {self.proporcoes['quentes']*100:.0f}%\n")
                f.write(f"#   Neutros: {self.proporcoes['neutros']*100:.0f}%\n")
                f.write(f"#   Frios: {self.proporcoes['frios']*100:.0f}%\n")
                f.write(f"#\n")
                f.write(f"# STATUS DOS NÚMEROS:\n")
                f.write(f"#   Pendentes: {sorted(self.numeros_pendentes)}\n")
                f.write(f"#   Quentes: {sorted(self.numeros_quentes)}\n")
                f.write(f"#   Neutros: {sorted(self.numeros_neutros)}\n")
                f.write(f"#   Frios: {sorted(self.numeros_frios)}\n")
                f.write(f"#\n")
                f.write(f"# Total de combinações: {len(combinacoes)}\n")
                f.write(f"#\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    f.write(f"{','.join(map(str, combinacao))}\n")
            
            print(f"✅ Arquivo salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return ""
    
    def mostrar_estatisticas(self, combinacoes: List[List[int]]):
        """Mostra estatísticas das combinações geradas"""
        if not combinacoes:
            return
        
        print(f"\n📊 ESTATÍSTICAS DAS COMBINAÇÕES GERADAS:")
        print(f"=" * 50)
        
        # Distribuição por status
        contadores_status = {'PENDENTE': 0, 'QUENTE': 0, 'NEUTRO': 0, 'FRIO': 0}
        
        for combinacao in combinacoes:
            for numero in combinacao:
                if numero in self.analise_ciclos:
                    status = self.analise_ciclos[numero]['status']
                    contadores_status[status] += 1
        
        total_numeros = len(combinacoes) * 15
        
        print(f"📈 DISTRIBUIÇÃO POR STATUS (total {total_numeros} números):")
        for status, count in contadores_status.items():
            percent = (count / total_numeros) * 100
            print(f"   {status}: {count} ({percent:.1f}%)")
        
        # Estatísticas gerais
        somas = [sum(comb) for comb in combinacoes]
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   Soma média: {statistics.mean(somas):.1f}")
        print(f"   Soma mínima: {min(somas)}")
        print(f"   Soma máxima: {max(somas)}")
        
        # Números mais utilizados
        contador_numeros = Counter()
        for combinacao in combinacoes:
            contador_numeros.update(combinacao)
        
        print(f"\n🔥 TOP 10 NÚMEROS MAIS UTILIZADOS:")
        for numero, freq in contador_numeros.most_common(10):
            percent = (freq / len(combinacoes)) * 100
            status = self.analise_ciclos.get(numero, {}).get('status', 'N/A')
            print(f"   {numero:2d}: {freq:2d}x ({percent:4.1f}%) - {status}")

def main():
    """Função principal"""
    print("🎯 GERADOR INTELIGENTE DE CICLOS - VERSÃO AJUSTADA")
    print("=" * 60)
    print("📊 Proporções configuradas:")
    print("   • 60% dos números pendentes")
    print("   • 60% dos números quentes")
    print("   • 25% dos números neutros")
    print("   • 15% dos números frios")
    print()
    
    gerador = GeradorInteligenteCiclos()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    try:
        # Gera combinações
        quantidade = int(input("Quantas combinações gerar (padrão 20): ") or "20")
        
        combinacoes = gerador.gerar_combinacoes(quantidade)
        
        if combinacoes:
            # Mostra estatísticas
            gerador.mostrar_estatisticas(combinacoes)
            
            # Pergunta se quer salvar
            salvar = input(f"\nSalvar {len(combinacoes)} combinações em arquivo? (s/n): ").lower()
            
            if salvar.startswith('s'):
                nome_arquivo = gerador.salvar_combinacoes(combinacoes)
                print(f"✅ Processo concluído! Arquivo: {nome_arquivo}")
            else:
                print("✅ Processo concluído!")
                
        else:
            print("❌ Nenhuma combinação foi gerada")
            
    except ValueError:
        print("❌ Quantidade inválida")
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
