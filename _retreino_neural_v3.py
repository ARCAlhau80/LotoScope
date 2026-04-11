# -*- coding: utf-8 -*-
"""
🔥 RETREINO NEURAL v3 (250 features) — Script não-interativo
=============================================================
Treina a rede neural do zero com a nova arquitetura v3:
  - 250 features (10 por número × 25)
  - Arquitetura: 250 → 96 → 48 → 25 (~30k params)
  - 3 níveis progressivos de treino

Uso: python _retreino_neural_v3.py
"""

import os
import sys
import time
import numpy as np
import pickle

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'lotofacil_lite', 'sistemas'))
sys.path.insert(0, os.path.join(BASE_DIR, 'lotofacil_lite', 'interfaces'))

from disputa_neural_pool23 import DisputaNeuralPool23, RedeNeuralExclusao

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DOS 3 NÍVEIS DE TREINO
# ═══════════════════════════════════════════════════════════════════════════════
NIVEIS = [
    {'nome': 'Nível 1 — Aquecimento',     'iteracoes': 3,  'epochs': 20, 'lr': 0.005},
    {'nome': 'Nível 2 — Consolidação',     'iteracoes': 5,  'epochs': 35, 'lr': 0.001},
    {'nome': 'Nível 3 — Refinamento',      'iteracoes': 10, 'epochs': 50, 'lr': 0.0005},
]

# Janela de treino: últimos 2000 concursos (valor ótimo)
JANELA_TREINO = 2000


def avaliar_modelo(disputa, idx_inicio, idx_fim):
    """Avalia o modelo neural atual no range dado. Retorna (taxa_2, stats)."""
    stats = {'acertos_2': 0, 'acertos_1': 0, 'erros': 0}
    total = idx_fim - idx_inicio + 1

    for idx in range(idx_inicio, idx_fim + 1):
        resultado = disputa.historico[idx]['set']
        features = disputa._extrair_features(idx)
        excluidos = disputa.neural.prever_exclusoes(features, 2)
        acertos = sum(1 for n in excluidos if n not in resultado)

        if acertos == 2:
            stats['acertos_2'] += 1
        elif acertos == 1:
            stats['acertos_1'] += 1
        else:
            stats['erros'] += 1

    taxa_2 = stats['acertos_2'] / total * 100 if total > 0 else 0
    return taxa_2, stats, total


def avaliar_invertida(disputa, idx_inicio, idx_fim):
    """Avalia a INVERTIDA v3.0 no range dado."""
    stats = {'acertos_2': 0, 'acertos_1': 0, 'erros': 0}
    total = idx_fim - idx_inicio + 1

    for idx in range(idx_inicio, idx_fim + 1):
        resultado = disputa.historico[idx]['set']
        scores_inv = disputa.invertida.calcular_scores_exclusao(disputa.historico, idx)
        excluidos = disputa.invertida.escolher_exclusoes(scores_inv, 2)
        acertos = sum(1 for n in excluidos if n not in resultado)

        if acertos == 2:
            stats['acertos_2'] += 1
        elif acertos == 1:
            stats['acertos_1'] += 1
        else:
            stats['erros'] += 1

    taxa_2 = stats['acertos_2'] / total * 100 if total > 0 else 0
    return taxa_2, stats, total


