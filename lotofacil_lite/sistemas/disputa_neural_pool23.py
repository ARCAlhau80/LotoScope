# -*- coding: utf-8 -*-
"""
🥊 DISPUTA NEURAL vs POOL 23 - SISTEMA DE BENCHMARK E APRENDIZADO
===================================================================

Sistema que compara a estratégia INVERTIDA v3.0 (Pool 23) com uma rede neural
treinada para escolher quais números excluir.

OBJETIVO:
- Treinar a rede neural para aprender o padrão de exclusão do Pool 23
- Comparar taxa de acerto de exclusão: Neural vs INVERTIDA v3.0
- Se a neural aprender, usar para ranquear candidatos a exclusão

MÉTRICAS:
- "Acerto de exclusão": os 2 excluídos NÃO estavam no resultado real
- Taxa de acerto: % de concursos onde acertou a exclusão

Autor: LotoScope AI
Data: 30/03/2026
"""

import os
import sys
import json
import math
import pickle
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
import pyodbc

# Adicionar paths do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE: REDE NEURAL PARA EXCLUSÃO
# ═══════════════════════════════════════════════════════════════════════════════
class RedeNeuralExclusao:
    """
    Rede Neural especializada em EXCLUIR números.

    Arquitetura v3 (250 features, 10 por número):
    - Entrada: 250 features (freq, atraso, consec, tendência, freq10, INVERTIDA,
              co-ocorrência, posicional, entropia, soft exclusion)
    - 2 camadas ocultas: 96 → 48 neurônios
    - Saída: 25 valores (score de exclusão para cada número)
    - L2 regularization (lambda=0.001) — penaliza pesos grandes
    - Dropout (rate=0.3) durante treino — força generalização
    - ~30k parâmetros — razão params/amostras ~15:1
    """

    def __init__(self, silencioso: bool = False,
                 dropout_rate: float = 0.3,
                 l2_lambda: float = 0.001):
        self.pesos = {}
        self.bias = {}
        self.historico_treino = []
        self.dropout_rate = dropout_rate
        self.l2_lambda = l2_lambda

        # Arquitetura: 250 → 96 → 48 → 25
        self.tamanhos = [250, 96, 48, 25]
        self._inicializar_pesos(silencioso)

    def _inicializar_pesos(self, silencioso: bool = False):
        """Inicializa pesos com He initialization (otimizado para ReLU)"""
        np.random.seed(42)

        if not silencioso:
            print("   🧠 Inicializando Rede Neural para Exclusão (v3 - 250 features)...")

        for i in range(len(self.tamanhos) - 1):
            # He initialization: scale = sqrt(2 / n_entrada)
            scale = np.sqrt(2.0 / self.tamanhos[i])
            self.pesos[f'W{i}'] = np.random.randn(self.tamanhos[i], self.tamanhos[i+1]).astype(np.float32) * scale
            self.bias[f'b{i}'] = np.zeros(self.tamanhos[i+1], dtype=np.float32)

        total_params = sum(w.size for w in self.pesos.values()) + sum(b.size for b in self.bias.values())
        if not silencioso:
            print(f"      • {total_params:,} parâmetros")
            print(f"      • Arquitetura: {' → '.join(map(str, self.tamanhos))}")
            print(f"      • Dropout: {self.dropout_rate} | L2: {self.l2_lambda}")

    def _relu(self, x):
        return np.maximum(0, x)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass sem dropout (modo inferência)"""
        a = x
        for i in range(len(self.pesos)):
            z = np.dot(a, self.pesos[f'W{i}']) + self.bias[f'b{i}']
            if i < len(self.pesos) - 1:
                a = self._relu(z)
            else:
                a = self._sigmoid(z)
        return a

    def treinar(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, lr: float = 0.001):
        """
        Treina com L2 regularization + Dropout inverted (anti-overfitting).

        y deve ter valores altos (perto de 1) para números que NÃO saíram.
        """
        keep_prob = 1.0 - self.dropout_rate

        for epoch in range(epochs):
            # Forward com dropout inverted nas camadas ocultas
            activations = [X]
            a = X
            for i in range(len(self.pesos)):
                z = np.dot(a, self.pesos[f'W{i}']) + self.bias[f'b{i}']
                if i < len(self.pesos) - 1:
                    a = self._relu(z)
                    # Dropout inverted: escala por 1/keep_prob para manter
                    # valor esperado igual ao forward sem dropout
                    if self.dropout_rate > 0:
                        mask = (np.random.rand(*a.shape) > self.dropout_rate).astype(np.float32)
                        a = a * mask / keep_prob
                else:
                    a = self._sigmoid(z)
                activations.append(a)

            # Binary cross-entropy loss gradient
            delta = activations[-1] - y

            # Backward com L2 e propagação através do dropout
            for i in range(len(self.pesos) - 1, -1, -1):
                grad_w = np.dot(activations[i].T, delta) / X.shape[0]
                grad_b = np.mean(delta, axis=0)

                # L2 regularization: penaliza pesos grandes
                grad_w += self.l2_lambda * self.pesos[f'W{i}']

                # Gradient clipping
                grad_w = np.clip(grad_w, -1.0, 1.0)
                grad_b = np.clip(grad_b, -1.0, 1.0)

                self.pesos[f'W{i}'] -= lr * grad_w
                self.bias[f'b{i}'] -= lr * grad_b

                if i > 0:
                    delta = np.dot(delta, self.pesos[f'W{i}'].T)
                    # Gradiente através de ReLU + dropout inverted:
                    # activations[i] == 0 quando neurônio morreu (relu) ou
                    # foi dropado → gradiente zero nesses casos
                    if self.dropout_rate > 0:
                        delta = delta * (activations[i] > 0) / keep_prob
                    else:
                        delta = delta * (activations[i] > 0)

    def prever_exclusoes(self, features: np.ndarray, top_k: int = 2) -> List[int]:
        """Retorna os top_k números com maior score de exclusão"""
        scores = self.forward(features.reshape(1, -1))[0]
        indices = np.argsort(scores)[::-1][:top_k]
        return [i + 1 for i in indices]  # Números 1-25

    def obter_scores(self, features: np.ndarray) -> Dict[int, float]:
        """Retorna scores de exclusão para todos os números"""
        scores = self.forward(features.reshape(1, -1))[0]
        return {i + 1: float(scores[i]) for i in range(25)}

    def salvar(self, caminho: str):
        """Salva modelo com metadados de regularização e versão"""
        with open(caminho, 'wb') as f:
            pickle.dump({
                'pesos': self.pesos,
                'bias': self.bias,
                'tamanhos': self.tamanhos,
                'historico_treino': self.historico_treino,
                'dropout_rate': self.dropout_rate,
                'l2_lambda': self.l2_lambda,
                'versao': 'v3',
            }, f)

    @classmethod
    def carregar(cls, caminho: str) -> 'RedeNeuralExclusao':
        """Carrega modelo salvo (compatível com v2=150 features e v3=250 features)"""
        with open(caminho, 'rb') as f:
            dados = pickle.load(f)

        versao = dados.get('versao', 'v2')
        tamanhos_salvos = dados.get('tamanhos', [150, 64, 32, 25])

        # Detectar modelo antigo (v2 com 150 features)
        if tamanhos_salvos[0] == 150:
            print("   ⚠️  Modelo v2 (150 features) detectado — incompatível com v3 (250 features)!")
            print("   🔄 Reinicializando rede com arquitetura v3. Retreine o modelo.")
            rede = cls(
                silencioso=True,
                dropout_rate=dados.get('dropout_rate', 0.3),
                l2_lambda=dados.get('l2_lambda', 0.001),
            )
            rede.historico_treino = dados.get('historico_treino', [])
            return rede

        rede = cls(
            silencioso=True,
            dropout_rate=dados.get('dropout_rate', 0.3),
            l2_lambda=dados.get('l2_lambda', 0.001),
        )
        rede.pesos = dados['pesos']
        rede.bias = dados['bias']
        rede.tamanhos = dados['tamanhos']
        rede.historico_treino = dados.get('historico_treino', [])
        return rede


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE: ESTRATÉGIA INVERTIDA V3.0 (Pool 23)
# ═══════════════════════════════════════════════════════════════════════════════
class EstrategiaInvertida:
    """
    Replica a lógica INVERTIDA v3.0 do Pool 23.
    
    Exclui os 2 números mais "quentes" (maior score de exclusão):
    - 10+ consecutivas → PROTEÇÃO (-5, NÃO excluir anomalias)
    - 5-9 consecutivas → +6
    - 4 consecutivas → +5
    - 3+ consecutivas + alta freq → +4
    - 100% freq nos últimos 5 → +4
    """
    
    @staticmethod
    def calcular_scores_exclusao(historico: List[Dict], idx_concurso: int, 
                                  janela: int = 30) -> Dict[int, int]:
        """
        Calcula score de exclusão para cada número baseado nos concursos anteriores.
        
        Retorna dict: {numero: score}
        Score ALTO = candidato a EXCLUSÃO
        """
        inicio = max(0, idx_concurso - janela)
        dados_janela = historico[inicio:idx_concurso]
        
        if len(dados_janela) < 5:
            return {n: 0 for n in range(1, 26)}
        
        scores = {n: 0 for n in range(1, 26)}
        
        # 1. Calcular frequência na janela
        freq = defaultdict(int)
        for h in dados_janela:
            for n in h['numeros']:
                freq[n] += 1
        
        # 2. Calcular consecutividade (aparições seguidas no final)
        consecutivo = {n: 0 for n in range(1, 26)}
        for h in reversed(dados_janela):
            for n in range(1, 26):
                if n in h['numeros']:
                    consecutivo[n] += 1
                else:
                    break
        
        # 3. Calcular scores
        for n in range(1, 26):
            cons = consecutivo[n]
            freq_n = freq[n]
            freq_pct = freq_n / len(dados_janela) * 100 if len(dados_janela) > 0 else 0
            
            # ANOMALIA: 10+ consecutivas → PROTEÇÃO
            if cons >= 10:
                scores[n] = -5  # NÃO excluir
            
            # 5-9 consecutivas → alta chance de parar
            elif cons >= 5:
                scores[n] = 6
            
            # 4 consecutivas → chance média
            elif cons == 4:
                scores[n] = 5
            
            # 3 consecutivas + alta freq → chance
            elif cons >= 3 and freq_pct >= 70:
                scores[n] = 4
            
            # 100% freq nos últimos 5
            elif cons >= 5:  # Apareceu em todos os últimos 5
                scores[n] = 4
            
            # Frequência muito alta (>80%) → bônus
            if freq_pct > 80:
                scores[n] += 2
        
        return scores
    
    @staticmethod
    def escolher_exclusoes(scores: Dict[int, int], quantidade: int = 2) -> List[int]:
        """
        Escolhe os números a excluir (maior score, evitando score -5).
        """
        # Filtrar números protegidos (anomalias)
        candidatos = [(n, s) for n, s in scores.items() if s > 0]
        
        # Se não há candidatos suficientes, relaxar
        if len(candidatos) < quantidade:
            candidatos = [(n, s) for n, s in scores.items() if s >= 0]
        
        # Ordenar por score decrescente
        candidatos.sort(key=lambda x: x[1], reverse=True)
        
        # Retornar os top
        return [n for n, _ in candidatos[:quantidade]]


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE: SISTEMA DE DISPUTA
# ═══════════════════════════════════════════════════════════════════════════════
class DisputaNeuralPool23:
    """
    Sistema de benchmark e aprendizado que compara:
    - INVERTIDA v3.0 (regras manuais)
    - Rede Neural (aprendizado)
    
    Objetivo: ver se a neural consegue aprender o padrão e superar as regras.
    """
    
    def __init__(self):
        self.historico = []
        self.neural = None
        self.invertida = EstrategiaInvertida()
        self.resultados = []
        
        # Caminho para salvar modelo
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.modelo_path = os.path.join(self.base_path, '..', 'dados', 'neural_exclusao.pkl')
        self.benchmark_path = os.path.join(self.base_path, '..', 'dados', 'neural_exclusao_benchmark.json')

    @staticmethod
    def carregar_benchmark_modelo(modelo_path: Optional[str] = None) -> Optional[Dict]:
        """Carrega metadados do último benchmark salvo para o modelo neural."""
        if modelo_path:
            dados_dir = os.path.dirname(modelo_path)
            benchmark_path = os.path.join(dados_dir, 'neural_exclusao_benchmark.json')
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            benchmark_path = os.path.join(base_path, '..', 'dados', 'neural_exclusao_benchmark.json')

        if not os.path.exists(benchmark_path):
            return None

        try:
            with open(benchmark_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _salvar_benchmark_modelo(self, taxa_neural: float, taxa_invertida: float,
                                 concurso_inicio: int, concurso_fim: int,
                                 total_concursos: int, origem: str):
        """Persiste o último benchmark para exibição dinâmica no gerador."""
        try:
            os.makedirs(os.path.dirname(self.benchmark_path), exist_ok=True)
            dados = {
                'taxa_neural': float(round(float(taxa_neural), 1)),
                'taxa_invertida': float(round(float(taxa_invertida), 1)),
                'diferenca_pp': float(round(float(taxa_neural) - float(taxa_invertida), 1)),
                'concurso_inicio': int(concurso_inicio),
                'concurso_fim': int(concurso_fim),
                'total_concursos': int(total_concursos),
                'origem': str(origem),
                'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            with open(self.benchmark_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def carregar_historico(self) -> bool:
        """Carrega histórico do banco de dados"""
        print("\n📊 Carregando histórico...")
        
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
        
        try:
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                    FROM Resultados_INT 
                    ORDER BY Concurso
                ''')
                
                for row in cursor.fetchall():
                    self.historico.append({
                        'concurso': row[0],
                        'numeros': sorted([row[i] for i in range(1, 16)]),
                        'set': set(row[i] for i in range(1, 16))
                    })
                
                print(f"   ✅ {len(self.historico)} concursos carregados")
                return True
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    
    def _extrair_features(self, idx_concurso: int) -> np.ndarray:
        """
        Extrai features para treinar/usar a rede neural.
        
        250 features (10 por número × 25 números):
        - 0-24: Frequência nos últimos 30 (normalizada)
        - 25-49: Atraso de cada número (normalizado)
        - 50-74: Consecutividade (aparições seguidas)
        - 75-99: Tendência (subindo/descendo)
        - 100-124: Frequência nos últimos 10
        - 125-149: Score INVERTIDA (para aprender!)
        - 150-174: Co-ocorrência score (top 5 parceiros)
        - 175-199: Heatmap posicional (concentração nas posições)
        - 200-224: Entropia do padrão de aparição
        - 225-249: Soft exclusion signal (histórico de exclusão)
        """
        features = np.zeros(250)
        
        janela_30 = self.historico[max(0, idx_concurso - 30):idx_concurso]
        janela_10 = self.historico[max(0, idx_concurso - 10):idx_concurso]
        
        if not janela_30:
            return features
        
        # Features 0-24: Frequência 30 concursos
        freq_30 = Counter()
        for h in janela_30:
            freq_30.update(h['numeros'])
        for n in range(1, 26):
            features[n-1] = freq_30[n] / len(janela_30)
        
        # Features 25-49: Atraso
        for n in range(1, 26):
            atraso = 0
            for h in reversed(janela_30):
                if n in h['numeros']:
                    break
                atraso += 1
            features[24 + n] = atraso / 30
        
        # Features 50-74: Consecutividade (aparições seguidas no final)
        for n in range(1, 26):
            cons = 0
            for h in reversed(janela_30):
                if n in h['numeros']:
                    cons += 1
                else:
                    break
            features[49 + n] = cons / 30
        
        # Features 75-99: Tendência (freq últimos 10 vs anteriores 10)
        freq_10 = Counter()
        for h in janela_10:
            freq_10.update(h['numeros'])
        
        janela_anterior = self.historico[max(0, idx_concurso - 20):max(0, idx_concurso - 10)]
        freq_anterior = Counter()
        for h in janela_anterior:
            freq_anterior.update(h['numeros'])
        
        for n in range(1, 26):
            if len(janela_10) > 0 and len(janela_anterior) > 0:
                tend = (freq_10[n] / len(janela_10)) - (freq_anterior[n] / len(janela_anterior))
                features[74 + n] = (tend + 1) / 2  # Normaliza para 0-1
        
        # Features 100-124: Frequência 10 concursos
        for n in range(1, 26):
            features[99 + n] = freq_10[n] / len(janela_10) if janela_10 else 0
        
        # Features 125-149: Score INVERTIDA (para a neural aprender a lógica!)
        scores_inv = self.invertida.calcular_scores_exclusao(self.historico, idx_concurso)
        max_score = max(scores_inv.values()) if scores_inv else 1
        for n in range(1, 26):
            features[124 + n] = scores_inv[n] / max(1, max_score) if max_score != 0 else 0
        
        # ─── NOVOS GRUPOS DE FEATURES (v3) ──────────────────────────────
        
        # Features 150-174: Co-ocorrência score (frequência de pares)
        # Para cada número, média das top 5 co-ocorrências com parceiros
        pair_count = Counter()
        for h in janela_30:
            nums = h['numeros']
            for i_n in range(len(nums)):
                for j_n in range(i_n + 1, len(nums)):
                    pair_count[(min(nums[i_n], nums[j_n]), max(nums[i_n], nums[j_n]))] += 1
        
        max_pair = max(pair_count.values()) if pair_count else 1
        for n in range(1, 26):
            pares_n = [pair_count.get((min(n, m), max(n, m)), 0) for m in range(1, 26) if m != n]
            features[149 + n] = (sum(sorted(pares_n, reverse=True)[:5]) / max(1, 5 * max_pair))
        
        # Features 175-199: Heatmap posicional
        # Quão concentrado cada número está nas suas posições históricas?
        pos_freq = {}  # {número: Counter de posições}
        for h in janela_30:
            nums_sorted = sorted(h['numeros'])
            for pos_idx, num in enumerate(nums_sorted):
                if num not in pos_freq:
                    pos_freq[num] = Counter()
                pos_freq[num][pos_idx] += 1
        
        for n in range(1, 26):
            if n in pos_freq:
                total_appearances = sum(pos_freq[n].values())
                if total_appearances > 0:
                    top3_pos = pos_freq[n].most_common(3)
                    top3_ratio = sum(c for _, c in top3_pos) / total_appearances
                    features[174 + n] = top3_ratio  # Já 0-1
        
        # Features 200-224: Entropia do padrão de aparição
        # Padrão regular = baixa entropia, caótico = alta entropia
        for n in range(1, 26):
            sequence = [1 if n in h['numeros'] else 0 for h in janela_30]
            
            transitions = Counter()
            for k in range(len(sequence) - 1):
                transitions[(sequence[k], sequence[k+1])] += 1
            
            total_trans = sum(transitions.values())
            if total_trans > 0:
                entropy = 0.0
                for count in transitions.values():
                    p = count / total_trans
                    if p > 0:
                        entropy -= p * math.log2(p)
                # Normalizar: entropia máxima para 4 estados = 2.0
                features[199 + n] = entropy / 2.0
        
        # Features 225-249: Soft Exclusion signal
        # O número foi excluído recentemente pela INVERTIDA? A exclusão acertou?
        exclusion_success = np.zeros(25)
        for lookback in range(min(5, idx_concurso)):
            idx_check = idx_concurso - 1 - lookback
            if idx_check < 30:
                continue
            scores_past = self.invertida.calcular_scores_exclusao(self.historico, idx_check)
            if not scores_past:
                continue
            top2 = sorted(scores_past, key=scores_past.get, reverse=True)[:2]
            resultado_check = set(self.historico[idx_check]['numeros'])
            for exc_num in top2:
                if exc_num not in resultado_check:
                    exclusion_success[exc_num - 1] += 0.2  # Exclusão correta
                else:
                    exclusion_success[exc_num - 1] -= 0.2  # Exclusão errada (apareceu!)
        
        for n in range(1, 26):
            features[224 + n] = (exclusion_success[n-1] + 1) / 2  # Normalizar para 0-1
        
        return features
    
    def executar_disputa(self, concurso_inicio: int = 3000, concurso_fim: int = None,
                         treinar_durante: bool = True) -> Dict:
        """
        Executa disputa entre INVERTIDA e Neural em um range de concursos.
        
        Args:
            concurso_inicio: Primeiro concurso a testar
            concurso_fim: Último concurso (None = último disponível)
            treinar_durante: Se True, treina a neural após cada erro
            
        Returns:
            Dict com estatísticas comparativas
        """
        print("\n" + "═" * 70)
        print("🥊 DISPUTA: NEURAL vs INVERTIDA v3.0")
        print("═" * 70)
        
        # Inicializar ou carregar neural
        if os.path.exists(self.modelo_path):
            print("\n🧠 Carregando modelo neural salvo...")
            self.neural = RedeNeuralExclusao.carregar(self.modelo_path)
        else:
            print("\n🧠 Criando nova rede neural...")
            self.neural = RedeNeuralExclusao()
        
        # Determinar range de concursos
        concursos_disponiveis = {h['concurso']: i for i, h in enumerate(self.historico)}
        
        if concurso_inicio not in concursos_disponiveis:
            concurso_inicio = min(c for c in concursos_disponiveis.keys() if c >= concurso_inicio)
        
        if concurso_fim is None:
            concurso_fim = max(concursos_disponiveis.keys())
        
        idx_inicio = concursos_disponiveis.get(concurso_inicio)
        idx_fim = concursos_disponiveis.get(concurso_fim)
        
        if idx_inicio is None or idx_fim is None:
            print("❌ Concursos não encontrados no histórico!")
            return {}
        
        # Ajustar índice inicial para garantir 30 anteriores
        idx_inicio_real = max(30, idx_inicio)  # Precisa de pelo menos 30 concursos anteriores
        
        total_real = idx_fim - idx_inicio_real + 1
        if total_real <= 0:
            print(f"\n❌ Range muito pequeno! Precisa de concursos com índice >= 30.")
            print(f"   idx_inicio={idx_inicio}, idx_fim={idx_fim}, precisamos idx >= 30")
            return {}
        
        print(f"\n📅 Range: #{concurso_inicio} a #{concurso_fim}")
        print(f"   Índices: {idx_inicio_real} a {idx_fim} ({total_real} concursos)")
        print(f"🔧 Treinar durante disputa: {'Sim' if treinar_durante else 'Não'}")
        
        # Estatísticas
        stats = {
            'invertida': {'acertos_2': 0, 'acertos_1': 0, 'erros': 0},
            'neural': {'acertos_2': 0, 'acertos_1': 0, 'erros': 0},
            'empates': 0,
            'neural_melhor': 0,
            'invertida_melhor': 0,
            'detalhes': []
        }
        
        # Para cada concurso (já temos 30 anteriores garantidos)
        for idx in range(idx_inicio_real, idx_fim + 1):
            concurso = self.historico[idx]['concurso']
            resultado = self.historico[idx]['set']
            
            # Extrair features
            features = self._extrair_features(idx)
            
            # INVERTIDA v3.0 escolhe exclusões
            scores_inv = self.invertida.calcular_scores_exclusao(self.historico, idx)
            excluidos_inv = self.invertida.escolher_exclusoes(scores_inv, 2)
            
            # Neural escolhe exclusões
            excluidos_neural = self.neural.prever_exclusoes(features, 2)
            
            # Avaliar: quantos excluídos NÃO estavam no resultado (ACERTO)
            acertos_inv = sum(1 for n in excluidos_inv if n not in resultado)
            acertos_neural = sum(1 for n in excluidos_neural if n not in resultado)
            
            # Atualizar estatísticas
            if acertos_inv == 2:
                stats['invertida']['acertos_2'] += 1
            elif acertos_inv == 1:
                stats['invertida']['acertos_1'] += 1
            else:
                stats['invertida']['erros'] += 1
            
            if acertos_neural == 2:
                stats['neural']['acertos_2'] += 1
            elif acertos_neural == 1:
                stats['neural']['acertos_1'] += 1
            else:
                stats['neural']['erros'] += 1
            
            # Comparar vencedor
            if acertos_neural > acertos_inv:
                stats['neural_melhor'] += 1
            elif acertos_inv > acertos_neural:
                stats['invertida_melhor'] += 1
            else:
                stats['empates'] += 1
            
            # Guardar detalhes
            stats['detalhes'].append({
                'concurso': concurso,
                'resultado': sorted(resultado),
                'excluidos_inv': excluidos_inv,
                'excluidos_neural': excluidos_neural,
                'acertos_inv': acertos_inv,
                'acertos_neural': acertos_neural
            })
            
            # TREINAR a neural após cada resultado (aprendizado online)
            if treinar_durante:
                # Target: números que NÃO saíram devem ter score alto
                y = np.zeros(25)
                for n in range(1, 26):
                    if n not in resultado:
                        y[n-1] = 1.0  # NÃO saiu → score alto (candidato a exclusão)
                
                self.neural.treinar(features.reshape(1, -1), y.reshape(1, -1), epochs=5, lr=0.001)
            
            # Progresso a cada 100 concursos
            if (idx - idx_inicio_real) % 100 == 0:
                pct = (idx - idx_inicio_real) / total_real * 100
                print(f"   [{pct:5.1f}%] Concurso #{concurso}", end="\r")
        
        print(f"   [100.0%] Concluído!                    ")
        
        # Salvar modelo treinado
        if treinar_durante:
            os.makedirs(os.path.dirname(self.modelo_path), exist_ok=True)
            self.neural.salvar(self.modelo_path)
            print(f"\n💾 Modelo neural salvo em: {self.modelo_path}")
        
        # Exibir resultados
        self._exibir_resultados(stats, total_real)

        taxa_2_inv = stats['invertida']['acertos_2'] / total_real * 100
        taxa_2_neu = stats['neural']['acertos_2'] / total_real * 100
        self._salvar_benchmark_modelo(
            taxa_neural=taxa_2_neu,
            taxa_invertida=taxa_2_inv,
            concurso_inicio=concurso_inicio,
            concurso_fim=concurso_fim,
            total_concursos=total_real,
            origem='disputa'
        )
        
        self.resultados = stats
        return stats
    
    def _exibir_resultados(self, stats: Dict, total: int):
        """Exibe resultados da disputa"""
        print("\n" + "═" * 70)
        print("📊 RESULTADOS DA DISPUTA")
        print("═" * 70)
        
        print(f"\n   Total de concursos testados: {total}")
        
        if total <= 0:
            print("   ⚠️  Nenhum concurso foi processado!")
            return
        
        # Tabela comparativa
        print("\n   ╔═══════════════════╤══════════════╤══════════════╗")
        print("   ║ Métrica           │ INVERTIDA    │ NEURAL       ║")
        print("   ╠═══════════════════╪══════════════╪══════════════╣")
        
        inv = stats['invertida']
        neu = stats['neural']
        
        taxa_2_inv = inv['acertos_2'] / total * 100
        taxa_2_neu = neu['acertos_2'] / total * 100
        taxa_1_inv = inv['acertos_1'] / total * 100
        taxa_1_neu = neu['acertos_1'] / total * 100
        taxa_0_inv = inv['erros'] / total * 100
        taxa_0_neu = neu['erros'] / total * 100
        
        melhor_2 = "⭐" if taxa_2_inv > taxa_2_neu else ("⭐" if taxa_2_neu > taxa_2_inv else "")
        melhor_1 = "⭐" if taxa_1_inv < taxa_1_neu else ("⭐" if taxa_1_neu < taxa_1_inv else "")
        
        print(f"   ║ Acerto 2/2 ✅    │ {inv['acertos_2']:4} ({taxa_2_inv:5.1f}%) │ {neu['acertos_2']:4} ({taxa_2_neu:5.1f}%) ║ {melhor_2}")
        print(f"   ║ Acerto 1/2       │ {inv['acertos_1']:4} ({taxa_1_inv:5.1f}%) │ {neu['acertos_1']:4} ({taxa_1_neu:5.1f}%) ║")
        print(f"   ║ Erro 0/2 ❌      │ {inv['erros']:4} ({taxa_0_inv:5.1f}%) │ {neu['erros']:4} ({taxa_0_neu:5.1f}%) ║")
        print("   ╟───────────────────┼──────────────┼──────────────╢")
        
        # Taxa de jackpot (se excluiu certo, o jackpot estaria no pool)
        taxa_jackpot_inv = (inv['acertos_2']) / total * 100
        taxa_jackpot_neu = (neu['acertos_2']) / total * 100
        melhor_jp = "⭐" if taxa_jackpot_inv > taxa_jackpot_neu else ("⭐" if taxa_jackpot_neu > taxa_jackpot_inv else "")
        
        print(f"   ║ Taxa Jackpot     │     {taxa_jackpot_inv:5.1f}%   │     {taxa_jackpot_neu:5.1f}%   ║ {melhor_jp}")
        print("   ╚═══════════════════╧══════════════╧══════════════╝")
        
        # Resumo da disputa
        print("\n   🏆 PLACAR GERAL:")
        print(f"      • Neural venceu: {stats['neural_melhor']} concursos ({stats['neural_melhor']/total*100:.1f}%)")
        print(f"      • INVERTIDA venceu: {stats['invertida_melhor']} concursos ({stats['invertida_melhor']/total*100:.1f}%)")
        print(f"      • Empates: {stats['empates']} concursos ({stats['empates']/total*100:.1f}%)")
        
        # Conclusão
        print("\n   📌 CONCLUSÃO:")
        if taxa_jackpot_neu >= taxa_jackpot_inv + 2:
            print("      🎉 A NEURAL SUPEROU a estratégia INVERTIDA!")
            print("      💡 Recomendação: usar Neural para ranquear exclusões")
        elif taxa_jackpot_inv >= taxa_jackpot_neu + 2:
            print("      📊 INVERTIDA v3.0 continua superior")
            print("      💡 Recomendação: manter estratégia atual")
        else:
            print("      🤝 Empate técnico (diferença < 2pp)")
            print("      💡 Recomendação: testar híbrido (Neural + INVERTIDA)")
    
    def retreinamento_intensivo(self, concurso_inicio: int = 3000, concurso_fim: int = None,
                                 iteracoes: int = 5, lr_inicial: float = 0.01,
                                 epochs_por_amostra: int = 10) -> Dict:
        """
        🔥 RETREINAMENTO INTENSIVO
        
        Permite múltiplas iterações completas sobre o mesmo dataset,
        variando parâmetros para buscar melhorias.
        
        Args:
            concurso_inicio: Primeiro concurso do range
            concurso_fim: Último concurso (None = último disponível)
            iteracoes: Quantas passagens completas pelo dataset
            lr_inicial: Learning rate inicial (decai a cada iteração)
            epochs_por_amostra: Épocas de treino por amostra
        
        Returns:
            Dict com histórico de resultados por iteração
        """
        print("\n" + "═" * 70)
        print("🔥 RETREINAMENTO INTENSIVO - Buscando melhorias")
        print("═" * 70)
        
        # Determinar range
        concursos_disponiveis = {h['concurso']: i for i, h in enumerate(self.historico)}
        
        if concurso_inicio not in concursos_disponiveis:
            concurso_inicio = min(c for c in concursos_disponiveis.keys() if c >= concurso_inicio)
        
        if concurso_fim is None:
            concurso_fim = max(concursos_disponiveis.keys())
        
        idx_inicio = max(30, concursos_disponiveis.get(concurso_inicio, 30))
        idx_fim = concursos_disponiveis.get(concurso_fim, len(self.historico) - 1)
        total_real = idx_fim - idx_inicio + 1
        
        print(f"\n📅 Range: #{concurso_inicio} a #{concurso_fim} ({total_real} concursos)")
        print(f"🔁 Iterações: {iteracoes}")
        print(f"📚 Épocas por amostra: {epochs_por_amostra}")
        print(f"📈 LR inicial: {lr_inicial}")
        
        # Histórico de resultados
        historico_iteracoes = []
        melhor_taxa = 0
        melhor_modelo = None
        
        # Resetar ou carregar modelo
        reset = input("\n🔄 Resetar rede neural? [s/N]: ").strip().lower() == 's'
        if reset or not os.path.exists(self.modelo_path):
            print("\n🧠 Criando nova rede neural...")
            self.neural = RedeNeuralExclusao()
        else:
            print("\n🧠 Carregando modelo existente...")
            self.neural = RedeNeuralExclusao.carregar(self.modelo_path)
        
        # Loop de iterações
        for it in range(iteracoes):
            lr = lr_inicial * (0.7 ** it)  # Decay de 30% por iteração
            
            print(f"\n{'─' * 60}")
            print(f"📊 ITERAÇÃO {it + 1}/{iteracoes} (LR: {lr:.6f})")
            print(f"{'─' * 60}")
            
            # Coletar features e targets
            X_all = []
            y_all = []
            
            for idx in range(idx_inicio, idx_fim + 1):
                resultado = self.historico[idx]['set']
                features = self._extrair_features(idx)
                
                # Target: números que NÃO saíram devem ter score alto
                y = np.zeros(25)
                for n in range(1, 26):
                    if n not in resultado:
                        y[n-1] = 1.0
                
                X_all.append(features)
                y_all.append(y)
            
            X = np.array(X_all)
            y = np.array(y_all)
            
            # Treinar batch (shuffle)
            indices = np.arange(len(X))
            np.random.shuffle(indices)
            
            for epoch in range(epochs_por_amostra):
                # Mini-batches de 32
                for i in range(0, len(X), 32):
                    batch_idx = indices[i:i+32]
                    X_batch = X[batch_idx]
                    y_batch = y[batch_idx]
                    self.neural.treinar(X_batch, y_batch, epochs=1, lr=lr)
                
                if (epoch + 1) % 5 == 0:
                    print(f"   📚 Época {epoch + 1}/{epochs_por_amostra}", end="\r")
            
            # Avaliar após iteração
            stats = {'acertos_2': 0, 'acertos_1': 0, 'erros': 0}
            
            for idx in range(idx_inicio, idx_fim + 1):
                resultado = self.historico[idx]['set']
                features = self._extrair_features(idx)
                excluidos = self.neural.prever_exclusoes(features, 2)
                acertos = sum(1 for n in excluidos if n not in resultado)
                
                if acertos == 2:
                    stats['acertos_2'] += 1
                elif acertos == 1:
                    stats['acertos_1'] += 1
                else:
                    stats['erros'] += 1
            
            taxa_2 = stats['acertos_2'] / total_real * 100
            taxa_1 = stats['acertos_1'] / total_real * 100
            taxa_erro = stats['erros'] / total_real * 100
            
            historico_iteracoes.append({
                'iteracao': it + 1,
                'lr': lr,
                'taxa_2_2': taxa_2,
                'taxa_1_2': taxa_1,
                'taxa_0_2': taxa_erro,
                'acertos_2': stats['acertos_2'],
                'total': total_real
            })
            
            print(f"   ✅ Acerto 2/2: {stats['acertos_2']:4} ({taxa_2:5.1f}%)")
            print(f"      Acerto 1/2: {stats['acertos_1']:4} ({taxa_1:5.1f}%)")
            print(f"   ❌ Erro 0/2:   {stats['erros']:4} ({taxa_erro:5.1f}%)")
            
            # Guardar melhor modelo
            if taxa_2 > melhor_taxa:
                melhor_taxa = taxa_2
                melhor_modelo = pickle.dumps({
                    'pesos': self.neural.pesos.copy(),
                    'bias': self.neural.bias.copy(),
                    'tamanhos': self.neural.tamanhos
                })
                print(f"   🏆 NOVO RECORDE! Taxa 2/2: {taxa_2:.1f}%")
        
        # Restaurar melhor modelo
        if melhor_modelo:
            dados = pickle.loads(melhor_modelo)
            self.neural.pesos = dados['pesos']
            self.neural.bias = dados['bias']
            
            # Salvar melhor modelo
            self.neural.salvar(self.modelo_path)
            print(f"\n💾 Melhor modelo salvo (Taxa 2/2: {melhor_taxa:.1f}%)")
        
        # Comparar com INVERTIDA
        print("\n" + "═" * 70)
        print("📊 COMPARAÇÃO FINAL COM INVERTIDA v3.0")
        print("═" * 70)
        
        stats_inv = {'acertos_2': 0, 'acertos_1': 0, 'erros': 0}
        
        for idx in range(idx_inicio, idx_fim + 1):
            resultado = self.historico[idx]['set']
            scores_inv = self.invertida.calcular_scores_exclusao(self.historico, idx)
            excluidos_inv = self.invertida.escolher_exclusoes(scores_inv, 2)
            acertos = sum(1 for n in excluidos_inv if n not in resultado)
            
            if acertos == 2:
                stats_inv['acertos_2'] += 1
            elif acertos == 1:
                stats_inv['acertos_1'] += 1
            else:
                stats_inv['erros'] += 1
        
        taxa_inv = stats_inv['acertos_2'] / total_real * 100
        
        print(f"\n   INVERTIDA v3.0: {stats_inv['acertos_2']:4} acertos 2/2 ({taxa_inv:.1f}%)")
        print(f"   NEURAL (melhor): {historico_iteracoes[-1]['acertos_2']:4} acertos 2/2 ({melhor_taxa:.1f}%)")
        print(f"\n   Diferença: {melhor_taxa - taxa_inv:+.1f}pp")
        
        if melhor_taxa > taxa_inv + 2:
            print("\n   🎉 NEURAL VENCEU! Superou INVERTIDA em mais de 2pp!")
        elif taxa_inv > melhor_taxa + 2:
            print("\n   📊 INVERTIDA v3.0 ainda é superior")
        else:
            print("\n   🤝 Empate técnico entre Neural e INVERTIDA")

        self._salvar_benchmark_modelo(
            taxa_neural=melhor_taxa,
            taxa_invertida=taxa_inv,
            concurso_inicio=concurso_inicio,
            concurso_fim=concurso_fim,
            total_concursos=total_real,
            origem='retreino'
        )
        
        return {
            'historico': historico_iteracoes,
            'melhor_taxa': melhor_taxa,
            'taxa_invertida': taxa_inv,
            'diferenca': melhor_taxa - taxa_inv
        }
    
    def retreinar_automatico(self, concurso_inicio: int = 3000, concurso_fim: int = None,
                              iteracoes: int = 5, lr_inicial: float = 0.01,
                              epochs_por_amostra: int = 10, resetar: bool = True) -> Dict:
        """
        🔥 RETREINAMENTO AUTOMÁTICO (sem prompts interativos)
        
        Versão do retreinamento intensivo para chamada programática.
        """
        print("\n" + "═" * 70)
        print("🔥 RETREINAMENTO AUTOMÁTICO - Sem interação")
        print("═" * 70)
        
        # Determinar range
        concursos_disponiveis = {h['concurso']: i for i, h in enumerate(self.historico)}
        
        if concurso_inicio not in concursos_disponiveis:
            concurso_inicio = min(c for c in concursos_disponiveis.keys() if c >= concurso_inicio)
        
        if concurso_fim is None:
            concurso_fim = max(concursos_disponiveis.keys())
        
        idx_inicio = max(30, concursos_disponiveis.get(concurso_inicio, 30))
        idx_fim = concursos_disponiveis.get(concurso_fim, len(self.historico) - 1)
        total_real = idx_fim - idx_inicio + 1
        
        print(f"\n📅 Range: #{concurso_inicio} a #{concurso_fim} ({total_real} concursos)")
        print(f"🔁 Iterações: {iteracoes}")
        print(f"📚 Épocas por amostra: {epochs_por_amostra}")
        print(f"📈 LR inicial: {lr_inicial}")
        print(f"🔄 Resetar modelo: {'Sim' if resetar else 'Não'}")
        
        # Histórico
        historico_iteracoes = []
        melhor_taxa = 0
        melhor_modelo = None
        
        # Criar ou carregar modelo
        if resetar:
            print("\n🧠 Criando nova rede neural (resetar=True)...")
            self.neural = RedeNeuralExclusao()
        elif os.path.exists(self.modelo_path):
            print("\n🧠 Carregando modelo existente...")
            self.neural = RedeNeuralExclusao.carregar(self.modelo_path)
        else:
            print("\n🧠 Modelo não encontrado, criando nova rede neural...")
            self.neural = RedeNeuralExclusao()
        
        # Loop de iterações
        for it in range(iteracoes):
            lr = lr_inicial * (0.7 ** it)
            
            print(f"\n{'─' * 60}")
            print(f"📊 ITERAÇÃO {it + 1}/{iteracoes} (LR: {lr:.6f})")
            print(f"{'─' * 60}")
            
            # Coletar features e targets
            X_all = []
            y_all = []
            
            for idx in range(idx_inicio, idx_fim + 1):
                resultado = self.historico[idx]['set']
                features = self._extrair_features(idx)
                
                y = np.zeros(25)
                for n in range(1, 26):
                    if n not in resultado:
                        y[n-1] = 1.0
                
                X_all.append(features)
                y_all.append(y)
            
            X = np.array(X_all)
            y = np.array(y_all)
            
            # Treinar batch (shuffle)
            indices = np.arange(len(X))
            np.random.shuffle(indices)
            
            for epoch in range(epochs_por_amostra):
                for i in range(0, len(X), 32):
                    batch_idx = indices[i:i+32]
                    X_batch = X[batch_idx]
                    y_batch = y[batch_idx]
                    self.neural.treinar(X_batch, y_batch, epochs=1, lr=lr)
                
                if (epoch + 1) % 5 == 0:
                    print(f"   📚 Época {epoch + 1}/{epochs_por_amostra}", end="\r")
            
            # Avaliar
            stats = {'acertos_2': 0, 'acertos_1': 0, 'erros': 0}
            
            for idx in range(idx_inicio, idx_fim + 1):
                resultado = self.historico[idx]['set']
                features = self._extrair_features(idx)
                excluidos = self.neural.prever_exclusoes(features, 2)
                acertos = sum(1 for n in excluidos if n not in resultado)
                
                if acertos == 2:
                    stats['acertos_2'] += 1
                elif acertos == 1:
                    stats['acertos_1'] += 1
                else:
                    stats['erros'] += 1
            
            taxa_2 = stats['acertos_2'] / total_real * 100
            taxa_1 = stats['acertos_1'] / total_real * 100
            taxa_erro = stats['erros'] / total_real * 100
            
            historico_iteracoes.append({
                'iteracao': it + 1,
                'lr': lr,
                'taxa_2_2': taxa_2,
                'taxa_1_2': taxa_1,
                'taxa_0_2': taxa_erro,
                'acertos_2': stats['acertos_2'],
                'total': total_real
            })
            
            print(f"   ✅ Acerto 2/2: {stats['acertos_2']:4} ({taxa_2:5.1f}%)")
            print(f"      Acerto 1/2: {stats['acertos_1']:4} ({taxa_1:5.1f}%)")
            print(f"   ❌ Erro 0/2:   {stats['erros']:4} ({taxa_erro:5.1f}%)")
            
            if taxa_2 > melhor_taxa:
                melhor_taxa = taxa_2
                melhor_modelo = pickle.dumps({
                    'pesos': {k: v.copy() for k, v in self.neural.pesos.items()},
                    'bias': {k: v.copy() for k, v in self.neural.bias.items()},
                    'tamanhos': self.neural.tamanhos
                })
                print(f"   🏆 NOVO RECORDE! Taxa 2/2: {taxa_2:.1f}%")
        
        # Restaurar melhor modelo
        if melhor_modelo:
            dados = pickle.loads(melhor_modelo)
            self.neural.pesos = dados['pesos']
            self.neural.bias = dados['bias']
            
            os.makedirs(os.path.dirname(self.modelo_path), exist_ok=True)
            self.neural.salvar(self.modelo_path)
            print(f"\n💾 Melhor modelo salvo (Taxa 2/2: {melhor_taxa:.1f}%)")
        
        # Comparar com INVERTIDA
        print("\n" + "═" * 70)
        print("📊 COMPARAÇÃO FINAL COM INVERTIDA v3.0")
        print("═" * 70)
        
        stats_inv = {'acertos_2': 0, 'acertos_1': 0, 'erros': 0}
        
        for idx in range(idx_inicio, idx_fim + 1):
            resultado = self.historico[idx]['set']
            scores_inv = self.invertida.calcular_scores_exclusao(self.historico, idx)
            excluidos_inv = self.invertida.escolher_exclusoes(scores_inv, 2)
            acertos = sum(1 for n in excluidos_inv if n not in resultado)
            
            if acertos == 2:
                stats_inv['acertos_2'] += 1
            elif acertos == 1:
                stats_inv['acertos_1'] += 1
            else:
                stats_inv['erros'] += 1
        
        taxa_inv = stats_inv['acertos_2'] / total_real * 100
        
        print(f"\n   INVERTIDA v3.0: {stats_inv['acertos_2']:4} acertos 2/2 ({taxa_inv:.1f}%)")
        print(f"   NEURAL (melhor): {int(melhor_taxa * total_real / 100):4} acertos 2/2 ({melhor_taxa:.1f}%)")
        print(f"\n   Diferença: {melhor_taxa - taxa_inv:+.1f}pp")
        
        if melhor_taxa > taxa_inv + 2:
            print("\n   🎉 NEURAL VENCEU! Superou INVERTIDA em mais de 2pp!")
        elif taxa_inv > melhor_taxa + 2:
            print("\n   📊 INVERTIDA v3.0 ainda é superior")
        else:
            print("\n   🤝 Empate técnico entre Neural e INVERTIDA")
        
        return {
            'historico': historico_iteracoes,
            'melhor_taxa': melhor_taxa,
            'taxa_invertida': taxa_inv,
            'diferenca': melhor_taxa - taxa_inv
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÃO: MENU DE DISPUTA
# ═══════════════════════════════════════════════════════════════════════════════
def menu_disputa():
    """Menu interativo para a disputa Neural vs Pool 23"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*20 + "🥊 DISPUTA NEURAL vs POOL 23" + " "*20 + "║")
    print("║" + " "*15 + "Sistema de Benchmark e Aprendizado" + " "*18 + "║")
    print("╚" + "═"*68 + "╝")
    
    print("\n📋 OPÇÕES:")
    print("   1️⃣  Executar disputa completa (treina durante)")
    print("   2️⃣  Testar modelo salvo (sem treinar)")
    print("   3️⃣  Resetar modelo neural")
    print("   4️⃣  🔥 Retreinamento INTENSIVO (múltiplas iterações)")
    print("   0️⃣  Voltar")
    
    opcao = input("\n   Escolha: ").strip()
    
    if opcao == "0":
        return
    
    disputa = DisputaNeuralPool23()
    
    if not disputa.carregar_historico():
        input("\n⏸️ Pressione ENTER para voltar...")
        return
    
    # Perguntar range
    print("\n📅 RANGE DE CONCURSOS:")
    try:
        inicio_str = input("   Concurso inicial [3000]: ").strip()
        inicio = int(inicio_str) if inicio_str else 3000
        
        fim_str = input("   Concurso final [último]: ").strip()
        fim = int(fim_str) if fim_str else None
    except:
        inicio = 3000
        fim = None
    
    if opcao == "1":
        disputa.executar_disputa(inicio, fim, treinar_durante=True)
    elif opcao == "2":
        disputa.executar_disputa(inicio, fim, treinar_durante=False)
    elif opcao == "3":
        modelo_path = os.path.join(disputa.base_path, '..', 'dados', 'neural_exclusao.pkl')
        if os.path.exists(modelo_path):
            os.remove(modelo_path)
            print("\n✅ Modelo neural resetado!")
        else:
            print("\n⚠️ Modelo não existe ainda")
    elif opcao == "4":
        # Retreinamento intensivo
        try:
            iter_str = input("\n   Número de iterações [5]: ").strip()
            iteracoes = int(iter_str) if iter_str else 5
            
            epochs_str = input("   Épocas por amostra [10]: ").strip()
            epochs = int(epochs_str) if epochs_str else 10
            
            lr_str = input("   Learning rate inicial [0.01]: ").strip()
            lr = float(lr_str) if lr_str else 0.01
        except:
            iteracoes = 5
            epochs = 10
            lr = 0.01
        
        disputa.retreinamento_intensivo(inicio, fim, iteracoes=iteracoes, 
                                         epochs_por_amostra=epochs, lr_inicial=lr)
    
    input("\n⏸️ Pressione ENTER para voltar...")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    menu_disputa()
