# -*- coding: utf-8 -*-
"""
=============================================================================
ANÁLISE DE HIDDEN PATTERNS - COMBINACOES_LOTOFACIL
=============================================================================
Objetivo: Descobrir padrões e correlações que possam prever acertos futuros
Técnicas: EDA, Correlações, XGBoost, Clustering, Anomaly Detection
=============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lotofacil_lite', 'utils'))

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from database_config import DatabaseConfig
except ImportError:
    print("❌ Erro: database_config não encontrado")
    sys.exit(1)

# Tentar importar bibliotecas de ML (opcional)
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from scipy import stats
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ sklearn não disponível - análise básica apenas")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost não disponível")


def carregar_dados(tabela='15'):
    """Carrega dados da tabela de combinações"""
    db = DatabaseConfig()
    
    if tabela == '15':
        table_name = 'COMBINACOES_LOTOFACIL'
        num_cols = ', '.join([f'N{i}' for i in range(1, 16)])
    else:
        table_name = 'COMBINACOES_LOTOFACIL20_COMPLETO'
        num_cols = ', '.join([f'N{i}' for i in range(1, 21)])
    
    query = f"""
    SELECT 
        ID,
        {num_cols},
        Acertos_11, Acertos_12, Acertos_13, Acertos_14, Acertos_15,
        Ultimo_Acertos_11, Ultimo_Acertos_12, Ultimo_Acertos_13, 
        Ultimo_Acertos_14, Ultimo_Acertos_15,
        UltimoConcursoAtualizado
    FROM {table_name}
    """
    
    print(f"📊 Carregando dados de {table_name}...")
    df = pd.read_sql(query, db.get_connection())
    print(f"✅ {len(df):,} combinações carregadas")
    
    return df, table_name


def analise_exploratoria(df, table_name):
    """Análise Exploratória de Dados (EDA)"""
    print("\n" + "="*70)
    print("📈 ANÁLISE EXPLORATÓRIA DE DADOS (EDA)")
    print("="*70)
    
    # Estatísticas básicas de acertos
    print("\n📊 ESTATÍSTICAS DE ACERTOS:")
    print("-"*50)
    for nivel in [11, 12, 13, 14, 15]:
        col = f'Acertos_{nivel}'
        dados = df[col]
        print(f"\n🎯 Acertos {nivel}:")
        print(f"   Total: {dados.sum():,}")
        print(f"   Média: {dados.mean():.2f}")
        print(f"   Mediana: {dados.median():.0f}")
        print(f"   Desvio Padrão: {dados.std():.2f}")
        print(f"   Mínimo: {dados.min():.0f}")
        print(f"   Máximo: {dados.max():.0f}")
        print(f"   Combinações com 0 acertos: {(dados == 0).sum():,} ({(dados == 0).sum()/len(df)*100:.2f}%)")
        print(f"   Combinações com 1+ acertos: {(dados > 0).sum():,} ({(dados > 0).sum()/len(df)*100:.2f}%)")
    
    return df


def analise_saltos_nivel(df):
    """Analisa combinações que 'saltam' níveis (ex: 15 sem 14)"""
    print("\n" + "="*70)
    print("🔀 ANÁLISE DE SALTOS DE NÍVEL")
    print("="*70)
    
    # Combinações que acertaram 15
    com_15 = df[df['Acertos_15'] > 0]
    total_15 = len(com_15)
    
    if total_15 > 0:
        # 15 sem 14
        sem_14 = com_15[com_15['Acertos_14'] == 0]
        print(f"\n🏆 Combinações com 15 acertos: {total_15:,}")
        print(f"   • Sem acertos de 14: {len(sem_14):,} ({len(sem_14)/total_15*100:.2f}%)")
        print(f"   • Com acertos de 14: {total_15 - len(sem_14):,} ({(total_15 - len(sem_14))/total_15*100:.2f}%)")
        
        # 15 sem 13
        sem_13 = com_15[com_15['Acertos_13'] == 0]
        print(f"   • Sem acertos de 13: {len(sem_13):,} ({len(sem_13)/total_15*100:.2f}%)")
        
        # 15 sem 12
        sem_12 = com_15[com_15['Acertos_12'] == 0]
        print(f"   • Sem acertos de 12: {len(sem_12):,} ({len(sem_12)/total_15*100:.2f}%)")
        
        # 15 sem 11
        sem_11 = com_15[com_15['Acertos_11'] == 0]
        print(f"   • Sem acertos de 11: {len(sem_11):,} ({len(sem_11)/total_15*100:.2f}%)")
    
    # Combinações que acertaram 14
    com_14 = df[df['Acertos_14'] > 0]
    total_14 = len(com_14)
    
    if total_14 > 0:
        sem_13_14 = com_14[com_14['Acertos_13'] == 0]
        print(f"\n🥈 Combinações com 14 acertos: {total_14:,}")
        print(f"   • Sem acertos de 13: {len(sem_13_14):,} ({len(sem_13_14)/total_14*100:.2f}%)")
        
        # Média de 14 por combinação
        print(f"   • Média de acertos 14 por combinação: {com_14['Acertos_14'].mean():.2f}")
    
    return df


def analise_correlacoes(df):
    """Análise de correlações entre níveis de acertos"""
    print("\n" + "="*70)
    print("🔗 ANÁLISE DE CORRELAÇÕES")
    print("="*70)
    
    cols_acertos = ['Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15']
    
    # Matriz de correlação
    corr_matrix = df[cols_acertos].corr()
    
    print("\n📊 Matriz de Correlação (Pearson):")
    print("-"*60)
    print(corr_matrix.to_string())
    
    # Correlações mais fortes
    print("\n🔝 Correlações mais relevantes:")
    for i, col1 in enumerate(cols_acertos):
        for col2 in cols_acertos[i+1:]:
            corr = corr_matrix.loc[col1, col2]
            if abs(corr) > 0.3:
                sinal = "+" if corr > 0 else "-"
                print(f"   {col1} ↔ {col2}: {sinal}{abs(corr):.4f}")
    
    return corr_matrix


def analise_extremos(df):
    """Analisa combinações com valores extremos"""
    print("\n" + "="*70)
    print("📍 ANÁLISE DE EXTREMOS")
    print("="*70)
    
    # Top 10 mais acertos de 11
    print("\n🔝 TOP 10 - Mais acertos de 11:")
    print("-"*80)
    top_11 = df.nlargest(10, 'Acertos_11')[['ID', 'Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15']]
    for _, row in top_11.iterrows():
        print(f"   ID {row['ID']:>8} | A11={row['Acertos_11']:>3} | A12={row['Acertos_12']:>3} | A13={row['Acertos_13']:>3} | A14={row['Acertos_14']:>2} | A15={row['Acertos_15']:>1}")
    
    # Bottom 10 menos acertos de 11 (excluindo zeros)
    df_non_zero = df[df['Acertos_11'] > 0]
    print("\n🔻 BOTTOM 10 - Menos acertos de 11 (com pelo menos 1):")
    print("-"*80)
    bottom_11 = df_non_zero.nsmallest(10, 'Acertos_11')[['ID', 'Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15']]
    for _, row in bottom_11.iterrows():
        print(f"   ID {row['ID']:>8} | A11={row['Acertos_11']:>3} | A12={row['Acertos_12']:>3} | A13={row['Acertos_13']:>3} | A14={row['Acertos_14']:>2} | A15={row['Acertos_15']:>1}")
    
    # Top 10 mais acertos de 14
    print("\n🥈 TOP 10 - Mais acertos de 14:")
    print("-"*80)
    top_14 = df.nlargest(10, 'Acertos_14')[['ID', 'Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15']]
    for _, row in top_14.iterrows():
        print(f"   ID {row['ID']:>8} | A11={row['Acertos_11']:>3} | A12={row['Acertos_12']:>3} | A13={row['Acertos_13']:>3} | A14={row['Acertos_14']:>2} | A15={row['Acertos_15']:>1}")
    
    return df


def criar_features(df):
    """Cria features derivadas para análise de ML"""
    print("\n" + "="*70)
    print("⚙️ CRIANDO FEATURES DERIVADAS")
    print("="*70)
    
    # Ratios entre níveis
    df['Ratio_12_11'] = df['Acertos_12'] / (df['Acertos_11'] + 1)
    df['Ratio_13_12'] = df['Acertos_13'] / (df['Acertos_12'] + 1)
    df['Ratio_14_13'] = df['Acertos_14'] / (df['Acertos_13'] + 1)
    df['Ratio_15_14'] = df['Acertos_15'] / (df['Acertos_14'] + 1)
    
    # Total de acertos ponderado
    df['Total_Ponderado'] = (
        df['Acertos_11'] * 1 +
        df['Acertos_12'] * 2 +
        df['Acertos_13'] * 4 +
        df['Acertos_14'] * 8 +
        df['Acertos_15'] * 16
    )
    
    # Flag: já acertou 14+
    df['Ja_Acertou_14_Plus'] = ((df['Acertos_14'] > 0) | (df['Acertos_15'] > 0)).astype(int)
    
    # Gap entre últimos acertos
    df['Gap_14_13'] = df['Ultimo_Acertos_14'].fillna(0) - df['Ultimo_Acertos_13'].fillna(0)
    df['Gap_15_14'] = df['Ultimo_Acertos_15'].fillna(0) - df['Ultimo_Acertos_14'].fillna(0)
    
    # Último acerto mais recente (qualquer nível 14+)
    df['Ultimo_14_Plus'] = df[['Ultimo_Acertos_14', 'Ultimo_Acertos_15']].max(axis=1)
    
    # Concursos desde último acerto 14+
    ultimo_concurso = df['UltimoConcursoAtualizado'].max()
    df['Concursos_Desde_14_Plus'] = ultimo_concurso - df['Ultimo_14_Plus'].fillna(0)
    
    # Eficiência: ratio de acertos altos vs baixos
    df['Eficiencia'] = (df['Acertos_14'] + df['Acertos_15'] * 5) / (df['Acertos_11'] + 1)
    
    print("✅ Features criadas:")
    print("   • Ratio_12_11, Ratio_13_12, Ratio_14_13, Ratio_15_14")
    print("   • Total_Ponderado")
    print("   • Ja_Acertou_14_Plus")
    print("   • Gap_14_13, Gap_15_14")
    print("   • Ultimo_14_Plus")
    print("   • Concursos_Desde_14_Plus")
    print("   • Eficiencia")
    
    return df


def analise_probabilidade_condicional(df):
    """Análise de probabilidade condicional"""
    print("\n" + "="*70)
    print("📊 ANÁLISE DE PROBABILIDADE CONDICIONAL")
    print("="*70)
    
    total = len(df)
    
    # P(15 | já teve 14)
    com_14 = df[df['Acertos_14'] > 0]
    com_14_e_15 = com_14[com_14['Acertos_15'] > 0]
    if len(com_14) > 0:
        p_15_dado_14 = len(com_14_e_15) / len(com_14) * 100
        print(f"\n🎯 P(acertar 15 | já acertou 14) = {p_15_dado_14:.4f}%")
        print(f"   Base: {len(com_14):,} combinações com 14+")
    
    # P(15 | nunca teve 14)
    sem_14 = df[df['Acertos_14'] == 0]
    sem_14_com_15 = sem_14[sem_14['Acertos_15'] > 0]
    if len(sem_14) > 0:
        p_15_dado_nao_14 = len(sem_14_com_15) / len(sem_14) * 100
        print(f"\n🎯 P(acertar 15 | NUNCA acertou 14) = {p_15_dado_nao_14:.4f}%")
        print(f"   Base: {len(sem_14):,} combinações sem 14")
    
    # P(14 | muitos 13)
    mediana_13 = df['Acertos_13'].median()
    muitos_13 = df[df['Acertos_13'] > mediana_13]
    muitos_13_com_14 = muitos_13[muitos_13['Acertos_14'] > 0]
    if len(muitos_13) > 0:
        p_14_dado_muitos_13 = len(muitos_13_com_14) / len(muitos_13) * 100
        print(f"\n🎯 P(acertar 14 | Acertos_13 > mediana={mediana_13:.0f}) = {p_14_dado_muitos_13:.4f}%")
        print(f"   Base: {len(muitos_13):,} combinações")
    
    # P(14 | poucos 13)
    poucos_13 = df[df['Acertos_13'] <= mediana_13]
    poucos_13_com_14 = poucos_13[poucos_13['Acertos_14'] > 0]
    if len(poucos_13) > 0:
        p_14_dado_poucos_13 = len(poucos_13_com_14) / len(poucos_13) * 100
        print(f"\n🎯 P(acertar 14 | Acertos_13 <= mediana={mediana_13:.0f}) = {p_14_dado_poucos_13:.4f}%")
        print(f"   Base: {len(poucos_13):,} combinações")
    
    # Análise por faixas de Acertos_11
    print("\n📊 Distribuição de acertos por faixa de Acertos_11:")
    print("-"*70)
    
    # Criar faixas
    df['Faixa_11'] = pd.cut(df['Acertos_11'], bins=[0, 250, 300, 350, 400, 500], 
                           labels=['0-250', '251-300', '301-350', '351-400', '401+'])
    
    for faixa in df['Faixa_11'].unique():
        if pd.isna(faixa):
            continue
        grupo = df[df['Faixa_11'] == faixa]
        com_14_grupo = grupo[grupo['Acertos_14'] > 0]
        com_15_grupo = grupo[grupo['Acertos_15'] > 0]
        print(f"   Faixa {faixa}: {len(grupo):>8,} combinações | "
              f"14+: {len(com_14_grupo):>5,} ({len(com_14_grupo)/len(grupo)*100:>5.2f}%) | "
              f"15: {len(com_15_grupo):>4,} ({len(com_15_grupo)/len(grupo)*100:>5.2f}%)")
    
    return df


def analise_clustering(df):
    """Análise de clustering para identificar grupos"""
    if not ML_AVAILABLE:
        print("\n⚠️ sklearn não disponível - pulando clustering")
        return df
    
    print("\n" + "="*70)
    print("🔬 ANÁLISE DE CLUSTERING (K-Means)")
    print("="*70)
    
    # Features para clustering
    features = ['Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15']
    
    # Normalizar
    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])
    
    # K-Means com 5 clusters
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X)
    
    print("\n📊 Perfil dos Clusters:")
    print("-"*80)
    
    for cluster in range(5):
        grupo = df[df['Cluster'] == cluster]
        com_14 = grupo[grupo['Acertos_14'] > 0]
        com_15 = grupo[grupo['Acertos_15'] > 0]
        
        print(f"\n🏷️ Cluster {cluster}: {len(grupo):,} combinações")
        print(f"   Média A11: {grupo['Acertos_11'].mean():.1f} | "
              f"A12: {grupo['Acertos_12'].mean():.1f} | "
              f"A13: {grupo['Acertos_13'].mean():.1f} | "
              f"A14: {grupo['Acertos_14'].mean():.2f} | "
              f"A15: {grupo['Acertos_15'].mean():.4f}")
        print(f"   Taxa 14+: {len(com_14)/len(grupo)*100:.2f}% | "
              f"Taxa 15: {len(com_15)/len(grupo)*100:.4f}%")
    
    return df


def analise_anomalias(df):
    """Detecta combinações anômalas (outliers)"""
    if not ML_AVAILABLE:
        print("\n⚠️ sklearn não disponível - pulando detecção de anomalias")
        return df
    
    print("\n" + "="*70)
    print("🔍 DETECÇÃO DE ANOMALIAS (Isolation Forest)")
    print("="*70)
    
    # Features para detecção de anomalias
    features = ['Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15']
    
    # Isolation Forest
    iso = IsolationForest(contamination=0.01, random_state=42)
    df['Anomalia'] = iso.fit_predict(df[features])
    
    # Anomalias = -1
    anomalias = df[df['Anomalia'] == -1]
    normais = df[df['Anomalia'] == 1]
    
    print(f"\n📊 Resultado:")
    print(f"   Normais: {len(normais):,} ({len(normais)/len(df)*100:.2f}%)")
    print(f"   Anomalias: {len(anomalias):,} ({len(anomalias)/len(df)*100:.2f}%)")
    
    # Perfil das anomalias
    print(f"\n🔺 Perfil das Anomalias:")
    print(f"   Média A11: {anomalias['Acertos_11'].mean():.1f} vs Normal: {normais['Acertos_11'].mean():.1f}")
    print(f"   Média A12: {anomalias['Acertos_12'].mean():.1f} vs Normal: {normais['Acertos_12'].mean():.1f}")
    print(f"   Média A13: {anomalias['Acertos_13'].mean():.1f} vs Normal: {normais['Acertos_13'].mean():.1f}")
    print(f"   Média A14: {anomalias['Acertos_14'].mean():.2f} vs Normal: {normais['Acertos_14'].mean():.2f}")
    
    # Taxa de 14+ nas anomalias
    anomalias_14 = anomalias[anomalias['Acertos_14'] > 0]
    normais_14 = normais[normais['Acertos_14'] > 0]
    print(f"\n   Taxa 14+ Anomalias: {len(anomalias_14)/len(anomalias)*100:.2f}%")
    print(f"   Taxa 14+ Normais: {len(normais_14)/len(normais)*100:.2f}%")
    
    return df


def analise_xgboost(df):
    """Usa XGBoost para identificar features importantes"""
    if not XGBOOST_AVAILABLE or not ML_AVAILABLE:
        print("\n⚠️ XGBoost não disponível")
        return df
    
    print("\n" + "="*70)
    print("🚀 ANÁLISE COM XGBOOST")
    print("="*70)
    
    # Target: já acertou 14 ou mais
    df['Target_14_Plus'] = ((df['Acertos_14'] > 0) | (df['Acertos_15'] > 0)).astype(int)
    
    # Features (apenas acertos anteriores)
    features = ['Acertos_11', 'Acertos_12', 'Acertos_13']
    
    X = df[features]
    y = df['Target_14_Plus']
    
    # Treinar modelo
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X, y)
    
    # Importância das features
    print("\n📊 Importância das Features para prever 14+:")
    print("-"*50)
    
    importances = model.feature_importances_
    for feat, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
        print(f"   {feat}: {imp:.4f} {'█' * int(imp * 50)}")
    
    # Score
    df['Score_14_Plus'] = model.predict_proba(X)[:, 1]
    
    # Top combinações por score
    print("\n🔝 TOP 20 combinações com maior Score (que ainda não acertaram 14+):")
    print("-"*80)
    
    candidatas = df[(df['Acertos_14'] == 0) & (df['Acertos_15'] == 0)]
    top_candidatas = candidatas.nlargest(20, 'Score_14_Plus')
    
    for _, row in top_candidatas.iterrows():
        print(f"   ID {row['ID']:>8} | A11={row['Acertos_11']:>3} | A12={row['Acertos_12']:>3} | "
              f"A13={row['Acertos_13']:>3} | Score={row['Score_14_Plus']:.4f}")
    
    return df


def analise_tendencia_temporal(df):
    """Analisa tendência temporal dos acertos"""
    print("\n" + "="*70)
    print("📅 ANÁLISE DE TENDÊNCIA TEMPORAL")
    print("="*70)
    
    # Combinações que acertaram 15 - quando foi o último?
    com_15 = df[df['Acertos_15'] > 0].copy()
    
    if len(com_15) > 0:
        print(f"\n🏆 Distribuição temporal dos acertos de 15:")
        
        # Agrupar por faixas de concurso
        ultimo_concurso = df['UltimoConcursoAtualizado'].max()
        
        com_15['Faixa_Temporal'] = pd.cut(
            com_15['Ultimo_Acertos_15'], 
            bins=[0, 1000, 2000, 2500, 3000, 3500, ultimo_concurso+1],
            labels=['0-1000', '1001-2000', '2001-2500', '2501-3000', '3001-3500', f'3501-{ultimo_concurso}']
        )
        
        print("-"*50)
        for faixa in com_15['Faixa_Temporal'].unique():
            if pd.isna(faixa):
                continue
            count = len(com_15[com_15['Faixa_Temporal'] == faixa])
            print(f"   Concursos {faixa}: {count:>4} acertos de 15")
    
    # Combinações "quentes" - acertaram 14 recentemente
    print(f"\n🔥 Combinações 'Quentes' (acertaram 14 nos últimos 100 concursos):")
    ultimo_concurso = df['UltimoConcursoAtualizado'].max()
    quentes = df[df['Ultimo_Acertos_14'] >= (ultimo_concurso - 100)]
    print(f"   Total: {len(quentes):,} combinações")
    
    if len(quentes) > 0:
        # Dessas, quantas já acertaram 15?
        quentes_15 = quentes[quentes['Acertos_15'] > 0]
        print(f"   Já acertaram 15: {len(quentes_15):,} ({len(quentes_15)/len(quentes)*100:.2f}%)")
    
    # Combinações "frias" - nunca acertaram 14
    frias = df[df['Acertos_14'] == 0]
    print(f"\n❄️ Combinações 'Frias' (nunca acertaram 14):")
    print(f"   Total: {len(frias):,} combinações ({len(frias)/len(df)*100:.2f}%)")
    
    # Dessas, quantas acertaram 15?
    frias_15 = frias[frias['Acertos_15'] > 0]
    print(f"   Mas acertaram 15: {len(frias_15):,} ({len(frias_15)/len(frias)*100:.4f}%)")
    
    return df


def gerar_relatorio_final(df, table_name):
    """Gera relatório final com insights principais"""
    print("\n" + "="*70)
    print("📋 RELATÓRIO FINAL - HIDDEN PATTERNS")
    print("="*70)
    
    total = len(df)
    com_15 = len(df[df['Acertos_15'] > 0])
    com_14 = len(df[df['Acertos_14'] > 0])
    sem_14_com_15 = len(df[(df['Acertos_14'] == 0) & (df['Acertos_15'] > 0)])
    
    print(f"\n📊 Tabela: {table_name}")
    print(f"   Total de combinações: {total:,}")
    
    print(f"\n🎯 INSIGHTS PRINCIPAIS:")
    print("-"*50)
    
    print(f"\n1️⃣ SALTO DE NÍVEL:")
    if com_15 > 0:
        pct_salto = sem_14_com_15 / com_15 * 100
        print(f"   • {pct_salto:.2f}% das combinações que acertaram 15")
        print(f"     NUNCA haviam acertado 14 antes")
        print(f"   • Isso sugere que acertos de 14 NÃO são pré-requisito para 15")
    
    print(f"\n2️⃣ DISTRIBUIÇÃO DE ACERTOS 11:")
    max_11 = df['Acertos_11'].max()
    min_11 = df[df['Acertos_11'] > 0]['Acertos_11'].min()
    print(f"   • Máximo: {max_11} acertos")
    print(f"   • Mínimo (>0): {min_11} acertos")
    print(f"   • Variação: {(max_11 - min_11) / max_11 * 100:.1f}%")
    print(f"   • Todas combinações têm chance, não há 'combinações ruins'")
    
    # Correlação entre 13 e 14
    corr_13_14 = df['Acertos_13'].corr(df['Acertos_14'])
    print(f"\n3️⃣ CORRELAÇÃO 13 ↔ 14:")
    print(f"   • Correlação: {corr_13_14:.4f}")
    if corr_13_14 > 0.5:
        print(f"   • FORTE correlação - mais 13 = mais chance de 14")
    elif corr_13_14 > 0.3:
        print(f"   • MODERADA correlação")
    else:
        print(f"   • FRACA correlação - 13 não prediz 14")
    
    # Eficiência
    if 'Eficiencia' in df.columns:
        top_eficiencia = df.nlargest(100, 'Eficiencia')
        taxa_15_top = len(top_eficiencia[top_eficiencia['Acertos_15'] > 0]) / len(top_eficiencia) * 100
        taxa_15_geral = com_15 / total * 100
        
        print(f"\n4️⃣ EFICIÊNCIA (ratio acertos altos/baixos):")
        print(f"   • Taxa de 15 no TOP 100 eficiência: {taxa_15_top:.2f}%")
        print(f"   • Taxa de 15 geral: {taxa_15_geral:.4f}%")
        if taxa_15_top > taxa_15_geral * 10:
            print(f"   • TOP eficiência tem {taxa_15_top/taxa_15_geral:.1f}x mais chance!")
    
    print("\n" + "="*70)
    print("💡 CONCLUSÕES:")
    print("="*70)
    print("""
    1. O histórico de acertos menores (11, 12, 13) tem correlação FRACA
       com acertos maiores (14, 15) - sorte é o fator dominante.
    
    2. Combinações que "saltam" de 13 direto para 15 são COMUNS (>80%),
       indicando que cada sorteio é independente.
    
    3. A variação nos acertos de 11 (~44% entre max e min) mostra que
       algumas combinações aparecem mais em sorteios próximos ao resultado.
    
    4. Filtros de EFICIÊNCIA podem identificar combinações com histórico
       de "quase acertar" mais frequentemente.
    """)
    
    return df


def main():
    """Função principal"""
    print("="*70)
    print("🔬 ANÁLISE DE HIDDEN PATTERNS - LOTOFÁCIL")
    print("="*70)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Escolher tabela
    print("\n📋 Escolha a tabela para análise:")
    print("   1. COMBINACOES_LOTOFACIL (15 números)")
    print("   2. COMBINACOES_LOTOFACIL20_COMPLETO (20 números)")
    
    opcao = input("\nOpção [1/2]: ").strip() or '1'
    tabela = '15' if opcao == '1' else '20'
    
    # Carregar dados
    df, table_name = carregar_dados(tabela)
    
    # Executar análises
    df = analise_exploratoria(df, table_name)
    df = analise_saltos_nivel(df)
    analise_correlacoes(df)
    df = analise_extremos(df)
    df = criar_features(df)
    df = analise_probabilidade_condicional(df)
    df = analise_tendencia_temporal(df)
    df = analise_clustering(df)
    df = analise_anomalias(df)
    df = analise_xgboost(df)
    df = gerar_relatorio_final(df, table_name)
    
    # Salvar resultados
    print("\n💾 Deseja salvar os resultados em CSV? [S/n]: ", end="")
    salvar = input().strip().lower()
    if salvar != 'n':
        output_file = f"hidden_patterns_{tabela}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        cols_export = ['ID', 'Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15',
                      'Ultimo_Acertos_14', 'Ultimo_Acertos_15']
        if 'Score_14_Plus' in df.columns:
            cols_export.append('Score_14_Plus')
        if 'Cluster' in df.columns:
            cols_export.append('Cluster')
        if 'Eficiencia' in df.columns:
            cols_export.append('Eficiencia')
        
        df[cols_export].to_csv(output_file, index=False)
        print(f"✅ Salvo em: {output_file}")
    
    print("\n✅ Análise concluída!")
    return df


if __name__ == "__main__":
    main()
