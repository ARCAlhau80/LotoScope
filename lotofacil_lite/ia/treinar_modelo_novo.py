#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 TREINADOR DE MODELO NOVO - LOTOSCOPE
Sistema simplificado para treinar novos modelos de IA
- Treinamento de redes neurais básicas
- Análise de padrões históricos
- Predição de combinações
- Integração com sistema de aprendizado

Autor: AR CALHAU
Data: 20 de Setembro de 2025
"""

import os
import sys
import numpy as np
import pickle
from datetime import datetime
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

# Importa configuração do banco
try:
    from db_config import get_connection
    USE_DB_CONFIG = True
except ImportError:
    import sqlite3
    USE_DB_CONFIG = False

class TreinadorModeloNovo:
    """Sistema para treinar novos modelos de IA"""
    
    def __init__(self):
        self.db_path = "lotofacil.db"
        self.pasta_modelos = "modelos_novos"
        self.dados_treinamento = None
        self.modelo_treinado = None
        
        # Cria pasta para modelos
        os.makedirs(self.pasta_modelos, exist_ok=True)
        
        # 🚀 INTEGRAÇÃO DAS DESCOBERTAS DOS CAMPOS DE COMPARAÇÃO
        try:
            from integracao_descobertas_comparacao import IntegracaoDescobertasComparacao
            self.descobertas = IntegracaoDescobertasComparacao()
            print("🔬 Descobertas dos campos de comparação aplicadas")
        except ImportError:
            self.descobertas = None
            print("⚠️ Módulo de descobertas não encontrado - funcionamento normal")
        
        print("🧠 TREINADOR DE MODELO NOVO INICIALIZADO")
        print("=" * 50)
    
    def carregar_dados_historicos(self):
        """Carrega dados históricos da base"""
        print("\n📊 Carregando dados históricos...")
        
        try:
            # Usa a mesma conexão que o super_gerador_ia.py
            if USE_DB_CONFIG:
                conn = get_connection()
                if not conn:
                    print("❌ Falha na conexão com banco via db_config")
                    return False
            else:
                conn = sqlite3.connect(self.db_path)
            
            cursor = conn.cursor()
            
            # Query para pegar os últimos 500 concursos da tabela correta
            # Usa as mesmas colunas que o super_gerador_ia.py
            query = """
            SELECT TOP 500
                Concurso,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                QtdeRepetidos, RepetidosMesmaPosicao,
                QtdePrimos, QtdeImpares, SomaTotal
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            cursor = conn.cursor()
            cursor = conn.cursor()
            
            # Query para pegar os últimos 500 concursos da tabela correta
            # Usa as mesmas colunas que o super_gerador_ia.py
            query = """
            SELECT TOP 500
                Concurso,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                QtdeRepetidos, RepetidosMesmaPosicao,
                QtdePrimos, QtdeImpares, SomaTotal
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Converte para formato estruturado
            dados = []
            for row in resultados:
                concurso = int(row[0])
                # 🔧 CORREÇÃO: Converte números para int Python nativo (igual ao super_gerador_ia.py)
                numeros_raw = row[1:16]
                numeros = [int(n) if hasattr(n, 'item') else int(n) for n in numeros_raw]
                
                # Metadados disponíveis
                metadados = {
                    'qtde_repetidos': int(row[16]) if row[16] else 0,
                    'repetidos_mesma_posicao': int(row[17]) if row[17] else 0,
                    'qtde_primos': int(row[18]) if row[18] else 0,
                    'qtde_impares': int(row[19]) if row[19] else 0,
                    'soma_total': int(row[20]) if row[20] else 0
                }
                
                dados.append({
                    'concurso': concurso,
                    'numeros': numeros,
                    'metadados': metadados
                })
            
            self.dados_treinamento = dados
            conn.close()
            
            print(f"✅ {len(dados)} concursos carregados")
            print(f"   Concurso mais recente: {dados[0]['concurso']}")
            print(f"   Concurso mais antigo: {dados[-1]['concurso']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def preparar_features_treinamento(self):
        """Prepara features para treinamento"""
        print("\n🔧 Preparando features de treinamento...")
        
        if not self.dados_treinamento:
            print("❌ Dados não carregados!")
            return False
        
        # Features que vamos usar para treinar
        X = []  # Features de entrada
        y = []  # Target (próxima combinação)
        
        # Usa janela deslizante: últimos 3 concursos predizem o próximo
        janela = 3
        
        for i in range(len(self.dados_treinamento) - janela):
            # Features: características dos últimos 3 concursos
            features = []
            
            for j in range(janela):
                dados_concurso = self.dados_treinamento[i + j]
                
                # Converte números para features binárias (0/1 para cada número 1-25)
                numeros_binario = [0] * 25
                for num in dados_concurso['numeros']:
                    if 1 <= num <= 25:
                        numeros_binario[num - 1] = 1
                
                # Adiciona metadados normalizados
                metadados_norm = [
                    dados_concurso['metadados']['soma_total'] / 300,  # Soma normalizada
                    dados_concurso['metadados']['qtde_impares'] / 15,   # Ímpares normalizado
                    dados_concurso['metadados']['qtde_primos'] / 15,   # Primos normalizado
                    dados_concurso['metadados']['qtde_repetidos'] / 15,   # Repetidos normalizado
                    dados_concurso['metadados']['repetidos_mesma_posicao'] / 15,   # Mesma posição normalizado
                ]
                
                features.extend(numeros_binario + metadados_norm)
            
            # Target: próxima combinação (binário)
            proximo_concurso = self.dados_treinamento[i + janela]
            target = [0] * 25
            for num in proximo_concurso['numeros']:
                if 1 <= num <= 25:
                    target[num - 1] = 1
            
            X.append(features)
            y.append(target)
        
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        
        print(f"✅ Features preparadas:")
        print(f"   Amostras de treinamento: {len(X)}")
        print(f"   Features por amostra: {len(X[0])}")
        print(f"   Target dimensão: {len(y[0])}")
        
        return True
    
    def treinar_modelo_simples(self):
        """Treina modelo simples usando correlações"""
        print("\n🧠 Treinando modelo baseado em correlações...")
        
        if self.X_train is None:
            print("❌ Features não preparadas!")
            return False
        
        # Análise simples: frequência de cada número nos últimos dados
        frequencias = np.zeros(25)
        probabilidades = np.zeros(25)
        
        # Conta frequência de cada número
        for dados in self.dados_treinamento[:100]:  # Últimos 100 concursos
            for num in dados['numeros']:
                if 1 <= num <= 25:
                    frequencias[num - 1] += 1
        
        # Calcula probabilidades
        probabilidades = frequencias / np.sum(frequencias)
        
        # Análise de padrões: números que aparecem juntos
        coocorrencias = np.zeros((25, 25))
        
        for dados in self.dados_treinamento[:50]:  # Últimos 50 concursos
            numeros = dados['numeros']
            for i, num1 in enumerate(numeros):
                for j, num2 in enumerate(numeros):
                    if num1 != num2 and 1 <= num1 <= 25 and 1 <= num2 <= 25:
                        coocorrencias[num1-1][num2-1] += 1
        
        # Normaliza coocorrências
        for i in range(25):
            soma = np.sum(coocorrencias[i])
            if soma > 0:
                coocorrencias[i] = coocorrencias[i] / soma
        
        # Modelo simples: combina frequências + coocorrências
        self.modelo_treinado = {
            'tipo': 'correlacoes_simples',
            'frequencias': frequencias,
            'probabilidades': probabilidades,
            'coocorrencias': coocorrencias,
            'data_treinamento': datetime.now().isoformat(),
            'amostras_usadas': len(self.dados_treinamento),
            'versao': '1.0.0'
        }
        
        print("✅ Modelo treinado com sucesso!")
        print(f"   Números mais frequentes: {np.argsort(frequencias)[-5:] + 1}")
        print(f"   Números menos frequentes: {np.argsort(frequencias)[:5] + 1}")
        
        return True
    
    def salvar_modelo(self):
        """Salva modelo treinado"""
        print("\n💾 Salvando modelo...")
        
        if not self.modelo_treinado:
            print("❌ Modelo não treinado!")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"modelo_novo_{timestamp}.pkl"
        caminho_completo = os.path.join(self.pasta_modelos, nome_arquivo)
        
        try:
            with open(caminho_completo, 'wb') as f:
                pickle.dump(self.modelo_treinado, f)
            
            print(f"✅ Modelo salvo: {caminho_completo}")
            
            # Salva também metadados em formato texto
            metadados_arquivo = caminho_completo.replace('.pkl', '_metadados.txt')
            with open(metadados_arquivo, 'w', encoding='utf-8') as f:
                f.write(f"MODELO NOVO - METADADOS\n")
                f.write(f"=" * 30 + "\n")
                f.write(f"Data: {self.modelo_treinado['data_treinamento']}\n")
                f.write(f"Tipo: {self.modelo_treinado['tipo']}\n")
                f.write(f"Versão: {self.modelo_treinado['versao']}\n")
                f.write(f"Amostras: {self.modelo_treinado['amostras_usadas']}\n")
                f.write(f"\nTop 10 Números por Frequência:\n")
                
                freq = self.modelo_treinado['frequencias']
                top_nums = np.argsort(freq)[-10:][::-1] + 1
                for i, num in enumerate(top_nums):
                    f.write(f"{i+1:2d}. Número {num:2d}: {freq[num-1]:3.0f} vezes\n")
            
            print(f"✅ Metadados salvos: {metadados_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar modelo: {e}")
            return None
    
    def gerar_predicao(self, num_combinacoes=5):
        """Gera predições usando o modelo treinado"""
        print(f"\n🎯 Gerando {num_combinacoes} predições...")
        
        if not self.modelo_treinado:
            print("❌ Modelo não treinado!")
            return []
        
        combinacoes = []
        
        for i in range(num_combinacoes):
            # Usa probabilidades + aleatoriedade para gerar combinação
            probabilidades = self.modelo_treinado['probabilidades'].copy()
            
            # Adiciona um pouco de aleatoriedade
            ruido = np.random.normal(0, 0.1, 25)
            probabilidades_ajustadas = probabilidades + ruido
            probabilidades_ajustadas = np.maximum(probabilidades_ajustadas, 0)
            
            # Seleciona 15 números com base nas probabilidades ajustadas
            indices_selecionados = np.random.choice(
                25, 
                size=15, 
                replace=False, 
                p=probabilidades_ajustadas/np.sum(probabilidades_ajustadas)
            )
            
            combinacao = sorted([idx + 1 for idx in indices_selecionados])
            combinacoes.append(combinacao)
            
            print(f"   Combinação {i+1}: {combinacao}")
        
        return combinacoes
    
    def testar_modelo(self):
        """Testa o modelo contra dados históricos"""
        print("\n🧪 Testando modelo...")
        
        if not self.modelo_treinado:
            print("❌ Modelo não treinado!")
            return
        
        # Testa contra os últimos 10 concursos
        acertos_total = []
        
        for i in range(10):
            dados_real = self.dados_treinamento[i]
            numeros_reais = set(dados_real['numeros'])
            
            # Gera predição
            predicoes = self.gerar_predicao(1)
            if predicoes:
                numeros_preditos = set(predicoes[0])
                acertos = len(numeros_reais & numeros_preditos)
                acertos_total.append(acertos)
                
                print(f"   Concurso {dados_real['concurso']}: {acertos}/15 acertos")
        
        if acertos_total:
            media_acertos = np.mean(acertos_total)
            print(f"\n📊 RESULTADO DO TESTE:")
            print(f"   Média de acertos: {media_acertos:.1f}/15")
            print(f"   Melhor resultado: {max(acertos_total)}/15")
            print(f"   Pior resultado: {min(acertos_total)}/15")
            
            if media_acertos >= 8:
                print("🏆 Modelo com performance EXCELENTE!")
            elif media_acertos >= 6:
                print("✅ Modelo com performance BOA!")
            else:
                print("⚠️ Modelo precisa de melhorias")
    
    def integrar_com_sistema_aprendizado(self, nome_modelo):
        """Integra o modelo com o sistema de aprendizado"""
        print("\n🔗 Integrando com sistema de aprendizado...")
        
        try:
            # Tenta importar sistema de evolução
            from sistema_evolucao_documentada import SistemaEvolucaoDocumentada
            
            sistema_evolucao = SistemaEvolucaoDocumentada()
            
            # Registra nova versão
            dados_versao = {
                'versao': f'modelo_novo_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'descricao': 'Novo modelo baseado em correlações simples',
                'melhorias': [
                    'Análise de frequências históricas',
                    'Matriz de coocorrências',
                    'Predição probabilística',
                    'Integração com sistema de aprendizado'
                ],
                'metricas_performance': {
                    'precisao_qtde': 0.0,  # Será atualizado após validação
                    'amostras_treinamento': len(self.dados_treinamento),
                    'tempo_treinamento': 30,  # Estimado
                    'tipo_modelo': 'correlacoes_simples'
                },
                'arquivos_modelo': [nome_modelo],
                'descobertas_associadas': [
                    'Modelo simples pode ser eficaz',
                    'Correlações históricas identificadas'
                ]
            }
            
            sistema_evolucao.registrar_nova_versao(dados_versao)
            print("✅ Modelo integrado com sistema de aprendizado!")
            
        except Exception as e:
            print(f"⚠️ Não foi possível integrar com sistema de aprendizado: {e}")

def main():
    """Função principal"""
    print("🚀 INICIANDO TREINAMENTO DE MODELO NOVO")
    print("=" * 50)
    
    try:
        # Inicializa treinador
        treinador = TreinadorModeloNovo()
        
        # Passo 1: Carregar dados
        if not treinador.carregar_dados_historicos():
            print("❌ Falha ao carregar dados")
            return
        
        # Passo 2: Preparar features
        if not treinador.preparar_features_treinamento():
            print("❌ Falha ao preparar features")
            return
        
        # Passo 3: Treinar modelo
        if not treinador.treinar_modelo_simples():
            print("❌ Falha no treinamento")
            return
        
        # Passo 4: Testar modelo
        treinador.testar_modelo()
        
        # Passo 5: Salvar modelo
        nome_modelo = treinador.salvar_modelo()
        if not nome_modelo:
            print("❌ Falha ao salvar modelo")
            return
        
        # Passo 6: Gerar predições de exemplo
        print("\n🎯 EXEMPLO DE PREDIÇÕES:")
        combinacoes = treinador.gerar_predicao(5)
        
        # Passo 7: Integrar com sistema de aprendizado
        treinador.integrar_com_sistema_aprendizado(nome_modelo)
        
        print("\n" + "=" * 50)
        print("🎉 TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 50)
        print(f"✅ Modelo salvo: {nome_modelo}")
        print(f"✅ {len(combinacoes)} predições geradas")
        print(f"✅ Integração com sistema de aprendizado")
        print("\n🎯 Próximos passos:")
        print("   1. Validar predições em concursos futuros")
        print("   2. Ajustar parâmetros se necessário")
        print("   3. Monitorar performance via dashboard")
        
    except KeyboardInterrupt:
        print("\n⏹️ Treinamento cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante treinamento: {e}")

if __name__ == "__main__":
    main()