def treinar_nivel(disputa, nivel_cfg, idx_inicio, idx_fim):
    """Executa um nível de treino completo."""
    nome = nivel_cfg['nome']
    iteracoes = nivel_cfg['iteracoes']
    epochs = nivel_cfg['epochs']
    lr_base = nivel_cfg['lr']
    total_real = idx_fim - idx_inicio + 1

    print(f"\n{'═' * 70}")
    print(f"🔥 {nome}")
    print(f"   Iterações: {iteracoes} | Épocas/amostra: {epochs} | LR: {lr_base}")
    print(f"{'═' * 70}")

    melhor_taxa = 0
    melhor_pesos = None

    # Preparar dataset uma vez (economiza tempo)
    print("   📦 Preparando dataset...", end="", flush=True)
    X_all = []
    y_all = []
    for idx in range(idx_inicio, idx_fim + 1):
        resultado = disputa.historico[idx]['set']
        features = disputa._extrair_features(idx)
        y = np.zeros(25)
        for n in range(1, 26):
            if n not in resultado:
                y[n - 1] = 1.0
        X_all.append(features)
        y_all.append(y)
    X = np.array(X_all)
    y = np.array(y_all)
    print(f" {len(X)} amostras ✅")

    for it in range(iteracoes):
        lr = lr_base * (0.7 ** it)
        t0 = time.time()

        # Shuffle indices
        indices = np.arange(len(X))
        np.random.shuffle(indices)

        # Treinar por mini-batches
        for epoch in range(epochs):
            for i in range(0, len(X), 32):
                batch_idx = indices[i:i + 32]
                disputa.neural.treinar(X[batch_idx], y[batch_idx], epochs=1, lr=lr)

        # Avaliar
        taxa_2, stats, _ = avaliar_modelo(disputa, idx_inicio, idx_fim)
        elapsed = time.time() - t0

        emoji = "🏆" if taxa_2 > melhor_taxa else "  "
        print(f"   [{it+1:2}/{iteracoes}] Acerto 2/2: {stats['acertos_2']:4} ({taxa_2:5.1f}%) | "
              f"1/2: {stats['acertos_1']:4} | 0/2: {stats['erros']:3} | "
              f"LR={lr:.6f} | {elapsed:.1f}s {emoji}")

        if taxa_2 > melhor_taxa:
            melhor_taxa = taxa_2
            melhor_pesos = {
                'pesos': {k: v.copy() for k, v in disputa.neural.pesos.items()},
                'bias': {k: v.copy() for k, v in disputa.neural.bias.items()},
            }

    # Restaurar melhor modelo deste nível
    if melhor_pesos:
        disputa.neural.pesos = melhor_pesos['pesos']
        disputa.neural.bias = melhor_pesos['bias']
        print(f"   ✅ Melhor deste nível: {melhor_taxa:.1f}%")

    return melhor_taxa


