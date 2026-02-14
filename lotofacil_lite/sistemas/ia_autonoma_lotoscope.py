#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 IA AUTÔNOMA LOTOSCOPE - SISTEMA DE APRENDIZADO SEMI-AUTÔNOMO
================================================================

Sistema avançado de IA que:
- Rede neural escalável (24k → 48k → 192k neurônios)
- Explora automaticamente todos os algoritmos disponíveis
- Testa combinações contra histórico de forma autônoma
- Sugere apostas otimizadas para máximo acerto
- Aprende continuamente e melhora com cada execução

Autor: LotoScope AI
Data: Janeiro 2026
"""

import os
import sys
import json
import random
import pickle
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict, field
import pyodbc

# Adiciona path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class ConfiguracaoIA:
    """Configurações da IA Autônoma"""
    # Rede Neural
    neuronios: int = 48000  # 24000, 48000, ou 192000
    camadas_ocultas: int = 5
    taxa_aprendizado: float = 0.001
    
    # Exploração
    max_iteracoes: int = 1000
    max_combinacoes_por_teste: int = 500
    
    # Validação
    concursos_validacao: int = 100  # Últimos N para validar
    concursos_treino: int = 3000     # Usar para treinar
    
    # Algoritmos a explorar
    algoritmos_ativos: List[str] = field(default_factory=lambda: [
        'frequencia',
        'atraso',
        'pares_impares',
        'posicional',
        'association_rules',
        'transicoes',
        'neural',
        'genetico',
        'ensemble'
    ])
    
    # Persistência
    arquivo_modelo: str = "ia_autonoma_modelo.pkl"
    arquivo_historico: str = "ia_autonoma_historico.json"
    arquivo_apostas_pendentes: str = "ia_autonoma_apostas_pendentes.json"


@dataclass
class ApostaPendente:
    """Aposta pendente de validação"""
    concurso_alvo: int
    combinacoes: List[List[int]]
    algoritmo_usado: str
    data_geracao: str
    validada: bool = False
    acertos: List[int] = field(default_factory=list)
    melhor_acerto: int = 0


@dataclass
class ResultadoIteracao:
    """Resultado de uma iteração de aprendizado"""
    iteracao: int
    algoritmo: str
    combinacoes_geradas: int
    media_acertos: float
    max_acertos: int
    min_acertos: int
    acertos_11_mais: int
    acertos_14_mais: int
    tempo_segundos: float
    parametros: Dict


class RedeNeuralAvancada:
    """
    Rede Neural Avançada para Lotofácil
    
    Arquitetura escalável:
    - 24.000 neurônios: Básico
    - 48.000 neurônios: Intermediário
    - 192.000 neurônios: Avançado
    """
    
    def __init__(self, neuronios: int = 48000, camadas: int = 5, silencioso: bool = False):
        self.neuronios = neuronios
        self.camadas = camadas
        self.pesos = {}
        self.bias = {}
        self.memoria = []
        self.historico_treino = []
        
        self._inicializar_arquitetura(silencioso)
        
    def _inicializar_arquitetura(self, silencioso: bool = False):
        """Inicializa arquitetura da rede neural"""
        np.random.seed(42)  # Reprodutibilidade
        
        # Calcula tamanho de cada camada
        # Entrada: 300 features (freq + atraso + última + posicional + FOCO JANELA 10)
        # Saída: 25 (score para cada número)
        
        entrada = 300
        saida = 25
        
        # Distribui neurônios pelas camadas ocultas
        neuronios_por_camada = self.neuronios // self.camadas
        
        tamanhos = [entrada]
        for i in range(self.camadas):
            # Aumenta no meio, diminui nas pontas (arquitetura "diamante")
            fator = 1.0 + 0.5 * (1 - abs(i - self.camadas/2) / (self.camadas/2))
            tamanhos.append(int(neuronios_por_camada * fator))
        tamanhos.append(saida)
        
        # Aviso para redes grandes
        if not silencioso:
            if self.neuronios >= 192000:
                print(f"   ⚠️ Rede grande ({self.neuronios:,} neurônios) - pode demorar 30-60s...")
            elif self.neuronios >= 48000:
                print(f"   ⏳ Inicializando {self.neuronios:,} neurônios...")
        
        # Inicializa pesos (Xavier initialization)
        total_camadas = len(tamanhos) - 1
        for i in range(total_camadas):
            if not silencioso:
                pct = int((i + 1) / total_camadas * 100)
                barra = '█' * (pct // 5) + '░' * (20 - pct // 5)
                print(f"      [{barra}] {pct:3d}% - Camada {i+1}/{total_camadas}", end='\r')
            
            scale = np.sqrt(2.0 / (tamanhos[i] + tamanhos[i+1]))
            self.pesos[f'W{i}'] = np.random.randn(tamanhos[i], tamanhos[i+1]).astype(np.float32) * scale
            self.bias[f'b{i}'] = np.zeros(tamanhos[i+1], dtype=np.float32)
        
        self.tamanhos = tamanhos
        
        if not silencioso:
            print(f"      [████████████████████] 100% - Concluído!          ")
            total_params = sum(w.size for w in self.pesos.values()) + sum(b.size for b in self.bias.values())
            print(f"   🧠 Rede Neural inicializada:")
            print(f"      • {self.neuronios:,} neurônios")
            print(f"      • {self.camadas} camadas ocultas")
            print(f"      • {total_params:,} parâmetros")
            print(f"      • Arquitetura: {' → '.join(map(str, tamanhos))}")
    
    def _relu(self, x):
        """Função de ativação ReLU"""
        return np.maximum(0, x)
    
    def _softmax(self, x):
        """Função softmax para saída"""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Propagação forward"""
        a = x
        for i in range(len(self.pesos)):
            z = np.dot(a, self.pesos[f'W{i}']) + self.bias[f'b{i}']
            if i < len(self.pesos) - 1:
                a = self._relu(z)
            else:
                a = self._softmax(z)
        return a
    
    def treinar(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, lr: float = 0.001):
        """Treina a rede neural com backpropagation"""
        for epoch in range(epochs):
            # Forward
            activations = [X]
            a = X
            for i in range(len(self.pesos)):
                z = np.dot(a, self.pesos[f'W{i}']) + self.bias[f'b{i}']
                if i < len(self.pesos) - 1:
                    a = self._relu(z)
                else:
                    a = self._softmax(z)
                activations.append(a)
            
            # Backward
            delta = activations[-1] - y
            for i in range(len(self.pesos) - 1, -1, -1):
                grad_w = np.dot(activations[i].T, delta) / X.shape[0]
                grad_b = np.mean(delta, axis=0)
                
                # Atualiza pesos
                self.pesos[f'W{i}'] -= lr * grad_w
                self.bias[f'b{i}'] -= lr * grad_b
                
                if i > 0:
                    delta = np.dot(delta, self.pesos[f'W{i}'].T)
                    delta = delta * (activations[i] > 0)  # ReLU derivative
        
        self.historico_treino.append({
            'epochs': epochs,
            'lr': lr,
            'timestamp': datetime.now().isoformat()
        })
    
    def treinar_foco_11(self, X: np.ndarray, y: np.ndarray, historico: List[Dict], 
                         epochs: int = 100, lr: float = 0.001, objetivo_media: float = 11.0):
        """
        Treino FOCADO em atingir média 11+ acertos
        
        Usa função de perda customizada que:
        1. Penaliza fortemente previsões com <11 acertos
        2. Recompensa previsões com 11+ acertos
        3. Ajusta pesos dos números baseado em performance real
        """
        # Calcula performance atual de cada número
        performance_numeros = np.ones(25)  # Base 1.0
        
        # Analisa últimos 100 concursos para ajustar importância
        ultimos = historico[-100:] if len(historico) >= 100 else historico
        
        freq_11_mais = defaultdict(int)  # Quantas vezes o número apareceu em combos que deram 11+
        freq_total = defaultdict(int)
        
        for h in ultimos:
            for n in h['numeros']:
                freq_total[n] += 1
        
        # Boost para números que aparecem consistentemente
        for n in range(1, 26):
            if freq_total[n] > 0:
                # Normaliza entre 0.5 e 1.5
                performance_numeros[n-1] = 0.5 + (freq_total[n] / max(freq_total.values()))
        
        for epoch in range(epochs):
            # Forward
            activations = [X]
            a = X
            for i in range(len(self.pesos)):
                z = np.dot(a, self.pesos[f'W{i}']) + self.bias[f'b{i}']
                if i < len(self.pesos) - 1:
                    a = self._relu(z)
                else:
                    a = self._softmax(z)
                activations.append(a)
            
            # LOSS CUSTOMIZADA FOCADA EM 11+
            # Pesa mais os números que ajudam a atingir 11+
            delta = (activations[-1] - y) * performance_numeros
            
            # Penaliza mais quando erra números importantes
            # (os 15 números do resultado real devem ter peso maior)
            peso_positivos = 2.0  # Dobra penalidade para errar números do resultado
            delta = delta * np.where(y > 0, peso_positivos, 1.0)
            
            for i in range(len(self.pesos) - 1, -1, -1):
                grad_w = np.dot(activations[i].T, delta) / X.shape[0]
                grad_b = np.mean(delta, axis=0)
                
                # Gradient clipping para estabilidade
                grad_w = np.clip(grad_w, -1.0, 1.0)
                grad_b = np.clip(grad_b, -1.0, 1.0)
                
                # Atualiza pesos
                self.pesos[f'W{i}'] -= lr * grad_w
                self.bias[f'b{i}'] -= lr * grad_b
                
                if i > 0:
                    delta = np.dot(delta, self.pesos[f'W{i}'].T)
                    delta = delta * (activations[i] > 0)
        
        self.historico_treino.append({
            'epochs': epochs,
            'lr': lr,
            'tipo': 'foco_11',
            'objetivo': objetivo_media,
            'timestamp': datetime.now().isoformat()
        })
    
    def prever_numeros(self, features: np.ndarray, top_k: int = 15) -> List[int]:
        """Prevê os top K números mais prováveis"""
        scores = self.forward(features.reshape(1, -1))[0]
        indices = np.argsort(scores)[::-1][:top_k]
        return [i + 1 for i in indices]  # Números 1-25
    
    def salvar(self, caminho: str):
        """Salva modelo"""
        with open(caminho, 'wb') as f:
            pickle.dump({
                'pesos': self.pesos,
                'bias': self.bias,
                'tamanhos': self.tamanhos,
                'neuronios': self.neuronios,
                'camadas': self.camadas,
                'memoria': self.memoria,
                'historico_treino': self.historico_treino
            }, f)
    
    @classmethod
    def carregar(cls, caminho: str) -> 'RedeNeuralAvancada':
        """Carrega modelo salvo"""
        with open(caminho, 'rb') as f:
            dados = pickle.load(f)
        
        rede = cls(dados['neuronios'], dados['camadas'], silencioso=True)
        rede.pesos = dados['pesos']
        rede.bias = dados['bias']
        rede.tamanhos = dados['tamanhos']
        rede.memoria = dados.get('memoria', [])
        rede.historico_treino = dados.get('historico_treino', [])
        return rede


