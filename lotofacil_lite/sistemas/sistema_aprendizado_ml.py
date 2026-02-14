"""
SISTEMA DE APRENDIZADO COM MACHINE LEARNING (7.12 AVANÇADO)
===========================================================

Versão aprimorada do sistema de janela deslizante com algoritmos acadêmicos:

1. THOMPSON SAMPLING (Multi-Armed Bandit)
   - Seleciona estratégia com equilíbrio exploração/exploração
   - Garantia teórica de convergência para ótimo

2. UCB1 (Upper Confidence Bound)
   - Alternativa determinística ao Thompson Sampling
   - Bound otimista para exploração

3. EXP3 (Exponential-weight algorithm for Exploration and Exploitation)
   - Multi-Armed Bandit para ambientes adversariais
   - Robusto a mudanças de distribuição

4. BAYESIAN OPTIMIZATION (TPE - Tree Parzen Estimator)
   - Otimiza hiperparâmetros automaticamente
   - Surrogate model para menos avaliações

5. GENETIC ALGORITHM
   - Evolui combinações em vez de gerar aleatoriamente
   - Crossover, mutação e seleção natural

6. SIMULATED ANNEALING
   - Otimização global com escape de mínimos locais
   - Temperatura decrescente

7. REWARD SHAPING
   - Recompensa proporcional ao valor esperado
   - Não apenas binário (sucesso/falha)

8. ENSEMBLE LEARNING
   - Combina estratégias com pesos adaptativos
   - Votação ponderada por performance histórica

9. EXPONENTIAL MOVING AVERAGE (EMA)
   - Tracking de performance com peso recente
   - Detecta mudanças de regime

10. FEATURE IMPORTANCE
    - Identifica quais features mais impactam
    - Foco em números/padrões importantes

11. ANTIPIVO (Combinações Inversas) ⭐ NOVO
    - 10 números FORA do último resultado = FIXOS
    - 5 MELHORES por fitness ML completam
    - Taxa de acerto validada: 61% nos antipivo

Autor: LotoScope ML Module
Versão: 3.1 (ML-Enhanced com 11 algoritmos + ANTIPIVO)
"""

import json
import random
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field, asdict
import statistics

# Tentar importar scipy para distribuições
try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("⚠️ scipy não instalado. Usando implementação básica de Thompson Sampling.")

# Tentar importar numpy
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️ numpy não instalado. Usando implementação básica.")

# Importar pyodbc para banco
import pyodbc

# Constantes
PREMIO = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
CUSTO_APOSTA = 3.50
TODOS_NUMEROS = list(range(1, 26))

# Diretório base
_BASE_DIR = Path(__file__).parent


# ============================================================================
# CLASSES DE SUPORTE PARA ALGORITMOS ML
# ============================================================================

@dataclass
class ThompsonSamplingArm:
    """
    Braço do Multi-Armed Bandit usando Thompson Sampling com Beta distribution.
    
    Para problemas de reward binário (sucesso/falha), usamos Beta(α, β):
    - α = sucessos + 1 (prior)
    - β = falhas + 1 (prior)
    
    Para rewards contínuos, usamos Normal-Gamma conjugate prior.
    """
    name: str
    alpha: float = 1.0  # Sucessos + prior
    beta: float = 1.0   # Falhas + prior
    
    # Para reward contínuo (ROI)
    mu: float = 0.0           # Média estimada
    kappa: float = 1.0        # Força do prior na média
    alpha_ng: float = 1.0     # Shape do prior na variância
    beta_ng: float = 1.0      # Rate do prior na variância
    
    n_pulls: int = 0          # Total de vezes selecionado
    total_reward: float = 0.0 # Soma de rewards
    rewards_history: List[float] = field(default_factory=list)
    
    def sample_beta(self) -> float:
        """
        Amostra da distribuição Beta para reward binário.
        Retorna probabilidade estimada de sucesso.
        """
        if HAS_SCIPY:
            return scipy_stats.beta.rvs(self.alpha, self.beta)
        else:
            # Implementação básica usando método de inversão
            # Aproximação usando gamma
            x = random.gammavariate(self.alpha, 1)
            y = random.gammavariate(self.beta, 1)
            return x / (x + y) if (x + y) > 0 else 0.5
    
    def sample_normal_gamma(self) -> float:
        """
        Amostra da distribuição Normal-Gamma para reward contínuo.
        Retorna valor esperado amostrado.
        """
        if HAS_NUMPY:
            # Amostra precisão (tau) de Gamma
            tau = np.random.gamma(self.alpha_ng, 1.0 / self.beta_ng)
            # Amostra média de Normal
            sigma = 1.0 / np.sqrt(self.kappa * tau)
            return np.random.normal(self.mu, sigma)
        else:
            # Aproximação simples
            if self.n_pulls == 0:
                return random.gauss(0, 1)
            mean_reward = self.total_reward / self.n_pulls
            std = statistics.stdev(self.rewards_history) if len(self.rewards_history) > 1 else 1.0
            return random.gauss(mean_reward, std / math.sqrt(self.n_pulls + 1))
    
    def update_beta(self, success: bool):
        """Atualiza posterior Beta com novo resultado binário."""
        if success:
            self.alpha += 1
        else:
            self.beta += 1
        self.n_pulls += 1
    
    def update_continuous(self, reward: float):
        """
        Atualiza posterior Normal-Gamma com novo reward contínuo.
        Usando conjugate update rules.
        """
        self.n_pulls += 1
        self.total_reward += reward
        self.rewards_history.append(reward)
        
        # Keep only last 100 rewards for efficiency
        if len(self.rewards_history) > 100:
            self.rewards_history = self.rewards_history[-100:]
        
        # Update Normal-Gamma parameters
        n = len(self.rewards_history)
        if n > 0:
            x_bar = sum(self.rewards_history) / n
            
            # Update rules for Normal-Gamma
            kappa_n = self.kappa + n
            mu_n = (self.kappa * self.mu + n * x_bar) / kappa_n
            alpha_n = self.alpha_ng + n / 2
            
            # Compute sum of squared deviations
            ss = sum((x - x_bar) ** 2 for x in self.rewards_history)
            beta_n = self.beta_ng + 0.5 * ss + (self.kappa * n * (x_bar - self.mu) ** 2) / (2 * kappa_n)
            
            self.mu = mu_n
            self.kappa = kappa_n
            self.alpha_ng = alpha_n
            self.beta_ng = beta_n
    
    def get_expected_value(self) -> float:
        """Retorna valor esperado estimado."""
        if self.n_pulls == 0:
            return 0.0
        return self.total_reward / self.n_pulls


@dataclass
class BayesianOptimizer:
    """
    Otimizador Bayesiano simplificado para hiperparâmetros.
    
    Usa Tree-structured Parzen Estimator (TPE) simplificado.
    Divide observações em "boas" (top 25%) e "ruins" (rest).
    """
    param_name: str
    min_val: float
    max_val: float
    observations: List[Tuple[float, float]] = field(default_factory=list)  # (param_value, score)
    
    gamma: float = 0.25  # Percentil para dividir bom/ruim
    
    def suggest(self) -> float:
        """
        Sugere próximo valor do parâmetro.
        Usa TPE simplificado ou random se poucas observações.
        """
        if len(self.observations) < 10:
            # Exploração pura no início
            return random.uniform(self.min_val, self.max_val)
        
        # Ordenar por score (maior = melhor)
        sorted_obs = sorted(self.observations, key=lambda x: x[1], reverse=True)
        
        # Dividir em bons e ruins
        n_good = max(1, int(len(sorted_obs) * self.gamma))
        good_params = [x[0] for x in sorted_obs[:n_good]]
        bad_params = [x[0] for x in sorted_obs[n_good:]]
        
        # Estimar densidades (KDE simplificado como mixture of Gaussians)
        if HAS_NUMPY:
            # Amostrar da distribuição "boa"
            good_mean = np.mean(good_params)
            good_std = np.std(good_params) + 0.01 * (self.max_val - self.min_val)
            
            # Sample e clip
            sample = np.random.normal(good_mean, good_std)
            return float(np.clip(sample, self.min_val, self.max_val))
        else:
            # Versão sem numpy
            good_mean = sum(good_params) / len(good_params)
            good_std = statistics.stdev(good_params) if len(good_params) > 1 else (self.max_val - self.min_val) / 4
            
            sample = random.gauss(good_mean, good_std)
            return max(self.min_val, min(self.max_val, sample))
    
    def observe(self, value: float, score: float):
        """Registra observação de (valor, score)."""
        self.observations.append((value, score))
        
        # Manter últimas 200 observações
        if len(self.observations) > 200:
            self.observations = self.observations[-200:]


@dataclass  
class EnsembleWeight:
    """
    Peso para ensemble learning com decay exponencial.
    """
    strategy: str
    weight: float = 1.0
    performance_history: List[float] = field(default_factory=list)
    decay: float = 0.95  # Peso de observações antigas
    
    def update(self, performance: float):
        """Atualiza peso com nova performance."""
        self.performance_history.append(performance)
        
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]
        
        # Calcular média ponderada com decay exponencial
        if self.performance_history:
            weighted_sum = 0.0
            weight_sum = 0.0
            for i, perf in enumerate(self.performance_history):
                w = self.decay ** (len(self.performance_history) - 1 - i)
                weighted_sum += w * perf
                weight_sum += w
            
            self.weight = max(0.1, weighted_sum / weight_sum if weight_sum > 0 else 1.0)


@dataclass
class UCB1Arm:
    """
    Upper Confidence Bound (UCB1) - Alternativa determinística ao Thompson Sampling.
    
    UCB1 = média_observada + c * sqrt(2 * ln(n) / n_arm)
    
    Onde:
    - c = parâmetro de exploração
    - n = total de pulls (todas as estratégias)
    - n_arm = pulls deste braço
    
    Referência: Auer et al., 2002 - "Finite-time Analysis of the Multiarmed Bandit Problem"
    """
    name: str
    n_pulls: int = 0
    total_reward: float = 0.0
    exploration_param: float = 1.414  # sqrt(2) é teoricamente ótimo
    
    def get_ucb_value(self, total_pulls: int) -> float:
        """Calcula valor UCB1 para este braço."""
        if self.n_pulls == 0:
            return float('inf')  # Prioridade máxima para braços não testados
        
        mean_reward = self.total_reward / self.n_pulls
        exploration_bonus = self.exploration_param * math.sqrt(2 * math.log(total_pulls) / self.n_pulls)
        
        return mean_reward + exploration_bonus
    
    def update(self, reward: float):
        """Atualiza com novo reward."""
        self.n_pulls += 1
        self.total_reward += reward
    
    def get_mean(self) -> float:
        """Retorna média de rewards."""
        return self.total_reward / self.n_pulls if self.n_pulls > 0 else 0.0


@dataclass
class EXP3Arm:
    """
    EXP3 (Exponential-weight algorithm for Exploration and Exploitation).
    
    Algoritmo para Multi-Armed Bandit em ambientes adversariais.
    Robusto a mudanças de distribuição (não assume estacionariedade).
    
    Referência: Auer et al., 2002 - "The Nonstochastic Multiarmed Bandit Problem"
    """
    name: str
    weight: float = 1.0
    cumulative_reward: float = 0.0
    n_pulls: int = 0
    
    def get_probability(self, gamma: float, total_weight: float, n_arms: int) -> float:
        """
        Calcula probabilidade de selecionar este braço.
        
        P(arm) = (1-gamma) * (weight / total_weight) + gamma / n_arms
        """
        exploitation = (1 - gamma) * (self.weight / total_weight) if total_weight > 0 else 0
        exploration = gamma / n_arms
        return exploitation + exploration
    
    def update(self, reward: float, probability: float, gamma: float, n_arms: int):
        """
        Atualiza peso com reward observado.
        
        Usa importance sampling para reward não observado.
        """
        self.n_pulls += 1
        self.cumulative_reward += reward
        
        # Estimated reward (importance sampling)
        estimated_reward = reward / probability if probability > 0 else 0
        
        # Update weight
        self.weight *= math.exp(gamma * estimated_reward / n_arms)


@dataclass
class GeneticIndividual:
    """
    Indivíduo para Algoritmo Genético.
    
    Representa uma combinação de 15 números com fitness associado.
    """
    genes: List[int]  # 15 números
    fitness: float = 0.0
    generation: int = 0
    
    def mutate(self, mutation_rate: float = 0.1) -> 'GeneticIndividual':
        """
        Aplica mutação: troca alguns números por outros não presentes.
        """
        new_genes = self.genes.copy()
        
        for i in range(len(new_genes)):
            if random.random() < mutation_rate:
                # Trocar por número não presente
                available = [n for n in TODOS_NUMEROS if n not in new_genes]
                if available:
                    new_genes[i] = random.choice(available)
        
        return GeneticIndividual(genes=sorted(new_genes), generation=self.generation + 1)
    
    @staticmethod
    def crossover(parent1: 'GeneticIndividual', parent2: 'GeneticIndividual') -> 'GeneticIndividual':
        """
        Crossover de dois pais para gerar filho.
        
        Usa crossover uniforme: cada gene vem de um pai aleatório.
        """
        child_genes = set()
        
        # Pegar alguns de cada pai
        genes_p1 = set(parent1.genes)
        genes_p2 = set(parent2.genes)
        
        # Genes comuns vão direto
        common = genes_p1 & genes_p2
        child_genes.update(common)
        
        # Genes únicos: escolher aleatoriamente
        unique_p1 = genes_p1 - common
        unique_p2 = genes_p2 - common
        
        all_unique = list(unique_p1 | unique_p2)
        random.shuffle(all_unique)
        
        while len(child_genes) < 15 and all_unique:
            child_genes.add(all_unique.pop())
        
        # Se ainda faltar, completar com números aleatórios
        while len(child_genes) < 15:
            available = [n for n in TODOS_NUMEROS if n not in child_genes]
            if available:
                child_genes.add(random.choice(available))
        
        return GeneticIndividual(
            genes=sorted(list(child_genes))[:15],
            generation=max(parent1.generation, parent2.generation) + 1
        )


@dataclass
class SimulatedAnnealingState:
    """
    Estado para Simulated Annealing.
    
    Permite escape de mínimos locais através de temperatura decrescente.
    """
    current_solution: List[int]
    current_energy: float  # Negativo do fitness (minimizamos energia)
    best_solution: List[int] = None
    best_energy: float = float('inf')
    temperature: float = 100.0
    cooling_rate: float = 0.995
    min_temperature: float = 0.1
    iterations: int = 0
    
    def __post_init__(self):
        if self.best_solution is None:
            self.best_solution = self.current_solution.copy()
            self.best_energy = self.current_energy
    
    def accept_probability(self, new_energy: float) -> float:
        """
        Probabilidade de aceitar nova solução.
        
        Se melhor (menor energia): aceita sempre
        Se pior: aceita com probabilidade exp(-(new - current) / T)
        """
        if new_energy < self.current_energy:
            return 1.0
        
        if self.temperature <= 0:
            return 0.0
        
        return math.exp(-(new_energy - self.current_energy) / self.temperature)
    
    def step(self, new_solution: List[int], new_energy: float) -> bool:
        """
        Tenta dar um passo para nova solução.
        
        Returns: True se aceitou, False se rejeitou
        """
        self.iterations += 1
        
        if random.random() < self.accept_probability(new_energy):
            self.current_solution = new_solution
            self.current_energy = new_energy
            
            if new_energy < self.best_energy:
                self.best_solution = new_solution.copy()
                self.best_energy = new_energy
            
            return True
        
        return False
    
    def cool(self):
        """Reduz temperatura."""
        self.temperature = max(self.min_temperature, self.temperature * self.cooling_rate)


@dataclass
class ExponentialMovingAverage:
    """
    Exponential Moving Average (EMA) para tracking de performance.
    
    Detecta mudanças de regime rapidamente.
    """
    name: str
    alpha: float = 0.1  # Fator de suavização (maior = mais peso ao recente)
    ema_value: float = 0.0
    ema_variance: float = 0.0
    n_observations: int = 0
    history: List[float] = field(default_factory=list)
    
    def update(self, value: float):
        """Atualiza EMA com novo valor."""
        self.n_observations += 1
        self.history.append(value)
        
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        if self.n_observations == 1:
            self.ema_value = value
            self.ema_variance = 0.0
        else:
            # EMA do valor
            delta = value - self.ema_value
            self.ema_value += self.alpha * delta
            
            # EMA da variância (para detectar instabilidade)
            self.ema_variance = (1 - self.alpha) * (self.ema_variance + self.alpha * delta * delta)
    
    def get_trend(self) -> str:
        """Detecta tendência recente."""
        if len(self.history) < 10:
            return "indefinida"
        
        recent = self.history[-5:]
        older = self.history[-10:-5]
        
        recent_mean = sum(recent) / len(recent)
        older_mean = sum(older) / len(older)
        
        diff = recent_mean - older_mean
        threshold = math.sqrt(self.ema_variance) if self.ema_variance > 0 else 0.01
        
        if diff > threshold:
            return "subindo"
        elif diff < -threshold:
            return "descendo"
        else:
            return "estável"


@dataclass
class FeatureImportance:
    """
    Tracker de importância de features para identificar padrões vencedores.
    
    Rastreia quais números/padrões aparecem mais em combinações vencedoras.
    """
    # Importância de cada número (1-25)
    number_importance: Dict[int, float] = field(default_factory=lambda: {n: 0.0 for n in range(1, 26)})
    
    # Importância de pares de números
    pair_importance: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    # Importância de features (paridade, soma, etc)
    feature_importance: Dict[str, float] = field(default_factory=lambda: {
        'pares_7': 0.0,
        'pares_8': 0.0,
        'soma_baixa': 0.0,
        'soma_media': 0.0,
        'soma_alta': 0.0,
        'sequencia_longa': 0.0,
        'sem_sequencia': 0.0
    })
    
    n_observations: int = 0
    alpha: float = 0.05  # Learning rate
    
    def update_from_result(self, combo: List[int], acertos: int, resultado_real: List[int]):
        """
        Atualiza importância baseado em resultado.
        
        Números que estavam no resultado E na combo ganham pontos.
        Features da combo também são atualizadas.
        """
        self.n_observations += 1
        
        # Reward baseado em acertos (normalizado)
        reward = (acertos - 7.5) / 7.5  # -1 a +1
        
        # Atualizar importância de números
        combo_set = set(combo)
        resultado_set = set(resultado_real)
        
        for num in combo:
            if num in resultado_set:
                # Número estava correto
                self.number_importance[num] += self.alpha * (1 - self.number_importance[num])
            else:
                # Número estava errado
                self.number_importance[num] += self.alpha * (0 - self.number_importance[num])
        
        # Atualizar pares - OTIMIZADO: só atualiza pares com acertos
        # Para evitar O(n²) em cada combo, só rastreamos pares que acertaram
        acertos_list = list(combo_set & resultado_set)
        if len(acertos_list) >= 2:
            for i, n1 in enumerate(acertos_list):
                for n2 in acertos_list[i+1:]:
                    pair = (min(n1, n2), max(n1, n2))
                    if pair not in self.pair_importance:
                        self.pair_importance[pair] = 0.0
                    self.pair_importance[pair] += self.alpha * (1 - self.pair_importance[pair])
        
        # Atualizar features
        pares = sum(1 for n in combo if n % 2 == 0)
        soma = sum(combo)
        
        if pares == 7:
            self.feature_importance['pares_7'] += self.alpha * reward
        elif pares == 8:
            self.feature_importance['pares_8'] += self.alpha * reward
        
        if soma < 175:
            self.feature_importance['soma_baixa'] += self.alpha * reward
        elif soma > 205:
            self.feature_importance['soma_alta'] += self.alpha * reward
        else:
            self.feature_importance['soma_media'] += self.alpha * reward
    
    def get_top_numbers(self, n: int = 10) -> List[int]:
        """Retorna os N números mais importantes."""
        sorted_nums = sorted(self.number_importance.items(), key=lambda x: x[1], reverse=True)
        return [num for num, _ in sorted_nums[:n]]
    
    def get_top_pairs(self, n: int = 10) -> List[Tuple[int, int]]:
        """Retorna os N pares mais importantes."""
        if not self.pair_importance:
            return []
        sorted_pairs = sorted(self.pair_importance.items(), key=lambda x: x[1], reverse=True)
        return [pair for pair, _ in sorted_pairs[:n]]


# ============================================================================
# ALGORITMOS DE PATTERN MINING (Padrões Ocultos)
# ============================================================================

