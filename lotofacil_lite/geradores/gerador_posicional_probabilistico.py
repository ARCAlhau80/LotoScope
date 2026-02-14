#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🎯 GERADOR POSICIONAL PROBABILÍSTICO
Gera números para cada posição usando probabilidades históricas

Cada posição (N1 a N15) tem seus números possíveis com pesos diferentes.
O número 1 em N1 tem 60.51% de peso, enquanto o 9 tem 0.03%.
Números não se repetem entre posições.

NOVO: Análise de números ENCALHADOS (frios) por posição!
- Remove números que não saem há X concursos
- Mostra relatório de números frios

Autor: LotoScope AI
Data: Dezembro 2025
"""

import sys
import random
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from datetime import datetime

# Configurar paths
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False


class GeradorPosicionalProbabilistico:
    """
    Gerador que usa probabilidades históricas por posição.
    
    Para cada posição N1-N15, sorteia um número usando os pesos
    da frequência histórica daquela posição específica.
    
    NOVO: Remove números "encalhados" (frios) que não saem há X concursos.
    """
    
    # Conexão com banco
    CONN_STR = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-K6JPBDS;"
        "DATABASE=LOTOFACIL;"
        "Trusted_Connection=yes;"
    )
    
    def __init__(self, limite_encalhado: int = 10, remover_encalhados: bool = True,
                 numeros_excluidos: List[int] = None,
                 exclusoes_posicionais: Dict[int, List[int]] = None):
        """
        Inicializa o gerador.
        
        Args:
            limite_encalhado: Quantos concursos sem sair para considerar "encalhado" (padrão=10)
            remover_encalhados: Se True, remove números encalhados da geração
            numeros_excluidos: Lista de números (1-9 números) que NÃO devem aparecer em NENHUMA posição
            exclusoes_posicionais: Dict {posicao: [numeros]} para excluir números apenas em posições específicas
                                   Ex: {2: [7, 8], 5: [10, 11]} exclui 7,8 apenas de N2 e 10,11 apenas de N5
        """
        self.limite_encalhado = limite_encalhado
        self.remover_encalhados = remover_encalhados
        self.numeros_excluidos = set(numeros_excluidos) if numeros_excluidos else set()
        self.exclusoes_posicionais = {}  # {posicao: set(numeros)}
        
        # Processar exclusões posicionais
        if exclusoes_posicionais:
            for pos, nums in exclusoes_posicionais.items():
                if 1 <= pos <= 15:
                    nums_validos = [n for n in nums if 1 <= n <= 25]
                    if nums_validos:
                        self.exclusoes_posicionais[pos] = set(nums_validos)
        
        # Validar números excluídos globais
        if self.numeros_excluidos:
            if len(self.numeros_excluidos) > 9:
                print("⚠️ Máximo de 9 números podem ser excluídos globalmente. Usando os primeiros 9.")
                self.numeros_excluidos = set(list(self.numeros_excluidos)[:9])
            
            invalidos = [n for n in self.numeros_excluidos if n < 1 or n > 25]
            if invalidos:
                print(f"⚠️ Números inválidos removidos: {invalidos}")
                self.numeros_excluidos = {n for n in self.numeros_excluidos if 1 <= n <= 25}
        
        # Tabela de probabilidades por posição
        self.probabilidades = self._criar_tabela_probabilidades()
        
        # Análise de encalhados
        self.encalhados = {}  # {posicao: {numero: concursos_sem_sair}}
        self.numeros_frios = {}  # {posicao: [numeros encalhados]}
        
        print("🎯 GERADOR POSICIONAL PROBABILÍSTICO")
        print("=" * 60)
        print("📊 Tabela de probabilidades carregada")
        
        # Mostrar números excluídos GLOBALMENTE
        if self.numeros_excluidos:
            excl_str = ", ".join(f"{n:02d}" for n in sorted(self.numeros_excluidos))
            print(f"🚫 Exclusão GLOBAL: {excl_str}")
            print(f"   (não aparecem em NENHUMA posição)")
        
        # Mostrar exclusões POSICIONAIS
        if self.exclusoes_posicionais:
            print(f"🎯 Exclusões POSICIONAIS:")
            for pos in sorted(self.exclusoes_posicionais.keys()):
                nums = self.exclusoes_posicionais[pos]
                nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                print(f"   N{pos:2}: excluídos [{nums_str}]")
        
        # Analisar encalhados
        if HAS_PYODBC:
            self._analisar_encalhados()
            self._mostrar_encalhados()
        else:
            print("⚠️ pyodbc não disponível - análise de encalhados desativada")
        
        self._mostrar_resumo()
    
    def _criar_tabela_probabilidades(self) -> Dict[int, List[Tuple[int, float]]]:
        """
        Cria a tabela de probabilidades baseada nos dados históricos.
        Dados extraídos da planilha fornecida.
        
        IMPORTANTE: Os números estão com suas probabilidades REAIS por posição.
        Dados corrigidos em 29/12/2025 conforme planilha do usuário.
        """
        tabela = {
            # N1: números 1-9 (1 mais frequente = 60.51%)
            1: [
                (1, 60.51), (2, 24.52), (3, 9.94), (4, 3.13), 
                (5, 1.46), (6, 0.34), (7, 0.06), (8, 0.03), (9, 0.03)
            ],
            # N2: números 2-10 (2 mais frequente = 35.32%)
            2: [
                (2, 35.32), (3, 30.42), (4, 18.61), (5, 8.79), 
                (6, 4.28), (7, 1.71), (8, 0.62), (9, 0.20), (10, 0.03)
            ],
            # N3: 4=27.29%, 5=23.48%, 3=19.98%...
            3: [
                (4, 27.29), (5, 23.48), (3, 19.98), (6, 14.55), 
                (7, 8.37), (8, 3.86), (9, 1.65), (10, 0.56), 
                (11, 0.20), (12, 0.03)
            ],
            # N4: 6=21.89%, 5=20.60%, 7=19.79%...
            4: [
                (6, 21.89), (5, 20.60), (7, 19.79), (8, 12.99), 
                (4, 11.28), (9, 7.81), (10, 3.81), (11, 1.32), 
                (12, 0.39), (13, 0.11)
            ],
            # N5: 8=20.18%, 7=19.26%, 9=16.68%...
            5: [
                (8, 20.18), (7, 19.26), (9, 16.68), (6, 14.75), 
                (10, 12.48), (11, 7.16), (5, 5.63), (12, 2.85), 
                (13, 0.76), (14, 0.22)
            ],
            # N6: 9=19.42%, 10=19.40%, 11=15.70%...
            6: [
                (9, 19.42), (10, 19.40), (11, 15.70), (8, 14.81), 
                (12, 11.31), (7, 8.87), (13, 5.35), (6, 2.77), 
                (14, 1.74), (15, 0.50), (16, 0.11)
            ],
            # N7: 11=19.17%, 12=17.77%, 10=17.10%...
            7: [
                (11, 19.17), (12, 17.77), (10, 17.10), (13, 15.06), 
                (9, 11.06), (14, 8.65), (8, 5.09), (15, 3.69), 
                (5, 1.18), (16, 1.01), (17, 0.20)
            ],
            # N8: 13=19.00%, 14=18.25%, 12=16.93%...
            8: [
                (13, 19.00), (14, 18.25), (12, 16.93), (11, 12.93), 
                (15, 12.45), (10, 7.39), (16, 6.97), (17, 2.69), 
                (9, 2.57), (18, 0.42), (8, 0.36)
            ],
            # N9: 15=19.68%, 14=18.28%, 16=15.45%...
            9: [
                (15, 19.68), (14, 18.28), (16, 15.45), (13, 14.11), 
                (17, 11.34), (12, 8.62), (18, 5.43), (11, 4.51), 
                (10, 1.29), (19, 1.09), (9, 0.20)
            ],
            # N10: 16=19.14%, 17=18.67%, 18=16.60%...
            10: [
                (16, 19.14), (17, 18.67), (18, 16.60), (15, 14.97), 
                (14, 10.58), (19, 8.87), (13, 5.63), (20, 2.77), 
                (12, 2.18), (11, 0.53), (10, 0.03)
            ],
            # N11: 19=21.16%, 18=19.93%, 17=17.52%...
            11: [
                (19, 21.16), (18, 19.93), (17, 17.52), (20, 14.27), 
                (16, 10.78), (15, 6.91), (21, 5.68), (14, 2.74), 
                (13, 0.84), (12, 0.14)
            ],
            # N12: 20=24.55%, 21=20.12%, 19=18.75%...
            12: [
                (20, 24.55), (21, 20.12), (19, 18.75), (18, 13.60), 
                (22, 11.02), (17, 7.02), (16, 3.19), (15, 1.26), 
                (14, 0.34), (13, 0.03)
            ],
            # N13: 22=26.39%, 21=23.01%, 23=20.82%...
            13: [
                (22, 26.39), (21, 23.01), (23, 20.82), (20, 16.26), 
                (19, 8.42), (18, 3.13), (17, 1.37), (16, 0.42), 
                (15, 0.14)
            ],
            # N14: 24=37.00%, 23=28.35%, 22=19.40%...
            14: [
                (24, 37.00), (23, 28.35), (22, 19.40), (21, 9.15), 
                (20, 4.28), (19, 1.23), (18, 0.45), (17, 0.11)
            ],
            # N15: 25=62.05%, 24=23.82%, 23=9.26%...
            15: [
                (25, 62.05), (24, 23.82), (23, 9.26), (22, 3.05), 
                (21, 1.37), (20, 0.28), (19, 0.11), (18, 0.03)
            ]
        }
        
        return tabela
    
    def _analisar_encalhados(self):
        """
        Analisa quantos concursos cada número está sem sair em cada posição.
        Consulta o banco de dados para calcular.
        """
        try:
            conn = pyodbc.connect(self.CONN_STR)
            cursor = conn.cursor()
            
            # Buscar todos os resultados ordenados por concurso DESC
            # TABELA CORRETA: Resultados_INT (tem os dados como inteiros)
            cursor.execute("""
                SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT
                ORDER BY Concurso DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                print("⚠️ Nenhum resultado encontrado no banco")
                return
            
            ultimo_concurso = rows[0][0]
            
            # Para cada posição, encontrar quando cada número saiu pela última vez
            for posicao in range(1, 16):
                self.encalhados[posicao] = {}
                self.numeros_frios[posicao] = []
                
                # Pegar todos os números possíveis para essa posição
                numeros_posicao = [num for num, _ in self.probabilidades[posicao]]
                
                for numero in numeros_posicao:
                    # Encontrar quantos concursos sem sair
                    concursos_sem_sair = 0
                    
                    for row in rows:
                        valor_posicao = int(row[posicao])  # posicao 1 = coluna 1 (N1)
                        if valor_posicao == numero:
                            break
                        concursos_sem_sair += 1
                    
                    self.encalhados[posicao][numero] = concursos_sem_sair
                    
                    # Marcar como frio se ultrapassou limite
                    if concursos_sem_sair >= self.limite_encalhado:
                        self.numeros_frios[posicao].append((numero, concursos_sem_sair))
            
            # Ordenar frios por quantidade de concursos sem sair
            for pos in self.numeros_frios:
                self.numeros_frios[pos].sort(key=lambda x: x[1], reverse=True)
                
        except Exception as e:
            print(f"❌ Erro ao analisar encalhados: {e}")
    
    def _mostrar_encalhados(self):
        """Mostra relatório de números encalhados por posição"""
        if not self.numeros_frios:
            return
        
        # Verificar se há encalhados
        total_encalhados = sum(len(v) for v in self.numeros_frios.values())
        
        if total_encalhados == 0:
            print(f"\n✅ Nenhum número encalhado (>= {self.limite_encalhado} concursos)")
            return
        
        print(f"\n🥶 NÚMEROS ENCALHADOS (>= {self.limite_encalhado} concursos sem sair):")
        print("-" * 60)
        
        for posicao in range(1, 16):
            frios = self.numeros_frios.get(posicao, [])
            if frios:
                frios_str = ", ".join([f"{n}({c}x)" for n, c in frios])
                print(f"   N{posicao:2}: {frios_str}")
        
        print("-" * 60)
        print(f"   Total: {total_encalhados} números encalhados em {sum(1 for v in self.numeros_frios.values() if v)} posições")
        
        if self.remover_encalhados:
            print(f"   ⚠️ Esses números serão REMOVIDOS da geração!")
        else:
            print(f"   ℹ️ Remoção de encalhados DESATIVADA")
        
        # Formato SQL-like para copiar/colar - mostra números DISPONÍVEIS (IN)
        print(f"\n📋 FORMATO SQL (para copiar) - Números DISPONÍVEIS:")
        print("-" * 60)
        primeiro = True
        for posicao in range(1, 16):
            # Pegar números REALMENTE disponíveis após filtrar encalhados
            probs_filtradas = self.get_probabilidades_filtradas(posicao)
            nums_disponiveis = sorted([n for n, _ in probs_filtradas])
            nums = ", ".join([str(n) for n in nums_disponiveis])
            if primeiro:
                print(f"       N{posicao} IN ({nums})")
                primeiro = False
            else:
                print(f"   AND N{posicao} IN ({nums})")
        print("-" * 60)
    
    def get_probabilidades_filtradas(self, posicao: int) -> List[Tuple[int, float]]:
        """
        Retorna probabilidades da posição, removendo:
        1. Números excluídos GLOBALMENTE
        2. Números excluídos POSICIONALMENTE (apenas nesta posição)
        3. Números encalhados (se configurado)
        """
        probs = self.probabilidades[posicao]
        
        # 1. Remover números excluídos GLOBALMENTE
        if self.numeros_excluidos:
            probs = [(num, peso) for num, peso in probs if num not in self.numeros_excluidos]
        
        # 2. Remover números excluídos POSICIONALMENTE (apenas nesta posição)
        if posicao in self.exclusoes_posicionais:
            excluidos_posicao = self.exclusoes_posicionais[posicao]
            probs = [(num, peso) for num, peso in probs if num not in excluidos_posicao]
        
        # 3. Remover encalhados se configurado
        if self.remover_encalhados and posicao in self.numeros_frios:
            encalhados = [n for n, _ in self.numeros_frios[posicao]]
            probs = [(num, peso) for num, peso in probs if num not in encalhados]
        
        return probs
    
    def get_posicoes_validas_para_numero(self, numero: int) -> List[int]:
        """
        Retorna lista de posições (1-15) onde um número pode aparecer.
        Baseado na tabela de probabilidades (se tem probabilidade > 0, pode aparecer).
        
        Args:
            numero: Número de 1 a 25
            
        Returns:
            Lista de posições válidas para esse número
        """
        posicoes = []
        for pos in range(1, 16):
            numeros_posicao = [n for n, _ in self.probabilidades[pos]]
            if numero in numeros_posicao:
                posicoes.append(pos)
        return posicoes
    
    def validar_numeros_obrigatorios(self, numeros: List[int]) -> Tuple[bool, str]:
        """
        Valida se os números obrigatórios podem ser usados juntos.
        Verifica se existe pelo menos uma configuração válida.
        
        Args:
            numeros: Lista de números obrigatórios (1-25)
            
        Returns:
            (valido, mensagem) - True se válido, False com mensagem de erro
        """
        if not numeros:
            return True, "Nenhum número obrigatório"
        
        # Verificar duplicatas
        if len(numeros) != len(set(numeros)):
            return False, "Números duplicados não são permitidos"
        
        # Verificar range
        for n in numeros:
            if n < 1 or n > 25:
                return False, f"Número {n} fora do range 1-25"
        
        # Verificar se cada número tem posição válida
        for n in numeros:
            posicoes = self.get_posicoes_validas_para_numero(n)
            if not posicoes:
                return False, f"Número {n} não tem posição válida na tabela de probabilidades"
        
        # Mostrar info sobre posições
        print(f"\n📍 POSIÇÕES VÁLIDAS DOS NÚMEROS OBRIGATÓRIOS:")
        print("-" * 50)
        for n in sorted(numeros):
            posicoes = self.get_posicoes_validas_para_numero(n)
            pos_str = ", ".join(f"N{p}" for p in posicoes)
            print(f"   Número {n:2}: {pos_str}")
        print("-" * 50)
        
        return True, "Números válidos"
    
    def consultar_posicao(self, posicao: int):
        """
        Mostra análise detalhada de uma posição específica.
        
        Args:
            posicao: Número da posição (1-15)
        """
        if posicao < 1 or posicao > 15:
            print(f"❌ Posição inválida: {posicao}. Use 1-15.")
            return
        
        print(f"\n📊 ANÁLISE DETALHADA - POSIÇÃO N{posicao}")
        print("=" * 60)
        
        # Probabilidades
        probs = self.probabilidades[posicao]
        probs_ordenadas = sorted(probs, key=lambda x: x[1], reverse=True)
        
        print(f"\n🎯 PROBABILIDADES (ordenado por frequência):")
        for i, (num, prob) in enumerate(probs_ordenadas, 1):
            # Verificar se está encalhado
            concursos_sem = self.encalhados.get(posicao, {}).get(num, 0)
            encalhado = "🥶" if concursos_sem >= self.limite_encalhado else "✅"
            
            print(f"   {i:2}. Número {num:2}: {prob:6.2f}% | Sem sair: {concursos_sem:4} concursos {encalhado}")
        
        # Resumo
        frios = self.numeros_frios.get(posicao, [])
        if frios:
            print(f"\n⚠️ NÚMEROS ENCALHADOS ({len(frios)}):")
            for num, conc in frios:
                prob = next((p for n, p in probs if n == num), 0)
                print(f"   • Número {num}: {prob:.2f}% de probabilidade, {conc} concursos sem sair")
    
    def analisar_encalhados_top(self, n: int = 3):
        """
        Mostra os TOP N números mais encalhados de cada posição.
        Foca em números que TÊM probabilidade alta mas estão encalhados.
        """
        print(f"\n🔥 TOP {n} NÚMEROS QUENTES QUE ESTÃO FRIOS (paradoxo!)")
        print("=" * 70)
        print("   Números com BOA probabilidade, mas encalhados há muito tempo")
        print("-" * 70)
        
        for posicao in range(1, 16):
            frios = self.numeros_frios.get(posicao, [])
            if not frios:
                continue
            
            # Filtrar apenas números com probabilidade >= 5%
            probs = dict(self.probabilidades[posicao])
            frios_relevantes = [
                (num, conc, probs.get(num, 0)) 
                for num, conc in frios 
                if probs.get(num, 0) >= 5.0
            ]
            
            if frios_relevantes:
                frios_relevantes.sort(key=lambda x: x[2], reverse=True)  # Ordenar por prob
                
                top_n = frios_relevantes[:n]
                frios_str = ", ".join([f"{num}({prob:.1f}%/{conc}x)" for num, conc, prob in top_n])
                print(f"   N{posicao:2}: {frios_str}")
        
        print("-" * 70)
        print("   Formato: número(probabilidade%/concursos_sem_sair)")
    
    def _mostrar_resumo(self):
        """Mostra resumo das probabilidades"""
        print()
        print("📋 Resumo por posição (número mais provável):")
        print("-" * 50)
        
        for pos in range(1, 16):
            probs = self.probabilidades[pos]
            # Pegar o mais provável
            mais_provavel = max(probs, key=lambda x: x[1])
            menos_provavel = min([p for p in probs if p[1] > 0], key=lambda x: x[1])
            
            print(f"   N{pos:2}: {mais_provavel[0]:2} ({mais_provavel[1]:5.2f}%) → "
                  f"{menos_provavel[0]:2} ({menos_provavel[1]:5.2f}%)")
    
    def _sortear_numero_posicao(self, posicao: int, 
                                 numeros_usados: Set[int]) -> int:
        """
        Sorteia um número para uma posição específica usando pesos.
        Exclui números já usados em posições anteriores.
        Exclui números encalhados se configurado.
        Exclui números definidos pelo usuário.
        """
        # Pegar probabilidades da posição (já filtradas)
        probs = self.get_probabilidades_filtradas(posicao)
        
        # Filtrar números já usados
        disponiveis = [(num, peso) for num, peso in probs 
                       if num not in numeros_usados and peso > 0]
        
        if not disponiveis:
            # Se não tem disponível nas probabilidades filtradas, usar todas (exceto excluídos)
            probs_todas = self.probabilidades[posicao]
            probs_todas = [(n, p) for n, p in probs_todas if n not in self.numeros_excluidos]
            disponiveis = [(num, peso) for num, peso in probs_todas 
                           if num not in numeros_usados and peso > 0]
        
        if not disponiveis:
            # Se ainda não tem, pegar qualquer número válido (exceto excluídos)
            todos_numeros = set(range(1, 26)) - self.numeros_excluidos
            restantes = list(todos_numeros - numeros_usados)
            if restantes:
                return random.choice(restantes)
            else:
                # Caso extremo: não tem mais números disponíveis
                raise ValueError("Não há números disponíveis para gerar combinação!")
        
        # Extrair números e pesos
        numeros = [n for n, _ in disponiveis]
        pesos = [p for _, p in disponiveis]
        
        # Sortear usando pesos
        escolhido = random.choices(numeros, weights=pesos, k=1)[0]
        
        return escolhido
    
    def gerar_combinacao(self) -> List[int]:
        """
        Gera UMA combinação usando probabilidades por posição.
        """
        numeros_usados = set()
        combinacao = []
        
        # Para cada posição N1 a N15
        for posicao in range(1, 16):
            numero = self._sortear_numero_posicao(posicao, numeros_usados)
            combinacao.append(numero)
            numeros_usados.add(numero)
        
        return sorted(combinacao)
    
    def gerar_combinacoes(self, quantidade: int = 3) -> List[List[int]]:
        """
        Gera múltiplas combinações únicas.
        """
        combinacoes = []
        tentativas = 0
        max_tentativas = quantidade * 100
        
        while len(combinacoes) < quantidade and tentativas < max_tentativas:
            comb = self.gerar_combinacao()
            
            # Verificar se é única
            if comb not in combinacoes:
                combinacoes.append(comb)
            
            tentativas += 1
        
        return combinacoes
    
    def gerar_e_mostrar(self, quantidade: int = 3):
        """
        Gera e mostra combinações formatadas.
        """
        print()
        print(f"🎲 Gerando {quantidade} combinação(ões)...")
        print("=" * 60)
        
        combinacoes = self.gerar_combinacoes(quantidade)
        
        for i, comb in enumerate(combinacoes, 1):
            nums_str = " - ".join(f"{n:02d}" for n in comb)
            print(f"   {i:3}. {nums_str}")
        
        print("=" * 60)
        print(f"✅ {len(combinacoes)} combinação(ões) gerada(s)")
        
        return combinacoes
    
    def gerar_com_detalhes(self, quantidade: int = 1):
        """
        Gera combinações mostrando o processo de decisão.
        """
        print()
        print(f"🔬 Gerando {quantidade} combinação(ões) COM DETALHES...")
        if self.numeros_excluidos:
            excl_str = ", ".join(f"{n:02d}" for n in sorted(self.numeros_excluidos))
            print(f"🚫 Excluindo: {excl_str}")
        print("=" * 70)
        
        for i in range(quantidade):
            print(f"\n📋 COMBINAÇÃO {i+1}:")
            print("-" * 70)
            
            numeros_usados = set()
            combinacao = []
            
            for posicao in range(1, 16):
                # Pegar probabilidades disponíveis (já filtradas)
                probs = self.get_probabilidades_filtradas(posicao)
                disponiveis = [(num, peso) for num, peso in probs 
                               if num not in numeros_usados and peso > 0]
                
                if disponiveis:
                    numeros = [n for n, _ in disponiveis]
                    pesos = [p for _, p in disponiveis]
                    
                    # Normalizar pesos para 100%
                    soma = sum(pesos)
                    pesos_norm = [p/soma*100 for p in pesos]
                    
                    # Sortear
                    escolhido = random.choices(numeros, weights=pesos, k=1)[0]
                    peso_escolhido = dict(disponiveis)[escolhido]
                    
                    # Mostrar top 3 opções
                    top3 = sorted(zip(numeros, pesos_norm), key=lambda x: -x[1])[:3]
                    opcoes_str = ", ".join(f"{n}({p:.1f}%)" for n, p in top3)
                    
                    print(f"   N{posicao:2}: Opções [{opcoes_str}...] → "
                          f"Escolhido: {escolhido:2} (peso original: {peso_escolhido:.2f}%)")
                else:
                    # Fallback (excluindo números do usuário)
                    todos = set(range(1, 26)) - self.numeros_excluidos
                    restantes = list(todos - numeros_usados)
                    escolhido = random.choice(restantes)
                    print(f"   N{posicao:2}: [FALLBACK] → Escolhido: {escolhido:2}")
                
                combinacao.append(escolhido)
                numeros_usados.add(escolhido)
            
            # Mostrar resultado final
            combinacao_ordenada = sorted(combinacao)
            nums_str = " - ".join(f"{n:02d}" for n in combinacao_ordenada)
            print(f"\n   🎯 RESULTADO: {nums_str}")
        
        print("\n" + "=" * 70)