def main():
    print("=" * 70)
    print("🧠 RETREINO NEURAL v3 — 250 features (DO ZERO)")
    print("=" * 70)

    # 1. Criar sistema e carregar dados
    disputa = DisputaNeuralPool23()
    if not disputa.carregar_historico():
        print("❌ Falha ao carregar histórico!")
        return

    total_concursos = len(disputa.historico)
    ultimo_idx = total_concursos - 1
    ultimo_concurso = disputa.historico[ultimo_idx]['concurso']

    # Range de treino: últimos JANELA_TREINO concursos
    idx_fim = ultimo_idx
    idx_inicio = max(30, ultimo_idx - JANELA_TREINO + 1)
    concurso_inicio = disputa.historico[idx_inicio]['concurso']
    total_treino = idx_fim - idx_inicio + 1

    print(f"\n📅 Range de treino: #{concurso_inicio} a #{ultimo_concurso} ({total_treino} concursos)")
    print(f"🧠 Arquitetura: 250 → 96 → 48 → 25 (~30k params)")

    # 2. Criar rede neural DO ZERO (v3)
    print("\n🔄 Inicializando rede neural v3 DO ZERO...")
    disputa.neural = RedeNeuralExclusao(silencioso=False)

    # 3. Baseline INVERTIDA
    print("\n📊 Calculando baseline INVERTIDA v3.0...")
    taxa_inv, stats_inv, _ = avaliar_invertida(disputa, idx_inicio, idx_fim)
    print(f"   INVERTIDA baseline: {stats_inv['acertos_2']} acertos 2/2 ({taxa_inv:.1f}%)")

    # 4. Linha-base neural (antes do treino)
    taxa_pre, stats_pre, _ = avaliar_modelo(disputa, idx_inicio, idx_fim)
    print(f"   Neural pré-treino: {stats_pre['acertos_2']} acertos 2/2 ({taxa_pre:.1f}%)")

    # 5. Executar 3 níveis de treino
    t_total = time.time()
    for nivel in NIVEIS:
        treinar_nivel(disputa, nivel, idx_inicio, idx_fim)

    elapsed_total = time.time() - t_total

    # 6. Avaliação final
    taxa_final, stats_final, _ = avaliar_modelo(disputa, idx_inicio, idx_fim)

    print(f"\n{'═' * 70}")
    print(f"📊 RESULTADO FINAL (treino em {elapsed_total:.0f}s)")
    print(f"{'═' * 70}")
    print(f"\n   ╔═══════════════════╤══════════════╤══════════════╗")
    print(f"   ║ Métrica           │ INVERTIDA    │ NEURAL v3    ║")
    print(f"   ╠═══════════════════╪══════════════╪══════════════╣")

    taxa_1_inv = stats_inv['acertos_1'] / total_treino * 100
    taxa_0_inv = stats_inv['erros'] / total_treino * 100
    taxa_1_neu = stats_final['acertos_1'] / total_treino * 100
    taxa_0_neu = stats_final['erros'] / total_treino * 100

    m2 = "⭐" if taxa_final > taxa_inv else ""
    print(f"   ║ Acerto 2/2 ✅    │ {stats_inv['acertos_2']:4} ({taxa_inv:5.1f}%) │ {stats_final['acertos_2']:4} ({taxa_final:5.1f}%) ║ {m2}")
    print(f"   ║ Acerto 1/2       │ {stats_inv['acertos_1']:4} ({taxa_1_inv:5.1f}%) │ {stats_final['acertos_1']:4} ({taxa_1_neu:5.1f}%) ║")
    print(f"   ║ Erro 0/2 ❌      │ {stats_inv['erros']:4} ({taxa_0_inv:5.1f}%) │ {stats_final['erros']:4} ({taxa_0_neu:5.1f}%) ║")
    print(f"   ╚═══════════════════╧══════════════╧══════════════╝")

    diff = taxa_final - taxa_inv
    print(f"\n   📈 Diferença: {diff:+.1f}pp")

    if diff >= 5:
        print("   🎉 NEURAL v3 SUPEROU INVERTIDA significativamente!")
    elif diff >= 2:
        print("   📊 Neural v3 tem vantagem moderada sobre INVERTIDA")
    elif diff >= 0:
        print("   🤝 Empate técnico (diferença < 2pp)")
    else:
        print("   ⚠️  INVERTIDA ainda superior — mais treino pode ajudar")

    # 7. Out-of-sample test (últimos 200 concursos fora do treino)
    # Treino = idx_inicio..idx_fim, OOS = últimos 200 do treino (in-sample, mas aviso)
    oos_size = min(200, total_treino // 5)
    oos_inicio = idx_fim - oos_size + 1
    taxa_oos_neu, stats_oos_neu, _ = avaliar_modelo(disputa, oos_inicio, idx_fim)
    taxa_oos_inv, stats_oos_inv, _ = avaliar_invertida(disputa, oos_inicio, idx_fim)

    print(f"\n   📈 Out-of-sample (últimos {oos_size} concursos):")
    print(f"      INVERTIDA: {taxa_oos_inv:.1f}% | Neural v3: {taxa_oos_neu:.1f}% | Δ={taxa_oos_neu - taxa_oos_inv:+.1f}pp")

    # 8. Salvar modelo
    modelo_path = disputa.modelo_path
    os.makedirs(os.path.dirname(modelo_path), exist_ok=True)
    disputa.neural.salvar(modelo_path)
    print(f"\n💾 Modelo v3 salvo em: {modelo_path}")

    # Salvar benchmark
    disputa._salvar_benchmark_modelo(
        taxa_neural=taxa_final,
        taxa_invertida=taxa_inv,
        concurso_inicio=concurso_inicio,
        concurso_fim=ultimo_concurso,
        total_concursos=total_treino,
        origem='retreino_v3_completo'
    )
    print(f"💾 Benchmark salvo em: {disputa.benchmark_path}")

    print(f"\n{'═' * 70}")
    print("✅ RETREINO v3 COMPLETO!")
    print(f"{'═' * 70}")


if __name__ == '__main__':
    main()