@dataclass
class AssociationRuleMiner:
    """
    Association Rule Mining AVANÇADO (Regras de Associação).
    
    VERSÃO 2.0 - Melhorias implementadas:
    1. Regras com antecedentes múltiplos: {X,Y} → Z
    2. Regras Negativas: X → ¬Y (se X aparece, Y NÃO aparece)
    3. Conviction metric: mede dependência real
    4. Zhang's Interest: detecta regras realmente interessantes
    5. Janela deslizante: baseado nos últimos N concursos
    6. Closed/Maximal Itemsets: reduz redundância
    7. Top-K por relevância configurável
    
    Métricas:
    - Support: P(X ∪ Y) - frequência do itemset
    - Confidence: P(Y|X) = P(X ∪ Y) / P(X)
    - Lift: P(Y|X) / P(Y) - quanto X aumenta prob de Y
    - Conviction: (1 - P(Y)) / (1 - Confidence) - dependência direcional
    - Zhang's Interest: (Confidence - P(Y)) / max(Confidence, P(Y)) * (1 - P(Y))
    
    Baseado no algoritmo Apriori (Agrawal & Srikant, 1994) + extensões.
    """
    # Suporte de cada número individual
    support: Dict[int, float] = field(default_factory=lambda: {n: 0.0 for n in range(1, 26)})
    
    # Suporte de pares (frequência de co-ocorrência)
    pair_support: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    # Suporte de triplas (padrões mais complexos)
    triple_support: Dict[Tuple[int, int, int], float] = field(default_factory=dict)
    
    # Suporte de NÃO co-ocorrência (para regras negativas)
    pair_negative_support: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    # Regras descobertas (antecedente -> consequente)
    rules: List[Dict] = field(default_factory=list)
    
    # Regras negativas (antecedente -> NÃO consequente)
    negative_rules: List[Dict] = field(default_factory=list)
    
    # Regras com antecedentes múltiplos {X,Y} -> Z
    multi_rules: List[Dict] = field(default_factory=list)
    
    # Contador de observações
    n_observations: int = 0
    min_support: float = 0.1
    min_confidence: float = 0.6
    
    # NOVO: Janela deslizante
    window_size: int = 500  # Últimos N concursos
    window_data: List[List[int]] = field(default_factory=list)
    
    # NOVO: Cache de suportes por janela
    window_support: Dict[int, float] = field(default_factory=lambda: {n: 0.0 for n in range(1, 26)})
    window_pair_support: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    def update(self, numeros: List[int]):
        """Atualiza suportes com novo resultado."""
        self.n_observations += 1
        
        # Adicionar à janela deslizante
        self.window_data.append(sorted(numeros))
        if len(self.window_data) > self.window_size:
            self.window_data.pop(0)
        
        # Atualizar suporte individual
        for n in numeros:
            self.support[n] = (self.support[n] * (self.n_observations - 1) + 1) / self.n_observations
        
        # Atualizar não-aparecimentos
        for n in range(1, 26):
            if n not in numeros:
                self.support[n] = (self.support[n] * (self.n_observations - 1)) / self.n_observations
        
        # Atualizar suporte de pares
        nums_sorted = sorted(numeros)
        for i, n1 in enumerate(nums_sorted):
            for n2 in nums_sorted[i+1:]:
                pair = (n1, n2)
                if pair not in self.pair_support:
                    self.pair_support[pair] = 0.0
                # Running average
                self.pair_support[pair] = (
                    (self.pair_support[pair] * (self.n_observations - 1) + 1) / self.n_observations
                )
        
        # Atualizar triplas (apenas top combinações para não explodir memória)
        if len(self.triple_support) < 5000:
            for i, n1 in enumerate(nums_sorted):
                for j, n2 in enumerate(nums_sorted[i+1:], i+1):
                    for n3 in nums_sorted[j+1:]:
                        triple = (n1, n2, n3)
                        if triple not in self.triple_support:
                            self.triple_support[triple] = 0.0
                        self.triple_support[triple] = (
                            (self.triple_support[triple] * (self.n_observations - 1) + 1) / self.n_observations
                        )
    
    def _recalculate_window_support(self):
        """Recalcula suportes baseado apenas na janela deslizante."""
        if not self.window_data:
            return
        
        n = len(self.window_data)
        
        # Reset
        self.window_support = {num: 0.0 for num in range(1, 26)}
        self.window_pair_support = {}
        
        # Contar
        for resultado in self.window_data:
            for num in resultado:
                self.window_support[num] += 1
            
            for i, n1 in enumerate(resultado):
                for n2 in resultado[i+1:]:
                    pair = (n1, n2)
                    self.window_pair_support[pair] = self.window_pair_support.get(pair, 0) + 1
        
        # Normalizar
        for num in self.window_support:
            self.window_support[num] /= n
        for pair in self.window_pair_support:
            self.window_pair_support[pair] /= n
    
    def _calculate_conviction(self, confidence: float, support_y: float) -> float:
        """
        Calcula Conviction: (1 - P(Y)) / (1 - Confidence)
        
        Conviction mede quanto a regra prediz Y vs o esperado aleatório.
        - Conviction = 1: X e Y são independentes
        - Conviction > 1: X implica Y (quanto maior, mais forte)
        - Conviction < 1: X implica ¬Y (regra negativa!)
        """
        if confidence >= 1.0:
            return float('inf')
        return (1 - support_y) / (1 - confidence)
    
    def _calculate_zhang_interest(self, confidence: float, support_y: float) -> float:
        """
        Calcula Zhang's Interest: medida simétrica de interesse.
        
        Varia de -1 a +1:
        - +1: perfeita associação positiva
        - 0: independência
        - -1: perfeita associação negativa
        """
        if support_y == 0 or support_y == 1:
            return 0.0
        
        max_val = max(confidence, support_y)
        if max_val == 0:
            return 0.0
        
        return (confidence - support_y) / max_val * (1 - support_y)
    
    def mine_rules(self, use_window: bool = False, top_k: int = 50) -> List[Dict]:
        """
        Extrai regras de associação significativas.
        
        Args:
            use_window: Se True, usa apenas dados da janela deslizante
            top_k: Número de regras a retornar
        """
        self.rules = []
        
        # Escolher fonte de dados
        if use_window and self.window_data:
            self._recalculate_window_support()
            support = self.window_support
            pair_support = self.window_pair_support
        else:
            support = self.support
            pair_support = self.pair_support
        
        # Regras de pares: Se X aparece -> Y aparece
        for (n1, n2), pair_sup in pair_support.items():
            if pair_sup < self.min_support:
                continue
            
            # Regra n1 -> n2
            if support[n1] > 0:
                confidence = pair_sup / support[n1]
                lift = confidence / support[n2] if support[n2] > 0 else 1.0
                conviction = self._calculate_conviction(confidence, support[n2])
                zhang = self._calculate_zhang_interest(confidence, support[n2])
                
                if confidence >= self.min_confidence:
                    self.rules.append({
                        'antecedent': [n1],
                        'consequent': [n2],
                        'support': pair_sup,
                        'confidence': confidence,
                        'lift': lift,
                        'conviction': conviction,
                        'zhang_interest': zhang,
                        'type': 'positive'
                    })
            
            # Regra n2 -> n1
            if support[n2] > 0:
                confidence = pair_sup / support[n2]
                lift = confidence / support[n1] if support[n1] > 0 else 1.0
                conviction = self._calculate_conviction(confidence, support[n1])
                zhang = self._calculate_zhang_interest(confidence, support[n1])
                
                if confidence >= self.min_confidence:
                    self.rules.append({
                        'antecedent': [n2],
                        'consequent': [n1],
                        'support': pair_sup,
                        'confidence': confidence,
                        'lift': lift,
                        'conviction': conviction,
                        'zhang_interest': zhang,
                        'type': 'positive'
                    })
        
        # Ordenar por lift (quanto maior, mais interessante)
        self.rules.sort(key=lambda x: x['lift'], reverse=True)
        
        return self.rules[:top_k]
    
    def mine_negative_rules(self, min_neg_confidence: float = 0.3, top_k: int = 30) -> List[Dict]:
        """
        Extrai regras NEGATIVAS: Se X aparece → Y NÃO aparece.
        
        Útil para identificar números que "se repelem".
        
        Cálculo correto:
        - P(Y NÃO aparece | X aparece) = 1 - P(Y aparece | X aparece)
        - P(Y aparece | X aparece) = P(X e Y aparecem) / P(X aparece)
        - Portanto: confidence_neg = 1 - (pair_support[X,Y] / support[X])
        """
        self.negative_rules = []
        
        # Para cada par de números
        for n1 in range(1, 26):
            if self.support[n1] <= 0:
                continue
                
            for n2 in range(1, 26):
                if n1 == n2:
                    continue
                
                # Obter suporte do par (ordenado)
                pair_key = (min(n1, n2), max(n1, n2))
                pair_sup = self.pair_support.get(pair_key, 0)
                
                # Calcular P(n2 aparece | n1 aparece)
                p_n2_given_n1 = pair_sup / self.support[n1] if self.support[n1] > 0 else 0
                
                # Confidence de n1 -> NOT n2
                confidence_neg = 1 - p_n2_given_n1
                
                # Lift negativo: comparado com P(NOT n2)
                p_not_n2 = 1 - self.support[n2]
                lift_neg = confidence_neg / p_not_n2 if p_not_n2 > 0 else 1.0
                
                # Regra interessante: confidence alta E lift > 1 (mais exclusão que o esperado)
                if confidence_neg >= min_neg_confidence and lift_neg > 1.05:
                    self.negative_rules.append({
                        'antecedent': [n1],
                        'consequent': [n2],  # NÃO consequente
                        'support': self.support[n1] * confidence_neg,  # P(n1 e NOT n2)
                        'confidence': confidence_neg,
                        'lift': lift_neg,
                        'type': 'negative',
                        'interpretation': f"Quando {n1} aparece, {n2} NÃO aparece em {confidence_neg*100:.1f}% dos casos"
                    })
        
        # Ordenar por lift (maior = mais exclusão)
        self.negative_rules.sort(key=lambda x: x['lift'], reverse=True)
        
        return self.negative_rules[:top_k]
    
    def mine_multi_antecedent_rules(self, top_k: int = 30) -> List[Dict]:
        """
        Extrai regras com antecedentes múltiplos: {X, Y} → Z
        
        Mais poderosas pois capturam interações entre números.
        """
        self.multi_rules = []
        
        # Usar triplas para extrair regras {n1, n2} -> n3
        for (n1, n2, n3), triple_sup in self.triple_support.items():
            if triple_sup < self.min_support * 0.5:  # Threshold menor para triplas
                continue
            
            # Calcular suporte do antecedente {n1, n2}
            pair_key = (n1, n2)
            if pair_key not in self.pair_support:
                continue
            
            ant_support = self.pair_support[pair_key]
            if ant_support < 0.01:
                continue
            
            # Regra {n1, n2} -> n3
            confidence = triple_sup / ant_support
            lift = confidence / self.support[n3] if self.support[n3] > 0 else 1.0
            conviction = self._calculate_conviction(confidence, self.support[n3])
            
            if confidence >= self.min_confidence * 0.8:  # Threshold menor
                self.multi_rules.append({
                    'antecedent': [n1, n2],
                    'consequent': [n3],
                    'support': triple_sup,
                    'confidence': confidence,
                    'lift': lift,
                    'conviction': conviction,
                    'type': 'multi_antecedent',
                    'interpretation': f"Se {{{n1}, {n2}}} aparecem → {n3} aparece ({confidence*100:.1f}%)"
                })
            
            # Regra {n1, n3} -> n2
            pair_key2 = (n1, n3)
            if pair_key2 in self.pair_support and self.pair_support[pair_key2] > 0.01:
                confidence2 = triple_sup / self.pair_support[pair_key2]
                lift2 = confidence2 / self.support[n2] if self.support[n2] > 0 else 1.0
                conviction2 = self._calculate_conviction(confidence2, self.support[n2])
                
                if confidence2 >= self.min_confidence * 0.8:
                    self.multi_rules.append({
                        'antecedent': [n1, n3],
                        'consequent': [n2],
                        'support': triple_sup,
                        'confidence': confidence2,
                        'lift': lift2,
                        'conviction': conviction2,
                        'type': 'multi_antecedent',
                        'interpretation': f"Se {{{n1}, {n3}}} aparecem → {n2} aparece ({confidence2*100:.1f}%)"
                    })
            
            # Regra {n2, n3} -> n1
            pair_key3 = (n2, n3)
            if pair_key3 in self.pair_support and self.pair_support[pair_key3] > 0.01:
                confidence3 = triple_sup / self.pair_support[pair_key3]
                lift3 = confidence3 / self.support[n1] if self.support[n1] > 0 else 1.0
                conviction3 = self._calculate_conviction(confidence3, self.support[n1])
                
                if confidence3 >= self.min_confidence * 0.8:
                    self.multi_rules.append({
                        'antecedent': [n2, n3],
                        'consequent': [n1],
                        'support': triple_sup,
                        'confidence': confidence3,
                        'lift': lift3,
                        'conviction': conviction3,
                        'type': 'multi_antecedent',
                        'interpretation': f"Se {{{n2}, {n3}}} aparecem → {n1} aparece ({confidence3*100:.1f}%)"
                    })
        
        # Ordenar por lift
        self.multi_rules.sort(key=lambda x: x['lift'], reverse=True)
        
        # Remover duplicatas
        seen = set()
        unique_rules = []
        for rule in self.multi_rules:
            key = (tuple(rule['antecedent']), tuple(rule['consequent']))
            if key not in seen:
                seen.add(key)
                unique_rules.append(rule)
        
        self.multi_rules = unique_rules
        return self.multi_rules[:top_k]
    
    def get_all_rules_ranked(self, top_k: int = 100) -> List[Dict]:
        """
        Retorna todas as regras (positivas, negativas, multi) rankeadas por relevância.
        
        Score combinado: lift * conviction * (1 + zhang_interest)
        """
        all_rules = []
        
        # Minerar todas
        self.mine_rules()
        self.mine_negative_rules()
        self.mine_multi_antecedent_rules()
        
        # Combinar
        for rule in self.rules:
            rule['combined_score'] = rule['lift'] * min(rule['conviction'], 10) * (1 + rule.get('zhang_interest', 0))
            all_rules.append(rule)
        
        for rule in self.negative_rules:
            rule['combined_score'] = rule['lift'] * 2  # Bonus para negativas
            all_rules.append(rule)
        
        for rule in self.multi_rules:
            rule['combined_score'] = rule['lift'] * min(rule['conviction'], 10) * 1.5  # Bonus para multi
            all_rules.append(rule)
        
        # Ordenar por score combinado
        all_rules.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        
        return all_rules[:top_k]
    
    def get_recommendations(self, numeros_presentes: List[int], n: int = 5) -> List[Tuple[int, float]]:
        """
        Dado números já escolhidos, recomenda próximos baseado em regras.
        MELHORADO: Usa todas as regras (positivas + multi) e evita negativos.
        """
        scores = defaultdict(float)
        avoid_scores = defaultdict(float)
        
        # Usar regras positivas simples
        for num in numeros_presentes:
            for rule in self.rules:
                if num in rule['antecedent']:
                    for conseq in rule['consequent']:
                        if conseq not in numeros_presentes:
                            scores[conseq] += rule['lift'] * rule['confidence']
        
        # Usar regras multi-antecedente (mais peso)
        for rule in self.multi_rules:
            if all(n in numeros_presentes for n in rule['antecedent']):
                for conseq in rule['consequent']:
                    if conseq not in numeros_presentes:
                        scores[conseq] += rule['lift'] * rule['confidence'] * 1.5
        
        # Penalizar baseado em regras negativas
        for rule in self.negative_rules:
            if any(n in numeros_presentes for n in rule['antecedent']):
                for conseq in rule['consequent']:
                    avoid_scores[conseq] += rule['lift'] * 0.3
        
        # Score final = positivo - penalidade
        final_scores = {}
        for num in range(1, 26):
            if num not in numeros_presentes:
                final_scores[num] = scores.get(num, 0) - avoid_scores.get(num, 0)
        
        sorted_recs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:n]
    
    def get_numbers_to_avoid(self, numeros_presentes: List[int], n: int = 5) -> List[Tuple[int, float]]:
        """
        Retorna números que devem ser EVITADOS dado os números presentes.
        Baseado em regras negativas.
        """
        avoid_scores = defaultdict(float)
        
        for rule in self.negative_rules:
            if any(num in numeros_presentes for num in rule['antecedent']):
                for conseq in rule['consequent']:
                    if conseq not in numeros_presentes:
                        avoid_scores[conseq] += rule['lift'] * rule['confidence']
        
        sorted_avoid = sorted(avoid_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_avoid[:n]
    
    def generate_combination_from_rules(self, seed_numbers: List[int] = None) -> List[int]:
        """
        NOVO: Gera uma combinação de 15 números baseada nas regras.
        
        Estratégia:
        1. Começa com seed ou números mais frequentes
        2. Adiciona números recomendados por regras
        3. Evita números com regras negativas
        4. Completa com números de alta probabilidade
        """
        if seed_numbers:
            combo = list(seed_numbers)[:5]  # Max 5 seeds
        else:
            # Usar top 5 números por suporte
            top_support = sorted(self.support.items(), key=lambda x: x[1], reverse=True)[:5]
            combo = [n for n, _ in top_support]
        
        combo = list(set(combo))  # Remover duplicatas
        
        # Números a evitar
        avoid = set()
        
        # Expandir usando regras
        max_iterations = 20
        iteration = 0
        
        while len(combo) < 15 and iteration < max_iterations:
            iteration += 1
            
            # Obter recomendações
            recs = self.get_recommendations(combo, n=10)
            to_avoid = self.get_numbers_to_avoid(combo, n=5)
            
            # Atualizar avoid set
            for num, score in to_avoid:
                if score > 0.5:
                    avoid.add(num)
            
            # Adicionar melhor recomendação que não está em avoid
            added = False
            for num, score in recs:
                if num not in combo and num not in avoid:
                    combo.append(num)
                    added = True
                    break
            
            # Se não conseguiu adicionar, pegar qualquer número fora
            if not added:
                remaining = [n for n in range(1, 26) if n not in combo and n not in avoid]
                if remaining:
                    # Ordenar por suporte
                    remaining.sort(key=lambda x: self.support[x], reverse=True)
                    combo.append(remaining[0])
                else:
                    # Último recurso: qualquer número
                    remaining = [n for n in range(1, 26) if n not in combo]
                    if remaining:
                        combo.append(remaining[0])
        
        return sorted(combo)[:15]
    
    def generate_multiple_combinations(self, quantidade: int = 10, diversidade: float = 0.3) -> List[List[int]]:
        """
        Gera múltiplas combinações com diversidade controlada.
        
        Args:
            quantidade: Número de combinações a gerar
            diversidade: 0.0 = todas similares, 1.0 = máxima diversidade
        """
        combinacoes = []
        usados_como_seed = set()
        
        for i in range(quantidade):
            # Variar seeds para diversidade
            if diversidade > 0 and i > 0:
                # Escolher seeds diferentes
                top_nums = sorted(self.support.items(), key=lambda x: x[1], reverse=True)[:15]
                available_seeds = [n for n, _ in top_nums if n not in usados_como_seed]
                
                if available_seeds and random.random() < diversidade:
                    seed = random.sample(available_seeds, min(3, len(available_seeds)))
                    usados_como_seed.update(seed)
                else:
                    seed = None
            else:
                seed = None
            
            combo = self.generate_combination_from_rules(seed)
            
            # Evitar duplicatas
            if combo not in combinacoes:
                combinacoes.append(combo)
            
            # Reset usados se já usou muitos
            if len(usados_como_seed) > 20:
                usados_como_seed.clear()
        
        return combinacoes
    
    def get_rule_summary(self) -> Dict:
        """Retorna resumo estatístico das regras descobertas."""
        self.mine_rules()
        self.mine_negative_rules()
        self.mine_multi_antecedent_rules()
        
        return {
            'n_observations': self.n_observations,
            'window_size': len(self.window_data),
            'n_positive_rules': len(self.rules),
            'n_negative_rules': len(self.negative_rules),
            'n_multi_rules': len(self.multi_rules),
            'n_pairs_tracked': len(self.pair_support),
            'n_triples_tracked': len(self.triple_support),
            'avg_confidence_positive': sum(r['confidence'] for r in self.rules) / len(self.rules) if self.rules else 0,
            'avg_lift_positive': sum(r['lift'] for r in self.rules) / len(self.rules) if self.rules else 0,
            'top_rule_positive': self.rules[0] if self.rules else None,
            'top_rule_negative': self.negative_rules[0] if self.negative_rules else None,
            'top_rule_multi': self.multi_rules[0] if self.multi_rules else None
        }


@dataclass
class SequentialPatternMiner:
    """
    Sequential Pattern Mining (Padrões Sequenciais).
    
    Encontra padrões temporais: "Depois que X aparece, Y tende a aparecer no próximo sorteio"
    Baseado em GSP (Generalized Sequential Patterns) - Srikant & Agrawal, 1996.
    """
    # Transições: número X -> números que aparecem depois
    transitions: Dict[int, Dict[int, int]] = field(default_factory=lambda: {
        n: defaultdict(int) for n in range(1, 26)
    })
    
    # Sequências de 2: (X no t) -> (Y no t+1)
    seq2_count: Dict[Tuple[int, int], int] = field(default_factory=lambda: defaultdict(int))
    
    # Gaps: Quantos sorteios até X reaparecer após aparecer
    reappearance_gaps: Dict[int, List[int]] = field(default_factory=lambda: {
        n: [] for n in range(1, 26)
    })
    
    # Último sorteio em que cada número apareceu
    last_seen: Dict[int, int] = field(default_factory=lambda: {n: -1 for n in range(1, 26)})
    
    # Contador de sorteios
    n_sorteios: int = 0
    
    # Memória do último resultado
    ultimo_resultado: List[int] = field(default_factory=list)
    
    def update(self, numeros: List[int]):
        """Atualiza padrões sequenciais com novo resultado."""
        self.n_sorteios += 1
        
        # Atualizar transições do resultado anterior
        if self.ultimo_resultado:
            for prev_num in self.ultimo_resultado:
                for curr_num in numeros:
                    self.transitions[prev_num][curr_num] += 1
                    self.seq2_count[(prev_num, curr_num)] += 1
        
        # Atualizar gaps de reaparecimento
        for num in numeros:
            if self.last_seen[num] >= 0:
                gap = self.n_sorteios - self.last_seen[num]
                self.reappearance_gaps[num].append(gap)
                # Manter só últimos 100
                if len(self.reappearance_gaps[num]) > 100:
                    self.reappearance_gaps[num] = self.reappearance_gaps[num][-100:]
            
            self.last_seen[num] = self.n_sorteios
        
        self.ultimo_resultado = numeros.copy()
    
    def get_likely_next(self, ultimo_resultado: List[int], n: int = 10) -> List[Tuple[int, float]]:
        """
        Prediz números mais prováveis no próximo sorteio baseado em padrões sequenciais.
        """
        scores = defaultdict(float)
        
        for prev_num in ultimo_resultado:
            trans = self.transitions[prev_num]
            total = sum(trans.values()) or 1
            
            for next_num, count in trans.items():
                prob = count / total
                scores[next_num] += prob
        
        # Normalizar
        if scores:
            max_score = max(scores.values())
            scores = {k: v / max_score for k, v in scores.items()}
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:n]
    
    def get_due_numbers(self, n: int = 10) -> List[Tuple[int, float]]:
        """
        Identifica números "devidos" baseado em gaps médios de reaparecimento.
        """
        due_scores = {}
        
        for num in range(1, 26):
            gaps = self.reappearance_gaps[num]
            if len(gaps) >= 5:
                avg_gap = sum(gaps) / len(gaps)
                current_gap = self.n_sorteios - self.last_seen[num]
                
                # Score: quanto maior o gap atual vs média, mais "devido"
                if avg_gap > 0:
                    due_scores[num] = current_gap / avg_gap
        
        sorted_due = sorted(due_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_due[:n]


@dataclass
class ClusterAnalyzer:
    """
    Cluster Analysis para agrupar sorteios similares.
    
    Identifica "tipos" de sorteios baseado em características:
    - Paridade (pares/ímpares)
    - Soma total
    - Distribuição por dezenas
    - Sequências consecutivas
    
    Usa K-Means simplificado para clustering.
    """
    # Centroides dos clusters (cada cluster tem características médias)
    n_clusters: int = 5
    centroids: List[Dict] = field(default_factory=list)
    
    # Histórico de features de cada sorteio
    feature_history: List[Dict] = field(default_factory=list)
    
    # Atribuição de cluster para cada sorteio
    cluster_assignments: List[int] = field(default_factory=list)
    
    # Contagem de sorteios por cluster
    cluster_counts: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    
    def extract_features(self, numeros: List[int]) -> Dict:
        """Extrai features de um sorteio para clustering."""
        return {
            'pares': sum(1 for n in numeros if n % 2 == 0),
            'soma': sum(numeros),
            'dezena_0_5': sum(1 for n in numeros if 1 <= n <= 5),
            'dezena_6_10': sum(1 for n in numeros if 6 <= n <= 10),
            'dezena_11_15': sum(1 for n in numeros if 11 <= n <= 15),
            'dezena_16_20': sum(1 for n in numeros if 16 <= n <= 20),
            'dezena_21_25': sum(1 for n in numeros if 21 <= n <= 25),
            'consecutivos': self._count_consecutivos(numeros),
            'amplitude': max(numeros) - min(numeros)
        }
    
    def _count_consecutivos(self, numeros: List[int]) -> int:
        """Conta pares de números consecutivos."""
        sorted_nums = sorted(numeros)
        return sum(1 for i in range(len(sorted_nums)-1) if sorted_nums[i+1] - sorted_nums[i] == 1)
    
    def update(self, numeros: List[int]):
        """Adiciona novo sorteio e atualiza clusters."""
        features = self.extract_features(numeros)
        self.feature_history.append(features)
        
        # Atribuir ao cluster mais próximo
        if self.centroids:
            cluster = self._find_nearest_cluster(features)
            self.cluster_assignments.append(cluster)
            self.cluster_counts[cluster] += 1
            
            # Atualizar centroide (running mean)
            self._update_centroid(cluster, features)
        else:
            self.cluster_assignments.append(0)
            self.cluster_counts[0] += 1
        
        # Recalcular centroides periodicamente
        if len(self.feature_history) % 100 == 0:
            self._recalculate_centroids()
    
    def _find_nearest_cluster(self, features: Dict) -> int:
        """Encontra cluster mais próximo usando distância euclidiana."""
        min_dist = float('inf')
        nearest = 0
        
        for i, centroid in enumerate(self.centroids):
            dist = sum((features.get(k, 0) - centroid.get(k, 0))**2 for k in features)
            if dist < min_dist:
                min_dist = dist
                nearest = i
        
        return nearest
    
    def _update_centroid(self, cluster: int, features: Dict):
        """Atualiza centroide com running mean."""
        if cluster < len(self.centroids):
            n = self.cluster_counts[cluster]
            for k, v in features.items():
                old = self.centroids[cluster].get(k, 0)
                self.centroids[cluster][k] = old + (v - old) / n
    
    def _recalculate_centroids(self):
        """Recalcula centroides usando K-Means simplificado."""
        if len(self.feature_history) < self.n_clusters * 10:
            # Não há dados suficientes
            if not self.centroids:
                # Inicializar com primeiros N sorteios
                self.centroids = [self.feature_history[i].copy() 
                                 for i in range(min(self.n_clusters, len(self.feature_history)))]
            return
        
        # K-Means com 5 iterações
        for _ in range(5):
            # Atribuir cada ponto ao cluster mais próximo
            new_assignments = []
            for features in self.feature_history:
                cluster = self._find_nearest_cluster(features)
                new_assignments.append(cluster)
            
            # Recalcular centroides
            for c in range(self.n_clusters):
                cluster_features = [
                    self.feature_history[i] for i, assignment in enumerate(new_assignments) 
                    if assignment == c
                ]
                if cluster_features:
                    # Média de cada feature
                    new_centroid = {}
                    for key in cluster_features[0].keys():
                        new_centroid[key] = sum(f[key] for f in cluster_features) / len(cluster_features)
                    if c < len(self.centroids):
                        self.centroids[c] = new_centroid
                    else:
                        self.centroids.append(new_centroid)
            
            self.cluster_assignments = new_assignments
    
    def get_cluster_profile(self, cluster: int) -> Dict:
        """Retorna perfil de um cluster."""
        if cluster >= len(self.centroids):
            return {}
        return self.centroids[cluster]
    
    def get_dominant_cluster(self) -> int:
        """Retorna cluster mais frequente."""
        if not self.cluster_counts:
            return 0
        return max(self.cluster_counts, key=self.cluster_counts.get)


@dataclass
class AnomalyDetector:
    """
    Anomaly Detection para identificar sorteios "anômalos".
    
    Usa Isolation Forest simplificado + Z-Score para detectar outliers.
    Sorteios anômalos podem indicar padrões interessantes.
    """
    # Estatísticas de features para Z-Score
    feature_means: Dict[str, float] = field(default_factory=dict)
    feature_stds: Dict[str, float] = field(default_factory=dict)
    feature_history: List[Dict] = field(default_factory=list)
    
    # Anomalias detectadas
    anomalies: List[Dict] = field(default_factory=list)
    
    # Threshold para considerar anomalia (em desvios padrão)
    threshold: float = 2.5
    
    def extract_features(self, numeros: List[int]) -> Dict:
        """Extrai features para detecção de anomalias."""
        sorted_nums = sorted(numeros)
        
        return {
            'soma': sum(numeros),
            'pares': sum(1 for n in numeros if n % 2 == 0),
            'consecutivos': sum(1 for i in range(len(sorted_nums)-1) 
                              if sorted_nums[i+1] - sorted_nums[i] == 1),
            'gaps_max': max(sorted_nums[i+1] - sorted_nums[i] 
                          for i in range(len(sorted_nums)-1)),
            'baixos_1_8': sum(1 for n in numeros if n <= 8),
            'altos_18_25': sum(1 for n in numeros if n >= 18),
            'centro_9_17': sum(1 for n in numeros if 9 <= n <= 17)
        }
    
    def update(self, numeros: List[int], concurso: int = 0):
        """Atualiza estatísticas e detecta anomalias."""
        features = self.extract_features(numeros)
        self.feature_history.append(features)
        
        # Atualizar médias e desvios (running statistics)
        n = len(self.feature_history)
        
        for key, value in features.items():
            if key not in self.feature_means:
                self.feature_means[key] = value
                self.feature_stds[key] = 0.0
            else:
                old_mean = self.feature_means[key]
                self.feature_means[key] = old_mean + (value - old_mean) / n
                
                # Welford's algorithm para variância
                if n > 1:
                    old_std = self.feature_stds[key]
                    self.feature_stds[key] = math.sqrt(
                        ((n - 2) * old_std**2 + (value - old_mean) * (value - self.feature_means[key])) / (n - 1)
                    ) if n > 2 else abs(value - self.feature_means[key])
        
        # Calcular anomaly score
        if n > 30:  # Precisa de histórico mínimo
            anomaly_score = self._calculate_anomaly_score(features)
            
            if anomaly_score > self.threshold:
                self.anomalies.append({
                    'concurso': concurso,
                    'numeros': numeros,
                    'score': anomaly_score,
                    'features': features
                })
                
                # Manter só últimas 50 anomalias
                if len(self.anomalies) > 50:
                    self.anomalies = self.anomalies[-50:]
    
    def _calculate_anomaly_score(self, features: Dict) -> float:
        """Calcula score de anomalia usando Z-Score multivariado."""
        z_scores = []
        
        for key, value in features.items():
            mean = self.feature_means.get(key, value)
            std = self.feature_stds.get(key, 1.0)
            
            if std > 0:
                z = abs(value - mean) / std
                z_scores.append(z)
        
        # Média dos Z-Scores (Mahalanobis simplificado)
        return sum(z_scores) / len(z_scores) if z_scores else 0.0
    
    def get_recent_anomalies(self, n: int = 10) -> List[Dict]:
        """Retorna anomalias recentes."""
        return self.anomalies[-n:]
    
    def is_anomalous(self, numeros: List[int]) -> Tuple[bool, float]:
        """Verifica se um sorteio é anômalo."""
        features = self.extract_features(numeros)
        score = self._calculate_anomaly_score(features)
        return score > self.threshold, score


@dataclass
class MotifDiscovery:
    """
    Motif Discovery para encontrar padrões recorrentes.
    
    Identifica "motifs" - subsequências que aparecem com frequência incomum.
    Similar ao que é usado em análise de séries temporais (Matrix Profile).
    """
    # Padrões de 3 números que aparecem juntos frequentemente
    motifs_3: Dict[Tuple[int, int, int], int] = field(default_factory=lambda: defaultdict(int))
    
    # Padrões de paridade (sequência de par/ímpar)
    parity_patterns: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Padrões de gaps entre números
    gap_patterns: Dict[Tuple, int] = field(default_factory=lambda: defaultdict(int))
    
    # Total de observações
    n_observations: int = 0
    
    def update(self, numeros: List[int]):
        """Atualiza contagem de padrões."""
        self.n_observations += 1
        sorted_nums = sorted(numeros)
        
        # Padrões de 3 números
        for i in range(len(sorted_nums) - 2):
            motif = (sorted_nums[i], sorted_nums[i+1], sorted_nums[i+2])
            self.motifs_3[motif] += 1
        
        # Padrão de paridade (primeiro 8 números)
        parity = ''.join('P' if n % 2 == 0 else 'I' for n in sorted_nums[:8])
        self.parity_patterns[parity] += 1
        
        # Padrão de gaps (primeiros 5 gaps)
        gaps = tuple(sorted_nums[i+1] - sorted_nums[i] for i in range(min(5, len(sorted_nums)-1)))
        self.gap_patterns[gaps] += 1
    
    def get_frequent_motifs(self, n: int = 20) -> List[Tuple[Tuple, float]]:
        """Retorna motifs mais frequentes com suas probabilidades."""
        if not self.motifs_3 or self.n_observations == 0:
            return []
        
        sorted_motifs = sorted(self.motifs_3.items(), key=lambda x: x[1], reverse=True)
        
        return [(motif, count / self.n_observations) for motif, count in sorted_motifs[:n]]
    
    def get_parity_patterns(self, n: int = 10) -> List[Tuple[str, float]]:
        """Retorna padrões de paridade mais frequentes."""
        if not self.parity_patterns or self.n_observations == 0:
            return []
        
        sorted_patterns = sorted(self.parity_patterns.items(), key=lambda x: x[1], reverse=True)
        
        return [(pattern, count / self.n_observations) for pattern, count in sorted_patterns[:n]]
    
    def suggest_completion(self, partial: List[int], n: int = 5) -> List[int]:
        """Sugere números para completar baseado em motifs frequentes."""
        suggestions = defaultdict(float)
        
        partial_sorted = sorted(partial)
        
        # Buscar motifs que começam com números do parcial
        for motif, count in self.motifs_3.items():
            # Verificar se o parcial "encaixa" no início do motif
            if len(partial_sorted) >= 2:
                if motif[0] in partial_sorted and motif[1] in partial_sorted:
                    if motif[2] not in partial_sorted:
                        suggestions[motif[2]] += count
        
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return [num for num, _ in sorted_suggestions[:n]]


# ============================================================================
# SISTEMA PRINCIPAL COM ML
# ============================================================================

class SistemaAprendizadoML:
    """
    Sistema de aprendizado com algoritmos de Machine Learning.
    
    Melhorias sobre o sistema básico:
    1. Thompson Sampling para seleção de estratégia
    2. Bayesian Optimization para hiperparâmetros
    3. Reward shaping com valor esperado
    4. Ensemble learning com pesos adaptativos
    5. Feature engineering avançado
    """
    
    def __init__(self, tamanho_janela: int = 30, combos_por_estrategia: int = 5):
        self.tamanho_janela = tamanho_janela
        self.combos_por_estrategia = combos_por_estrategia
        self.historico_completo = []
        self.total_concursos = 0
        
        # Arquivo de aprendizado ML
        self.arquivo_aprendizado = _BASE_DIR / "aprendizado_ml.json"
        
        # Inicializar componentes ML
        self._inicializar_ml()
        
        # Carregar aprendizado salvo
        self._carregar_aprendizado()
        
        # Estatísticas da sessão
        self._resetar_stats_sessao()
    
    def _inicializar_ml(self):
        """Inicializa componentes de ML."""
        # ===== MULTI-ARMED BANDIT ALGORITHMS =====
        
        # 1. Thompson Sampling para cada estratégia
        self.bandits = {
            'atrasados': ThompsonSamplingArm(name='atrasados'),
            'quentes': ThompsonSamplingArm(name='quentes'),
            'equilibrada': ThompsonSamplingArm(name='equilibrada')
        }
        
        # 2. UCB1 (Upper Confidence Bound)
        self.ucb_arms = {
            'atrasados': UCB1Arm(name='atrasados'),
            'quentes': UCB1Arm(name='quentes'),
            'equilibrada': UCB1Arm(name='equilibrada')
        }
        
        # 3. EXP3 (Adversarial Bandit)
        self.exp3_arms = {
            'atrasados': EXP3Arm(name='atrasados'),
            'quentes': EXP3Arm(name='quentes'),
            'equilibrada': EXP3Arm(name='equilibrada')
        }
        self.exp3_gamma = 0.1  # Parâmetro de exploração EXP3
        
        # ===== OPTIMIZATION ALGORITHMS =====
        
        # 4. Otimizadores Bayesianos para hiperparâmetros
        self.optimizers = {
            'limite_atraso_minimo': BayesianOptimizer('limite_atraso_minimo', 2, 10),
            'limite_frequencia_quente': BayesianOptimizer('limite_frequencia_quente', 0.4, 0.8),
            'peso_atrasados_mix': BayesianOptimizer('peso_atrasados_mix', 3, 8),
            'peso_quentes_mix': BayesianOptimizer('peso_quentes_mix', 3, 8)
        }
        
        # 5. Genetic Algorithm
        self.genetic_population: List[GeneticIndividual] = []
        self.genetic_population_size = 50
        self.genetic_mutation_rate = 0.15
        self.genetic_elite_ratio = 0.2
        
        # 6. Simulated Annealing
        initial_combo = sorted(random.sample(TODOS_NUMEROS, 15))
        self.simulated_annealing = SimulatedAnnealingState(
            current_solution=initial_combo,
            current_energy=0.0
        )
        
        # ===== TRACKING ALGORITHMS =====
        
        # 7. Ensemble weights
        self.ensemble_weights = {
            'atrasados': EnsembleWeight('atrasados'),
            'quentes': EnsembleWeight('quentes'),
            'equilibrada': EnsembleWeight('equilibrada')
        }
        
        # 8. Exponential Moving Average por estratégia
        self.ema_trackers = {
            'atrasados': ExponentialMovingAverage(name='atrasados', alpha=0.1),
            'quentes': ExponentialMovingAverage(name='quentes', alpha=0.1),
            'equilibrada': ExponentialMovingAverage(name='equilibrada', alpha=0.1)
        }
        
        # 9. Feature Importance
        self.feature_tracker = FeatureImportance()
        
        # ===== PATTERN MINING ALGORITHMS (Padrões Ocultos) =====
        
        # 10. Association Rules - Regras de associação (Apriori)
        self.association_miner = AssociationRuleMiner()
        
        # 11. Sequential Patterns - Padrões temporais
        self.sequential_miner = SequentialPatternMiner()
        
        # 12. Cluster Analysis - Agrupamento de sorteios
        self.cluster_analyzer = ClusterAnalyzer()
        
        # 13. Anomaly Detection - Detecção de outliers
        self.anomaly_detector = AnomalyDetector()
        
        # 14. Motif Discovery - Padrões recorrentes
        self.motif_miner = MotifDiscovery()
        
        # ===== ALGORITHM SELECTION =====
        
        # Meta-algoritmo para escolher qual algoritmo usar
        self.bandit_algorithm = 'thompson'  # 'thompson', 'ucb1', 'exp3', 'ensemble'
        self.algorithm_performance = {
            'thompson': [],
            'ucb1': [],
            'exp3': [],
            'ensemble': []
        }
        
        # Hiperparâmetros atuais
        self.hyperparams = {
            'limite_atraso_minimo': 5,
            'limite_frequencia_quente': 0.6,
            'peso_atrasados_mix': 5,
            'peso_quentes_mix': 5
        }
        
        # ===== SISTEMA ANTI-REGRESSÃO =====
        # Guarda o melhor estado para evitar perda de aprendizado
        self.melhor_checkpoint = None
        self.melhor_roi_checkpoint = float('-inf')
        self.sessoes_desde_checkpoint = 0
        self.limite_regressao = 15.0  # Se ROI piorar mais que 15 pontos, faz rollback
        self.limite_paciencia = 5  # Quantas sessões aguardar antes de rollback
        self.modo_exploracao = 'normal'  # 'normal', 'conservador', 'checkpoint'
    
    def _resetar_stats_sessao(self):
        """Reseta estatísticas da sessão atual."""
        self.stats_sessao = {
            estrategia: {
                'acertos': defaultdict(int),
                'lucro_total': 0.0,
                'custo_total': 0.0,
                'rewards': []  # Para tracking de reward por janela
            }
            for estrategia in ['atrasados', 'quentes', 'equilibrada']
        }
    
    def _carregar_aprendizado(self):
        """Carrega estado de aprendizado do disco."""
        if self.arquivo_aprendizado.exists():
            try:
                with open(self.arquivo_aprendizado, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Restaurar bandits
                for name, arm_data in data.get('bandits', {}).items():
                    if name in self.bandits:
                        self.bandits[name].alpha = arm_data.get('alpha', 1.0)
                        self.bandits[name].beta = arm_data.get('beta', 1.0)
                        self.bandits[name].mu = arm_data.get('mu', 0.0)
                        self.bandits[name].kappa = arm_data.get('kappa', 1.0)
                        self.bandits[name].alpha_ng = arm_data.get('alpha_ng', 1.0)
                        self.bandits[name].beta_ng = arm_data.get('beta_ng', 1.0)
                        self.bandits[name].n_pulls = arm_data.get('n_pulls', 0)
                        self.bandits[name].total_reward = arm_data.get('total_reward', 0.0)
                        self.bandits[name].rewards_history = arm_data.get('rewards_history', [])[-100:]
                
                # Restaurar otimizadores
                for name, opt_data in data.get('optimizers', {}).items():
                    if name in self.optimizers:
                        self.optimizers[name].observations = [
                            tuple(obs) for obs in opt_data.get('observations', [])
                        ][-200:]
                
                # Restaurar ensemble weights
                for name, ew_data in data.get('ensemble_weights', {}).items():
                    if name in self.ensemble_weights:
                        self.ensemble_weights[name].weight = ew_data.get('weight', 1.0)
                        self.ensemble_weights[name].performance_history = ew_data.get('performance_history', [])[-50:]
                
                # Restaurar hiperparâmetros
                self.hyperparams = data.get('hyperparams', self.hyperparams)
                
                # Metadados
                self.metadata = data.get('metadata', {
                    'sessoes': 0,
                    'total_janelas': 0,
                    'melhor_roi_historico': float('-inf'),
                    'melhor_estrategia_historica': None
                })
                
                # Carregar checkpoint anti-regressão
                checkpoint_data = data.get('checkpoint_antiregress', {})
                if checkpoint_data:
                    self.melhor_roi_checkpoint = checkpoint_data.get('melhor_roi', float('-inf'))
                    self.sessoes_desde_checkpoint = checkpoint_data.get('sessoes_desde', 0)
                    self.modo_exploracao = checkpoint_data.get('modo', 'normal')
                    self.melhor_checkpoint = checkpoint_data.get('snapshot', None)
                    print(f"   🛡️ Anti-regressão: ROI={self.melhor_roi_checkpoint:.2f}%, Modo={self.modo_exploracao}")
                
                # Restaurar performance de algoritmos
                self.algorithm_performance = data.get('algorithm_performance', {
                    'thompson': [], 'ucb1': [], 'exp3': [], 'ensemble': []
                })
                
                print(f"📚 Aprendizado ML carregado: {self.metadata.get('sessoes', 0)} sessões anteriores")
                
            except Exception as e:
                print(f"⚠️ Erro ao carregar aprendizado: {e}")
                self._inicializar_aprendizado_novo()
        else:
            self._inicializar_aprendizado_novo()
    
    def _inicializar_aprendizado_novo(self):
        """Inicializa novo estado de aprendizado."""
        self.metadata = {
            'sessoes': 0,
            'total_janelas': 0,
            'melhor_roi_historico': float('-inf'),
            'melhor_estrategia_historica': None,
            'historico_sessoes': []
        }
    
    # ===== SISTEMA ANTI-REGRESSÃO =====
    
    def _criar_checkpoint(self, roi_atual: float):
        """
        Cria checkpoint do estado atual se for o melhor já encontrado.
        Isso permite rollback em caso de regressão severa.
        """
        if roi_atual > self.melhor_roi_checkpoint:
            print(f"   💾 NOVO CHECKPOINT! ROI: {roi_atual:.2f}% (anterior: {self.melhor_roi_checkpoint:.2f}%)")
            
            self.melhor_roi_checkpoint = roi_atual
            self.sessoes_desde_checkpoint = 0
            
            # Salvar snapshot completo do estado
            self.melhor_checkpoint = {
                'bandits': {
                    name: {
                        'alpha': arm.alpha,
                        'beta': arm.beta,
                        'mu': arm.mu,
                        'kappa': arm.kappa,
                        'alpha_ng': arm.alpha_ng,
                        'beta_ng': arm.beta_ng,
                        'n_pulls': arm.n_pulls,
                        'total_reward': arm.total_reward,
                        'rewards_history': arm.rewards_history.copy()
                    }
                    for name, arm in self.bandits.items()
                },
                'hyperparams': self.hyperparams.copy(),
                'ensemble_weights': {
                    name: {
                        'weight': ew.weight,
                        'performance_history': ew.performance_history.copy()
                    }
                    for name, ew in self.ensemble_weights.items()
                },
                'algorithm_performance': {
                    algo: perfs.copy() for algo, perfs in self.algorithm_performance.items()
                },
                'roi': roi_atual
            }
            
            # Salvar checkpoint em arquivo separado
            checkpoint_file = Path(__file__).parent / 'checkpoint_ml.json'
            try:
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'roi': roi_atual,
                        'hyperparams': self.hyperparams,
                        'sessao': self.metadata.get('sessoes', 0),
                        'data': datetime.now().isoformat()
                    }, f, indent=2)
            except:
                pass
            
            return True
        else:
            self.sessoes_desde_checkpoint += 1
            return False
    
    def _verificar_regressao(self, roi_atual: float) -> bool:
        """
        Verifica se houve regressão severa e se deve fazer rollback.
        
        Returns: True se fez rollback, False caso contrário
        """
        if self.melhor_checkpoint is None:
            return False
        
        diferenca = self.melhor_roi_checkpoint - roi_atual
        
        # Verificar regressão severa
        if diferenca > self.limite_regressao:
            print(f"\n   ⚠️ REGRESSÃO DETECTADA!")
            print(f"      ROI atual: {roi_atual:.2f}%")
            print(f"      Melhor ROI: {self.melhor_roi_checkpoint:.2f}%")
            print(f"      Diferença: -{diferenca:.2f} pontos")
            
            # Se já passou limite de paciência, fazer rollback
            if self.sessoes_desde_checkpoint >= self.limite_paciencia:
                print(f"\n   🔄 ROLLBACK AUTOMÁTICO para checkpoint!")
                self._restaurar_checkpoint()
                return True
            else:
                restante = self.limite_paciencia - self.sessoes_desde_checkpoint
                print(f"      Aguardando {restante} sessões antes de rollback...")
                
                # Mudar para modo conservador
                if self.modo_exploracao != 'conservador':
                    print(f"      Mudando para modo CONSERVADOR (menos exploração)")
                    self.modo_exploracao = 'conservador'
        
        return False
    
    def _restaurar_checkpoint(self):
        """Restaura o estado do melhor checkpoint."""
        if self.melhor_checkpoint is None:
            print("   ❌ Nenhum checkpoint disponível!")
            return
        
        print(f"   ✅ Restaurando checkpoint (ROI: {self.melhor_checkpoint['roi']:.2f}%)")
        
        # Restaurar bandits
        for name, arm_data in self.melhor_checkpoint['bandits'].items():
            if name in self.bandits:
                self.bandits[name].alpha = arm_data['alpha']
                self.bandits[name].beta = arm_data['beta']
                self.bandits[name].mu = arm_data['mu']
                self.bandits[name].kappa = arm_data['kappa']
                self.bandits[name].alpha_ng = arm_data['alpha_ng']
                self.bandits[name].beta_ng = arm_data['beta_ng']
                self.bandits[name].n_pulls = arm_data['n_pulls']
                self.bandits[name].total_reward = arm_data['total_reward']
                self.bandits[name].rewards_history = arm_data['rewards_history'].copy()
        
        # Restaurar hiperparâmetros
        self.hyperparams = self.melhor_checkpoint['hyperparams'].copy()
        
        # Restaurar ensemble weights
        for name, ew_data in self.melhor_checkpoint['ensemble_weights'].items():
            if name in self.ensemble_weights:
                self.ensemble_weights[name].weight = ew_data['weight']
                self.ensemble_weights[name].performance_history = ew_data['performance_history'].copy()
        
        # Restaurar performance de algoritmos
        for algo, perfs in self.melhor_checkpoint['algorithm_performance'].items():
            if algo in self.algorithm_performance:
                self.algorithm_performance[algo] = perfs.copy()
        
        # Resetar contadores
        self.sessoes_desde_checkpoint = 0
        self.modo_exploracao = 'checkpoint'  # Modo pós-rollback
        
        print(f"   ✅ Estado restaurado! Modo: {self.modo_exploracao}")
    
    def _ajustar_exploracao(self, roi_atual: float):
        """
        Ajusta taxa de exploração baseado no modo atual.
        Modo conservador = menos exploração
        Modo checkpoint = exploração mínima
        """
        if self.modo_exploracao == 'conservador':
            # Reduzir exploração EXP3
            self.exp3_gamma = 0.03  # Era 0.1
            # Reduzir temperatura do SA
            self.simulated_annealing.cooling_rate = 0.99  # Era 0.995
            self.simulated_annealing.temperature = max(1.0, self.simulated_annealing.temperature)
            
        elif self.modo_exploracao == 'checkpoint':
            # Exploração mínima após rollback
            self.exp3_gamma = 0.01
            self.simulated_annealing.cooling_rate = 0.999
            self.simulated_annealing.temperature = max(0.5, self.simulated_annealing.temperature)
            
            # Voltar ao normal se ROI melhorar
            if roi_atual > self.melhor_roi_checkpoint - 5:
                print(f"   📈 ROI recuperando! Voltando ao modo normal.")
                self.modo_exploracao = 'normal'
            
        else:  # normal
            self.exp3_gamma = 0.1
            self.simulated_annealing.cooling_rate = 0.995

    def _salvar_aprendizado(self):
        """Salva estado de aprendizado no disco."""
        data = {
            'bandits': {
                name: {
                    'alpha': arm.alpha,
                    'beta': arm.beta,
                    'mu': arm.mu,
                    'kappa': arm.kappa,
                    'alpha_ng': arm.alpha_ng,
                    'beta_ng': arm.beta_ng,
                    'n_pulls': arm.n_pulls,
                    'total_reward': arm.total_reward,
                    'rewards_history': arm.rewards_history[-100:]
                }
                for name, arm in self.bandits.items()
            },
            'optimizers': {
                name: {
                    'observations': list(opt.observations)[-200:]
                }
                for name, opt in self.optimizers.items()
            },
            'ensemble_weights': {
                name: {
                    'weight': ew.weight,
                    'performance_history': ew.performance_history[-50:]
                }
                for name, ew in self.ensemble_weights.items()
            },
            'hyperparams': self.hyperparams,
            'metadata': self.metadata,
            # Anti-regressão
            'checkpoint_antiregress': {
                'melhor_roi': self.melhor_roi_checkpoint,
                'sessoes_desde': self.sessoes_desde_checkpoint,
                'modo': self.modo_exploracao,
                'snapshot': self.melhor_checkpoint
            },
            # Performance de algoritmos
            'algorithm_performance': {
                algo: perfs[-200:] for algo, perfs in self.algorithm_performance.items()
            }
        }
        
        try:
            with open(self.arquivo_aprendizado, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erro ao salvar aprendizado: {e}")
    
    def carregar_historico(self) -> bool:
        """Carrega histórico de concursos do banco de dados."""
        try:
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost;"
                "DATABASE=Lotofacil;"
                "Trusted_Connection=yes;"
            )
            
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Concurso, 
                           N1, N2, N3, N4, N5, N6, N7, N8, 
                           N9, N10, N11, N12, N13, N14, N15
                    FROM Resultados_INT
                    ORDER BY Concurso ASC
                """)
                
                self.historico_completo = []
                for row in cursor.fetchall():
                    self.historico_completo.append({
                        'concurso': row.Concurso,
                        'numeros': sorted([row[i] for i in range(1, 16)])
                    })
                
                self.total_concursos = len(self.historico_completo)
                print(f"✅ Carregados {self.total_concursos} concursos")
                
                # Treinar Pattern Miners com histórico completo
                self._treinar_pattern_miners()
                
                return True
                
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            return False
    
    def _treinar_pattern_miners(self):
        """Treina os algoritmos de Pattern Mining com o histórico completo."""
        print("   🔍 Treinando Pattern Miners...")
        
        for resultado in self.historico_completo:
            numeros = resultado['numeros']
            concurso = resultado['concurso']
            
            # Association Rules
            self.association_miner.update(numeros)
            
            # Sequential Patterns
            self.sequential_miner.update(numeros)
            
            # Cluster Analysis
            self.cluster_analyzer.update(numeros)
            
            # Anomaly Detection
            self.anomaly_detector.update(numeros, concurso)
            
            # Motif Discovery
            self.motif_miner.update(numeros)
        
        # Extrair regras de associação (todas as versões v2.0)
        self.association_miner.mine_rules()
        self.association_miner.mine_negative_rules()
        self.association_miner.mine_multi_antecedent_rules()
        
        # Mostrar resumo do Association Rules v2.0
        summary = self.association_miner.get_rule_summary()
        print(f"   📊 Association Rules v2.0:")
        print(f"      • {summary['total_positive_rules']} regras positivas")
        print(f"      • {summary['total_negative_rules']} regras negativas")
        print(f"      • {summary['total_multi_antecedent_rules']} regras multi-antecedente")
        
        print(f"   ✅ Pattern Miners treinados com {self.total_concursos} concursos")
    
    def _calcular_features_avancados(self, janela: List[Dict]) -> Dict:
        """
        Calcula features avançados para uma janela de concursos.
        
        Features:
        - Frequência de cada número
        - Atraso (concursos desde última aparição)
        - Padrões posicionais (em qual posição cada número aparece)
        - Sequências consecutivas
        - Paridade (pares/ímpares)
        - Distribuição por dezenas
        - Soma média
        """
        features = {
            'frequencia': defaultdict(int),
            'atraso': {},
            'posicao_freq': defaultdict(lambda: defaultdict(int)),
            'sequencias': defaultdict(int),
            'paridade': {'pares': 0, 'impares': 0},
            'dezenas': defaultdict(int),
            'somas': [],
            'media_soma': 0,
            'std_soma': 0
        }
        
        ultimo_aparecimento = {n: -100 for n in TODOS_NUMEROS}
        
        for idx, resultado in enumerate(janela):
            numeros = resultado['numeros']
            
            # Frequência
            for num in numeros:
                features['frequencia'][num] += 1
                ultimo_aparecimento[num] = idx
            
            # Posição
            for pos, num in enumerate(numeros):
                features['posicao_freq'][num][pos] += 1
            
            # Sequências consecutivas
            seq_atual = 1
            for i in range(1, len(numeros)):
                if numeros[i] == numeros[i-1] + 1:
                    seq_atual += 1
                else:
                    features['sequencias'][seq_atual] += 1
                    seq_atual = 1
            features['sequencias'][seq_atual] += 1
            
            # Paridade
            pares = sum(1 for n in numeros if n % 2 == 0)
            features['paridade']['pares'] += pares
            features['paridade']['impares'] += (15 - pares)
            
            # Dezenas
            for num in numeros:
                dezena = (num - 1) // 5
                features['dezenas'][dezena] += 1
            
            # Soma
            features['somas'].append(sum(numeros))
        
        # Calcular atrasos finais
        tam_janela = len(janela)
        for num in TODOS_NUMEROS:
            features['atraso'][num] = tam_janela - 1 - ultimo_aparecimento[num]
        
        # Média e std da soma
        if features['somas']:
            features['media_soma'] = sum(features['somas']) / len(features['somas'])
            if len(features['somas']) > 1:
                features['std_soma'] = statistics.stdev(features['somas'])
        
        return features
    
    def selecionar_estrategia_thompson(self) -> str:
        """
        Seleciona estratégia usando Thompson Sampling.
        
        Amostra de cada bandit e escolhe o maior.
        Isso naturalmente equilibra exploração vs exploração.
        """
        samples = {}
        for name, arm in self.bandits.items():
            # Usar sample de Normal-Gamma para reward contínuo (ROI)
            samples[name] = arm.sample_normal_gamma()
        
        # Escolher estratégia com maior sample
        return max(samples, key=samples.get)
    
    def selecionar_estrategia_ucb1(self) -> str:
        """
        Seleciona estratégia usando UCB1 (Upper Confidence Bound).
        
        UCB1 é determinístico e teoricamente ótimo para bandits estocásticos.
        """
        total_pulls = sum(arm.n_pulls for arm in self.ucb_arms.values())
        
        if total_pulls == 0:
            # Primeiro pull: escolher aleatoriamente
            return random.choice(list(self.ucb_arms.keys()))
        
        ucb_values = {}
        for name, arm in self.ucb_arms.items():
            ucb_values[name] = arm.get_ucb_value(total_pulls)
        
        return max(ucb_values, key=ucb_values.get)
    
    def selecionar_estrategia_exp3(self) -> str:
        """
        Seleciona estratégia usando EXP3 (Adversarial Bandit).
        
        Robusto a mudanças de distribuição.
        """
        n_arms = len(self.exp3_arms)
        total_weight = sum(arm.weight for arm in self.exp3_arms.values())
        
        # Calcular probabilidades
        probs = {}
        for name, arm in self.exp3_arms.items():
            probs[name] = arm.get_probability(self.exp3_gamma, total_weight, n_arms)
        
        # Amostrar baseado em probabilidades
        r = random.random()
        cumulative = 0.0
        
        for name, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                return name
        
        return list(probs.keys())[-1]  # Fallback
    
    def selecionar_estrategia_ensemble(self) -> str:
        """
        Seleciona estratégia usando Ensemble Voting ponderado.
        
        Combina votos de todos os algoritmos.
        """
        votes = defaultdict(float)
        
        # Voto do Thompson Sampling
        ts_choice = self.selecionar_estrategia_thompson()
        votes[ts_choice] += 1.0
        
        # Voto do UCB1
        ucb_choice = self.selecionar_estrategia_ucb1()
        votes[ucb_choice] += 1.0
        
        # Voto do EXP3
        exp3_choice = self.selecionar_estrategia_exp3()
        votes[exp3_choice] += 0.8  # Peso menor por ser adversarial
        
        # Voto dos Ensemble Weights
        best_ew = max(self.ensemble_weights, key=lambda x: self.ensemble_weights[x].weight)
        votes[best_ew] += self.ensemble_weights[best_ew].weight
        
        # Voto dos EMA trends
        for name, ema in self.ema_trackers.items():
            if ema.get_trend() == "subindo":
                votes[name] += 0.5
            elif ema.get_trend() == "descendo":
                votes[name] -= 0.3
        
        return max(votes, key=votes.get)
    
    def selecionar_estrategia_meta(self) -> Tuple[str, str]:
        """
        Meta-seletor que escolhe qual algoritmo usar baseado em performance.
        
        ANTI-REGRESSÃO: Em modos conservador/checkpoint, usa menos exploração.
        
        Returns: (estratégia, algoritmo_usado)
        """
        # ===== ANTI-REGRESSÃO: Ajustar baseado no modo =====
        if self.modo_exploracao == 'checkpoint':
            # Pós-rollback: usar SOMENTE o melhor algoritmo conhecido
            if self.algorithm_performance:
                avg_perf = {
                    algo: sum(perfs[-20:]) / len(perfs[-20:]) if perfs else float('-inf')
                    for algo, perfs in self.algorithm_performance.items()
                }
                algoritmo = max(avg_perf, key=avg_perf.get)
            else:
                algoritmo = 'thompson'
        
        elif self.modo_exploracao == 'conservador':
            # Conservador: 90% exploitation, 10% exploration
            if random.random() > 0.1 and self.algorithm_performance:
                avg_perf = {
                    algo: sum(perfs[-20:]) / len(perfs[-20:]) if perfs else float('-inf')
                    for algo, perfs in self.algorithm_performance.items()
                }
                algoritmo = max(avg_perf, key=avg_perf.get)
            else:
                algoritmo = random.choice(['thompson', 'ucb1', 'exp3', 'ensemble'])
        
        else:
            # Modo normal: exploração UCB padrão
            if not any(self.algorithm_performance.values()):
                algoritmo = 'thompson'
            else:
                avg_perf = {}
                for algo, perfs in self.algorithm_performance.items():
                    if perfs:
                        avg_perf[algo] = sum(perfs[-50:]) / len(perfs[-50:])
                    else:
                        avg_perf[algo] = 0.0
                
                total = sum(len(p) for p in self.algorithm_performance.values())
                if total > 0:
                    ucb_scores = {}
                    for algo, avg in avg_perf.items():
                        n_algo = len(self.algorithm_performance[algo])
                        if n_algo > 0:
                            ucb_scores[algo] = avg + math.sqrt(2 * math.log(total) / n_algo)
                        else:
                            ucb_scores[algo] = float('inf')
                    
                    algoritmo = max(ucb_scores, key=ucb_scores.get)
                else:
                    algoritmo = 'thompson'
        
        # Aplicar algoritmo escolhido
        if algoritmo == 'thompson':
            estrategia = self.selecionar_estrategia_thompson()
        elif algoritmo == 'ucb1':
            estrategia = self.selecionar_estrategia_ucb1()
        elif algoritmo == 'exp3':
            estrategia = self.selecionar_estrategia_exp3()
        else:  # ensemble
            estrategia = self.selecionar_estrategia_ensemble()
        
        return estrategia, algoritmo
    
    def gerar_combinacoes_genetico(self, features: Dict, quantidade: int) -> List[List[int]]:
        """
        Gera combinações usando Algoritmo Genético.
        
        Evolui população de combinações ao longo das gerações.
        """
        # Inicializar população se vazia
        if not self.genetic_population:
            for _ in range(self.genetic_population_size):
                genes = sorted(random.sample(TODOS_NUMEROS, 15))
                self.genetic_population.append(GeneticIndividual(genes=genes))
        
        # Aplicar features para guiar evolução
        top_numbers = self.feature_tracker.get_top_numbers(10)
        
        # Ordenar por fitness
        self.genetic_population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Selecionar elite
        n_elite = max(2, int(len(self.genetic_population) * self.genetic_elite_ratio))
        elite = self.genetic_population[:n_elite]
        
        # Gerar nova população
        new_population = list(elite)  # Elite passa direto
        
        while len(new_population) < self.genetic_population_size:
            # Seleção por torneio
            tournament_size = 3
            parent1 = max(random.sample(self.genetic_population, tournament_size), key=lambda x: x.fitness)
            parent2 = max(random.sample(self.genetic_population, tournament_size), key=lambda x: x.fitness)
            
            # Crossover
            child = GeneticIndividual.crossover(parent1, parent2)
            
            # Mutação (com bias para top_numbers)
            if random.random() < self.genetic_mutation_rate:
                child = child.mutate(self.genetic_mutation_rate)
                
                # Bias: tentar incluir top_numbers
                if top_numbers and random.random() < 0.3:
                    for top_num in top_numbers[:3]:
                        if top_num not in child.genes:
                            # Substituir número aleatório
                            idx = random.randint(0, 14)
                            child.genes[idx] = top_num
                            child.genes = sorted(set(child.genes))
                            
                            # Completar se necessário
                            while len(child.genes) < 15:
                                available = [n for n in TODOS_NUMEROS if n not in child.genes]
                                child.genes.append(random.choice(available))
                            child.genes = sorted(child.genes[:15])
                            break
            
            new_population.append(child)
        
        self.genetic_population = new_population
        
        # Retornar top combinações
        return [ind.genes for ind in sorted(self.genetic_population, key=lambda x: x.fitness, reverse=True)[:quantidade]]
    
    def gerar_combinacao_simulated_annealing(self, features: Dict) -> List[int]:
        """
        Gera uma combinação usando Simulated Annealing.
        
        Explora espaço de soluções com escape de mínimos locais.
        """
        # Gerar vizinho (perturbação da solução atual)
        current = self.simulated_annealing.current_solution.copy()
        
        # Trocar 1-3 números
        n_changes = random.randint(1, 3)
        for _ in range(n_changes):
            idx = random.randint(0, 14)
            available = [n for n in TODOS_NUMEROS if n not in current]
            if available:
                current[idx] = random.choice(available)
        
        current = sorted(current)
        
        # Para SA, precisamos de uma função de energia (negativo do fitness esperado)
        # Usar features para estimar "qualidade"
        energy = self._calcular_energia_combo(current, features)
        
        # Tentar aceitar nova solução
        self.simulated_annealing.step(current, energy)
        self.simulated_annealing.cool()
        
        return self.simulated_annealing.best_solution
    
    def _calcular_energia_combo(self, combo: List[int], features: Dict) -> float:
        """
        Calcula energia (quanto menor, melhor) de uma combinação.
        
        Baseado em features e importância de números.
        """
        energia = 0.0
        
        # Penalizar números com baixa importância
        for num in combo:
            importancia = self.feature_tracker.number_importance.get(num, 0.0)
            energia -= importancia  # Subtrair porque queremos minimizar
        
        # Penalizar soma fora do range ideal
        soma = sum(combo)
        soma_ideal = features.get('media_soma', 190)
        energia += abs(soma - soma_ideal) / 100
        
        # Penalizar paridade extrema
        pares = sum(1 for n in combo if n % 2 == 0)
        energia += abs(pares - 7.5) / 10
        
        return energia

    def gerar_combinacoes_inteligente(self, features: Dict, estrategia: str, quantidade: int) -> List[List[int]]:
        """
        Gera combinações usando features avançados e hiperparâmetros otimizados.
        """
        combinacoes = []
        
        # Obter hiperparâmetros atuais
        limite_atraso = int(self.hyperparams['limite_atraso_minimo'])
        limite_freq = self.hyperparams['limite_frequencia_quente']
        peso_atrasados = int(self.hyperparams['peso_atrasados_mix'])
        peso_quentes = int(self.hyperparams['peso_quentes_mix'])
        
        # Identificar números por categoria
        freq = features['frequencia']
        atraso = features['atraso']
        
        max_freq = max(freq.values()) if freq else 1
        
        # Números quentes (frequência > limite)
        quentes = [n for n in TODOS_NUMEROS if freq[n] >= max_freq * limite_freq]
        
        # Números atrasados (atraso > limite)
        atrasados = [n for n in TODOS_NUMEROS if atraso[n] >= limite_atraso]
        
        # Números neutros
        neutros = [n for n in TODOS_NUMEROS if n not in quentes and n not in atrasados]
        
        # Garantir mínimos
        if len(quentes) < 5:
            quentes = sorted(TODOS_NUMEROS, key=lambda x: freq[x], reverse=True)[:8]
        if len(atrasados) < 5:
            atrasados = sorted(TODOS_NUMEROS, key=lambda x: atraso[x], reverse=True)[:8]
        if not neutros:
            neutros = [n for n in TODOS_NUMEROS if n not in quentes[:5] and n not in atrasados[:5]]
        
        for _ in range(quantidade * 3):  # Gerar mais e filtrar
            if estrategia == 'atrasados':
                # Foco em atrasados
                n_atrasados = min(9, len(atrasados))
                n_outros = 15 - n_atrasados
                
                escolhidos = random.sample(atrasados, n_atrasados)
                pool_outros = [n for n in TODOS_NUMEROS if n not in escolhidos]
                escolhidos.extend(random.sample(pool_outros, n_outros))
                
            elif estrategia == 'quentes':
                # Foco em quentes
                n_quentes = min(9, len(quentes))
                n_outros = 15 - n_quentes
                
                escolhidos = random.sample(quentes, n_quentes)
                pool_outros = [n for n in TODOS_NUMEROS if n not in escolhidos]
                escolhidos.extend(random.sample(pool_outros, n_outros))
                
            else:  # equilibrada
                # Mix inteligente baseado em features
                n_quentes = min(peso_quentes, len(quentes))
                n_atrasados = min(peso_atrasados, len(atrasados))
                n_neutros = 15 - n_quentes - n_atrasados
                
                escolhidos = []
                escolhidos.extend(random.sample(quentes, n_quentes))
                
                pool_atrasados = [n for n in atrasados if n not in escolhidos]
                if len(pool_atrasados) >= n_atrasados:
                    escolhidos.extend(random.sample(pool_atrasados, n_atrasados))
                else:
                    escolhidos.extend(pool_atrasados)
                    n_neutros += n_atrasados - len(pool_atrasados)
                
                pool_neutros = [n for n in TODOS_NUMEROS if n not in escolhidos]
                n_faltando = 15 - len(escolhidos)
                if len(pool_neutros) >= n_faltando:
                    escolhidos.extend(random.sample(pool_neutros, n_faltando))
                else:
                    escolhidos.extend(pool_neutros)
                    # Completar com qualquer número disponível
                    resto = [n for n in TODOS_NUMEROS if n not in escolhidos]
                    escolhidos.extend(random.sample(resto, 15 - len(escolhidos)))
            
            combo = sorted(escolhidos[:15])
            
            # Validar qualidade da combinação
            if self._validar_qualidade_combo(combo, features):
                combinacoes.append(combo)
            
            if len(combinacoes) >= quantidade:
                break
        
        # Se não conseguiu gerar suficientes, completar sem filtro
        while len(combinacoes) < quantidade:
            combo = sorted(random.sample(TODOS_NUMEROS, 15))
            if combo not in combinacoes:
                combinacoes.append(combo)
        
        return combinacoes[:quantidade]
    
    def _validar_qualidade_combo(self, combo: List[int], features: Dict) -> bool:
        """
        Valida qualidade de uma combinação baseada em features históricos.
        """
        # Soma dentro de 2 desvios padrão da média
        soma = sum(combo)
        media = features['media_soma']
        std = features['std_soma'] if features['std_soma'] > 0 else 15
        
        if abs(soma - media) > 2.5 * std:
            return False
        
        # Paridade não extrema (pelo menos 4 pares E 4 ímpares)
        pares = sum(1 for n in combo if n % 2 == 0)
        if pares < 4 or pares > 11:
            return False
        
        # Pelo menos 2 números de cada dezena de 5
        dezenas = [0] * 5
        for n in combo:
            dezenas[(n - 1) // 5] += 1
        
        if min(dezenas) < 1 or max(dezenas) > 6:
            return False
        
        # Não muitas sequências longas
        seq_count = 0
        for i in range(1, len(combo)):
            if combo[i] == combo[i-1] + 1:
                seq_count += 1
        
        if seq_count > 8:  # Máximo 8 números em sequência
            return False
        
        return True
    
    def calcular_reward(self, resultado_validacao: Dict) -> float:
        """
        Calcula reward shaped para uma validação.
        
        Reward = (lucro_liquido / custo) normalizado
        
        Isso dá mais informação que simplesmente sucesso/falha.
        """
        lucro_liquido = resultado_validacao['lucro_liquido']
        custo = resultado_validacao['custo']
        
        if custo == 0:
            return 0.0
        
        # ROI como reward
        roi = lucro_liquido / custo
        
        # Bonus por acertos altos
        acertos = resultado_validacao.get('acertos', {})
        if acertos.get(15, 0) > 0:
            roi += 100  # Bonus enorme por 15 acertos
        elif acertos.get(14, 0) > 0:
            roi += 10   # Bonus por 14 acertos
        
        return roi
    
    def validar_combinacoes(self, combinacoes: List[List[int]], resultado_real: List[int]) -> Dict:
        """Valida combinações contra resultado real."""
        resultado = {
            'acertos': defaultdict(int),
            'custo': len(combinacoes) * CUSTO_APOSTA,
            'lucro_bruto': 0.0,
            'lucro_liquido': 0.0,
            'sucesso': False,
            'detalhes': []
        }
        
        resultado_set = set(resultado_real)
        
        for combo in combinacoes:
            acertos = len(set(combo) & resultado_set)
            resultado['acertos'][acertos] += 1
            
            if acertos >= 11:
                premio = PREMIO.get(acertos, 0)
                resultado['lucro_bruto'] += premio
                resultado['sucesso'] = True
                resultado['detalhes'].append({
                    'combo': combo,
                    'acertos': acertos,
                    'premio': premio
                })
        
        resultado['lucro_liquido'] = resultado['lucro_bruto'] - resultado['custo']
        
        return resultado
    
    def processar_janela_ml(self, idx_inicio: int, idx_fim: int) -> Dict:
        """
        Processa uma janela usando TODOS os algoritmos ML.
        """
        # Janela de análise
        janela = self.historico_completo[idx_inicio:idx_fim]
        
        # Resultado para validação
        resultado_real = self.historico_completo[idx_fim]
        
        # Calcular features
        features = self._calcular_features_avancados(janela)
        
        # ===== SELEÇÃO DE ESTRATÉGIA COM META-ALGORITMO =====
        estrategia_selecionada, algoritmo_usado = self.selecionar_estrategia_meta()
        
        # ===== GERAÇÃO DE COMBINAÇÕES =====
        # Combinar múltiplos métodos de geração
        combinacoes = []
        
        # 1. Geração baseada em estratégia (método principal)
        n_estrategia = max(1, self.combos_por_estrategia - 2)
        combos_estrategia = self.gerar_combinacoes_inteligente(
            features, 
            estrategia_selecionada, 
            n_estrategia
        )
        combinacoes.extend(combos_estrategia)
        
        # 2. Geração via Algoritmo Genético (1 combo)
        combos_genetico = self.gerar_combinacoes_genetico(features, 1)
        combinacoes.extend(combos_genetico)
        
        # 3. Geração via Simulated Annealing (1 combo)
        combo_sa = self.gerar_combinacao_simulated_annealing(features)
        if combo_sa not in combinacoes:
            combinacoes.append(combo_sa)
        
        # Garantir quantidade correta
        combinacoes = combinacoes[:self.combos_por_estrategia]
        
        # ===== VALIDAÇÃO =====
        validacao = self.validar_combinacoes(combinacoes, resultado_real['numeros'])
        
        # ===== CALCULAR REWARD =====
        reward = self.calcular_reward(validacao)
        
        # ===== ATUALIZAR TODOS OS ALGORITMOS =====
        
        # 1. Thompson Sampling
        self.bandits[estrategia_selecionada].update_continuous(reward)
        
        # 2. UCB1
        self.ucb_arms[estrategia_selecionada].update(reward)
        
        # 3. EXP3
        n_arms = len(self.exp3_arms)
        total_weight = sum(arm.weight for arm in self.exp3_arms.values())
        prob = self.exp3_arms[estrategia_selecionada].get_probability(
            self.exp3_gamma, total_weight, n_arms
        )
        self.exp3_arms[estrategia_selecionada].update(reward, prob, self.exp3_gamma, n_arms)
        
        # 4. Ensemble weights
        norm_reward = max(0, min(1, (reward + 1) / 2))
        self.ensemble_weights[estrategia_selecionada].update(norm_reward)
        
        # 5. EMA Trackers
        self.ema_trackers[estrategia_selecionada].update(reward)
        
        # 6. Feature Importance
        for combo in combinacoes:
            acertos = len(set(combo) & set(resultado_real['numeros']))
            self.feature_tracker.update_from_result(combo, acertos, resultado_real['numeros'])
        
        # 7. Atualizar fitness do Algoritmo Genético
        for combo in combinacoes:
            acertos = len(set(combo) & set(resultado_real['numeros']))
            for ind in self.genetic_population:
                if ind.genes == combo:
                    ind.fitness = acertos / 15.0
                    break
        
        # 8. Atualizar Simulated Annealing
        if combo_sa:
            acertos_sa = len(set(combo_sa) & set(resultado_real['numeros']))
            energia_real = -acertos_sa / 15.0  # Negativo porque minimizamos energia
            self.simulated_annealing.current_energy = energia_real
            if energia_real < self.simulated_annealing.best_energy:
                self.simulated_annealing.best_solution = combo_sa
                self.simulated_annealing.best_energy = energia_real
        
        # 9. Registrar performance do algoritmo usado
        self.algorithm_performance[algoritmo_usado].append(reward)
        if len(self.algorithm_performance[algoritmo_usado]) > 200:
            self.algorithm_performance[algoritmo_usado] = self.algorithm_performance[algoritmo_usado][-200:]
        
        return {
            'janela_inicio': janela[0]['concurso'],
            'janela_fim': janela[-1]['concurso'],
            'concurso_validacao': resultado_real['concurso'],
            'estrategia_usada': estrategia_selecionada,
            'algoritmo_usado': algoritmo_usado,
            'validacao': validacao,
            'reward': reward,
            'features_resumo': {
                'top_quentes': sorted(features['frequencia'].items(), key=lambda x: x[1], reverse=True)[:5],
                'top_atrasados': sorted(features['atraso'].items(), key=lambda x: x[1], reverse=True)[:5],
                'media_soma': features['media_soma']
            },
            'trends': {name: ema.get_trend() for name, ema in self.ema_trackers.items()}
        }
    
    def otimizar_hiperparametros(self):
        """
        Otimiza hiperparâmetros usando Bayesian Optimization.
        Chamado a cada N janelas ou no final da sessão.
        """
        # Calcular score atual (média de rewards recentes de todas as estratégias)
        rewards_recentes = []
        for arm in self.bandits.values():
            rewards_recentes.extend(arm.rewards_history[-20:])
        
        if not rewards_recentes:
            return
        
        score_atual = sum(rewards_recentes) / len(rewards_recentes)
        
        # Registrar observação nos otimizadores
        for name, value in self.hyperparams.items():
            if name in self.optimizers:
                self.optimizers[name].observe(value, score_atual)
        
        # Sugerir novos valores
        novos_params = {}
        for name, optimizer in self.optimizers.items():
            novos_params[name] = optimizer.suggest()
        
        # Aplicar com suavização (não mudar bruscamente)
        alpha = 0.3  # Taxa de atualização
        for name, novo_valor in novos_params.items():
            antigo = self.hyperparams[name]
            self.hyperparams[name] = antigo + alpha * (novo_valor - antigo)
    
    def executar_sessao(self, exportar_report: bool = True) -> Dict:
        """
        Executa sessão completa de aprendizado com ML.
        """
        print("\n" + "=" * 70)
        print("� SISTEMA DE APRENDIZADO COM MACHINE LEARNING (7.12)")
        print("   10 ALGORITMOS ACADÊMICOS INTEGRADOS")
        print("=" * 70)
        
        if not self.carregar_historico():
            return {'erro': 'Falha ao carregar histórico'}
        
        total_janelas = self.total_concursos - self.tamanho_janela
        print(f"\n📊 Total de janelas: {total_janelas}")
        print(f"   Sessões anteriores: {self.metadata.get('sessoes', 0)}")
        
        # Mostrar algoritmos ativos
        print(f"\n🎓 ALGORITMOS ATIVOS:")
        print(f"   1. Thompson Sampling (Multi-Armed Bandit)")
        print(f"   2. UCB1 (Upper Confidence Bound)")
        print(f"   3. EXP3 (Adversarial Bandit)")
        print(f"   4. Bayesian Optimization (TPE)")
        print(f"   5. Genetic Algorithm (população: {self.genetic_population_size})")
        print(f"   6. Simulated Annealing (T={self.simulated_annealing.temperature:.1f})")
        print(f"   7. Ensemble Learning")
        print(f"   8. Exponential Moving Average")
        print(f"   9. Feature Importance")
        print(f"   10. Meta-Bandit (seleção de algoritmo)")
        
        # Mostrar estado dos bandits
        print(f"\n🎰 Estado Multi-Armed Bandits:")
        print(f"   Thompson Sampling:")
        for name, arm in self.bandits.items():
            ev = arm.get_expected_value()
            print(f"      {name.capitalize()}: n={arm.n_pulls}, E[R]={ev:.4f}")
        
        print(f"\n   UCB1:")
        total_ucb = sum(arm.n_pulls for arm in self.ucb_arms.values())
        for name, arm in self.ucb_arms.items():
            ucb = arm.get_ucb_value(max(1, total_ucb))
            print(f"      {name.capitalize()}: n={arm.n_pulls}, UCB={ucb:.4f}")
        
        # Mostrar hiperparâmetros atuais
        print(f"\n⚙️ Hiperparâmetros (Bayesian Optimization):")
        for name, value in self.hyperparams.items():
            print(f"   {name}: {value:.3f}")
        
        # Processar janelas
        print(f"\n🔄 Processando janelas com todos os algoritmos...")
        inicio_sessao = datetime.now()
        
        resultados = []
        contagem_estrategias = defaultdict(int)
        contagem_algoritmos = defaultdict(int)
        
        for i in range(total_janelas):
            resultado = self.processar_janela_ml(i, i + self.tamanho_janela)
            resultados.append(resultado)
            
            contagem_estrategias[resultado['estrategia_usada']] += 1
            contagem_algoritmos[resultado.get('algoritmo_usado', 'thompson')] += 1
            
            # Atualizar stats
            estrategia = resultado['estrategia_usada']
            val = resultado['validacao']
            self.stats_sessao[estrategia]['custo_total'] += val['custo']
            self.stats_sessao[estrategia]['lucro_total'] += val['lucro_bruto']
            for ac, qtd in val['acertos'].items():
                self.stats_sessao[estrategia]['acertos'][ac] += qtd
            self.stats_sessao[estrategia]['rewards'].append(resultado['reward'])
            
            # Otimizar a cada 100 janelas
            if (i + 1) % 100 == 0:
                self.otimizar_hiperparametros()
            
            # Progresso a cada 10%
            if (i + 1) % max(1, total_janelas // 10) == 0:
                progresso = (i + 1) / total_janelas * 100
                # Mostrar algoritmo mais usado até agora
                best_algo = max(contagem_algoritmos, key=contagem_algoritmos.get) if contagem_algoritmos else 'N/A'
                print(f"   ▓ {progresso:5.1f}% | Janela {i+1}/{total_janelas} | Algo: {best_algo}")
        
        duracao = (datetime.now() - inicio_sessao).total_seconds()
        print(f"\n✅ Processamento em {duracao:.1f}s")
        
        # Mostrar distribuição de algoritmos
        print(f"\n📊 Distribuição de algoritmos usados:")
        for algo, count in sorted(contagem_algoritmos.items(), key=lambda x: x[1], reverse=True):
            pct = count / total_janelas * 100
            print(f"   {algo.upper()}: {count} ({pct:.1f}%)")
        
        # Mostrar top números (Feature Importance)
        print(f"\n🔢 Top 10 números mais importantes (Feature Importance):")
        top_nums = self.feature_tracker.get_top_numbers(10)
        print(f"   {top_nums}")
        
        # Mostrar trends (EMA)
        print(f"\n📈 Tendências (EMA):")
        for name, ema in self.ema_trackers.items():
            print(f"   {name.capitalize()}: {ema.get_trend()} (EMA={ema.ema_value:.4f})")
        
        # Otimização final
        self.otimizar_hiperparametros()
        
        # Gerar relatório
        relatorio = self._gerar_relatorio_ml(resultados, contagem_estrategias, duracao)
        relatorio['contagem_algoritmos'] = dict(contagem_algoritmos)
        relatorio['top_numeros'] = top_nums
        
        # ===== SISTEMA ANTI-REGRESSÃO =====
        roi_atual = relatorio.get('roi_geral', -100)
        
        # Registrar no histórico
        self.metadata['historico_sessoes'].append({
            'sessao': self.metadata['sessoes'] + 1,
            'roi_medio': roi_atual
        })
        # Manter últimas 200 sessões
        self.metadata['historico_sessoes'] = self.metadata['historico_sessoes'][-200:]
        
        # 1. Verificar se é melhor ROI - criar checkpoint
        checkpoint_criado = self._criar_checkpoint(roi_atual)
        
        # 2. Verificar regressão e fazer rollback se necessário
        rollback_feito = self._verificar_regressao(roi_atual)
        
        # 3. Ajustar taxa de exploração
        self._ajustar_exploracao(roi_atual)
        
        # Mostrar status anti-regressão
        print(f"\n🛡️ ANTI-REGRESSÃO:")
        print(f"   Modo: {self.modo_exploracao.upper()}")
        print(f"   Melhor ROI histórico: {self.melhor_roi_checkpoint:.2f}%")
        print(f"   ROI atual: {roi_atual:.2f}%")
        print(f"   Sessões desde checkpoint: {self.sessoes_desde_checkpoint}")
        
        if checkpoint_criado:
            print(f"   ✅ Novo checkpoint criado!")
        if rollback_feito:
            print(f"   🔄 Rollback executado!")
        
        # Atualizar metadata
        self.metadata['sessoes'] += 1
        self.metadata['total_janelas'] += len(resultados)
        
        # Salvar aprendizado
        self._salvar_aprendizado()
        
        if exportar_report:
            self._exportar_relatorio_ml(relatorio)
        
        return relatorio
    
    def _gerar_relatorio_ml(self, resultados: List[Dict], contagem: Dict, duracao: float) -> Dict:
        """Gera relatório da sessão ML."""
        
        # Stats por estratégia
        stats = {}
        for estrategia in ['atrasados', 'quentes', 'equilibrada']:
            dados = self.stats_sessao[estrategia]
            custo = dados['custo_total']
            lucro = dados['lucro_total']
            
            stats[estrategia] = {
                'vezes_selecionada': contagem.get(estrategia, 0),
                'custo_total': custo,
                'lucro_bruto': lucro,
                'lucro_liquido': lucro - custo,
                'roi': ((lucro - custo) / custo * 100) if custo > 0 else 0,
                'acertos': dict(dados['acertos']),
                'reward_medio': (sum(dados['rewards']) / len(dados['rewards'])) if dados['rewards'] else 0
            }
            
            # Métricas adicionais
            total_combos = sum(dados['acertos'].values())
            acertos_premiados = sum(qtd for ac, qtd in dados['acertos'].items() if ac >= 11)
            stats[estrategia]['total_combinacoes'] = total_combos
            stats[estrategia]['acertos_premiados'] = acertos_premiados
        
        # Melhor estratégia por ROI
        melhor_roi = max(stats, key=lambda x: stats[x]['roi'])
        
        # Melhor por Thompson Sampling (expected value)
        melhor_thompson = max(self.bandits, key=lambda x: self.bandits[x].get_expected_value())
        
        # Calcular melhoria em relação à sessão anterior
        melhoria = self._calcular_melhoria(stats)
        
        return {
            'data': datetime.now().isoformat(),
            'sessao': self.metadata['sessoes'],
            'janelas': len(resultados),
            'duracao_segundos': duracao,
            'estatisticas': stats,
            'melhor_estrategia_roi': melhor_roi,
            'melhor_estrategia_thompson': melhor_thompson,
            'contagem_selecoes': dict(contagem),
            'hiperparametros': self.hyperparams.copy(),
            'bandits_estado': {
                name: {
                    'expected_value': arm.get_expected_value(),
                    'n_pulls': arm.n_pulls,
                    'alpha': arm.alpha,
                    'beta': arm.beta
                }
                for name, arm in self.bandits.items()
            },
            'melhoria': melhoria
        }
    
    def _calcular_melhoria(self, stats_atual: Dict) -> Dict:
        """Calcula melhoria em relação ao estado anterior."""
        melhoria = {
            'roi_medio_atual': 0,
            'roi_medio_anterior': 0,
            'delta_roi': 0,
            'melhorou': False
        }
        
        # ROI médio atual
        rois = [stats_atual[e]['roi'] for e in stats_atual]
        melhoria['roi_medio_atual'] = sum(rois) / len(rois) if rois else 0
        
        # Comparar com histórico de sessões
        if self.metadata.get('historico_sessoes'):
            ultima = self.metadata['historico_sessoes'][-1]
            melhoria['roi_medio_anterior'] = ultima.get('roi_medio', 0)
            melhoria['delta_roi'] = melhoria['roi_medio_atual'] - melhoria['roi_medio_anterior']
            melhoria['melhorou'] = melhoria['delta_roi'] > 0
        
        # Salvar para próxima comparação
        if 'historico_sessoes' not in self.metadata:
            self.metadata['historico_sessoes'] = []
        
        self.metadata['historico_sessoes'].append({
            'sessao': self.metadata['sessoes'],
            'roi_medio': melhoria['roi_medio_atual']
        })
        
        # Manter só últimas 50 sessões
        self.metadata['historico_sessoes'] = self.metadata['historico_sessoes'][-50:]
        
        return melhoria
    
    def executar_multiplas_sessoes(self, quantidade: int = 5, exportar_report: bool = True) -> List[Dict]:
        """
        Executa múltiplas sessões de aprendizado de uma vez.
        
        Args:
            quantidade: Número de sessões a executar
            exportar_report: Se deve exportar relatório no final
        
        Returns:
            Lista de relatórios de cada sessão
        """
        print(f"\n🔄 Executando {quantidade} sessões consecutivas...")
        print("=" * 70)
        
        relatorios = []
        
        for i in range(quantidade):
            print(f"\n{'='*70}")
            print(f"📍 SESSÃO {i+1} DE {quantidade}")
            print(f"{'='*70}")
            
            # Não exportar relatório individual a cada sessão
            relatorio = self.executar_sessao(exportar_report=False)
            relatorios.append(relatorio)
            
            # Mostrar resumo rápido
            roi = relatorio.get('melhoria', {}).get('roi_medio_atual', 0)
            melhor = relatorio.get('melhor_estrategia_roi', 'N/A')
            print(f"\n   📊 ROI médio: {roi:.2f}%")
            print(f"   🏆 Melhor: {melhor.upper()}")
            
            # Reinicializar stats para próxima sessão
            self._reiniciar_stats_sessao()
        
        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO DE TODAS AS SESSÕES")
        print("=" * 70)
        
        for i, r in enumerate(relatorios, 1):
            roi = r.get('melhoria', {}).get('roi_medio_atual', 0)
            melhor_algo = max(r.get('contagem_algoritmos', {'N/A': 1}), 
                            key=r.get('contagem_algoritmos', {'N/A': 1}).get)
            print(f"   Sessão {i}: ROI {roi:.2f}% | Algoritmo dominante: {melhor_algo.upper()}")
        
        # Evolução
        if len(relatorios) >= 2:
            primeiro_roi = relatorios[0].get('melhoria', {}).get('roi_medio_atual', 0)
            ultimo_roi = relatorios[-1].get('melhoria', {}).get('roi_medio_atual', 0)
            delta = ultimo_roi - primeiro_roi
            sinal = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
            print(f"\n   {sinal} Evolução: {delta:+.2f}% (de {primeiro_roi:.2f}% para {ultimo_roi:.2f}%)")
        
        # Exportar relatório consolidado
        if exportar_report:
            self._exportar_relatorio_consolidado(relatorios)
        
        return relatorios
    
    def _reiniciar_stats_sessao(self):
        """Reinicia estatísticas da sessão para nova execução."""
        self.stats_sessao = {
            'atrasados': {'acertos': defaultdict(int), 'custo_total': 0, 'lucro_total': 0, 'rewards': []},
            'quentes': {'acertos': defaultdict(int), 'custo_total': 0, 'lucro_total': 0, 'rewards': []},
            'equilibrada': {'acertos': defaultdict(int), 'custo_total': 0, 'lucro_total': 0, 'rewards': []}
        }
    
    def _exportar_relatorio_consolidado(self, relatorios: List[Dict]):
        """Exporta relatório consolidado de múltiplas sessões."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = _BASE_DIR / f"relatorio_ml_consolidado_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("🤖 RELATÓRIO CONSOLIDADO - MÚLTIPLAS SESSÕES ML\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"📅 Data: {datetime.now().isoformat()}\n")
            f.write(f"🔢 Sessões executadas: {len(relatorios)}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("📊 EVOLUÇÃO POR SESSÃO\n")
            f.write("-" * 70 + "\n\n")
            
            for i, r in enumerate(relatorios, 1):
                roi = r.get('melhoria', {}).get('roi_medio_atual', 0)
                melhor = r.get('melhor_estrategia_roi', 'N/A')
                f.write(f"   Sessão {i}: ROI {roi:.2f}% | Melhor: {melhor.upper()}\n")
            
            if len(relatorios) >= 2:
                primeiro = relatorios[0].get('melhoria', {}).get('roi_medio_atual', 0)
                ultimo = relatorios[-1].get('melhoria', {}).get('roi_medio_atual', 0)
                f.write(f"\n   Evolução total: {ultimo - primeiro:+.2f}%\n")
        
        print(f"\n   📄 Relatório consolidado: {arquivo}")
    
    # =========================================================================
    # ESTRATÉGIA ANTIPIVO - Combinações Inversas
    # =========================================================================
    
    def _calcular_fitness_numero_ml(self, numero: int, features: Dict) -> float:
        """
        Calcula fitness individual de um número para antipivo.
        
        Critérios:
        1. Frequência (40%)
        2. Atraso baixo = quente (30%)
        3. Feature Importance (30%)
        """
        fitness = 0.0
        
        # 1. Score de frequência (40%)
        freq = features.get('frequencia', {})
        if freq:
            max_freq = max(freq.values()) if freq.values() else 1
            freq_score = freq.get(numero, 0) / max_freq
            fitness += freq_score * 0.4
        else:
            fitness += 0.2
        
        # 2. Score de atraso (quente = baixo atraso) (30%)
        atraso = features.get('atraso', {})
        if atraso:
            atraso_num = atraso.get(numero, 0)
            if atraso_num <= 2:
                atraso_score = 1.0
            elif atraso_num <= 5:
                atraso_score = 0.7
            elif atraso_num <= 10:
                atraso_score = 0.4
            else:
                atraso_score = 0.2
            fitness += atraso_score * 0.3
        else:
            fitness += 0.15
        
        # 3. Feature Importance (30%)
        top_nums = self.feature_tracker.get_top_numbers(15)
        if numero in top_nums:
            pos = top_nums.index(numero)
            importance_score = 1.0 - (pos / 15)
            fitness += importance_score * 0.3
        else:
            fitness += 0.1
        
        return fitness
    
    def _gerar_anticombinacoes_ml(self, pivo_base: List[int], 
                                   features: Dict, quantidade: int) -> List[List[int]]:
        """
        🔄 GERADOR DE ANTICOMBINAÇÕES CORRIGIDO PARA ML 7.12
        
        Conceito CORRETO:
        - Os 10 números FORA DO PIVO se tornam FIXOS (100% em todas as anti's)
        - Os 5 MELHORES (por fitness ML) DO PIVO completam
        
        Fórmula: Anticombinação = 10 FORA do PIVO + 5 melhores DO PIVO
        
        Garantia Matemática:
        - Se PIVO acerta X, ANTIPIVO acerta pelo menos (15-X)
        - Range possível: (15-X) a (15-X)+5
        
        Args:
            pivo_base: 15 números que definem o PIVO
            features: Features calculados (frequência, atraso, etc.)
            quantidade: Quantas anticombinações gerar
            
        Returns:
            Lista de anticombinações com 10 fixos + 5 variáveis
        """
        anticombinacoes = []
        pivo_set = set(pivo_base)
        
        # Os 10 números FORA DO PIVO (SEMPRE FIXOS em todas as anti's)
        numeros_fora_pivo = sorted([n for n in TODOS_NUMEROS if n not in pivo_set])
        
        # Calcular fitness de cada número DO PIVO (para escolher os 5 melhores)
        fitness_pivo = []
        for n in pivo_base:
            fit = self._calcular_fitness_numero_ml(n, features)
            fitness_pivo.append((n, fit))
        
        # Ordenar por fitness (decrescente)
        fitness_pivo.sort(key=lambda x: x[1], reverse=True)
        
        # Gerar variações de anticombinações
        for i in range(quantidade):
            # Selecionar 5 DO PIVO com variação
            if i == 0:
                # Primeira: os 5 melhores exatos
                cinco_do_pivo = [n for n, _ in fitness_pivo[:5]]
            elif i < quantidade // 3:
                # Variações com top 8
                top_8 = [n for n, _ in fitness_pivo[:8]]
                cinco_do_pivo = random.sample(top_8, 5)
            else:
                # Mais variação com top 10
                top_10 = [n for n, _ in fitness_pivo[:10]]
                cinco_do_pivo = random.sample(top_10, 5)
            
            # Montar anticombinação: 10 FORA do PIVO + 5 DO PIVO
            anticomb = sorted(numeros_fora_pivo + cinco_do_pivo)
            
            if anticomb not in anticombinacoes:
                anticombinacoes.append(anticomb)
        
        return anticombinacoes
    
    def gerar_palpites_ml(self, quantidade: int = None) -> List[List[int]]:
        """
        Gera palpites para o próximo concurso usando aprendizado ML.
        
        Usa todos os 10 algoritmos para criar combinações inteligentes:
        - Feature Importance para identificar números-chave
        - Thompson Sampling para selecionar estratégia
        - Genetic Algorithm para evoluir combinações
        - Ensemble para combinar votações
        
        Args:
            quantidade: Número de palpites (None = calcular automaticamente)
        
        Returns:
            Lista de combinações otimizadas
        """
        print("\n" + "=" * 70)
        print("🎯 GERAÇÃO DE PALPITES ML PARA PRÓXIMO CONCURSO")
        print("   (Usando 10 algoritmos de Machine Learning)")
        print("=" * 70)
        
        # Carregar histórico se necessário
        if not self.historico_completo:
            if not self.carregar_historico():
                print("   ❌ Erro ao carregar histórico")
                return []
        
        # Último concurso
        ultimo = self.historico_completo[-1]
        proximo_concurso = ultimo['concurso'] + 1
        print(f"\n   📅 Último concurso: {ultimo['concurso']}")
        print(f"   🎯 Gerando palpites para: {proximo_concurso}")
        
        # Analisar última janela
        idx_inicio = len(self.historico_completo) - self.tamanho_janela
        janela = self.historico_completo[idx_inicio:]
        features = self._calcular_features_avancados(janela)
        
        # Determinar quantidade
        if quantidade is None:
            # Baseado no desempenho: mais sessões = menos palpites necessários
            n_sessoes = max(1, self.metadata.get('sessoes', 1))
            quantidade = max(10, min(50, 100 // n_sessoes))
            print(f"   📊 Quantidade automática: {quantidade} (baseado em {n_sessoes} sessões)")
        
        # ===== ESTRATÉGIA 1: Distribuição por Thompson Sampling =====
        print("\n   🎰 1. Seleção por Thompson Sampling...")
        
        # Determinar proporção de cada estratégia usando bandits
        samples = {name: arm.sample_normal_gamma() for name, arm in self.bandits.items()}
        total_sample = sum(abs(s) for s in samples.values()) or 1
        
        props = {name: max(0.1, abs(s) / total_sample) for name, s in samples.items()}
        total_prop = sum(props.values())
        props = {k: v/total_prop for k, v in props.items()}
        
        n_atrasados = max(1, int(quantidade * props['atrasados']))
        n_quentes = max(1, int(quantidade * props['quentes']))
        n_equilibrada = quantidade - n_atrasados - n_quentes
        
        print(f"      Atrasados: {n_atrasados} ({props['atrasados']*100:.1f}%)")
        print(f"      Quentes: {n_quentes} ({props['quentes']*100:.1f}%)")
        print(f"      Equilibrada: {n_equilibrada} ({props['equilibrada']*100:.1f}%)")
        
        # ===== ESTRATÉGIA 2: Feature Importance =====
        print("\n   🔢 2. Feature Importance - Números prioritários:")
        top_numeros = self.feature_tracker.get_top_numbers(12)
        print(f"      Top 12: {top_numeros}")
        
        # ===== ESTRATÉGIA 3: Genetic Algorithm =====
        print("\n   🧬 3. Genetic Algorithm - Combinações evoluídas...")
        combos_genetico = self.gerar_combinacoes_genetico(features, quantidade // 3)
        print(f"      {len(combos_genetico)} combinações via evolução genética")
        
        # ===== ESTRATÉGIA 4: Simulated Annealing =====
        print("\n   🌡️ 4. Simulated Annealing - Otimização global...")
        combos_sa = []
        for _ in range(quantidade // 4):
            combo = self.gerar_combinacao_simulated_annealing(features)
            if combo not in combos_sa:
                combos_sa.append(combo)
        print(f"      {len(combos_sa)} combinações via SA")
        
        # ===== ESTRATÉGIA 5: Estratégias tradicionais com hiperparâmetros otimizados =====
        print("\n   ⚙️ 5. Estratégias tradicionais (hiperparâmetros otimizados)...")
        combos_atrasados = self.gerar_combinacoes_inteligente(features, 'atrasados', n_atrasados)
        combos_quentes = self.gerar_combinacoes_inteligente(features, 'quentes', n_quentes)
        combos_equilibrada = self.gerar_combinacoes_inteligente(features, 'equilibrada', n_equilibrada)
        
        # ===== ESTRATÉGIA 6: PATTERN MINING (Padrões Ocultos) =====
        print("\n   🔍 6. Pattern Mining - Padrões ocultos...")
        
        # 6.1. Sequential Patterns - Números prováveis baseado em transições
        likely_next = self.sequential_miner.get_likely_next(ultimo['numeros'], 10)
        nums_likely = [n for n, _ in likely_next]
        print(f"      Prováveis (transições): {nums_likely[:5]}")
        
        # 6.2. Sequential Patterns - Números "devidos"
        due_nums = self.sequential_miner.get_due_numbers(10)
        nums_due = [n for n, _ in due_nums]
        print(f"      Devidos (gap): {nums_due[:5]}")
        
        # 6.3. Association Rules - Recomendações (MELHORADO)
        recs = self.association_miner.get_recommendations(top_numeros[:5], 10)
        nums_assoc = [n for n, _ in recs]
        print(f"      Associados (positivo): {nums_assoc[:5]}")
        
        # 6.3b. Association Rules - Números a EVITAR (regras negativas)
        avoid = self.association_miner.get_numbers_to_avoid(top_numeros[:5], 5)
        nums_avoid = [n for n, _ in avoid]
        print(f"      A evitar (negativo): {nums_avoid[:5]}")
        
        # 6.4. Motif Discovery - Completar com motifs
        motifs = self.motif_miner.get_frequent_motifs(5)
        nums_motif = set()
        for motif, _ in motifs:
            nums_motif.update(motif)
        print(f"      Motifs frequentes: {list(nums_motif)[:5]}")
        
        # Gerar combinações baseadas em padrões ocultos (EVITANDO números negativos)
        combos_pattern = []
        nums_pattern = list(set(nums_likely[:5] + nums_due[:5] + nums_assoc[:5] + list(nums_motif)[:5]))
        # Remover números a evitar
        nums_pattern = [n for n in nums_pattern if n not in nums_avoid]
        
        for _ in range(quantidade // 5):
            if len(nums_pattern) >= 8:
                # Usar números de padrões + completar
                base = random.sample(nums_pattern[:min(12, len(nums_pattern))], min(8, len(nums_pattern)))
                restantes = [n for n in TODOS_NUMEROS if n not in base and n not in nums_avoid]
                combo = sorted(base + random.sample(restantes, 15 - len(base)))
                if combo not in combos_pattern:
                    combos_pattern.append(combo)
        
        print(f"      {len(combos_pattern)} combinações via patterns")
        
        # ===== ESTRATÉGIA 7: ASSOCIATION RULES DIRETO =====
        print("\n   🔗 7. Association Rules - Geração direta...")
        combos_assoc_rules = self.association_miner.generate_multiple_combinations(quantidade // 5, diversidade=0.4)
        print(f"      {len(combos_assoc_rules)} combinações via Association Rules")
        
        # ===== ESTRATÉGIA 8: ANTIPIVO (Inverso das combinações) =====
        print("\n   🔄 8. ANTIPIVO - Combinações inversas...")
        # Usa o último resultado como PIVO: 10 que NÃO saíram + 5 melhores que saíram
        # Garantia: se o último resultado se repetir 0-5x, antipivo garante 10-15 acertos
        combos_antipivo = self._gerar_anticombinacoes_ml(ultimo['numeros'], features, quantidade // 4)
        print(f"      {len(combos_antipivo)} combinações via antipivo")
        print(f"      10 fixos (fora último): {sorted([n for n in TODOS_NUMEROS if n not in ultimo['numeros']])}")
        
        # ===== COMBINAR TODAS =====
        todas = combos_genetico + combos_sa + combos_atrasados + combos_quentes + combos_equilibrada + combos_pattern + combos_assoc_rules + combos_antipivo
        
        # Remover duplicatas mantendo ordem
        vistas = set()
        unicas = []
        for combo in todas:
            key = tuple(sorted(combo))
            if key not in vistas:
                vistas.add(key)
                unicas.append(sorted(combo))
        
        # Priorizar combinações com números importantes E padrões ocultos
        # PENALIZAR combinações com números de regras negativas
        def score_combo(combo):
            score = 0
            # Feature Importance
            for i, num in enumerate(top_numeros[:10]):
                if num in combo:
                    score += (10 - i)
            # Padrões ocultos: números prováveis
            for num in nums_likely[:5]:
                if num in combo:
                    score += 3
            # Padrões ocultos: números devidos
            for num in nums_due[:5]:
                if num in combo:
                    score += 2
            # Padrões ocultos: associações
            for num in nums_assoc[:5]:
                if num in combo:
                    score += 2
            # PENALIZAR números a evitar (regras negativas)
            for num in nums_avoid[:5]:
                if num in combo:
                    score -= 3  # Penalidade
            return score
        
        unicas_ordenadas = sorted(unicas, key=score_combo, reverse=True)
        
        # Limitar à quantidade solicitada
        palpites_finais = unicas_ordenadas[:quantidade]
        
        print(f"\n   ✅ {len(palpites_finais)} palpites finais gerados")
        
        # Custo
        custo = len(palpites_finais) * CUSTO_APOSTA
        print(f"   💰 Custo total: R$ {custo:.2f}")
        
        # Mostrar top 5
        print(f"\n   🎯 Top 5 palpites (por score ML):")
        for i, combo in enumerate(palpites_finais[:5], 1):
            score = score_combo(combo)
            print(f"      {i}. {combo} (score: {score})")
        
        # Exportar
        self._exportar_palpites_ml(proximo_concurso, palpites_finais)
        
        return palpites_finais
    
    def _exportar_palpites_ml(self, concurso: int, palpites: List[List[int]]):
        """Exporta palpites ML em arquivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = _BASE_DIR / f"palpites_ml_concurso_{concurso}_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write(f"🎯 PALPITES ML PARA CONCURSO {concurso}\n")
            f.write("   Gerado com 10 algoritmos de Machine Learning\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"🔢 Total de palpites: {len(palpites)}\n")
            f.write(f"💰 Custo total: R$ {len(palpites) * CUSTO_APOSTA:.2f}\n\n")
            
            # Algoritmos usados
            f.write("-" * 70 + "\n")
            f.write("🎓 ALGORITMOS UTILIZADOS:\n")
            f.write("-" * 70 + "\n")
            f.write("   1. Thompson Sampling - seleção de estratégia\n")
            f.write("   2. UCB1 - balanceamento exploração/explotação\n")
            f.write("   3. Feature Importance - números prioritários\n")
            f.write("   4. Genetic Algorithm - evolução de combinações\n")
            f.write("   5. Simulated Annealing - otimização global\n")
            f.write("   6. Bayesian Optimization - hiperparâmetros\n")
            f.write("   7. Ensemble Learning - votação ponderada\n\n")
            
            # Top números
            top_nums = self.feature_tracker.get_top_numbers(10)
            f.write(f"🔢 Top 10 números (Feature Importance): {top_nums}\n\n")
            
            # Palpites
            f.write("-" * 70 + "\n")
            f.write("🎲 PALPITES:\n")
            f.write("-" * 70 + "\n\n")
            
            for i, combo in enumerate(palpites, 1):
                nums_str = " ".join(f"{n:02d}" for n in combo)
                f.write(f"   {i:3d}. {nums_str}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("   BOA SORTE! 🍀\n")
            f.write("=" * 70 + "\n")
        
        print(f"\n   📄 Palpites exportados: {arquivo}")
        
        # Também exportar CSV para fácil importação
        arquivo_csv = _BASE_DIR / f"palpites_ml_concurso_{concurso}_{timestamp}.csv"
        with open(arquivo_csv, 'w', encoding='utf-8') as f:
            f.write("N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15\n")
            for combo in palpites:
                f.write(",".join(str(n) for n in combo) + "\n")
        
        print(f"   📊 CSV exportado: {arquivo_csv}")
        
        # Salvar em JSON para validação posterior
        self._salvar_palpites_para_validacao(concurso, palpites)
    
    def _salvar_palpites_para_validacao(self, concurso: int, palpites: List[List[int]]):
        """Salva palpites em JSON para validação posterior."""
        arquivo_validacao = _BASE_DIR / "palpites_pendentes.json"
        
        # Carregar palpites existentes
        pendentes = {}
        if arquivo_validacao.exists():
            try:
                with open(arquivo_validacao, 'r', encoding='utf-8') as f:
                    pendentes = json.load(f)
            except:
                pendentes = {}
        
        # Adicionar novos palpites
        pendentes[str(concurso)] = {
            'concurso': concurso,
            'data_geracao': datetime.now().isoformat(),
            'palpites': palpites,
            'validado': False,
            'resultado': None,
            'acertos': None
        }
        
        # Salvar
        with open(arquivo_validacao, 'w', encoding='utf-8') as f:
            json.dump(pendentes, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Palpites salvos para validação futura")
    
    def validar_palpites_pendentes(self) -> Dict:
        """
        Valida palpites pendentes contra resultados reais e aprende.
        
        Returns:
            Dict com resultados da validação
        """
        print("\n" + "=" * 70)
        print("🔄 VALIDAÇÃO DE PALPITES REAIS")
        print("   (Feedback Loop para Aprendizado)")
        print("=" * 70)
        
        arquivo_validacao = _BASE_DIR / "palpites_pendentes.json"
        
        if not arquivo_validacao.exists():
            print("\n   ❌ Nenhum palpite pendente para validar")
            return {'validados': 0}
        
        # Carregar palpites pendentes
        with open(arquivo_validacao, 'r', encoding='utf-8') as f:
            pendentes = json.load(f)
        
        if not pendentes:
            print("\n   ❌ Nenhum palpite pendente para validar")
            return {'validados': 0}
        
        # Carregar histórico se necessário
        if not self.historico_completo:
            if not self.carregar_historico():
                print("   ❌ Erro ao carregar histórico")
                return {'validados': 0}
        
        # Criar índice de concursos
        concursos_db = {r['concurso']: r['numeros'] for r in self.historico_completo}
        ultimo_concurso = max(concursos_db.keys())
        
        print(f"\n   📅 Último concurso no banco: {ultimo_concurso}")
        print(f"   📋 Palpites pendentes: {len(pendentes)}")
        
        resultados_validacao = {
            'validados': 0,
            'acertos_totais': defaultdict(int),
            'melhor_acerto': 0,
            'premio_total': 0,
            'custo_total': 0,
            'roi': 0,
            'detalhes': []
        }
        
        concursos_para_remover = []
        
        for concurso_str, dados in pendentes.items():
            concurso = int(concurso_str)
            
            if dados['validado']:
                continue
            
            # Verificar se o resultado já saiu
            if concurso not in concursos_db:
                print(f"\n   ⏳ Concurso {concurso}: Resultado ainda não disponível")
                continue
            
            resultado_real = concursos_db[concurso]
            palpites = dados['palpites']
            
            print(f"\n   🎯 Validando concurso {concurso}...")
            print(f"      Resultado real: {resultado_real}")
            
            # Validar cada palpite
            acertos_concurso = defaultdict(int)
            premio_concurso = 0
            melhor_acerto = 0
            
            for palpite in palpites:
                acertos = len(set(palpite) & set(resultado_real))
                acertos_concurso[acertos] += 1
                resultados_validacao['acertos_totais'][acertos] += 1
                
                if acertos > melhor_acerto:
                    melhor_acerto = acertos
                
                if acertos in PREMIO:
                    premio_concurso += PREMIO[acertos]
                    resultados_validacao['premio_total'] += PREMIO[acertos]
            
            custo_concurso = len(palpites) * CUSTO_APOSTA
            resultados_validacao['custo_total'] += custo_concurso
            
            # Mostrar resumo
            print(f"      Palpites: {len(palpites)} | Custo: R$ {custo_concurso:.2f}")
            print(f"      Melhor acerto: {melhor_acerto} números")
            
            acertos_str = ", ".join(f"{k}:{v}" for k, v in sorted(acertos_concurso.items(), reverse=True))
            print(f"      Distribuição: {acertos_str}")
            
            if premio_concurso > 0:
                print(f"      🏆 PRÊMIO: R$ {premio_concurso:.2f}")
            
            # Atualizar aprendizado com feedback real
            self._aprender_com_feedback(palpites, resultado_real, melhor_acerto)
            
            # Marcar como validado
            dados['validado'] = True
            dados['resultado'] = resultado_real
            dados['acertos'] = dict(acertos_concurso)
            dados['premio'] = premio_concurso
            dados['melhor_acerto'] = melhor_acerto
            
            resultados_validacao['validados'] += 1
            resultados_validacao['detalhes'].append({
                'concurso': concurso,
                'melhor_acerto': melhor_acerto,
                'premio': premio_concurso,
                'custo': custo_concurso
            })
            
            if resultados_validacao['melhor_acerto'] < melhor_acerto:
                resultados_validacao['melhor_acerto'] = melhor_acerto
            
            # Mover para histórico após validação
            concursos_para_remover.append(concurso_str)
        
        # Remover validados dos pendentes
        for c in concursos_para_remover:
            del pendentes[c]
        
        # Salvar pendentes atualizados
        with open(arquivo_validacao, 'w', encoding='utf-8') as f:
            json.dump(pendentes, f, indent=2, ensure_ascii=False)
        
        # Salvar no histórico de validações
        self._salvar_historico_validacoes(resultados_validacao)
        
        # Resumo final
        if resultados_validacao['validados'] > 0:
            print("\n" + "-" * 70)
            print("📊 RESUMO DA VALIDAÇÃO")
            print("-" * 70)
            print(f"   Concursos validados: {resultados_validacao['validados']}")
            print(f"   Melhor acerto geral: {resultados_validacao['melhor_acerto']} números")
            print(f"   Custo total: R$ {resultados_validacao['custo_total']:.2f}")
            print(f"   Prêmio total: R$ {resultados_validacao['premio_total']:.2f}")
            
            if resultados_validacao['custo_total'] > 0:
                roi = ((resultados_validacao['premio_total'] - resultados_validacao['custo_total']) 
                       / resultados_validacao['custo_total'] * 100)
                resultados_validacao['roi'] = roi
                sinal = "📈" if roi > 0 else "📉"
                print(f"   {sinal} ROI Real: {roi:.2f}%")
            
            print("\n   ✅ Aprendizado atualizado com feedback real!")
            self._salvar_aprendizado()
        
        return resultados_validacao
    
    def _aprender_com_feedback(self, palpites: List[List[int]], resultado_real: List[int], melhor_acerto: int):
        """
        Atualiza o aprendizado com base em feedback real de palpites.
        
        Isso é diferente do treinamento histórico - aqui usamos
        palpites que foram efetivamente gerados pelo sistema.
        """
        # Calcular reward baseado no melhor acerto
        # Scale: 0-10=negativo, 11=neutro, 12+=positivo
        if melhor_acerto >= 15:
            reward = 1.0  # Jackpot!
        elif melhor_acerto >= 14:
            reward = 0.8
        elif melhor_acerto >= 13:
            reward = 0.5
        elif melhor_acerto >= 12:
            reward = 0.2
        elif melhor_acerto >= 11:
            reward = 0.0
        else:
            reward = -0.5
        
        # Atualizar Feature Importance com números que acertaram
        for palpite in palpites:
            acertos_lista = [n for n in palpite if n in resultado_real]
            for num in acertos_lista:
                # Boost para números que acertaram em palpites reais
                self.feature_tracker.number_importance[num] += 0.05
        
        # Atualizar Thompson Sampling com feedback real
        # Usamos peso maior para feedback real vs histórico
        for name, arm in self.bandits.items():
            arm.update_continuous(reward * 1.5)  # Peso 1.5x para feedback real
        
        # Atualizar Ensemble weights
        norm_reward = max(0, min(1, (reward + 1) / 2))
        for name, ew in self.ensemble_weights.items():
            ew.update(norm_reward)
        
        # Atualizar EMA
        for name, ema in self.ema_trackers.items():
            ema.update(reward)
        
        # Registrar no metadata
        if 'feedback_real' not in self.metadata:
            self.metadata['feedback_real'] = []
        
        self.metadata['feedback_real'].append({
            'data': datetime.now().isoformat(),
            'melhor_acerto': melhor_acerto,
            'reward': reward,
            'n_palpites': len(palpites)
        })
        
        # Manter só últimos 100
        self.metadata['feedback_real'] = self.metadata['feedback_real'][-100:]
    
    def _salvar_historico_validacoes(self, resultados: Dict):
        """Salva histórico de validações em arquivo separado."""
        arquivo_hist = _BASE_DIR / "historico_validacoes.json"
        
        historico = []
        if arquivo_hist.exists():
            try:
                with open(arquivo_hist, 'r', encoding='utf-8') as f:
                    historico = json.load(f)
            except:
                historico = []
        
        historico.append({
            'data': datetime.now().isoformat(),
            'validados': resultados['validados'],
            'melhor_acerto': resultados['melhor_acerto'],
            'premio_total': resultados['premio_total'],
            'custo_total': resultados['custo_total'],
            'roi': resultados.get('roi', 0),
            'detalhes': resultados['detalhes']
        })
        
        with open(arquivo_hist, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)
    
    def ver_palpites_pendentes(self):
        """Mostra palpites pendentes de validação."""
        arquivo_validacao = _BASE_DIR / "palpites_pendentes.json"
        
        print("\n" + "=" * 70)
        print("📋 PALPITES PENDENTES DE VALIDAÇÃO")
        print("=" * 70)
        
        if not arquivo_validacao.exists():
            print("\n   ❌ Nenhum palpite pendente")
            return
        
        with open(arquivo_validacao, 'r', encoding='utf-8') as f:
            pendentes = json.load(f)
        
        if not pendentes:
            print("\n   ❌ Nenhum palpite pendente")
            return
        
        print(f"\n   Total: {len(pendentes)} concursos com palpites pendentes\n")
        
        for concurso_str, dados in sorted(pendentes.items()):
            status = "✅ Validado" if dados['validado'] else "⏳ Pendente"
            n_palpites = len(dados['palpites'])
            data = dados['data_geracao'][:10]
            print(f"   Concurso {concurso_str}: {n_palpites} palpites | {data} | {status}")
    
    def ver_historico_validacoes(self):
        """Mostra histórico de validações."""
        arquivo_hist = _BASE_DIR / "historico_validacoes.json"
        
        print("\n" + "=" * 70)
        print("📊 HISTÓRICO DE VALIDAÇÕES REAIS")
        print("=" * 70)
        
        if not arquivo_hist.exists():
            print("\n   ❌ Nenhuma validação realizada ainda")
            return
        
        with open(arquivo_hist, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        if not historico:
            print("\n   ❌ Nenhuma validação realizada ainda")
            return
        
        print(f"\n   Total de validações: {len(historico)}")
        
        # Estatísticas gerais
        total_premio = sum(h['premio_total'] for h in historico)
        total_custo = sum(h['custo_total'] for h in historico)
        melhor_geral = max(h['melhor_acerto'] for h in historico)
        
        print(f"\n   💰 Total investido: R$ {total_custo:.2f}")
        print(f"   🏆 Total ganho: R$ {total_premio:.2f}")
        
        if total_custo > 0:
            roi_geral = (total_premio - total_custo) / total_custo * 100
            sinal = "📈" if roi_geral > 0 else "📉"
            print(f"   {sinal} ROI Geral: {roi_geral:.2f}%")
        
        print(f"   🎯 Melhor acerto: {melhor_geral} números")
        
        # Últimas validações
        print("\n   Últimas validações:")
        for h in historico[-5:]:
            data = h['data'][:10]
            melhor = h['melhor_acerto']
            premio = h['premio_total']
            roi = h.get('roi', 0)
            print(f"      {data}: Melhor={melhor}, Prêmio=R${premio:.2f}, ROI={roi:.1f}%")

    def _exportar_relatorio_ml(self, relatorio: Dict):
        """Exporta relatório ML em formato legível."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = _BASE_DIR / f"relatorio_ml_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("🤖 RELATÓRIO DE APRENDIZADO COM MACHINE LEARNING (10 ALGORITMOS)\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"📅 Data: {relatorio['data']}\n")
            f.write(f"🔢 Sessão #: {relatorio['sessao']}\n")
            f.write(f"📊 Janelas: {relatorio['janelas']}\n")
            f.write(f"⏱️ Duração: {relatorio['duracao_segundos']:.1f}s\n\n")
            
            # ===== ALGORITMOS USADOS =====
            f.write("-" * 70 + "\n")
            f.write("🎓 DISTRIBUIÇÃO DE ALGORITMOS (META-BANDIT)\n")
            f.write("-" * 70 + "\n\n")
            
            contagem_algos = relatorio.get('contagem_algoritmos', {})
            if contagem_algos:
                for algo, count in sorted(contagem_algos.items(), key=lambda x: x[1], reverse=True):
                    pct = count / relatorio['janelas'] * 100
                    f.write(f"   {algo.upper()}: {count} seleções ({pct:.1f}%)\n")
            
            # ===== MULTI-ARMED BANDITS =====
            f.write("\n" + "-" * 70 + "\n")
            f.write("🎰 MULTI-ARMED BANDITS\n")
            f.write("-" * 70 + "\n\n")
            
            f.write("   THOMPSON SAMPLING:\n")
            for name, data in relatorio['bandits_estado'].items():
                f.write(f"      {name.capitalize()}: E[R]={data['expected_value']:.4f} (n={data['n_pulls']})\n")
            
            f.write(f"\n   Melhor por E[reward]: {relatorio['melhor_estrategia_thompson'].upper()}\n")
            
            # ===== SELEÇÕES POR ESTRATÉGIA =====
            f.write("\n   Seleções por estratégia:\n")
            for estrategia, count in relatorio['contagem_selecoes'].items():
                pct = count / relatorio['janelas'] * 100
                f.write(f"      {estrategia.capitalize()}: {count} ({pct:.1f}%)\n")
            
            # ===== FEATURE IMPORTANCE =====
            f.write("\n" + "-" * 70 + "\n")
            f.write("🔢 FEATURE IMPORTANCE - Top Números\n")
            f.write("-" * 70 + "\n\n")
            
            top_nums = relatorio.get('top_numeros', [])
            if top_nums:
                f.write(f"   Top 10 números mais importantes: {top_nums}\n")
                f.write("   (Números que mais contribuem para acertos)\n")
            
            # ===== ESTATÍSTICAS POR ESTRATÉGIA =====
            f.write("\n" + "-" * 70 + "\n")
            f.write("📈 ESTATÍSTICAS POR ESTRATÉGIA\n")
            f.write("-" * 70 + "\n\n")
            
            for estrategia, dados in relatorio['estatisticas'].items():
                f.write(f"🎯 {estrategia.upper()}\n")
                f.write(f"   Vezes selecionada: {dados['vezes_selecionada']}\n")
                f.write(f"   ROI: {dados['roi']:.1f}%\n")
                f.write(f"   Reward médio: {dados['reward_medio']:.4f}\n")
                f.write(f"   Custo: R$ {dados['custo_total']:.2f}\n")
                f.write(f"   Lucro líquido: R$ {dados['lucro_liquido']:.2f}\n")
                f.write(f"   Acertos 11+: {dados['acertos_premiados']}\n")
                
                for ac in [15, 14, 13, 12, 11]:
                    if dados['acertos'].get(ac, 0) > 0:
                        f.write(f"      {ac} acertos: {dados['acertos'][ac]}x\n")
                f.write("\n")
            
            # ===== HIPERPARÂMETROS =====
            f.write("-" * 70 + "\n")
            f.write("⚙️ HIPERPARÂMETROS (Bayesian Optimization / TPE)\n")
            f.write("-" * 70 + "\n\n")
            
            for name, value in relatorio['hiperparametros'].items():
                f.write(f"   {name}: {value:.4f}\n")
            
            # ===== EVOLUÇÃO =====
            f.write("\n" + "-" * 70 + "\n")
            f.write("📊 EVOLUÇÃO DO APRENDIZADO\n")
            f.write("-" * 70 + "\n\n")
            
            mel = relatorio['melhoria']
            f.write(f"   ROI médio atual: {mel['roi_medio_atual']:.2f}%\n")
            if mel.get('roi_medio_anterior'):
                f.write(f"   ROI médio anterior: {mel['roi_medio_anterior']:.2f}%\n")
                sinal = "📈" if mel['melhorou'] else "📉"
                f.write(f"   Delta: {sinal} {mel['delta_roi']:+.2f}%\n")
                
                if mel['melhorou']:
                    f.write("\n   ✅ SISTEMA MELHOROU NESTA SESSÃO!\n")
                else:
                    f.write("\n   ⚠️ Performance abaixo da sessão anterior.\n")
                    f.write("   Meta-Bandit irá ajustar automaticamente.\n")
            
            # ===== RESUMO DOS 10 ALGORITMOS =====
            f.write("\n" + "=" * 70 + "\n")
            f.write("🎓 10 ALGORITMOS ACADÊMICOS IMPLEMENTADOS\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("   1. THOMPSON SAMPLING (Auer et al.)\n")
            f.write("      Convergência assintótica garantida para estratégia ótima.\n\n")
            
            f.write("   2. UCB1 - Upper Confidence Bound (Auer et al., 2002)\n")
            f.write("      Bound otimista determinístico para exploração.\n\n")
            
            f.write("   3. EXP3 - Adversarial Bandit (Auer et al., 2002)\n")
            f.write("      Robusto a mudanças de distribuição.\n\n")
            
            f.write("   4. BAYESIAN OPTIMIZATION / TPE\n")
            f.write("      Otimização de hiperparâmetros com menos avaliações.\n\n")
            
            f.write("   5. GENETIC ALGORITHM (Holland, 1975)\n")
            f.write("      Evolui combinações via crossover, mutação e seleção.\n\n")
            
            f.write("   6. SIMULATED ANNEALING (Kirkpatrick et al., 1983)\n")
            f.write("      Escape de mínimos locais via temperatura.\n\n")
            
            f.write("   7. ENSEMBLE LEARNING\n")
            f.write("      Combina votos de múltiplos algoritmos.\n\n")
            
            f.write("   8. EXPONENTIAL MOVING AVERAGE (EMA)\n")
            f.write("      Detecta mudanças de tendência rapidamente.\n\n")
            
            f.write("   9. FEATURE IMPORTANCE\n")
            f.write("      Identifica números/padrões mais importantes.\n\n")
            
            f.write("   10. META-BANDIT (UCB sobre algoritmos)\n")
            f.write("       Seleciona qual algoritmo usar baseado em performance.\n")
        
        print(f"\n   📄 Relatório exportado: {arquivo}")


def main():
    """Interface principal do sistema ML."""
    print("\n" + "=" * 70)
    print("🤖 SISTEMA DE APRENDIZADO COM MACHINE LEARNING (7.12)")
    print("   15 ALGORITMOS ACADÊMICOS INTEGRADOS")
    print("=" * 70)
    print()
    print("🎓 ALGORITMOS DE ML:")
    print("   1. Thompson Sampling    6. Simulated Annealing")
    print("   2. UCB1                  7. Ensemble Learning")
    print("   3. EXP3                  8. EMA (Tendências)")
    print("   4. Bayesian Optimization 9. Feature Importance")
    print("   5. Genetic Algorithm    10. Meta-Bandit")
    print()
    print("🔍 PATTERN MINING (Padrões Ocultos):")
    print("   11. Association Rules   14. Anomaly Detection")
    print("   12. Sequential Patterns 15. Motif Discovery")
    print("   13. Cluster Analysis")
    print()
    print("✨ GARANTIAS TEÓRICAS:")
    print("   • Convergência assintótica para estratégia ótima")
    print("   • Descoberta de padrões ocultos nos dados")
    print("   • Adaptação a mudanças de distribuição")
    print()
    
    sistema = SistemaAprendizadoML()
    
    while True:
        print("\n" + "=" * 70)
        print("📋 MENU ML - 15 ALGORITMOS ACADÊMICOS")
        print("=" * 70)
        print("   1. Executar sessão de aprendizado ML")
        print("   2. Executar MÚLTIPLAS sessões (definir quantidade)")
        print("   3. Gerar palpites para próximo concurso")
        print("   4. 🔄 VALIDAR palpites (após resultado sair)")
        print("   5. Ver palpites pendentes de validação")
        print("   6. Ver histórico de validações reais")
        print("   7. Ver estado de TODOS os algoritmos")
        print("   8. 🔍 Ver PADRÕES OCULTOS descobertos")
        print("   9. Resetar aprendizado ML")
        print("  10. 🔗 EXPLORER DE ASSOCIATION RULES ⭐ NOVO!")
        print("   0. Voltar")
        
        opcao = input("\n🎯 Escolha: ").strip()
        
        if opcao == "1":
            sistema.executar_sessao()
        
        elif opcao == "2":
            try:
                qtd = input("\n   🔢 Quantas sessões executar? ").strip()
                qtd = int(qtd)
                if qtd >= 1:
                    sistema.executar_multiplas_sessoes(qtd)
                else:
                    print("   ❌ Quantidade deve ser maior que 0")
            except ValueError:
                print("   ❌ Digite um número válido")
        
        elif opcao == "3":
            try:
                qtd = input("\n   🎲 Quantos palpites gerar? (Enter=automático): ").strip()
                if qtd:
                    qtd = int(qtd)
                    if 1 <= qtd <= 1000:
                        sistema.gerar_palpites_ml(qtd)
                    else:
                        print("   ❌ Quantidade deve ser entre 1 e 1000")
                else:
                    sistema.gerar_palpites_ml()
            except ValueError:
                print("   ❌ Digite um número válido")
        
        elif opcao == "4":
            # Validar palpites pendentes
            sistema.validar_palpites_pendentes()
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "5":
            # Ver palpites pendentes
            sistema.ver_palpites_pendentes()
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "6":
            # Ver histórico de validações
            sistema.ver_historico_validacoes()
            input("\n   Pressione ENTER para continuar...")
            
        elif opcao == "7":
            print("\n" + "=" * 70)
            print("🎓 ESTADO DOS 10 ALGORITMOS")
            print("=" * 70)
            
            # 1. Thompson Sampling
            print("\n1️⃣ THOMPSON SAMPLING:")
            for name, arm in sistema.bandits.items():
                print(f"   {name.capitalize()}: n={arm.n_pulls}, E[R]={arm.get_expected_value():.4f}")
            
            # 2. UCB1
            print("\n2️⃣ UCB1 (Upper Confidence Bound):")
            total_ucb = sum(arm.n_pulls for arm in sistema.ucb_arms.values())
            for name, arm in sistema.ucb_arms.items():
                ucb = arm.get_ucb_value(max(1, total_ucb))
                print(f"   {name.capitalize()}: n={arm.n_pulls}, UCB={ucb:.4f}, mean={arm.get_mean():.4f}")
            
            # 3. EXP3
            print("\n3️⃣ EXP3 (Adversarial Bandit):")
            for name, arm in sistema.exp3_arms.items():
                print(f"   {name.capitalize()}: weight={arm.weight:.4f}, n={arm.n_pulls}")
            
            # 4. Bayesian Optimization
            print("\n4️⃣ BAYESIAN OPTIMIZATION (TPE):")
            for name, value in sistema.hyperparams.items():
                n_obs = len(sistema.optimizers[name].observations)
                print(f"   {name}: {value:.4f} (observações: {n_obs})")
            
            # 5. Genetic Algorithm
            print("\n5️⃣ GENETIC ALGORITHM:")
            print(f"   População: {len(sistema.genetic_population)}")
            if sistema.genetic_population:
                best = max(sistema.genetic_population, key=lambda x: x.fitness)
                print(f"   Melhor fitness: {best.fitness:.4f}")
                print(f"   Melhor combo: {best.genes}")
            
            # 6. Simulated Annealing
            print("\n6️⃣ SIMULATED ANNEALING:")
            sa = sistema.simulated_annealing
            print(f"   Temperatura: {sa.temperature:.2f}")
            print(f"   Iterações: {sa.iterations}")
            print(f"   Melhor energia: {sa.best_energy:.4f}")
            print(f"   Melhor combo: {sa.best_solution}")
            
            # 7. Ensemble Weights
            print("\n7️⃣ ENSEMBLE LEARNING:")
            for name, ew in sistema.ensemble_weights.items():
                print(f"   {name.capitalize()}: peso={ew.weight:.4f}")
            
            # 8. EMA
            print("\n8️⃣ EXPONENTIAL MOVING AVERAGE:")
            for name, ema in sistema.ema_trackers.items():
                print(f"   {name.capitalize()}: EMA={ema.ema_value:.4f}, trend={ema.get_trend()}")
            
            # 9. Feature Importance
            print("\n9️⃣ FEATURE IMPORTANCE:")
            top_nums = sistema.feature_tracker.get_top_numbers(10)
            print(f"   Top 10 números: {top_nums}")
            top_pairs = sistema.feature_tracker.get_top_pairs(5)
            if top_pairs:
                print(f"   Top 5 pares: {top_pairs}")
            
            # 10. Meta-Bandit
            print("\n🔟 META-BANDIT (Seleção de Algoritmo):")
            for algo, perfs in sistema.algorithm_performance.items():
                if perfs:
                    avg = sum(perfs[-50:]) / len(perfs[-50:])
                    print(f"   {algo.upper()}: avg_reward={avg:.4f} (n={len(perfs)})")
                else:
                    print(f"   {algo.upper()}: sem dados ainda")
            
            # Histórico
            print("\n" + "=" * 70)
            print("📊 HISTÓRICO DE SESSÕES")
            print("=" * 70)
            
            print(f"   Total de sessões: {sistema.metadata.get('sessoes', 0)}")
            print(f"   Total de janelas: {sistema.metadata.get('total_janelas', 0)}")
            
            hist = sistema.metadata.get('historico_sessoes', [])
            if hist:
                print("\n   Últimas 5 sessões (ROI médio):")
                for h in hist[-5:]:
                    print(f"      Sessão {h['sessao']}: {h['roi_medio']:.2f}%")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "8":
            # Ver padrões ocultos
            print("\n" + "=" * 70)
            print("🔍 PADRÕES OCULTOS DESCOBERTOS")
            print("   (Pattern Mining Algorithms)")
            print("=" * 70)
            
            # Carregar histórico se necessário
            if not sistema.historico_completo:
                sistema.carregar_historico()
            
            # 11. Association Rules - VERSÃO EXPANDIDA
            print("\n1️⃣1️⃣ ASSOCIATION RULES (Regras de Associação) - AVANÇADO:")
            
            # Regras positivas
            print("\n   📗 REGRAS POSITIVAS (Se X aparece → Y aparece):")
            rules = sistema.association_miner.mine_rules(top_k=10)
            if rules:
                for i, rule in enumerate(rules[:5], 1):
                    ant = rule['antecedent']
                    cons = rule['consequent']
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    conv = rule.get('conviction', 0)
                    conv_str = f"{conv:.2f}" if conv < 100 else "∞"
                    print(f"   {i}. {ant} → {cons} | conf: {conf:.1f}% | lift: {lift:.2f} | conv: {conv_str}")
            else:
                print("   (Ainda sem regras - execute uma sessão primeiro)")
            
            # Regras negativas
            print("\n   📕 REGRAS NEGATIVAS (Se X aparece → Y NÃO aparece):")
            neg_rules = sistema.association_miner.mine_negative_rules(top_k=10)
            if neg_rules:
                for i, rule in enumerate(neg_rules[:5], 1):
                    ant = rule['antecedent']
                    cons = rule['consequent']
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    print(f"   {i}. {ant} → ¬{cons} | conf: {conf:.1f}% | lift: {lift:.2f}")
                    print(f"      {rule.get('interpretation', '')}")
            else:
                print("   (Ainda sem regras negativas - execute uma sessão primeiro)")
            
            # Regras multi-antecedente
            print("\n   📘 REGRAS MULTI-ANTECEDENTE (Se {X,Y} aparecem → Z aparece):")
            multi_rules = sistema.association_miner.mine_multi_antecedent_rules(top_k=10)
            if multi_rules:
                for i, rule in enumerate(multi_rules[:5], 1):
                    ant = rule['antecedent']
                    cons = rule['consequent']
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    print(f"   {i}. {{{ant[0]}, {ant[1]}}} → {cons} | conf: {conf:.1f}% | lift: {lift:.2f}")
            else:
                print("   (Ainda sem regras multi - execute uma sessão primeiro)")
            
            # Resumo estatístico
            summary = sistema.association_miner.get_rule_summary()
            print(f"\n   📊 RESUMO:")
            print(f"      Observações: {summary['n_observations']}")
            print(f"      Janela deslizante: {summary['window_size']} concursos")
            print(f"      Regras positivas: {summary['n_positive_rules']}")
            print(f"      Regras negativas: {summary['n_negative_rules']}")
            print(f"      Regras multi: {summary['n_multi_rules']}")
            print(f"      Pares rastreados: {summary['n_pairs_tracked']}")
            
            # 12. Sequential Patterns
            print("\n1️⃣2️⃣ SEQUENTIAL PATTERNS (Padrões Temporais):")
            print("   Números 'devidos' (baseado em gap médio de reaparecimento)")
            due_nums = sistema.sequential_miner.get_due_numbers(10)
            if due_nums:
                for num, score in due_nums[:5]:
                    print(f"   • Número {num:2d}: {score:.2f}x o gap médio")
            else:
                print("   (Ainda sem dados - execute uma sessão primeiro)")
            
            # Prováveis no próximo
            if sistema.historico_completo:
                ultimo = sistema.historico_completo[-1]['numeros']
                likely = sistema.sequential_miner.get_likely_next(ultimo, 10)
                if likely:
                    print("\n   Mais prováveis no PRÓXIMO sorteio (baseado em transições):")
                    nums_likely = [n for n, _ in likely[:10]]
                    print(f"   {nums_likely}")
            
            # 13. Cluster Analysis
            print("\n1️⃣3️⃣ CLUSTER ANALYSIS (Tipos de Sorteios):")
            dominant = sistema.cluster_analyzer.get_dominant_cluster()
            profile = sistema.cluster_analyzer.get_cluster_profile(dominant)
            if profile:
                print(f"   Cluster dominante: #{dominant}")
                print(f"   Perfil: {int(profile.get('pares', 0))} pares, soma ~{int(profile.get('soma', 0))}")
                print(f"          {int(profile.get('consecutivos', 0))} consecutivos")
            else:
                print("   (Ainda sem clusters - execute uma sessão primeiro)")
            
            # 14. Anomaly Detection
            print("\n1️⃣4️⃣ ANOMALY DETECTION (Sorteios Anômalos):")
            anomalies = sistema.anomaly_detector.get_recent_anomalies(5)
            if anomalies:
                print("   Sorteios que fugiram do padrão normal:")
                for a in anomalies[-3:]:
                    print(f"   • Concurso {a['concurso']}: score={a['score']:.2f}")
                    print(f"     Números: {a['numeros']}")
            else:
                print("   (Nenhuma anomalia detectada ainda)")
            
            # 15. Motif Discovery
            print("\n1️⃣5️⃣ MOTIF DISCOVERY (Padrões Recorrentes):")
            motifs = sistema.motif_miner.get_frequent_motifs(10)
            if motifs:
                print("   Triplas mais frequentes:")
                for motif, freq in motifs[:5]:
                    print(f"   • {motif}: {freq*100:.2f}% dos sorteios")
            else:
                print("   (Ainda sem motifs - execute uma sessão primeiro)")
            
            # Padrões de paridade
            parity = sistema.motif_miner.get_parity_patterns(5)
            if parity:
                print("\n   Padrões de paridade mais comuns (P=par, I=ímpar):")
                for pattern, freq in parity[:3]:
                    print(f"   • {pattern}: {freq*100:.2f}%")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "9":
            if input("\n   ⚠️ Confirma reset? (s/n): ").strip().lower() == 's':
                sistema._inicializar_ml()
                sistema._inicializar_aprendizado_novo()
                sistema._salvar_aprendizado()
                print("   ✅ Aprendizado ML resetado!")
        
        elif opcao == "10":
            # Explorer de Association Rules - NOVO!
            _menu_association_rules_explorer(sistema)
        
        elif opcao == "0":
            break
    
    print("\n👋 Até a próxima sessão ML!")


def _menu_association_rules_explorer(sistema):
    """
    🔗 EXPLORER DE ASSOCIATION RULES
    
    Menu dedicado para explorar regras de associação e gerar combinações.
    """
    # Carregar histórico se necessário
    if not sistema.historico_completo:
        print("\n   📥 Carregando histórico...")
        sistema.carregar_historico()
    
    while True:
        print("\n" + "=" * 70)
        print("🔗 EXPLORER DE ASSOCIATION RULES")
        print("   Análise avançada de regras e geração de combinações")
        print("=" * 70)
        
        # Mostrar resumo rápido
        summary = sistema.association_miner.get_rule_summary()
        print(f"\n📊 RESUMO ATUAL:")
        print(f"   Observações: {summary['n_observations']} | Janela: {summary['window_size']}")
        print(f"   Positivas: {summary['n_positive_rules']} | Negativas: {summary['n_negative_rules']} | Multi: {summary['n_multi_rules']}")
        
        print("\n📋 OPÇÕES:")
        print("   1. Ver TOP regras positivas (com conviction e Zhang)")
        print("   2. Ver TOP regras NEGATIVAS (números que se repelem)")
        print("   3. Ver TOP regras MULTI-ANTECEDENTE ({X,Y} → Z)")
        print("   4. Ver TODAS as regras rankeadas por relevância")
        print("   5. Configurar thresholds (support, confidence)")
        print("   6. 🎰 GERAR combinações baseadas em regras")
        print("   7. 🔍 Consultar números específicos")
        print("   8. 📊 Usar JANELA DESLIZANTE (últimos N concursos)")
        print("   9. 💾 Exportar regras para arquivo")
        print("   0. Voltar")
        
        opcao = input("\n🎯 Escolha: ").strip()
        
        if opcao == "1":
            # Top regras positivas
            print("\n" + "=" * 70)
            print("📗 TOP REGRAS POSITIVAS")
            print("   Se X aparece → Y também aparece")
            print("=" * 70)
            
            rules = sistema.association_miner.mine_rules(top_k=20)
            if rules:
                print(f"\n{'#':<3} {'Antecedente':<12} {'Consequente':<12} {'Conf%':<8} {'Lift':<7} {'Conv':<8} {'Zhang':<7}")
                print("-" * 70)
                for i, rule in enumerate(rules, 1):
                    ant = str(rule['antecedent'])
                    cons = str(rule['consequent'])
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    conv = rule.get('conviction', 0)
                    conv_str = f"{conv:.2f}" if conv < 100 else "∞"
                    zhang = rule.get('zhang_interest', 0)
                    print(f"{i:<3} {ant:<12} {cons:<12} {conf:<8.1f} {lift:<7.2f} {conv_str:<8} {zhang:<7.3f}")
            else:
                print("\n   ❌ Nenhuma regra encontrada. Execute uma sessão ML primeiro.")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "2":
            # Regras negativas
            print("\n" + "=" * 70)
            print("📕 TOP REGRAS NEGATIVAS")
            print("   Se X aparece → Y NÃO aparece (exclusão mútua)")
            print("=" * 70)
            
            neg_rules = sistema.association_miner.mine_negative_rules(top_k=20)
            if neg_rules:
                print(f"\n{'#':<3} {'Quando aparece':<15} {'NÃO aparece':<15} {'Conf%':<8} {'Lift':<7}")
                print("-" * 70)
                for i, rule in enumerate(neg_rules, 1):
                    ant = str(rule['antecedent'])
                    cons = str(rule['consequent'])
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    print(f"{i:<3} {ant:<15} ¬{cons:<14} {conf:<8.1f} {lift:<7.2f}")
                
                print("\n💡 INTERPRETAÇÃO:")
                print("   Números que 'se repelem' - quando um aparece, o outro tende a NÃO aparecer.")
                print("   Use para EVITAR combinações que incluam ambos.")
            else:
                print("\n   ❌ Nenhuma regra negativa encontrada.")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "3":
            # Regras multi-antecedente
            print("\n" + "=" * 70)
            print("📘 TOP REGRAS MULTI-ANTECEDENTE")
            print("   Se {X, Y} aparecem JUNTOS → Z também aparece")
            print("=" * 70)
            
            multi_rules = sistema.association_miner.mine_multi_antecedent_rules(top_k=20)
            if multi_rules:
                print(f"\n{'#':<3} {'Antecedentes':<15} {'Consequente':<12} {'Conf%':<8} {'Lift':<7} {'Conv':<8}")
                print("-" * 70)
                for i, rule in enumerate(multi_rules, 1):
                    ant = f"{{{rule['antecedent'][0]}, {rule['antecedent'][1]}}}"
                    cons = str(rule['consequent'])
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    conv = rule.get('conviction', 0)
                    conv_str = f"{conv:.2f}" if conv < 100 else "∞"
                    print(f"{i:<3} {ant:<15} {cons:<12} {conf:<8.1f} {lift:<7.2f} {conv_str:<8}")
                
                print("\n💡 USO:")
                print("   Quando você já tem 2 números, estas regras indicam quais completam melhor.")
            else:
                print("\n   ❌ Nenhuma regra multi encontrada.")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "4":
            # Todas as regras rankeadas
            print("\n" + "=" * 70)
            print("📊 TODAS AS REGRAS RANKEADAS")
            print("   Score = Lift × Conviction × (1 + Zhang)")
            print("=" * 70)
            
            all_rules = sistema.association_miner.get_all_rules_ranked(top_k=30)
            if all_rules:
                print(f"\n{'#':<3} {'Tipo':<10} {'Regra':<25} {'Score':<10} {'Conf%':<8}")
                print("-" * 70)
                for i, rule in enumerate(all_rules, 1):
                    tipo = rule.get('type', 'positive')[:8]
                    if tipo == 'positive':
                        regra = f"{rule['antecedent']} → {rule['consequent']}"
                    elif tipo == 'negative':
                        regra = f"{rule['antecedent']} → ¬{rule['consequent']}"
                    else:
                        regra = f"{{{rule['antecedent'][0]},{rule['antecedent'][1]}}} → {rule['consequent']}"
                    score = rule.get('combined_score', 0)
                    conf = rule['confidence'] * 100
                    print(f"{i:<3} {tipo:<10} {regra:<25} {score:<10.2f} {conf:<8.1f}")
            else:
                print("\n   ❌ Nenhuma regra encontrada.")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "5":
            # Configurar thresholds
            print("\n" + "=" * 70)
            print("⚙️ CONFIGURAR THRESHOLDS")
            print("=" * 70)
            
            print(f"\n   Valores atuais:")
            print(f"   • min_support:    {sistema.association_miner.min_support:.2f}")
            print(f"   • min_confidence: {sistema.association_miner.min_confidence:.2f}")
            print(f"   • window_size:    {sistema.association_miner.window_size}")
            
            print("\n   Novos valores (Enter para manter):")
            
            try:
                new_sup = input(f"   min_support [{sistema.association_miner.min_support:.2f}]: ").strip()
                if new_sup:
                    sistema.association_miner.min_support = float(new_sup)
                
                new_conf = input(f"   min_confidence [{sistema.association_miner.min_confidence:.2f}]: ").strip()
                if new_conf:
                    sistema.association_miner.min_confidence = float(new_conf)
                
                new_win = input(f"   window_size [{sistema.association_miner.window_size}]: ").strip()
                if new_win:
                    sistema.association_miner.window_size = int(new_win)
                
                print("\n   ✅ Thresholds atualizados!")
            except ValueError:
                print("\n   ❌ Valor inválido!")
        
        elif opcao == "6":
            # Gerar combinações baseadas em regras
            print("\n" + "=" * 70)
            print("🎰 GERAR COMBINAÇÕES BASEADAS EM REGRAS")
            print("=" * 70)
            
            print("\n   Estratégia:")
            print("   • Começa com números mais frequentes ou seeds")
            print("   • Adiciona números recomendados por regras positivas")
            print("   • Usa regras multi-antecedente para completar")
            print("   • EVITA números indicados por regras negativas")
            
            try:
                qtd = input("\n   Quantas combinações gerar? [10]: ").strip()
                qtd = int(qtd) if qtd else 10
                
                div = input("   Nível de diversidade (0.0 a 1.0)? [0.3]: ").strip()
                div = float(div) if div else 0.3
                
                seed_input = input("   Números seed (opcional, ex: 3,7,12): ").strip()
                seeds = None
                if seed_input:
                    seeds = [int(n.strip()) for n in seed_input.replace(',', ' ').split() if n.strip()]
                
                print(f"\n   🎲 Gerando {qtd} combinações...")
                
                if seeds:
                    combinacoes = []
                    for _ in range(qtd):
                        combo = sistema.association_miner.generate_combination_from_rules(seeds)
                        if combo not in combinacoes:
                            combinacoes.append(combo)
                else:
                    combinacoes = sistema.association_miner.generate_multiple_combinations(qtd, div)
                
                print(f"\n   ✅ {len(combinacoes)} combinações geradas:\n")
                
                for i, combo in enumerate(combinacoes, 1):
                    nums_str = ','.join(f"{n:02d}" for n in combo)
                    print(f"   {i:>3}. [{nums_str}]")
                
                # Perguntar se quer salvar
                salvar = input("\n   💾 Salvar em arquivo? (s/n) [n]: ").strip().lower()
                if salvar == 's':
                    from datetime import datetime
                    filename = _BASE_DIR / f"combinacoes_association_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("# Combinações geradas por Association Rules\n")
                        f.write(f"# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"# Quantidade: {len(combinacoes)}\n")
                        f.write(f"# Diversidade: {div}\n")
                        if seeds:
                            f.write(f"# Seeds: {seeds}\n")
                        f.write("#\n")
                        for combo in combinacoes:
                            f.write(','.join(map(str, combo)) + '\n')
                    print(f"\n   ✅ Salvo em: {filename}")
                
            except ValueError:
                print("\n   ❌ Valor inválido!")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "7":
            # Consultar números específicos
            print("\n" + "=" * 70)
            print("🔍 CONSULTAR NÚMEROS ESPECÍFICOS")
            print("=" * 70)
            
            nums_input = input("\n   Digite os números para consultar (ex: 3,7,12): ").strip()
            if nums_input:
                try:
                    nums = [int(n.strip()) for n in nums_input.replace(',', ' ').split() if n.strip()]
                    
                    print(f"\n   📊 Análise para: {nums}")
                    print("-" * 50)
                    
                    # Suporte individual
                    print("\n   SUPORTE INDIVIDUAL:")
                    for n in nums:
                        sup = sistema.association_miner.support.get(n, 0)
                        print(f"   • Número {n:2d}: {sup*100:.1f}% de presença")
                    
                    # Recomendações
                    recs = sistema.association_miner.get_recommendations(nums, n=10)
                    if recs:
                        print("\n   NÚMEROS RECOMENDADOS (baseado em regras):")
                        for num, score in recs:
                            print(f"   • Número {num:2d}: score {score:.2f}")
                    
                    # Números a evitar
                    avoid = sistema.association_miner.get_numbers_to_avoid(nums, n=5)
                    if avoid:
                        print("\n   ⚠️ NÚMEROS A EVITAR (regras negativas):")
                        for num, score in avoid:
                            print(f"   • Número {num:2d}: penalidade {score:.2f}")
                    
                    # Regras multi que aplicam
                    if len(nums) >= 2:
                        print("\n   REGRAS MULTI-ANTECEDENTE APLICÁVEIS:")
                        found = 0
                        for rule in sistema.association_miner.multi_rules[:20]:
                            if all(n in nums for n in rule['antecedent']):
                                cons = rule['consequent'][0]
                                conf = rule['confidence'] * 100
                                print(f"   • {{{rule['antecedent'][0]}, {rule['antecedent'][1]}}} → {cons} ({conf:.1f}%)")
                                found += 1
                                if found >= 5:
                                    break
                        if found == 0:
                            print("   (Nenhuma regra aplicável)")
                    
                except ValueError:
                    print("\n   ❌ Entrada inválida!")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "8":
            # Usar janela deslizante
            print("\n" + "=" * 70)
            print("📊 ANÁLISE COM JANELA DESLIZANTE")
            print("=" * 70)
            
            print(f"\n   Janela atual: {len(sistema.association_miner.window_data)} concursos")
            print(f"   Tamanho máximo: {sistema.association_miner.window_size}")
            
            print("\n   Esta análise usa apenas os concursos mais recentes,")
            print("   capturando tendências atuais do jogo.")
            
            rules = sistema.association_miner.mine_rules(use_window=True, top_k=15)
            if rules:
                print(f"\n   TOP 10 REGRAS (baseado na janela):")
                print("-" * 50)
                for i, rule in enumerate(rules[:10], 1):
                    ant = rule['antecedent']
                    cons = rule['consequent']
                    conf = rule['confidence'] * 100
                    lift = rule['lift']
                    print(f"   {i}. {ant} → {cons} | conf: {conf:.1f}% | lift: {lift:.2f}")
            else:
                print("\n   ❌ Janela vazia. Execute uma sessão ML primeiro.")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "9":
            # Exportar regras
            print("\n" + "=" * 70)
            print("💾 EXPORTAR REGRAS")
            print("=" * 70)
            
            from datetime import datetime
            filename = _BASE_DIR / f"association_rules_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            try:
                all_rules = sistema.association_miner.get_all_rules_ranked(top_k=100)
                summary = sistema.association_miner.get_rule_summary()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 70 + "\n")
                    f.write("ASSOCIATION RULES - LOTOSCOPE ML\n")
                    f.write(f"Exportado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 70 + "\n\n")
                    
                    f.write("RESUMO:\n")
                    f.write(f"  Observações: {summary['n_observations']}\n")
                    f.write(f"  Janela: {summary['window_size']} concursos\n")
                    f.write(f"  Regras positivas: {summary['n_positive_rules']}\n")
                    f.write(f"  Regras negativas: {summary['n_negative_rules']}\n")
                    f.write(f"  Regras multi: {summary['n_multi_rules']}\n\n")
                    
                    f.write("REGRAS (ordenadas por relevância):\n")
                    f.write("-" * 70 + "\n")
                    
                    for i, rule in enumerate(all_rules, 1):
                        tipo = rule.get('type', 'positive')
                        if tipo == 'positive':
                            regra = f"{rule['antecedent']} → {rule['consequent']}"
                        elif tipo == 'negative':
                            regra = f"{rule['antecedent']} → ¬{rule['consequent']}"
                        else:
                            regra = f"{{{rule['antecedent'][0]},{rule['antecedent'][1]}}} → {rule['consequent']}"
                        
                        f.write(f"{i:>3}. [{tipo:>10}] {regra:<25} | ")
                        f.write(f"conf: {rule['confidence']*100:.1f}% | ")
                        f.write(f"lift: {rule['lift']:.2f} | ")
                        f.write(f"score: {rule.get('combined_score', 0):.2f}\n")
                    
                    f.write("\n" + "=" * 70 + "\n")
                    f.write("MÉTRICAS:\n")
                    f.write("  - Support: frequência do itemset\n")
                    f.write("  - Confidence: P(Y|X) - probabilidade condicional\n")
                    f.write("  - Lift: quanto X aumenta a probabilidade de Y\n")
                    f.write("  - Conviction: dependência direcional (>1 = associação)\n")
                    f.write("  - Zhang Interest: -1 a +1, 0 = independência\n")
                
                print(f"\n   ✅ Exportado para: {filename}")
            except Exception as e:
                print(f"\n   ❌ Erro ao exportar: {e}")
            
            input("\n   Pressione ENTER para continuar...")
        
        elif opcao == "0":
            break


if __name__ == "__main__":
    main()
