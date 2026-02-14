#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 LOTOFÁCIL GENERATOR - VERSÃO LITE
Gerador de combinações inteligentes para Lotofácil
Autor: AR CALHAU
Data: 04 de Agosto de 2025
"""

import sys
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import random
import itertools
from datetime import datetime
from typing import List, Dict, Tuple, Set
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class LotofacilGenerator:
    """Gerador principal de combinações da Lotofácil"""
    
    def __init__(self):
        self.numeros_lotofacil = list(range(1, 26))  # 1 a 25
        self.tamanho_combinacao = 15
        
        # Sistema de intuição
        self.numeros_obrigatorios = set()
        self.numeros_proibidos = set()
        
        # Cache de dados da base
        self._cache_frequencias = None
        self._cache_ciclos = None
        
    def configure_intuition_numbers(self, obrigatorios: List[int] = None, proibidos: List[int] = None):
        """
        Configura números obrigatórios e proibidos (sistema de intuição)
        
        Args:
            obrigatorios (List[int]): Números que DEVEM estar na combinação
            proibidos (List[int]): Números que NÃO PODEM estar na combinação
        """
        self.numeros_obrigatorios = set(obrigatorios or [])
        self.numeros_proibidos = set(proibidos or [])
        
        # Validações
        if len(self.numeros_obrigatorios) > self.tamanho_combinacao:
            raise ValueError(f"Muitos números obrigatórios: {len(self.numeros_obrigatorios)} > {self.tamanho_combinacao}")
        
        if self.numeros_obrigatorios & self.numeros_proibidos:
            conflito = self.numeros_obrigatorios & self.numeros_proibidos
            raise ValueError(f"Conflito: números {conflito} são obrigatórios E proibidos")
        
        print(f"✅ Intuição configurada: {len(self.numeros_obrigatorios)} obrigatórios, {len(self.numeros_proibidos)} proibidos")
    
    def validate_intuition_constraints(self, combinacao: List[int]) -> bool:
        """
        Valida se a combinação atende às restrições de intuição
        
        Args:
            combinacao (List[int]): Combinação a ser validada
            
        Returns:
            bool: True se válida
        """
        conjunto_comb = set(combinacao)
        
        # Verifica se todos os obrigatórios estão presentes
        if not self.numeros_obrigatorios.issubset(conjunto_comb):
            return False
        
        # Verifica se nenhum proibido está presente
        if conjunto_comb & self.numeros_proibidos:
            return False
        
        return True
    
    def _carregar_frequencias(self) -> Dict[int, int]:
        """
        Carrega frequências dos números da base de dados (tabela Resultados_INT)
        
        Returns:
            Dict[int, int]: Frequência de cada número
        """
        if self._cache_frequencias is not None:
            return self._cache_frequencias
        
        print("📊 Carregando frequências da base...")
        
        # Usa a tabela oficial Resultados_INT
        if not db_config.verificar_tabela_existe('Resultados_INT'):
            print("   ❌ Tabela Resultados_INT não encontrada")
            return {i: 1 for i in range(1, 26)}  # Frequência padrão
        
        print("   🎯 Usando tabela Resultados_INT (oficial)")
        query = """
        SELECT Numero, COUNT(*) as Frequencia
        FROM (
            SELECT N1 as Numero FROM Resultados_INT WHERE N1 IS NOT NULL
            UNION ALL SELECT N2 FROM Resultados_INT WHERE N2 IS NOT NULL
            UNION ALL SELECT N3 FROM Resultados_INT WHERE N3 IS NOT NULL
            UNION ALL SELECT N4 FROM Resultados_INT WHERE N4 IS NOT NULL
            UNION ALL SELECT N5 FROM Resultados_INT WHERE N5 IS NOT NULL
            UNION ALL SELECT N6 FROM Resultados_INT WHERE N6 IS NOT NULL
            UNION ALL SELECT N7 FROM Resultados_INT WHERE N7 IS NOT NULL
            UNION ALL SELECT N8 FROM Resultados_INT WHERE N8 IS NOT NULL
            UNION ALL SELECT N9 FROM Resultados_INT WHERE N9 IS NOT NULL
            UNION ALL SELECT N10 FROM Resultados_INT WHERE N10 IS NOT NULL
            UNION ALL SELECT N11 FROM Resultados_INT WHERE N11 IS NOT NULL
            UNION ALL SELECT N12 FROM Resultados_INT WHERE N12 IS NOT NULL
            UNION ALL SELECT N13 FROM Resultados_INT WHERE N13 IS NOT NULL
            UNION ALL SELECT N14 FROM Resultados_INT WHERE N14 IS NOT NULL
            UNION ALL SELECT N15 FROM Resultados_INT WHERE N15 IS NOT NULL
        ) as NumerosSorteados
        GROUP BY Numero
        ORDER BY Numero
        """
        
        resultado = db_config.execute_query(query)
        
        if resultado:
            self._cache_frequencias = {row[0]: row[1] for row in resultado}
            print(f"✅ Frequências carregadas: {len(self._cache_frequencias)} números")
        else:
            # Fallback: frequências iguais
            self._cache_frequencias = {i: 100 for i in self.numeros_lotofacil}
            print("⚠️ Usando frequências padrão")
        
        return self._cache_frequencias
    
    def _carregar_dados_ciclos(self) -> Dict[int, Dict]:
        """
        Carrega dados de ciclos da base (tabela NumerosCiclos da arquitetura completa)
        
        Returns:
            Dict[int, Dict]: Dados de ciclos por número
        """
        if self._cache_ciclos is not None:
            return self._cache_ciclos
        
        print("🔄 Carregando dados de ciclos...")
        
        # Verifica se existe a tabela NumerosCiclos da arquitetura completa
        if db_config.verificar_tabela_existe('NumerosCiclos'):
            print("   🎯 Usando tabela NumerosCiclos (arquitetura completa)")
            
            # Query adaptada para a estrutura real da sua tabela
            query = """
            SELECT 
                Numero, 
                MAX(Ciclo) as UltimoCiclo,
                AVG(CAST(QtdSorteados as FLOAT)) as MediaSorteados,
                COUNT(*) as TotalCiclos,
                MAX(ConcursoFechamento) as UltimoConcurso
            FROM NumerosCiclos
            WHERE ConcursoFechamento IS NOT NULL
            GROUP BY Numero
            ORDER BY Numero
            """
            
            resultado = db_config.execute_query(query)
            
            if resultado:
                # Calcula urgência baseada nos dados reais dos ciclos
                ultimo_concurso_global = max(row[4] for row in resultado if row[4])
                
                self._cache_ciclos = {}
                for row in resultado:
                    numero = row[0]
                    ultimo_ciclo = row[1] if row[1] else 0
                    media_sorteados = row[2] if row[2] else 1.0
                    total_ciclos = row[3] if row[3] else 1
                    ultimo_concurso_num = row[4] if row[4] else 0
                    
                    # Calcula urgência: quanto mais tempo sem aparecer, maior urgência
                    concursos_sem_sortear = ultimo_concurso_global - ultimo_concurso_num
                    urgencia = 1.0 + (concursos_sem_sortear * 0.1)  # Base + tempo sem sortear
                    
                    # Ajusta pela média de sorteios
                    if media_sorteados > 0:
                        urgencia *= (2.0 / media_sorteados)  # Números com menos sorteios ficam mais urgentes
                    
                    self._cache_ciclos[numero] = {
                        'ultimo_ciclo': ultimo_ciclo,
                        'media_sorteados': media_sorteados,
                        'total_ciclos': total_ciclos,
                        'ultimo_concurso': ultimo_concurso_num,
                        'urgencia': min(urgencia, 10.0),  # Limita urgência máxima
                        'concursos_sem_sortear': concursos_sem_sortear
                    }
                
                print(f"✅ Dados de ciclos carregados: {len(self._cache_ciclos)} números")
                
                # Mostra top 5 mais urgentes para debug
                top_urgentes = sorted(self._cache_ciclos.items(), 
                                    key=lambda x: x[1]['urgencia'], reverse=True)[:5]
                print("   📊 Top 5 números mais urgentes:")
                for num, dados in top_urgentes:
                    print(f"      N{num}: Urgência={dados['urgencia']:.2f}, "
                          f"Sem sortear há {dados['concursos_sem_sortear']} concursos")
                
            else:
                print("⚠️ Erro ao carregar dados de ciclos, usando padrão")
                self._cache_ciclos = self._gerar_dados_ciclos_padrao()
        else:
            print("   💡 Tabela NumerosCiclos não encontrada, usando dados padrão")
            self._cache_ciclos = self._gerar_dados_ciclos_padrao()
        
        return self._cache_ciclos
    
    def _gerar_dados_ciclos_padrao(self) -> Dict[int, Dict]:
        """Gera dados de ciclos padrão quando não há tabela específica"""
        return {
            i: {
                'ultimo_sorteio': 0, 
                'ciclo_atual': 0, 
                'urgencia': 1.0,
                'estado': 'NORMAL'
            }
            for i in self.numeros_lotofacil
        }
    
    def generate_random_combinations(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera combinações completamente aleatórias (método de controle)
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🎲 Gerando {quantidade} combinações aleatórias...")
        
        combinacoes = []
        tentativas = 0
        max_tentativas = quantidade * 100
        
        while len(combinacoes) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            
            # Números disponíveis (excluindo proibidos)
            numeros_disponiveis = [n for n in self.numeros_lotofacil if n not in self.numeros_proibidos]
            
            # Combina obrigatórios + aleatórios
            combinacao = list(self.numeros_obrigatorios)
            faltam = self.tamanho_combinacao - len(combinacao)
            
            if faltam > 0:
                # Remove obrigatórios dos disponíveis
                for obrig in self.numeros_obrigatorios:
                    if obrig in numeros_disponiveis:
                        numeros_disponiveis.remove(obrig)
                
                # Adiciona números aleatórios
                if len(numeros_disponiveis) >= faltam:
                    adicionais = random.sample(numeros_disponiveis, faltam)
                    combinacao.extend(adicionais)
                    
                    # Ordena e valida
                    combinacao.sort()
                    if self.validate_intuition_constraints(combinacao):
                        combinacoes.append(combinacao)
        
        print(f"✅ {len(combinacoes)} combinações aleatórias geradas")
        return combinacoes
    
    def generate_frequency_based_combinations(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera combinações baseadas em frequência histórica
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"📊 Gerando {quantidade} combinações baseadas em frequência...")
        
        frequencias = self._carregar_frequencias()
        combinacoes = []
        
        # Ordena números por frequência (mais frequentes primeiro)
        numeros_por_freq = sorted(
            [n for n in self.numeros_lotofacil if n not in self.numeros_proibidos],
            key=lambda x: frequencias.get(x, 0),
            reverse=True
        )
        
        for i in range(quantidade):
            combinacao = list(self.numeros_obrigatorios)
            faltam = self.tamanho_combinacao - len(combinacao)
            
            if faltam > 0:
                # Seleciona com peso baseado na frequência
                numeros_disponiveis = [n for n in numeros_por_freq if n not in combinacao]
                
                # Aplica randomização ponderada
                selecionados = []
                for _ in range(faltam):
                    if numeros_disponiveis:
                        # Maior chance para números mais frequentes
                        pesos = [frequencias.get(n, 1) for n in numeros_disponiveis]
                        numero = random.choices(numeros_disponiveis, weights=pesos, k=1)[0]
                        selecionados.append(numero)
                        numeros_disponiveis.remove(numero)
                
                combinacao.extend(selecionados)
                combinacao.sort()
                
                if self.validate_intuition_constraints(combinacao):
                    combinacoes.append(combinacao)
        
        print(f"✅ {len(combinacoes)} combinações por frequência geradas")
        return combinacoes
    
    def generate_cycles_based_combinations(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera combinações baseadas em inteligência de ciclos
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🔄 Gerando {quantidade} combinações baseadas em ciclos...")
        
        ciclos = self._carregar_dados_ciclos()
        combinacoes = []
        
        # Ordena números por urgência (mais urgentes primeiro)
        numeros_por_urgencia = sorted(
            [n for n in self.numeros_lotofacil if n not in self.numeros_proibidos],
            key=lambda x: ciclos.get(x, {}).get('urgencia', 1),
            reverse=True
        )
        
        for i in range(quantidade):
            combinacao = list(self.numeros_obrigatorios)
            faltam = self.tamanho_combinacao - len(combinacao)
            
            if faltam > 0:
                # Prioriza números mais urgentes
                numeros_disponiveis = [n for n in numeros_por_urgencia if n not in combinacao]
                
                # Seleciona com peso baseado na urgência
                selecionados = []
                for _ in range(faltam):
                    if numeros_disponiveis:
                        urgencias = [ciclos.get(n, {}).get('urgencia', 1) for n in numeros_disponiveis]
                        numero = random.choices(numeros_disponiveis, weights=urgencias, k=1)[0]
                        selecionados.append(numero)
                        numeros_disponiveis.remove(numero)
                
                combinacao.extend(selecionados)
                combinacao.sort()
                
                if self.validate_intuition_constraints(combinacao):
                    combinacoes.append(combinacao)
        
        print(f"✅ {len(combinacoes)} combinações por ciclos geradas")
        return combinacoes
    
    def generate_balanced_combinations(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera combinações balanceadas (pares/ímpares, baixos/altos)
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"⚖️ Gerando {quantidade} combinações balanceadas...")
        
        combinacoes = []
        tentativas = 0
        max_tentativas = quantidade * 100
        
        while len(combinacoes) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            
            combinacao = list(self.numeros_obrigatorios)
            faltam = self.tamanho_combinacao - len(combinacao)
            
            if faltam > 0:
                # Categoriza números disponíveis
                disponiveis = [n for n in self.numeros_lotofacil if n not in self.numeros_proibidos and n not in combinacao]
                
                baixos = [n for n in disponiveis if n <= 12]  # 1-12
                altos = [n for n in disponiveis if n >= 13]   # 13-25
                pares = [n for n in disponiveis if n % 2 == 0]
                impares = [n for n in disponiveis if n % 2 == 1]
                
                # Tenta balancear
                selecionados = []
                
                # Distribui entre baixos e altos
                target_baixos = min(len(baixos), faltam // 2)
                target_altos = faltam - target_baixos
                
                if len(baixos) >= target_baixos and len(altos) >= target_altos:
                    selecionados.extend(random.sample(baixos, target_baixos))
                    selecionados.extend(random.sample(altos, target_altos))
                else:
                    # Se não conseguir balancear, usa seleção aleatória
                    selecionados = random.sample(disponiveis, min(faltam, len(disponiveis)))
                
                combinacao.extend(selecionados)
                combinacao.sort()
                
                if self.validate_intuition_constraints(combinacao):
                    # Verifica se está razoavelmente balanceada
                    pares_comb = len([n for n in combinacao if n % 2 == 0])
                    if 6 <= pares_comb <= 9:  # Entre 6 e 9 pares é um bom balanço
                        combinacoes.append(combinacao)
        
        print(f"✅ {len(combinacoes)} combinações balanceadas geradas")
        return combinacoes
    
    def generate_pattern_combinations(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera combinações baseadas em padrões simples
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🔍 Gerando {quantidade} combinações por padrões...")
        
        combinacoes = []
        
        # Padrões simples a testar
        padroes = [
            # Sequencial com saltos
            lambda: list(range(1, 16)),  # 1-15
            lambda: list(range(3, 18)),  # 3-17  
            lambda: list(range(5, 20)),  # 5-19
            lambda: list(range(8, 23)),  # 8-22
            lambda: list(range(11, 26)), # 11-25
            
            # Saltos de 2
            lambda: [i for i in range(1, 26) if i % 2 == 1][:15],  # Ímpares
            lambda: [i for i in range(2, 26) if i % 2 == 0][:15],  # Pares
            
            # Padrões matemáticos
            lambda: [1,2,3,5,8,13,21,4,7,11,18,6,10,16,25],  # Fibonacci modificado
            lambda: [2,3,5,7,11,13,17,19,23,1,4,6,8,9,10],   # Primos + complementos
        ]
        
        for i in range(quantidade):
            tentativas = 0
            while tentativas < 50:  # Limite de tentativas por combinação
                tentativas += 1
                
                # Escolhe padrão aleatório
                padrao = random.choice(padroes)
                base = padrao()
                
                # Adapta para restrições
                candidatos = [n for n in base if n not in self.numeros_proibidos]
                
                # Garante obrigatórios
                combinacao = list(self.numeros_obrigatorios)
                faltam = self.tamanho_combinacao - len(combinacao)
                
                # Remove obrigatórios dos candidatos
                candidatos = [n for n in candidatos if n not in combinacao]
                
                # Completa combinação
                if len(candidatos) >= faltam:
                    combinacao.extend(candidatos[:faltam])
                else:
                    # Completa com números aleatórios
                    disponiveis = [n for n in self.numeros_lotofacil 
                                 if n not in combinacao and n not in self.numeros_proibidos]
                    adicionar = min(faltam - len(candidatos), len(disponiveis))
                    combinacao.extend(candidatos)
                    combinacao.extend(random.sample(disponiveis, adicionar))
                
                combinacao = combinacao[:self.tamanho_combinacao]
                combinacao.sort()
                
                if len(combinacao) == self.tamanho_combinacao and self.validate_intuition_constraints(combinacao):
                    combinacoes.append(combinacao)
                    break
        
        print(f"✅ {len(combinacoes)} combinações por padrões geradas")
        return combinacoes
        
    def generate_quinas_based_combinations(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera combinações baseadas na análise de quinas usando Combin_Quinas (se disponível)
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🔍 Gerando {quantidade} combinações baseadas em quinas...")
        
        combinacoes = []
        
        # Verifica se existe a tabela Combin_Quinas da arquitetura completa
        if db_config.verificar_tabela_existe('Combin_Quinas'):
            print("   🎯 Usando análise da tabela Combin_Quinas")
            
            # Busca quinas com melhor performance ou mais frequentes
            query = """
            SELECT TOP 20 N1, N2, N3, N4, N5, 
                   ISNULL(FrequenciaAparicao, 0) as Freq,
                   ISNULL(UltimaAparicao, 999) as Ultima
            FROM Combin_Quinas
            WHERE N1 IS NOT NULL AND N2 IS NOT NULL AND N3 IS NOT NULL 
                  AND N4 IS NOT NULL AND N5 IS NOT NULL
            ORDER BY FrequenciaAparicao DESC, UltimaAparicao ASC
            """
            
            resultado = db_config.execute_query(query)
            
            if resultado and len(resultado) > 0:
                quinas_disponiveis = []
                for row in resultado:
                    quina = [row[0], row[1], row[2], row[3], row[4]]
                    # Valida se a quina atende às restrições
                    if not any(n in self.numeros_proibidos for n in quina):
                        quinas_disponiveis.append(quina)
                
                # Gera combinações expandindo as quinas
                for i in range(min(quantidade, len(quinas_disponiveis))):
                    quina = quinas_disponiveis[i]
                    
                    try:
                        expandidas = self.expand_quina_to_combination(quina, 1)
                        if expandidas:
                            combinacoes.extend(expandidas)
                    except:
                        # Se falhar na expansão, gera aleatória
                        pass
                
                # Completa com combinações aleatórias se necessário
                faltam = quantidade - len(combinacoes)
                if faltam > 0:
                    aleatorias = self.generate_random_combinations(faltam)
                    combinacoes.extend(aleatorias)
            
            else:
                print("   ⚠️ Dados de quinas não disponíveis, usando método alternativo")
                combinacoes = self.generate_frequency_based_combinations(quantidade)
        
        else:
            print("   💡 Tabela Combin_Quinas não encontrada, usando frequências")
            combinacoes = self.generate_frequency_based_combinations(quantidade)
        
        print(f"✅ {len(combinacoes)} combinações baseadas em quinas geradas")
        return combinacoes[:quantidade]
    
    def generate_positional_combinations(self, quantidade: int = 5) -> List[List[int]]:
        """
        Gera combinações usando análise posicional avançada
        Integra com o gerador posicional sofisticado
        
        Args:
            quantidade (int): Quantidade de combinações
            
        Returns:
            List[List[int]]: Lista de combinações
        """
        print(f"🎯 Gerando {quantidade} combinações posicionais avançadas...")
        
        try:
            # Importa o gerador posicional
            from gerador_posicional import gerar_combinacoes_posicionais
            
            combinacoes = gerar_combinacoes_posicionais(quantidade)
            
            # Aplica restrições de intuição se houver
            combinacoes_validas = []
            for comb in combinacoes:
                if self.validate_intuition_constraints(comb):
                    combinacoes_validas.append(comb)
            
            # Se não há combinações válidas, gera backup
            if not combinacoes_validas:
                print("⚠️ Nenhuma combinação posicional atende às restrições, gerando backup...")
                combinacoes_validas = self.generate_frequency_based_combinations(quantidade)
            
            print(f"✅ {len(combinacoes_validas)} combinações posicionais geradas")
            return combinacoes_validas[:quantidade]
            
        except ImportError:
            print("⚠️ Gerador posicional não disponível, usando método alternativo")
            return self.generate_balanced_combinations(quantidade)
        except Exception as e:
            print(f"❌ Erro no gerador posicional: {e}")
            print("🔄 Usando método de backup...")
            return self.generate_balanced_combinations(quantidade)
    
    def expand_quina_to_combination(self, quina: List[int], quantidade: int = 5) -> List[List[int]]:
        """
        Expande uma quina (5 números) para combinações completas (15 números)
        
        Args:
            quina (List[int]): Lista com 5 números
            quantidade (int): Quantas combinações gerar
            
        Returns:
            List[List[int]]: Lista de combinações completas
        """
        if len(quina) != 5:
            raise ValueError("Quina deve ter exatamente 5 números")
        
        print(f"🔧 Expandindo quina {quina} para {quantidade} combinações...")
        
        combinacoes = []
        
        # Números disponíveis (excluindo a quina e proibidos)
        disponiveis = [n for n in self.numeros_lotofacil 
                      if n not in quina and n not in self.numeros_proibidos]
        
        # Garante obrigatórios (se não estão na quina)
        obrigatorios_faltantes = [n for n in self.numeros_obrigatorios if n not in quina]
        
        for i in range(quantidade):
            combinacao = list(quina) + obrigatorios_faltantes
            faltam = self.tamanho_combinacao - len(combinacao)
            
            if faltam > 0:
                # Remove já selecionados dos disponíveis
                resto_disponiveis = [n for n in disponiveis if n not in combinacao]
                
                if len(resto_disponiveis) >= faltam:
                    adicionais = random.sample(resto_disponiveis, faltam)
                    combinacao.extend(adicionais)
                    combinacao.sort()
                    
                    if self.validate_intuition_constraints(combinacao):
                        combinacoes.append(combinacao)
        
        print(f"✅ {len(combinacoes)} combinações expandidas da quina")
        return combinacoes
    
    def salvar_combinacoes(self, combinacoes: List[List[int]], nome_arquivo: str = None):
        """
        Salva combinações em arquivo TXT
        
        Args:
            combinacoes (List[List[int]]): Lista de combinações
            nome_arquivo (str): Nome do arquivo (opcional)
        """
        if not combinacoes:
            print("⚠️ Nenhuma combinação para salvar")
            return
        
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_lotofacil_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("COMBINAÇÕES LOTOFÁCIL\n")
                f.write("=" * 50 + "\n")
                f.write(f"Geradas em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total: {len(combinacoes)} combinações\n")
                
                if self.numeros_obrigatorios:
                    f.write(f"Números obrigatórios: {sorted(self.numeros_obrigatorios)}\n")
                if self.numeros_proibidos:
                    f.write(f"Números proibidos: {sorted(self.numeros_proibidos)}\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
                
                for i, comb in enumerate(combinacoes, 1):
                    f.write(f"{i:2d}: {' '.join(f'{n:2d}' for n in comb)}\n")
            
            print(f"💾 Combinações salvas em: {nome_arquivo}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    print("🎯 TESTE DO GERADOR LOTOFÁCIL")
    print("=" * 50)
    
    generator = LotofacilGenerator()
    
    # Teste básico
    print("\n1. Combinações aleatórias:")
    aleatorias = generator.generate_random_combinations(3)
    for i, comb in enumerate(aleatorias, 1):
        print(f"   {i}: {comb}")
    
    print("\n2. Combinações balanceadas:")
    balanceadas = generator.generate_balanced_combinations(3)
    for i, comb in enumerate(balanceadas, 1):
        print(f"   {i}: {comb}")
    
    print("\n3. Teste com intuição:")
    generator.configure_intuition_numbers(obrigatorios=[8, 15], proibidos=[1, 25])
    com_intuicao = generator.generate_random_combinations(2)
    for i, comb in enumerate(com_intuicao, 1):
        print(f"   {i}: {comb}")
    
    # Salva exemplo
    todas = aleatorias + balanceadas + com_intuicao
    generator.salvar_combinacoes(todas, "teste_combinacoes.txt")