def main():
    """Menu interativo"""
    print()
    print("🎯" * 30)
    print("  GERADOR POSICIONAL PROBABILÍSTICO")
    print("🎯" * 30)
    print()
    
    # =====================================================
    # PASSO 1: Exclusão GLOBAL
    # =====================================================
    print("=" * 60)
    print("🚫 PASSO 1: EXCLUSÃO GLOBAL (opcional)")
    print("=" * 60)
    print("   Números que NÃO aparecem em NENHUMA posição (máx 9).")
    print("   Exemplo: 3, 9, 16 ou 3 9 16")
    print()
    excluir_str = input("   Números a excluir GLOBALMENTE (Enter para nenhum): ").strip()
    
    numeros_excluidos = None
    if excluir_str:
        try:
            if ',' in excluir_str:
                numeros_excluidos = [int(n.strip()) for n in excluir_str.split(',')]
            else:
                numeros_excluidos = [int(n.strip()) for n in excluir_str.split()]
            
            # Validar quantidade
            if len(numeros_excluidos) > 9:
                print(f"   ⚠️ Máximo 9 números. Usando os primeiros 9.")
                numeros_excluidos = numeros_excluidos[:9]
            
            # Validar range
            numeros_excluidos = [n for n in numeros_excluidos if 1 <= n <= 25]
            
            if not numeros_excluidos:
                print("   ⚠️ Nenhum número válido informado.")
                numeros_excluidos = None
            else:
                excl_str = ", ".join(f"{n:02d}" for n in sorted(numeros_excluidos))
                print(f"   ✅ Exclusão GLOBAL: {excl_str}")
        except:
            print("   ⚠️ Formato inválido. Nenhum número será excluído.")
            numeros_excluidos = None
    
    # =====================================================
    # PASSO 2: Exclusão POSICIONAL
    # =====================================================
    print()
    print("=" * 60)
    print("🎯 PASSO 2: EXCLUSÃO POSICIONAL (opcional)")
    print("=" * 60)
    print("   Números excluídos apenas de posições específicas.")
    print("   Ex: Excluir 7,8 apenas de N2 (mas podem aparecer em N3, N4, etc)")
    print()
    
    exclusoes_posicionais = {}
    
    configurar_pos = input("   Deseja configurar exclusões posicionais? (s/N): ").strip().lower()
    
    if configurar_pos in ('s', 'sim', 'y', 'yes'):
        print()
        print("   Para cada posição, digite os números a excluir.")
        print("   Exemplo: 7, 8 ou 7 8")
        print("   Enter para pular a posição.")
        print()
        
        for pos in range(1, 16):
            nums_str = input(f"   N{pos:2} - Números a excluir: ").strip()
            
            if nums_str:
                try:
                    if ',' in nums_str:
                        nums = [int(n.strip()) for n in nums_str.split(',')]
                    else:
                        nums = [int(n.strip()) for n in nums_str.split()]
                    
                    nums = [n for n in nums if 1 <= n <= 25]
                    
                    if nums:
                        exclusoes_posicionais[pos] = set(nums)
                        nums_fmt = ", ".join(f"{n:02d}" for n in sorted(nums))
                        print(f"        ✅ N{pos}: excluídos [{nums_fmt}]")
                except:
                    print(f"        ⚠️ Formato inválido, ignorado.")
        
        if exclusoes_posicionais:
            print()
            print("   📋 Resumo das exclusões posicionais:")
            for pos in sorted(exclusoes_posicionais.keys()):
                nums = exclusoes_posicionais[pos]
                nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                print(f"      N{pos:2}: excluídos [{nums_str}]")
        else:
            print("   Nenhuma exclusão posicional configurada.")
    
    print()
    gerador = GeradorPosicionalProbabilistico(
        numeros_excluidos=numeros_excluidos,
        exclusoes_posicionais=exclusoes_posicionais if exclusoes_posicionais else None
    )
    
    while True:
        print("\n📋 OPÇÕES:")
        print("   1. Gerar combinações (simples)")
        print("   2. Gerar combinações (com detalhes)")
        print("   3. Ver tabela de probabilidades")
        print("   4. Alterar exclusão GLOBAL")
        print("   5. Alterar exclusão POSICIONAL ⭐ NOVO")
        print("   6. Ver exclusões ativas")
        print("   0. Sair")
        
        opcao = input("\n   Escolha: ").strip()
        
        if opcao == "0":
            print("\n👋 Até logo!")
            break
        
        elif opcao == "1":
            try:
                qtd = input("   Quantas combinações? [3]: ").strip()
                qtd = int(qtd) if qtd else 3
            except:
                qtd = 3
            
            gerador.gerar_e_mostrar(qtd)
        
        elif opcao == "2":
            try:
                qtd = input("   Quantas combinações? [1]: ").strip()
                qtd = int(qtd) if qtd else 1
            except:
                qtd = 1
            
            gerador.gerar_com_detalhes(qtd)
        
        elif opcao == "3":
            print("\n📊 TABELA DE PROBABILIDADES POR POSIÇÃO:")
            print("=" * 80)
            
            for pos in range(1, 16):
                probs = gerador.probabilidades[pos]
                nums_str = " | ".join(f"{n}:{p:.1f}%" for n, p in probs if p > 0)
                print(f"   N{pos:2}: {nums_str}")
            
            if gerador.numeros_excluidos:
                excl_str = ", ".join(f"{n:02d}" for n in sorted(gerador.numeros_excluidos))
                print(f"\n   🚫 Exclusão global: {excl_str}")
            
            if gerador.exclusoes_posicionais:
                print(f"\n   🎯 Exclusões posicionais:")
                for pos in sorted(gerador.exclusoes_posicionais.keys()):
                    nums = gerador.exclusoes_posicionais[pos]
                    nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                    print(f"      N{pos:2}: {nums_str}")
            
            print("=" * 80)
        
        elif opcao == "4":
            print("\n🚫 ALTERAR EXCLUSÃO GLOBAL")
            print("   (Números que NÃO aparecem em NENHUMA posição)")
            if gerador.numeros_excluidos:
                excl_str = ", ".join(f"{n:02d}" for n in sorted(gerador.numeros_excluidos))
                print(f"   Atual: {excl_str}")
            else:
                print("   Atual: Nenhum")
            
            print("   Digite os números a excluir (1-9 números, 1-25):")
            print("   Exemplo: 3, 9, 16 ou 3 9 16 (Enter para limpar)")
            excluir_str = input("   Números: ").strip()
            
            if not excluir_str:
                gerador.numeros_excluidos = set()
                print("   ✅ Exclusão global limpa!")
            else:
                try:
                    if ',' in excluir_str:
                        novos = [int(n.strip()) for n in excluir_str.split(',')]
                    else:
                        novos = [int(n.strip()) for n in excluir_str.split()]
                    
                    novos = [n for n in novos if 1 <= n <= 25][:9]
                    
                    if novos:
                        gerador.numeros_excluidos = set(novos)
                        excl_str = ", ".join(f"{n:02d}" for n in sorted(gerador.numeros_excluidos))
                        print(f"   ✅ Exclusão global: {excl_str}")
                    else:
                        print("   ⚠️ Nenhum número válido.")
                except:
                    print("   ❌ Formato inválido!")
        
        elif opcao == "5":
            print("\n🎯 ALTERAR EXCLUSÃO POSICIONAL")
            print("   (Números excluídos APENAS em posições específicas)")
            print("=" * 60)
            
            # Mostrar exclusões atuais
            if gerador.exclusoes_posicionais:
                print("   Exclusões atuais:")
                for pos in sorted(gerador.exclusoes_posicionais.keys()):
                    nums = gerador.exclusoes_posicionais[pos]
                    nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                    print(f"      N{pos:2}: {nums_str}")
            else:
                print("   Nenhuma exclusão posicional ativa")
            
            print("\n   Opções:")
            print("   1. Adicionar exclusão para uma posição")
            print("   2. Remover exclusão de uma posição")
            print("   3. Limpar todas as exclusões posicionais")
            print("   0. Voltar")
            
            sub_opcao = input("   Escolha: ").strip()
            
            if sub_opcao == "1":
                try:
                    pos_str = input("   Qual posição? (1-15): ").strip()
                    pos = int(pos_str)
                    if not 1 <= pos <= 15:
                        print("   ❌ Posição deve ser de 1 a 15!")
                        continue
                    
                    print(f"   Quais números excluir da posição N{pos}?")
                    print(f"   (Exemplo: 7, 8 ou 7 8)")
                    nums_str = input("   Números: ").strip()
                    
                    if ',' in nums_str:
                        nums = [int(n.strip()) for n in nums_str.split(',')]
                    else:
                        nums = [int(n.strip()) for n in nums_str.split()]
                    
                    nums = [n for n in nums if 1 <= n <= 25]
                    
                    if nums:
                        gerador.exclusoes_posicionais[pos] = set(nums)
                        nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                        print(f"   ✅ N{pos}: excluídos [{nums_str}]")
                    else:
                        print("   ⚠️ Nenhum número válido.")
                except:
                    print("   ❌ Formato inválido!")
            
            elif sub_opcao == "2":
                if not gerador.exclusoes_posicionais:
                    print("   ⚠️ Nenhuma exclusão posicional para remover.")
                    continue
                
                try:
                    pos_str = input("   Qual posição limpar? (1-15): ").strip()
                    pos = int(pos_str)
                    if pos in gerador.exclusoes_posicionais:
                        del gerador.exclusoes_posicionais[pos]
                        print(f"   ✅ Exclusão da posição N{pos} removida!")
                    else:
                        print(f"   ⚠️ Posição N{pos} não tinha exclusão.")
                except:
                    print("   ❌ Formato inválido!")
            
            elif sub_opcao == "3":
                gerador.exclusoes_posicionais = {}
                print("   ✅ Todas as exclusões posicionais removidas!")
        
        elif opcao == "6":
            print("\n📋 EXCLUSÕES ATIVAS:")
            print("=" * 60)
            
            if gerador.numeros_excluidos:
                excl_str = ", ".join(f"{n:02d}" for n in sorted(gerador.numeros_excluidos))
                print(f"   🚫 GLOBAL: {excl_str}")
                print(f"      (não aparecem em NENHUMA posição)")
            else:
                print("   🚫 GLOBAL: Nenhum")
            
            print()
            
            if gerador.exclusoes_posicionais:
                print("   🎯 POSICIONAL:")
                for pos in sorted(gerador.exclusoes_posicionais.keys()):
                    nums = gerador.exclusoes_posicionais[pos]
                    nums_str = ", ".join(f"{n:02d}" for n in sorted(nums))
                    print(f"      N{pos:2}: excluídos [{nums_str}]")
            else:
                print("   🎯 POSICIONAL: Nenhum")
            
            print("=" * 60)


if __name__ == "__main__":
    main()