class IAAutonomaLotoScope:
    """
    🧠 IA AUTÔNOMA PARA LOTOSCOPE
    
    Sistema semi-autônomo que:
    1. Carrega histórico completo
    2. Explora diferentes algoritmos
    3. Testa contra histórico
    4. Aprende e melhora continuamente
    5. Sugere melhores apostas
    """
    
    def __init__(self, config: ConfiguracaoIA = None):
        self.config = config or ConfiguracaoIA()
        self.rede_neural = None
        self.historico = []
        self.resultados_algoritmos = defaultdict(list)
        self.melhor_algoritmo = None
        self.melhor_score = 0
        self.iteracao_atual = 0
        self.pesos_algoritmos = {}  # Pesos ajustados pelo feedback
        self.feedback_historico = []  # Histórico de validações
        self.aprendizado = {
            'frequencia': defaultdict(float),
            'pares': defaultdict(float),
            'transicoes': defaultdict(lambda: defaultdict(float)),
            'posicional': defaultdict(lambda: defaultdict(float)),
            'coocorrencia': defaultdict(float),
            'regras_negativas': set(),
            'padroes_vencedores': []
        }
        
        # Caminho base
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
    def inicializar(self):
        """Inicializa o sistema completo"""
        print("\n" + "=" * 70)
        print("🧠 IA AUTÔNOMA LOTOSCOPE - INICIALIZAÇÃO")
        print("=" * 70)
        
        # 1. Carregar histórico
        print("\n📊 Carregando histórico...")
        if not self._carregar_historico():
            return False
        
        # 2. Inicializar rede neural
        print(f"\n🧠 Inicializando rede neural ({self.config.neuronios:,} neurônios)...")
        self._inicializar_rede_neural()
        
        # 3. Carregar aprendizado anterior (se existir)
        self._carregar_aprendizado()
        
        # 4. Validar apostas pendentes automaticamente
        self._validar_apostas_pendentes()
        
        print("\n✅ Sistema inicializado com sucesso!")
        return True
    
    def _carregar_historico(self) -> bool:
        """Carrega histórico do banco de dados"""
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
        
        try:
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                    FROM Resultados_INT 
                    ORDER BY Concurso
                ''')
                rows = cursor.fetchall()
                
                for row in rows:
                    self.historico.append({
                        'concurso': row[0],
                        'numeros': sorted([row[i] for i in range(1, 16)])
                    })
                
                print(f"   ✅ {len(self.historico)} concursos carregados")
                return True
                
        except Exception as e:
            print(f"   ❌ Erro ao carregar histórico: {e}")
            return False
    
    def _inicializar_rede_neural(self):
        """Inicializa ou carrega rede neural"""
        modelo_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_modelo)
        
        if os.path.exists(modelo_path):
            try:
                self.rede_neural = RedeNeuralAvancada.carregar(modelo_path)
                
                # Verifica compatibilidade da arquitetura (300 inputs agora)
                input_esperado = 300
                input_modelo = self.rede_neural.tamanhos[0] if self.rede_neural.tamanhos else 0
                
                if input_modelo != input_esperado:
                    print(f"   ⚠️ Modelo antigo incompatível ({input_modelo} inputs vs {input_esperado} esperados)")
                    print(f"   🔄 Reinicializando rede neural com nova arquitetura...")
                    self.rede_neural = RedeNeuralAvancada(self.config.neuronios, self.config.camadas_ocultas)
                else:
                    print(f"   ✅ Modelo carregado: {self.rede_neural.neuronios:,} neurônios")
            except Exception as e:
                print(f"   ⚠️ Erro ao carregar modelo: {e}")
                self.rede_neural = RedeNeuralAvancada(self.config.neuronios, self.config.camadas_ocultas)
        else:
            self.rede_neural = RedeNeuralAvancada(self.config.neuronios, self.config.camadas_ocultas)
    
    def _carregar_aprendizado(self):
        """Carrega aprendizado anterior"""
        hist_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_historico)
        
        if os.path.exists(hist_path):
            try:
                with open(hist_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.resultados_algoritmos = defaultdict(list, dados.get('resultados', {}))
                    self.melhor_algoritmo = dados.get('melhor_algoritmo')
                    self.melhor_score = dados.get('melhor_score', 0)
                    self.iteracao_atual = dados.get('iteracao', 0)
                    self.pesos_algoritmos = dados.get('pesos_algoritmos', {})
                    self.feedback_historico = dados.get('feedback_historico', [])
                    
                    print(f"   ✅ Aprendizado anterior carregado (iteração {self.iteracao_atual})")
                    if self.pesos_algoritmos:
                        print(f"   📊 Pesos de {len(self.pesos_algoritmos)} algoritmos carregados")
                    if self.feedback_historico:
                        print(f"   🔄 {len(self.feedback_historico)} feedbacks de validação carregados")
            except Exception as e:
                print(f"   ⚠️ Iniciando aprendizado do zero ({e})")
    
    def _salvar_aprendizado(self):
        """Salva estado do aprendizado"""
        os.makedirs(os.path.join(self.base_path, '..', 'dados'), exist_ok=True)
        
        # Salvar histórico JSON
        hist_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_historico)
        with open(hist_path, 'w', encoding='utf-8') as f:
            json.dump({
                'resultados': dict(self.resultados_algoritmos),
                'melhor_algoritmo': self.melhor_algoritmo,
                'melhor_score': self.melhor_score,
                'iteracao': self.iteracao_atual,
                'pesos_algoritmos': dict(self.pesos_algoritmos),
                'feedback_historico': self.feedback_historico[-100:],  # Últimos 100
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        # Salvar modelo neural
        modelo_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_modelo)
        self.rede_neural.salvar(modelo_path)
    
    def _salvar_apostas_pendentes(self, apostas: List[List[int]], concurso_alvo: int, algoritmo: str):
        """Salva apostas para validação futura"""
        pendentes_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_apostas_pendentes)
        
        # Carregar existentes
        apostas_existentes = []
        if os.path.exists(pendentes_path):
            try:
                with open(pendentes_path, 'r', encoding='utf-8') as f:
                    apostas_existentes = json.load(f)
            except:
                apostas_existentes = []
        
        # Adicionar nova
        nova_aposta = {
            'concurso_alvo': concurso_alvo,
            'combinacoes': apostas,
            'algoritmo_usado': algoritmo,
            'data_geracao': datetime.now().isoformat(),
            'validada': False,
            'acertos': [],
            'melhor_acerto': 0
        }
        apostas_existentes.append(nova_aposta)
        
        # Salvar
        with open(pendentes_path, 'w', encoding='utf-8') as f:
            json.dump(apostas_existentes, f, indent=2)
        
        print(f"   💾 Apostas salvas para validação (concurso alvo: {concurso_alvo})")
    
    def _validar_apostas_pendentes(self):
        """Valida apostas pendentes contra resultados reais - FEEDBACK AUTOMÁTICO"""
        pendentes_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_apostas_pendentes)
        
        if not os.path.exists(pendentes_path):
            return
        
        try:
            with open(pendentes_path, 'r', encoding='utf-8') as f:
                apostas_pendentes = json.load(f)
        except:
            return
        
        if not apostas_pendentes:
            return
        
        # Concursos disponíveis no histórico
        concursos_disponiveis = {h['concurso']: h['numeros'] for h in self.historico}
        
        validadas = 0
        feedback_dado = []
        
        for aposta in apostas_pendentes:
            if aposta['validada']:
                continue
            
            concurso_alvo = aposta['concurso_alvo']
            
            # Verifica se o resultado já está disponível
            if concurso_alvo in concursos_disponiveis:
                resultado = concursos_disponiveis[concurso_alvo]
                acertos_lista = []
                
                for combo in aposta['combinacoes']:
                    acertos = len(set(combo) & set(resultado))
                    acertos_lista.append(acertos)
                
                aposta['validada'] = True
                aposta['acertos'] = acertos_lista
                aposta['melhor_acerto'] = max(acertos_lista) if acertos_lista else 0
                aposta['data_validacao'] = datetime.now().isoformat()
                
                validadas += 1
                
                # FEEDBACK: Ajustar pesos do algoritmo
                algoritmo = aposta['algoritmo_usado']
                media_acertos = sum(acertos_lista) / len(acertos_lista) if acertos_lista else 0
                melhor = aposta['melhor_acerto']
                
                # Recompensa/Punição baseada em performance
                # Baseline esperado: ~9 acertos (aleatório)
                recompensa = (media_acertos - 9) * 0.1
                if melhor >= 14:
                    recompensa += 1.0  # Bônus grande por 14+
                elif melhor >= 12:
                    recompensa += 0.5  # Bônus por 12+
                elif melhor >= 11:
                    recompensa += 0.2  # Bônus por 11+
                
                # Atualizar peso do algoritmo
                if algoritmo not in self.pesos_algoritmos:
                    self.pesos_algoritmos[algoritmo] = 1.0
                
                self.pesos_algoritmos[algoritmo] = max(0.1, 
                    self.pesos_algoritmos[algoritmo] + recompensa)
                
                feedback_dado.append({
                    'concurso': concurso_alvo,
                    'algoritmo': algoritmo,
                    'media_acertos': media_acertos,
                    'melhor_acerto': melhor,
                    'recompensa': recompensa,
                    'novo_peso': self.pesos_algoritmos[algoritmo]
                })
                
                self.feedback_historico.append({
                    'concurso': concurso_alvo,
                    'algoritmo': algoritmo,
                    'acertos': acertos_lista,
                    'recompensa': recompensa,
                    'timestamp': datetime.now().isoformat()
                })
        
        if validadas > 0:
            print(f"\n🔄 VALIDAÇÃO AUTOMÁTICA DE APOSTAS PENDENTES:")
            print("=" * 60)
            print(f"   ✅ {validadas} apostas validadas com novos resultados!")
            print()
            
            for fb in feedback_dado:
                status = "🏆" if fb['melhor_acerto'] >= 14 else "✅" if fb['melhor_acerto'] >= 11 else "📊"
                print(f"   {status} Concurso {fb['concurso']}:")
                print(f"      Algoritmo: {fb['algoritmo']}")
                print(f"      Média acertos: {fb['media_acertos']:.2f}")
                print(f"      Melhor acerto: {fb['melhor_acerto']}")
                print(f"      Recompensa: {fb['recompensa']:+.2f}")
                print(f"      Novo peso: {fb['novo_peso']:.2f}")
                print()
            
            # Salvar apostas atualizadas
            with open(pendentes_path, 'w', encoding='utf-8') as f:
                json.dump(apostas_pendentes, f, indent=2)
            
            # Salvar aprendizado atualizado
            self._salvar_aprendizado()
            
            # Retreinar rede neural com feedback
            self._aplicar_feedback_rede_neural(feedback_dado)
    
    def _aplicar_feedback_rede_neural(self, feedback: List[Dict]):
        """Aplica feedback para ajustar rede neural"""
        if not feedback:
            return
        
        print("   🧠 Aplicando feedback à rede neural...")
        
        for fb in feedback:
            concurso = fb['concurso']
            
            # Encontra índice do concurso
            idx = None
            for i, h in enumerate(self.historico):
                if h['concurso'] == concurso:
                    idx = i
                    break
            
            if idx is None:
                continue
            
            # Extrai features e retreina com peso baseado na recompensa
            features = self._extrair_features(idx)
            resultado = self.historico[idx]['numeros']
            
            # Target: one-hot dos números sorteados
            target = np.zeros(25)
            for n in resultado:
                target[n-1] = 1
            
            # Treina com learning rate proporcional à recompensa
            # FOCO EM 11+: lr mais alto quando acertou menos (precisa aprender mais)
            media_acertos = fb['media_acertos']
            if media_acertos < 11:
                # Abaixo de 11: precisa aprender mais, lr mais alto
                lr = min(0.01, 0.002 * (11 - media_acertos + 1))
            else:
                # Acima de 11: está bom, ajuste fino
                lr = max(0.0001, 0.001 * (1 + fb['recompensa']))
            
            # Usa treino focado em 11+
            self.rede_neural.treinar_foco_11(
                features.reshape(1, -1), 
                target.reshape(1, -1),
                self.historico,
                epochs=10 if media_acertos < 11 else 5,  # Mais treino se está ruim
                lr=lr,
                objetivo_media=11.0
            )
        
        print("   ✅ Rede neural atualizada com feedback (foco em 11+)!")
    
    def _extrair_features(self, idx_concurso: int) -> np.ndarray:
        """
        Extrai features para um concurso (usando histórico anterior)
        
        FEATURES EXPANDIDAS (300 total):
        - 0-24: Frequência geral (50 concursos)
        - 25-49: Atraso de cada número
        - 50-74: Última aparição (binário)
        - 75-149: Posicional multi-janela (15 posições × 5 janelas)
        - 150-224: Força do top por posição (15 pos × 5 janelas)
        - 225-249: ⭐ FOCO JANELA 10 - Frequência detalhada
        - 250-274: ⭐ FOCO JANELA 10 - Tendência (subindo/descendo)
        - 275-299: ⭐ FOCO JANELA 10 - Posição dominante por número
        """
        features = np.zeros(300)
        
        # Usa últimos 50 concursos anteriores
        inicio = max(0, idx_concurso - 50)
        janela = self.historico[inicio:idx_concurso]
        
        if not janela:
            return features
        
        # Features 0-24: Frequência de cada número
        for h in janela:
            for n in h['numeros']:
                features[n-1] += 1
        features[:25] = features[:25] / len(janela)
        
        # Features 25-49: Atraso de cada número
        ultimo = self.historico[idx_concurso - 1] if idx_concurso > 0 else None
        if ultimo:
            for n in range(1, 26):
                atraso = 0
                for i in range(idx_concurso - 1, max(0, idx_concurso - 20), -1):
                    if n in self.historico[i]['numeros']:
                        break
                    atraso += 1
                features[24 + n] = atraso / 20
        
        # Features 50-74: Última aparição (binário)
        if ultimo:
            for n in ultimo['numeros']:
                features[49 + n] = 1
        
        # ============================================
        # Features 75-224 - POSICIONAL MULTI-JANELA
        # ============================================
        # Janelas: 30, 15, 10, 5, 3 concursos
        # PESO MAIOR para janela 10 (índice 2)
        janelas = [30, 15, 10, 5, 3]
        pesos_janela = [0.5, 0.7, 1.5, 1.0, 0.8]  # Janela 10 tem peso 1.5x
        
        for j_idx, tamanho_janela in enumerate(janelas):
            inicio_j = max(0, idx_concurso - tamanho_janela)
            janela_atual = self.historico[inicio_j:idx_concurso]
            
            if not janela_atual:
                continue
            
            peso = pesos_janela[j_idx]
            
            # Para cada posição (N1-N15), encontra número mais frequente
            for pos in range(15):
                freq_pos = defaultdict(int)
                for h in janela_atual:
                    n = h['numeros'][pos]
                    freq_pos[n] += 1
                
                if freq_pos:
                    # Feature: número mais frequente nesta posição/janela
                    top_num = max(freq_pos.items(), key=lambda x: x[1])[0]
                    # Índice: 75 + (j_idx * 15) + pos
                    features[75 + (j_idx * 15) + pos] = (top_num / 25.0) * peso
                    
                    # Feature adicional: força do top (frequência relativa)
                    max_freq = max(freq_pos.values())
                    features[150 + (j_idx * 15) + pos] = (max_freq / len(janela_atual)) * peso
        
        # ============================================
        # ⭐ FOCO JANELA 10 - Features especiais (225-299)
        # ============================================
        janela_10 = self.historico[max(0, idx_concurso - 10):idx_concurso]
        janela_5_anterior = self.historico[max(0, idx_concurso - 15):max(0, idx_concurso - 5)]
        
        if janela_10:
            # Features 225-249: Frequência detalhada nos últimos 10
            freq_10 = defaultdict(int)
            for h in janela_10:
                for n in h['numeros']:
                    freq_10[n] += 1
            
            for n in range(1, 26):
                features[224 + n] = freq_10[n] / 10.0  # Normalizado
            
            # Features 250-274: Tendência (comparando últimos 5 vs 5 anteriores)
            if len(janela_10) >= 5 and janela_5_anterior:
                freq_ultimos_5 = defaultdict(int)
                freq_anteriores_5 = defaultdict(int)
                
                for h in janela_10[-5:]:
                    for n in h['numeros']:
                        freq_ultimos_5[n] += 1
                
                for h in janela_5_anterior[-5:]:
                    for n in h['numeros']:
                        freq_anteriores_5[n] += 1
                
                for n in range(1, 26):
                    # Tendência: positivo = subindo, negativo = descendo
                    tendencia = (freq_ultimos_5[n] - freq_anteriores_5[n]) / 5.0
                    features[249 + n] = (tendencia + 1) / 2  # Normaliza 0-1
            
            # Features 275-299: Em qual posição o número mais aparece na janela 10
            for n in range(1, 26):
                pos_freq = defaultdict(int)
                for h in janela_10:
                    if n in h['numeros']:
                        pos = h['numeros'].index(n)
                        pos_freq[pos] += 1
                
                if pos_freq:
                    pos_dominante = max(pos_freq.items(), key=lambda x: x[1])[0]
                    features[274 + n] = pos_dominante / 14.0  # Normaliza 0-1
        
        return features
    
    def _gerar_combinacao_algoritmo(self, algoritmo: str, idx_concurso: int, params: Dict = None) -> List[int]:
        """Gera combinação usando um algoritmo específico"""
        params = params or {}
        janela = self.historico[max(0, idx_concurso - 100):idx_concurso]
        
        if not janela:
            return sorted(random.sample(range(1, 26), 15))
        
        if algoritmo == 'frequencia':
            # Números mais frequentes
            freq = defaultdict(int)
            for h in janela[-params.get('janela', 50):]:
                for n in h['numeros']:
                    freq[n] += 1
            ordenados = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            return sorted([n for n, _ in ordenados[:15]])
        
        elif algoritmo == 'atraso':
            # Números mais atrasados
            ultimo_visto = {}
            for i, h in enumerate(janela):
                for n in h['numeros']:
                    ultimo_visto[n] = i
            
            atrasos = [(n, len(janela) - ultimo_visto.get(n, 0)) for n in range(1, 26)]
            atrasos.sort(key=lambda x: x[1], reverse=True)
            return sorted([n for n, _ in atrasos[:15]])
        
        elif algoritmo == 'pares_impares':
            # Balanceamento pares/ímpares baseado em padrão histórico
            dist_pi = defaultdict(int)
            for h in janela[-30:]:
                pares = sum(1 for n in h['numeros'] if n % 2 == 0)
                dist_pi[pares] += 1
            
            melhor_pares = max(dist_pi.items(), key=lambda x: x[1])[0]
            impares = 15 - melhor_pares
            
            todos_pares = [n for n in range(1, 26) if n % 2 == 0]
            todos_impares = [n for n in range(1, 26) if n % 2 == 1]
            
            combo = random.sample(todos_pares, min(melhor_pares, len(todos_pares)))
            combo += random.sample(todos_impares, min(impares, len(todos_impares)))
            
            while len(combo) < 15:
                restantes = [n for n in range(1, 26) if n not in combo]
                combo.append(random.choice(restantes))
            
            return sorted(combo[:15])
        
        elif algoritmo == 'posicional':
            # ALGORITMO POSICIONAL MULTI-JANELA (30, 15, 10, 5, 3)
            # Analisa tendências de curto, médio e longo prazo por posição
            janelas_tamanho = [30, 15, 10, 5, 3]
            pesos_janela = [0.10, 0.15, 0.20, 0.25, 0.30]  # Mais peso para curto prazo
            
            # Score por número e posição
            scores_posicao = defaultdict(lambda: defaultdict(float))
            
            for j_idx, tam in enumerate(janelas_tamanho):
                peso = pesos_janela[j_idx]
                janela_atual = janela[-tam:] if len(janela) >= tam else janela
                
                if not janela_atual:
                    continue
                
                for h in janela_atual:
                    for pos, n in enumerate(h['numeros']):
                        scores_posicao[pos][n] += peso
            
            # Seleciona melhor número para cada posição
            combo = []
            numeros_usados = set()
            
            for pos in range(15):
                if scores_posicao[pos]:
                    # Ordena candidatos por score, exclui já usados
                    candidatos = [(n, s) for n, s in scores_posicao[pos].items() 
                                  if n not in numeros_usados]
                    if candidatos:
                        candidatos.sort(key=lambda x: x[1], reverse=True)
                        melhor = candidatos[0][0]
                        combo.append(melhor)
                        numeros_usados.add(melhor)
            
            while len(combo) < 15:
                restantes = [n for n in range(1, 26) if n not in combo]
                combo.append(random.choice(restantes))
            
            return sorted(combo[:15])
        
        elif algoritmo == 'association_rules':
            # Regras de associação simples
            freq = defaultdict(int)
            cooc = defaultdict(int)
            
            for h in janela[-50:]:
                for n in h['numeros']:
                    freq[n] += 1
                for i, n1 in enumerate(h['numeros']):
                    for n2 in h['numeros'][i+1:]:
                        cooc[(n1, n2)] += 1
            
            # Score: frequência + co-ocorrência com outros frequentes
            scores = {}
            top_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            top_nums = [n for n, _ in top_freq]
            
            for n in range(1, 26):
                scores[n] = freq[n]
                for m in top_nums:
                    if n != m:
                        par = (min(n, m), max(n, m))
                        scores[n] += cooc[par] * 0.5
            
            ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return sorted([n for n, _ in ordenados[:15]])
        
        elif algoritmo == 'transicoes':
            # Transições entre concursos consecutivos
            trans = defaultdict(lambda: defaultdict(int))
            for i in range(1, len(janela)):
                for n1 in janela[i-1]['numeros']:
                    for n2 in janela[i]['numeros']:
                        trans[n1][n2] += 1
            
            ultimo = janela[-1]['numeros'] if janela else []
            scores = defaultdict(float)
            
            for n1 in ultimo:
                for n2, count in trans[n1].items():
                    scores[n2] += count
            
            ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            combo = [n for n, _ in ordenados[:15]]
            
            while len(combo) < 15:
                restantes = [n for n in range(1, 26) if n not in combo]
                combo.append(random.choice(restantes))
            
            return sorted(combo[:15])
        
        elif algoritmo == 'neural':
            # Usa rede neural
            features = self._extrair_features(idx_concurso)
            return self.rede_neural.prever_numeros(features, 15)
        
        elif algoritmo == 'genetico':
            # Algoritmo genético simples
            populacao = [sorted(random.sample(range(1, 26), 15)) for _ in range(50)]
            
            for _ in range(params.get('geracoes', 20)):
                # Fitness: soma de frequências
                freq = defaultdict(int)
                for h in janela[-30:]:
                    for n in h['numeros']:
                        freq[n] += 1
                
                fitness = [(sum(freq[n] for n in ind), ind) for ind in populacao]
                fitness.sort(reverse=True)
                
                # Seleção
                melhores = [ind for _, ind in fitness[:20]]
                
                # Crossover
                nova_pop = melhores.copy()
                while len(nova_pop) < 50:
                    p1, p2 = random.sample(melhores, 2)
                    filho = sorted(list(set(p1[:8] + p2[7:])))[:15]
                    while len(filho) < 15:
                        filho.append(random.choice([n for n in range(1, 26) if n not in filho]))
                    nova_pop.append(sorted(filho))
                
                # Mutação
                for i in range(20, len(nova_pop)):
                    if random.random() < 0.1:
                        idx = random.randint(0, 14)
                        novo = random.choice([n for n in range(1, 26) if n not in nova_pop[i]])
                        nova_pop[i][idx] = novo
                        nova_pop[i] = sorted(nova_pop[i])
                
                populacao = nova_pop
            
            return populacao[0]
        
        elif algoritmo == 'ensemble':
            # Combina todos os algoritmos
            votos = defaultdict(int)
            
            for alg in ['frequencia', 'atraso', 'posicional', 'transicoes', 'association_rules']:
                combo = self._gerar_combinacao_algoritmo(alg, idx_concurso)
                for n in combo:
                    votos[n] += 1
            
            ordenados = sorted(votos.items(), key=lambda x: x[1], reverse=True)
            return sorted([n for n, _ in ordenados[:15]])
        
        # Default: aleatório
        return sorted(random.sample(range(1, 26), 15))
    
    def _avaliar_combinacao(self, combo: List[int], resultado: List[int]) -> int:
        """Calcula acertos entre combinação e resultado"""
        return len(set(combo) & set(resultado))
    
    def executar_exploracao(self, iteracoes: int = None):
        """
        Executa exploração autônoma de algoritmos
        
        Este é o método principal que:
        1. Testa cada algoritmo contra histórico
        2. Mede performance de cada um
        3. Aprende quais funcionam melhor
        4. Evolui parâmetros
        """
        iteracoes = iteracoes or self.config.max_iteracoes
        
        print("\n" + "=" * 70)
        print("🚀 IA AUTÔNOMA - INICIANDO EXPLORAÇÃO")
        print("=" * 70)
        print(f"   • Iterações: {iteracoes}")
        print(f"   • Algoritmos: {len(self.config.algoritmos_ativos)}")
        print(f"   • Validação: últimos {self.config.concursos_validacao} concursos")
        print("=" * 70)
        
        inicio = datetime.now()
        
        # Índices para validação
        idx_inicio_val = len(self.historico) - self.config.concursos_validacao
        idx_fim_val = len(self.historico)
        
        resultados_gerais = []
        
        for it in range(iteracoes):
            self.iteracao_atual += 1
            
            print(f"\n📊 Iteração {self.iteracao_atual}/{self.iteracao_atual + iteracoes - it - 1}")
            
            # Testa cada algoritmo
            for algoritmo in self.config.algoritmos_ativos:
                acertos_lista = []
                
                # Varia parâmetros
                params = self._gerar_parametros_aleatorios(algoritmo)
                
                # Testa contra validação
                for idx in range(idx_inicio_val, idx_fim_val):
                    combo = self._gerar_combinacao_algoritmo(algoritmo, idx, params)
                    resultado = self.historico[idx]['numeros']
                    acertos = self._avaliar_combinacao(combo, resultado)
                    acertos_lista.append(acertos)
                
                # Estatísticas
                media = sum(acertos_lista) / len(acertos_lista)
                acertos_11_mais = sum(1 for a in acertos_lista if a >= 11)
                acertos_14_mais = sum(1 for a in acertos_lista if a >= 14)
                
                resultado = ResultadoIteracao(
                    iteracao=self.iteracao_atual,
                    algoritmo=algoritmo,
                    combinacoes_geradas=len(acertos_lista),
                    media_acertos=media,
                    max_acertos=max(acertos_lista),
                    min_acertos=min(acertos_lista),
                    acertos_11_mais=acertos_11_mais,
                    acertos_14_mais=acertos_14_mais,
                    tempo_segundos=0,
                    parametros=params
                )
                
                self.resultados_algoritmos[algoritmo].append(asdict(resultado))
                resultados_gerais.append(resultado)
                
                # Atualiza melhor
                score = media + (acertos_11_mais / len(acertos_lista)) * 2
                if score > self.melhor_score:
                    self.melhor_score = score
                    self.melhor_algoritmo = algoritmo
                
                print(f"   {algoritmo:20s}: média={media:.2f}, 11+={acertos_11_mais:3d}, 14+={acertos_14_mais:2d}")
            
            # Treina rede neural com feedback
            if 'neural' in self.config.algoritmos_ativos:
                self._treinar_rede_com_feedback(idx_inicio_val)
            
            # Salva progresso a cada 10 iterações
            if self.iteracao_atual % 10 == 0:
                self._salvar_aprendizado()
                print(f"\n   💾 Progresso salvo (iteração {self.iteracao_atual})")
        
        tempo_total = (datetime.now() - inicio).total_seconds()
        
        # Resumo final
        print("\n" + "=" * 70)
        print("📊 RESUMO DA EXPLORAÇÃO")
        print("=" * 70)
        print(f"   • Iterações completadas: {iteracoes}")
        print(f"   • Tempo total: {tempo_total:.1f}s")
        print(f"   • Melhor algoritmo: {self.melhor_algoritmo}")
        print(f"   • Melhor score: {self.melhor_score:.4f}")
        
        self._salvar_aprendizado()
        
        return resultados_gerais
    
    def _gerar_parametros_aleatorios(self, algoritmo: str) -> Dict:
        """Gera parâmetros aleatórios para exploração"""
        if algoritmo == 'frequencia':
            return {'janela': random.choice([20, 30, 50, 100])}
        elif algoritmo == 'genetico':
            return {'geracoes': random.choice([10, 20, 50])}
        return {}
    
    def _treinar_rede_com_feedback(self, idx_inicio: int):
        """Treina rede neural com feedback dos resultados - FOCO EM 11+ ACERTOS"""
        X = []
        y = []
        
        for idx in range(max(50, idx_inicio - 100), idx_inicio):
            features = self._extrair_features(idx)
            resultado = self.historico[idx]['numeros']
            
            # Target: one-hot dos números sorteados
            target = np.zeros(25)
            for n in resultado:
                target[n-1] = 1
            
            X.append(features)
            y.append(target)
        
        if X:
            X = np.array(X)
            y = np.array(y)
            # USA TREINO FOCADO EM 11+
            self.rede_neural.treinar_foco_11(
                X, y, 
                self.historico, 
                epochs=15,  # Mais epochs para convergir
                lr=self.config.taxa_aprendizado,
                objetivo_media=11.0
            )
    
    def gerar_apostas_otimizadas(self, quantidade: int = 10) -> List[List[int]]:
        """
        Gera apostas otimizadas baseadas no aprendizado
        
        Usa o melhor algoritmo descoberto e combina com ensemble
        para maximizar chances de acerto.
        """
        print("\n" + "=" * 70)
        print("🎯 GERANDO APOSTAS OTIMIZADAS")
        print("=" * 70)
        
        apostas = []
        idx_atual = len(self.historico)
        
        # 1. Gera usando melhor algoritmo
        if self.melhor_algoritmo:
            print(f"   📌 Usando algoritmo: {self.melhor_algoritmo}")
            for _ in range(quantidade // 2):
                combo = self._gerar_combinacao_algoritmo(self.melhor_algoritmo, idx_atual)
                if combo not in apostas:
                    apostas.append(combo)
        
        # 2. Completa com ensemble
        print(f"   📌 Completando com ensemble...")
        while len(apostas) < quantidade:
            combo = self._gerar_combinacao_algoritmo('ensemble', idx_atual)
            # Adiciona variação
            if random.random() < 0.3:
                # Troca 1-2 números
                combo = list(combo)
                for _ in range(random.randint(1, 2)):
                    idx = random.randint(0, 14)
                    novo = random.choice([n for n in range(1, 26) if n not in combo])
                    combo[idx] = novo
                combo = sorted(combo)
            
            if combo not in apostas:
                apostas.append(combo)
        
        # 3. Valida contra padrões aprendidos
        apostas_validadas = []
        for combo in apostas:
            # Verifica se não viola regras negativas
            valida = True
            for regra in self.aprendizado.get('regras_negativas', set()):
                if isinstance(regra, tuple) and regra[0] in combo and regra[1] in combo:
                    valida = False
                    break
            
            if valida:
                apostas_validadas.append(combo)
            else:
                # Ajusta combinação
                combo_ajustada = self._ajustar_combinacao(combo)
                apostas_validadas.append(combo_ajustada)
        
        print(f"\n   ✅ {len(apostas_validadas)} apostas geradas!")
        
        # Mostra apostas
        print("\n   📋 APOSTAS SUGERIDAS:")
        print("   " + "-" * 50)
        for i, combo in enumerate(apostas_validadas, 1):
            nums_str = ','.join(f'{n:02d}' for n in combo)
            print(f"   {i:2d}. {nums_str}")
        print("   " + "-" * 50)
        
        # Determina próximo concurso para validação
        ultimo_concurso = self.historico[-1]['concurso'] if self.historico else 0
        proximo_concurso = ultimo_concurso + 1
        
        # Salva apostas para validação futura
        algoritmo_usado = self.melhor_algoritmo or 'ensemble'
        self._salvar_apostas_pendentes(apostas_validadas, proximo_concurso, algoritmo_usado)
        
        print(f"\n   ⏳ Estas apostas serão validadas automaticamente quando o")
        print(f"      resultado do concurso {proximo_concurso} estiver disponível.")
        print(f"      Execute a IA novamente após o sorteio para ver o feedback!")
        
        return apostas_validadas
    
    def _ajustar_combinacao(self, combo: List[int]) -> List[int]:
        """Ajusta combinação que viola regras"""
        combo = list(combo)
        for regra in self.aprendizado.get('regras_negativas', set()):
            if isinstance(regra, tuple) and regra[0] in combo and regra[1] in combo:
                # Remove o segundo número da regra
                idx = combo.index(regra[1])
                novo = random.choice([n for n in range(1, 26) if n not in combo])
                combo[idx] = novo
        return sorted(combo)
    
    def exibir_estatisticas(self):
        """Exibe estatísticas do aprendizado"""
        print("\n" + "=" * 70)
        print("📊 ESTATÍSTICAS DO APRENDIZADO")
        print("=" * 70)
        
        print(f"\n   🧠 Rede Neural: {self.rede_neural.neuronios:,} neurônios")
        print(f"   📈 Iterações: {self.iteracao_atual}")
        print(f"   🏆 Melhor algoritmo: {self.melhor_algoritmo}")
        print(f"   📊 Melhor score: {self.melhor_score:.4f}")
        
        print("\n   📋 PERFORMANCE POR ALGORITMO:")
        print("   " + "-" * 60)
        
        for alg in self.config.algoritmos_ativos:
            resultados = self.resultados_algoritmos.get(alg, [])
            if resultados:
                medias = [r['media_acertos'] for r in resultados[-10:]]
                media = sum(medias) / len(medias) if medias else 0
                max_11 = max(r['acertos_11_mais'] for r in resultados[-10:]) if resultados else 0
                print(f"   {alg:20s}: média últimas 10 = {media:.2f}, máx 11+ = {max_11}")
        
        print("   " + "-" * 60)
    
    def exibir_historico_validacoes(self):
        """Exibe histórico de validações realizadas"""
        print("\n" + "=" * 70)
        print("📋 HISTÓRICO DE VALIDAÇÕES (FEEDBACK REAL)")
        print("=" * 70)
        
        if not self.feedback_historico:
            print("\n   ⚠️ Nenhuma validação realizada ainda.")
            print("   Gere apostas e aguarde o sorteio para ver os resultados.")
            return
        
        # Agrupa por concurso
        por_concurso = defaultdict(list)
        for fb in self.feedback_historico:
            por_concurso[fb['concurso']].append(fb)
        
        total_validacoes = len(por_concurso)
        acertos_totais = []
        
        for concurso, feedbacks in sorted(por_concurso.items(), reverse=True)[:10]:  # Últimos 10
            print(f"\n   🎯 CONCURSO {concurso}:")
            
            for fb in feedbacks:
                algoritmo = fb['algoritmo']
                acertos = fb.get('acertos', [])
                recompensa = fb.get('recompensa', 0)
                
                if acertos:
                    media = sum(acertos) / len(acertos)
                    melhor = max(acertos)
                    acertos_totais.extend(acertos)
                    
                    status = "🏆" if melhor >= 14 else "✅" if melhor >= 11 else "📊"
                    print(f"      {status} Algoritmo: {algoritmo}")
                    print(f"         Média: {media:.2f} | Melhor: {melhor} | Recompensa: {recompensa:+.2f}")
                    
                    # Distribuição de acertos
                    dist = defaultdict(int)
                    for a in acertos:
                        dist[a] += 1
                    dist_str = ', '.join(f'{a}:{c}' for a, c in sorted(dist.items(), reverse=True))
                    print(f"         Distribuição: {dist_str}")
        
        # Estatísticas gerais
        if acertos_totais:
            print("\n" + "-" * 60)
            print("   📊 ESTATÍSTICAS GERAIS:")
            print(f"      Total validações: {total_validacoes}")
            print(f"      Média geral: {sum(acertos_totais)/len(acertos_totais):.2f}")
            print(f"      Melhor acerto: {max(acertos_totais)}")
            print(f"      Pior acerto: {min(acertos_totais)}")
            
            # Contagem por faixa
            f11 = sum(1 for a in acertos_totais if a >= 11)
            f12 = sum(1 for a in acertos_totais if a >= 12)
            f13 = sum(1 for a in acertos_totais if a >= 13)
            f14 = sum(1 for a in acertos_totais if a >= 14)
            f15 = sum(1 for a in acertos_totais if a >= 15)
            
            total = len(acertos_totais)
            print(f"\n      11+ acertos: {f11:4d} ({100*f11/total:.1f}%)")
            print(f"      12+ acertos: {f12:4d} ({100*f12/total:.1f}%)")
            print(f"      13+ acertos: {f13:4d} ({100*f13/total:.1f}%)")
            print(f"      14+ acertos: {f14:4d} ({100*f14/total:.1f}%)")
            print(f"      15 acertos:  {f15:4d} ({100*f15/total:.1f}%)")
    
    def exibir_apostas_pendentes(self):
        """Exibe apostas aguardando validação"""
        print("\n" + "=" * 70)
        print("⏳ APOSTAS PENDENTES DE VALIDAÇÃO")
        print("=" * 70)
        
        pendentes_path = os.path.join(self.base_path, '..', 'dados', self.config.arquivo_apostas_pendentes)
        
        if not os.path.exists(pendentes_path):
            print("\n   ⚠️ Nenhuma aposta pendente.")
            return
        
        try:
            with open(pendentes_path, 'r', encoding='utf-8') as f:
                apostas = json.load(f)
        except:
            print("\n   ⚠️ Erro ao ler apostas pendentes.")
            return
        
        pendentes = [a for a in apostas if not a.get('validada', False)]
        validadas = [a for a in apostas if a.get('validada', False)]
        
        if pendentes:
            print(f"\n   📋 {len(pendentes)} apostas aguardando resultado:")
            
            for ap in pendentes:
                concurso = ap['concurso_alvo']
                data_geracao = ap.get('data_geracao', 'N/A')[:10]
                algoritmo = ap.get('algoritmo_usado', 'N/A')
                qtd = len(ap.get('combinacoes', []))
                
                print(f"\n      🎯 Concurso alvo: {concurso}")
                print(f"         Data geração: {data_geracao}")
                print(f"         Algoritmo: {algoritmo}")
                print(f"         Combinações: {qtd}")
        else:
            print("\n   ✅ Nenhuma aposta pendente!")
        
        if validadas:
            print(f"\n   📊 {len(validadas)} apostas já validadas:")
            
            for ap in validadas[-5:]:  # Últimas 5
                concurso = ap['concurso_alvo']
                melhor = ap.get('melhor_acerto', 0)
                acertos = ap.get('acertos', [])
                media = sum(acertos) / len(acertos) if acertos else 0
                
                status = "🏆" if melhor >= 14 else "✅" if melhor >= 11 else "📊"
                print(f"\n      {status} Concurso {concurso}: melhor={melhor}, média={media:.2f}")


def menu_ia_autonoma():
    """Menu interativo da IA Autônoma"""
    print("\n" + "=" * 70)
    print("🧠 IA AUTÔNOMA LOTOSCOPE - MENU PRINCIPAL")
    print("=" * 70)
    
    # Configuração inicial
    print("\n⚙️ CONFIGURAÇÃO DA REDE NEURAL:")
    print("   1. 24.000 neurônios (Básico - mais rápido)")
    print("   2. 48.000 neurônios (Intermediário - recomendado)")
    print("   3. 192.000 neurônios (Avançado - mais lento)")
    
    escolha_rede = input("\n   Escolha [2]: ").strip() or "2"
    neuronios = {
        "1": 24000,
        "2": 48000,
        "3": 192000
    }.get(escolha_rede, 48000)
    
    config = ConfiguracaoIA(neuronios=neuronios)
    ia = IAAutonomaLotoScope(config)
    
    if not ia.inicializar():
        print("❌ Falha na inicialização!")
        return
    
    while True:
        print("\n" + "=" * 70)
        print("🧠 IA AUTÔNOMA - MENU")
        print("=" * 70)
        print("   1. 🚀 Executar exploração autônoma")
        print("   2. 🎯 Gerar apostas otimizadas")
        print("   3. 📊 Ver estatísticas de aprendizado")
        print("   4. � Ver histórico de validações")
        print("   5. ⏳ Ver apostas pendentes")
        print("   6. 🔄 Resetar aprendizado")
        print("   7. ⚙️ Alterar configurações")
        print("   0. 🔙 Voltar")
        
        opcao = input("\n   Escolha: ").strip()
        
        if opcao == "1":
            iteracoes = input("\n   Quantas iterações? [100]: ").strip()
            iteracoes = int(iteracoes) if iteracoes.isdigit() else 100
            ia.executar_exploracao(iteracoes)
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "2":
            qtd = input("\n   Quantas apostas gerar? [10]: ").strip()
            qtd = int(qtd) if qtd.isdigit() else 10
            apostas = ia.gerar_apostas_otimizadas(qtd)
            
            salvar = input("\n   Salvar em arquivo? (s/n) [s]: ").strip().lower() != 'n'
            if salvar:
                nome = f"apostas_ia_autonoma_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                caminho = os.path.join(ia.base_path, '..', 'dados', nome)
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write("# APOSTAS GERADAS PELA IA AUTÔNOMA LOTOSCOPE\n")
                    f.write(f"# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Neurônios: {ia.rede_neural.neuronios:,}\n")
                    f.write(f"# Melhor algoritmo: {ia.melhor_algoritmo}\n")
                    f.write("#" + "=" * 50 + "\n\n")
                    
                    for combo in apostas:
                        f.write(','.join(map(str, combo)) + '\n')
                
                print(f"\n✅ Salvo em: {caminho}")
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "3":
            ia.exibir_estatisticas()
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "4":
            # Ver histórico de validações
            ia.exibir_historico_validacoes()
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "5":
            # Ver apostas pendentes
            ia.exibir_apostas_pendentes()
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "6":
            confirma = input("\n   ⚠️ Isso apagará todo aprendizado. Confirmar? (s/n): ").strip().lower()
            if confirma == 's':
                ia.iteracao_atual = 0
                ia.resultados_algoritmos = defaultdict(list)
                ia.melhor_algoritmo = None
                ia.melhor_score = 0
                ia._inicializar_rede_neural()
                print("\n✅ Aprendizado resetado!")
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "7":
            print("\n⚙️ CONFIGURAÇÕES ATUAIS:")
            print(f"   • Neurônios: {config.neuronios:,}")
            print(f"   • Camadas: {config.camadas_ocultas}")
            print(f"   • Taxa aprendizado: {config.taxa_aprendizado}")
            print(f"   • Algoritmos: {len(config.algoritmos_ativos)}")
            
            # Exibir pesos dos algoritmos
            if ia.pesos_algoritmos:
                print("\n   📊 PESOS DOS ALGORITMOS (baseado em feedback):")
                for alg, peso in sorted(ia.pesos_algoritmos.items(), key=lambda x: x[1], reverse=True):
                    print(f"      {alg:20s}: {peso:.2f}")
            
            input("\n⏸️ Pressione ENTER para continuar...")
        
        elif opcao == "0":
            break


if __name__ == "__main__":
    menu_ia_autonoma()
