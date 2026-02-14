"""
🔬 ANALISADOR ACADÊMICO SIMPLIFICADO - MODO DEMO
================================================
Versão que funciona sem conexão ao banco, usando dados simulados
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class AnalisadorAcademicoDemo:
    """
    Versão demo do analisador acadêmico que funciona sem banco de dados
    Gera dados simulados realistas para demonstração das análises
    """
    
    def __init__(self):
        self.dados = None
        self.resultados_analise = {}
        
    def gerar_dados_simulados(self, num_concursos=100):
        """Gera dados simulados realistas da Lotofácil"""
        print(f"🧪 Gerando {num_concursos} concursos simulados...")
        
        np.random.seed(42)  # Para reprodutibilidade
        
        dados_simulados = []
        
        for i in range(num_concursos):
            concurso = 3000 + i
            data_sorteio = datetime(2024, 1, 1) + timedelta(days=i*3)
            
            # Gerar 15 números únicos entre 1 e 25
            numeros = sorted(np.random.choice(range(1, 26), size=15, replace=False))
            
            # Calcular estatísticas baseadas nos números
            primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
            fibonacci = [1, 2, 3, 5, 8, 13, 21]
            
            qtde_primos = sum(1 for n in numeros if n in primos)
            qtde_fibonacci = sum(1 for n in numeros if n in fibonacci)
            qtde_impares = sum(1 for n in numeros if n % 2 == 1)
            soma_total = sum(numeros)
            
            # Quintis (distribuição por faixas)
            quintil1 = sum(1 for n in numeros if 1 <= n <= 5)
            quintil2 = sum(1 for n in numeros if 6 <= n <= 10)
            quintil3 = sum(1 for n in numeros if 11 <= n <= 15)
            quintil4 = sum(1 for n in numeros if 16 <= n <= 20)
            quintil5 = sum(1 for n in numeros if 21 <= n <= 25)
            
            # Gaps (diferenças entre números consecutivos)
            gaps = [numeros[j] - numeros[j-1] - 1 for j in range(1, len(numeros))]
            qtde_gaps = sum(gaps)
            
            # SEQ (números em sequência)
            seq = sum(1 for j in range(1, len(numeros)) if numeros[j] == numeros[j-1] + 1)
            
            # Distância entre extremos
            distancia_extremos = numeros[-1] - numeros[0]
            
            # Múltiplos de 3
            qtde_multiplos3 = sum(1 for n in numeros if n % 3 == 0)
            
            # Faixas
            faixa_baixa = sum(1 for n in numeros if 1 <= n <= 8)
            faixa_media = sum(1 for n in numeros if 9 <= n <= 17)
            faixa_alta = sum(1 for n in numeros if 18 <= n <= 25)
            
            registro = {
                'Concurso': concurso,
                'Data_Sorteio': data_sorteio,
                **{f'N{i+1}': numeros[i] for i in range(15)},
                'QtdePrimos': qtde_primos,
                'QtdeFibonacci': qtde_fibonacci,
                'QtdeImpares': qtde_impares,
                'SomaTotal': soma_total,
                'Quintil1': quintil1,
                'Quintil2': quintil2,
                'Quintil3': quintil3,
                'Quintil4': quintil4,
                'Quintil5': quintil5,
                'QtdeGaps': qtde_gaps,
                'QtdeRepetidos': 0,  # Simulado
                'SEQ': seq,
                'DistanciaExtremos': distancia_extremos,
                'ParesSequencia': 0,  # Simulado
                'QtdeMultiplos3': qtde_multiplos3,
                'ParesSaltados': 0,  # Simulado
                'Faixa_Baixa': faixa_baixa,
                'Faixa_Media': faixa_media,
                'Faixa_Alta': faixa_alta,
                'RepetidosMesmaPosicao': 0,  # Simulado
                'menor_que_ultimo': np.random.randint(0, 8),
                'maior_que_ultimo': np.random.randint(0, 8),
                'igual_ao_ultimo': np.random.randint(0, 3)
            }
            
            dados_simulados.append(registro)
        
        self.dados = pd.DataFrame(dados_simulados)
        print(f"✅ {len(self.dados)} concursos simulados gerados")
        return True
    
    def analise_frequencias_numeros_demo(self):
        """Análise de frequências simplificada"""
        print("\n🔍 ANÁLISE DE FREQUÊNCIAS (DEMO)...")
        
        # Coletar todos os números
        numeros_colunas = [f'N{i}' for i in range(1, 16)]
        todos_numeros = []
        
        for _, row in self.dados.iterrows():
            for col in numeros_colunas:
                todos_numeros.append(row[col])
        
        # Análise de frequência
        freq_numeros = Counter(todos_numeros)
        freq_esperada = len(todos_numeros) / 25
        
        # Simular chi-quadrado
        frequencias_observadas = [freq_numeros[i] for i in range(1, 26)]
        chi2_stat = np.random.uniform(20, 40)  # Simulado
        p_value = np.random.uniform(0.1, 0.9)  # Simulado
        
        # Números quentes e frios
        freq_media = np.mean(frequencias_observadas)
        freq_std = np.std(frequencias_observadas)
        
        numeros_quentes = [i for i in range(1, 26) if freq_numeros[i] > freq_media + freq_std]
        numeros_frios = [i for i in range(1, 26) if freq_numeros[i] < freq_media - freq_std]
        
        cv = freq_std / freq_media
        
        resultado = {
            'frequencias': dict(freq_numeros),
            'freq_esperada': freq_esperada,
            'chi2_uniformidade': {'estatistica': chi2_stat, 'p_valor': p_value},
            'numeros_quentes': numeros_quentes,
            'numeros_frios': numeros_frios,
            'coeficiente_variacao': cv,
            'interpretacao': [
                f"🎲 Frequência esperada: {freq_esperada:.1f} por número",
                f"📊 Coeficiente de variação: {cv:.3f}",
                f"🔥 Números mais frequentes: {numeros_quentes[:3]}",
                f"❄️ Números menos frequentes: {numeros_frios[:3]}"
            ]
        }
        
        self.resultados_analise['frequencias_numeros'] = resultado
        return resultado
    
    def analise_correlacoes_demo(self):
        """Análise de correlações simplificada"""
        print("\n🔍 ANÁLISE DE CORRELAÇÕES (DEMO)...")
        
        campos_numericos = ['SomaTotal', 'QtdePrimos', 'QtdeImpares', 'QtdeGaps']
        
        # Calcular matriz de correlação
        df_campos = self.dados[campos_numericos]
        matriz_correlacao = df_campos.corr()
        
        # Identificar correlações fortes
        correlacoes_fortes = []
        for i in range(len(matriz_correlacao.columns)):
            for j in range(i+1, len(matriz_correlacao.columns)):
                corr_val = matriz_correlacao.iloc[i, j]
                if abs(corr_val) > 0.3:  # Limiar mais baixo para demo
                    correlacoes_fortes.append({
                        'campo1': matriz_correlacao.columns[i],
                        'campo2': matriz_correlacao.columns[j],
                        'correlacao': corr_val
                    })
        
        resultado = {
            'matriz_correlacao': matriz_correlacao.to_dict(),
            'correlacoes_fortes': correlacoes_fortes,
            'interpretacao': [
                f"🔗 {len(correlacoes_fortes)} correlações moderadas detectadas",
                "📈 Matriz de correlação calculada para campos principais",
                "🔄 Dados simulados para demonstração"
            ]
        }
        
        self.resultados_analise['correlacoes_temporais'] = resultado
        return resultado
    
    def analise_clustering_demo(self):
        """Análise de clustering simplificada"""
        print("\n🔍 ANÁLISE DE CLUSTERING (DEMO)...")
        
        # Simular 3 clusters
        k_otimo = 3
        clusters = np.random.choice([0, 1, 2], size=len(self.dados))
        
        analise_clusters = {}
        for cluster_id in range(k_otimo):
            mask = clusters == cluster_id
            tamanho = int(np.sum(mask))
            
            analise_clusters[cluster_id] = {
                'tamanho': tamanho,
                'percentual': float(tamanho / len(self.dados) * 100),
                'caracteristicas': {
                    'SomaTotal': {
                        'media': float(np.random.uniform(180, 220)),
                        'std': float(np.random.uniform(10, 30))
                    },
                    'QtdePrimos': {
                        'media': float(np.random.uniform(5, 8)),
                        'std': float(np.random.uniform(1, 2))
                    }
                }
            }
        
        resultado = {
            'k_otimo': k_otimo,
            'analise_clusters': analise_clusters,
            'interpretacao': [
                f"🎯 {k_otimo} padrões distintos identificados (simulado)",
                f"📊 Distribuição aproximadamente uniforme",
                "🔬 Análise baseada em dados de demonstração"
            ]
        }
        
        self.resultados_analise['clustering_padroes'] = resultado
        return resultado
    
    def analise_entropia_demo(self):
        """Análise de entropia simplificada"""
        print("\n🔍 ANÁLISE DE ENTROPIA (DEMO)...")
        
        # Simular entropias por posição
        entropias_posicao = {}
        for i in range(1, 16):
            entropia_norm = np.random.uniform(0.85, 0.95)  # Alta aleatoriedade simulada
            entropias_posicao[f'posicao_{i}'] = {
                'entropia_normalizada': entropia_norm,
                'uniformidade': entropia_norm
            }
        
        # Simular testes de runs
        testes_runs = {}
        for campo in ['SomaTotal', 'QtdePrimos', 'QtdeImpares']:
            testes_runs[campo] = {
                'p_valor': np.random.uniform(0.1, 0.9),
                'aleatorio': np.random.choice([True, False], p=[0.8, 0.2])
            }
        
        resultado = {
            'entropias_posicao': entropias_posicao,
            'testes_runs': testes_runs,
            'interpretacao': [
                f"🎲 Alta aleatoriedade simulada (entropia > 0.85)",
                f"✅ Maioria dos testes confirma aleatoriedade",
                "📊 Dados de demonstração com comportamento realista"
            ]
        }
        
        self.resultados_analise['entropia_aleatoriedade'] = resultado
        return resultado
    
    def gerar_relatorio_demo(self):
        """Gera relatório da análise demo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_demo_academico_{timestamp}.json"
        
        relatorio = {
            'timestamp': timestamp,
            'modo': 'DEMONSTRACAO',
            'total_concursos_analisados': len(self.dados),
            'periodo_simulado': {
                'inicio': int(self.dados['Concurso'].min()),
                'fim': int(self.dados['Concurso'].max())
            },
            'analises_realizadas': self.resultados_analise,
            'aviso': 'Dados simulados para demonstração do sistema'
        }
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Relatório demo salvo: {nome_arquivo}")
        return nome_arquivo
    
    def executar_demo_completo(self):
        """Executa demonstração completa do sistema"""
        print("🧪 INICIANDO DEMONSTRAÇÃO DO SISTEMA ACADÊMICO...")
        print("=" * 60)
        print("⚠️  MODO DEMONSTRAÇÃO: Usando dados simulados")
        print("🎯 Objetivo: Mostrar funcionalidades do sistema")
        print()
        
        # Gerar dados simulados
        if not self.gerar_dados_simulados(150):
            return False
        
        # Executar análises
        analises = [
            ('Frequências e Distribuições', self.analise_frequencias_numeros_demo),
            ('Correlações Temporais', self.analise_correlacoes_demo),
            ('Clustering de Padrões', self.analise_clustering_demo),
            ('Entropia e Aleatoriedade', self.analise_entropia_demo)
        ]
        
        for nome, metodo in analises:
            try:
                print(f"\n📊 Executando: {nome}...")
                metodo()
                print(f"✅ {nome} concluída")
            except Exception as e:
                print(f"❌ Erro em {nome}: {e}")
        
        # Gerar relatório
        arquivo_relatorio = self.gerar_relatorio_demo()
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print(f"📄 Relatório: {arquivo_relatorio}")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Instale as dependências: pip install seaborn")
        print("2. Configure conexão com banco de dados")
        print("3. Execute análise completa com dados reais")
        
        return arquivo_relatorio

if __name__ == "__main__":
    demo = AnalisadorAcademicoDemo()
    demo.executar_demo_completo()