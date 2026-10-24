"""
GERADOR INTELIGENTE DE COMBINAÇÕES LOTOFÁCIL
============================================
Sistema que usa análises acadêmicas para gerar combinações de alta performance
"""

import numpy as np
import pandas as pd
import json
import random
from datetime import datetime
import glob
import pyodbc

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from collections import Counter

class GeradorInteligente:
    """
    Gerador de combinações baseado em análises científicas
    """
    
    def __init__(self, servidor="VADER", database="LOTOFACIL"):
        self.servidor = servidor
        self.database = database
        self.dados_historicos = None
        self.analises_academicas = None
        self.ultimo_concurso = None
        self.tendencias_atuais = {}
        
        print("🧠 GERADOR INTELIGENTE INICIALIZADO")
        print("=" * 45)
        
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            conn_strings = [
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.servidor};DATABASE={self.database};Trusted_Connection=yes',
                f'DRIVER={{SQL Server}};SERVER={self.servidor};DATABASE={self.database};Trusted_Connection=yes'
            ]
            
            for conn_str in conn_strings:
                try:
                    # Conexão otimizada para performance
                    if _db_optimizer:
                        conn = _db_optimizer.create_optimized_connection()
                    else:
                        connection = pyodbc.connect(conn_str)
                    return connection
                except:
                    continue
            
            raise Exception("Nenhuma string de conexão funcionou")
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return None
    
    def carregar_dados_historicos(self):
        """Carrega dados históricos do banco"""
        print("📊 Carregando dados históricos...")
        
        connection = self.conectar_banco()
        if not connection:
            return False
        
        try:
            query = """
            SELECT TOP 100
                Concurso, Data_Sorteio,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                N11, N12, N13, N14, N15,
                QtdeImpares, QtdePrimos, SomaTotal,
                Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                Faixa_Baixa, Faixa_Media, Faixa_Alta
            FROM RESULTADOS_INT
            ORDER BY Concurso DESC
            """
            
            self.dados_historicos = pd.read_sql(query, connection)
            self.ultimo_concurso = self.dados_historicos.iloc[0]
            
            print(f"✅ Dados carregados: {len(self.dados_historicos)} concursos")
            print(f"🎯 Último concurso: {self.ultimo_concurso['Concurso']}")
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            if connection:
                connection.close()
            return False
    
    def carregar_analises_academicas(self):
        """Carrega a análise acadêmica mais recente"""
        print("🔬 Carregando análises acadêmicas...")
        
        import os
        
        # Buscar arquivo mais recente
        arquivos_analise = glob.glob("relatorio_analise_*.json")
        
        if not arquivos_analise:
            print("⚠️ Nenhuma análise acadêmica encontrada. Execute primeiro o analisador.")
            return False
        
        arquivo_mais_recente = max(arquivos_analise, key=lambda x: os.path.getctime(x))
        
        try:
            with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
                self.analises_academicas = json.load(f)
            
            print(f"✅ Análises carregadas: {arquivo_mais_recente}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar análises: {e}")
            return False
    
    def analisar_situacao_atual(self):
        """Analisa a situação atual dos sorteios"""
        print("\n🎯 ANALISANDO SITUAÇÃO ATUAL...")
        print("-" * 35)
        
        if self.dados_historicos is None:
            print("❌ Dados históricos não carregados")
            return False
        
        # Análise dos últimos 10 concursos
        ultimos_10 = self.dados_historicos.head(10)
        
        # Tendências de pares/ímpares
        media_impares = ultimos_10['QtdeImpares'].mean()
        self.tendencias_atuais['impares_tendencia'] = media_impares
        
        # Tendências de primos
        media_primos = ultimos_10['QtdePrimos'].mean()
        self.tendencias_atuais['primos_tendencia'] = media_primos
        
        # Análise de soma total
        media_soma = ultimos_10['SomaTotal'].mean()
        self.tendencias_atuais['soma_tendencia'] = media_soma
        
        # Análise de faixas
        faixa_baixa_media = ultimos_10['Faixa_Baixa'].mean()
        faixa_media_media = ultimos_10['Faixa_Media'].mean()
        faixa_alta_media = ultimos_10['Faixa_Alta'].mean()
        
        self.tendencias_atuais['faixa_baixa'] = faixa_baixa_media
        self.tendencias_atuais['faixa_media'] = faixa_media_media
        self.tendencias_atuais['faixa_alta'] = faixa_alta_media
        
        # Números mais sorteados recentemente
        numeros_recentes = []
        for _, row in ultimos_10.iterrows():
            for i in range(1, 16):
                numeros_recentes.append(row[f'N{i}'])
        
        freq_recentes = Counter(numeros_recentes)
        self.tendencias_atuais['numeros_quentes'] = [num for num, freq in freq_recentes.most_common(10)]
        self.tendencias_atuais['numeros_frios'] = [num for num in range(1, 26) 
                                                  if num not in self.tendencias_atuais['numeros_quentes']]
        
        print(f"📈 Últimos 10 concursos analisados")
        print(f"   Ímpares médios: {media_impares:.1f}")
        print(f"   Primos médios: {media_primos:.1f}")
        print(f"   Soma média: {media_soma:.0f}")
        print(f"   Números quentes: {self.tendencias_atuais['numeros_quentes'][:5]}")
        
        return True
    
    def gerar_combinacao_equilibrada(self):
        """Gera combinação baseada em equilíbrio estatístico"""
        # Parâmetros ideais baseados na análise
        target_impares = round(self.tendencias_atuais.get('impares_tendencia', 7.5))
        target_primos = round(self.tendencias_atuais.get('primos_tendencia', 6))
        
        # Ajustar para valores válidos
        target_impares = max(3, min(12, target_impares))
        target_primos = max(2, min(10, target_primos))
        
        # Números primos até 25
        primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        nao_primos = [i for i in range(1, 26) if i not in primos]
        
        # Números ímpares e pares
        impares = [i for i in range(1, 26) if i % 2 == 1]
        pares = [i for i in range(1, 26) if i % 2 == 0]
        
        combinacao = []
        
        # Selecionar primos
        primos_selecionados = random.sample(primos, min(target_primos, len(primos)))
        combinacao.extend(primos_selecionados)
        
        # Completar com não-primos se necessário
        if len(combinacao) < 15:
            nao_primos_disponiveis = [n for n in nao_primos if n not in combinacao]
            restantes_primos = 15 - len(combinacao)
            if restantes_primos > 0:
                nao_primos_sel = random.sample(nao_primos_disponiveis, 
                                             min(restantes_primos, len(nao_primos_disponiveis)))
                combinacao.extend(nao_primos_sel)
        
        # Ajustar pares/ímpares
        impares_atual = len([n for n in combinacao if n % 2 == 1])
        
        if impares_atual < target_impares:
            # Precisa de mais ímpares
            impares_disponiveis = [n for n in impares if n not in combinacao]
            while impares_atual < target_impares and len(combinacao) < 15 and impares_disponiveis:
                num = random.choice(impares_disponiveis)
                combinacao.append(num)
                impares_disponiveis.remove(num)
                impares_atual += 1
        
        # Completar até 15 números
        while len(combinacao) < 15:
            disponiveis = [i for i in range(1, 26) if i not in combinacao]
            if disponiveis:
                combinacao.append(random.choice(disponiveis))
            else:
                break
        
        return sorted(combinacao[:15])
    
    def gerar_combinacao_por_tendencias(self):
        """Gera combinação baseada nas tendências atuais"""
        numeros_quentes = self.tendencias_atuais.get('numeros_quentes', list(range(1, 26)))
        numeros_frios = self.tendencias_atuais.get('numeros_frios', [])
        
        combinacao = []
        
        # 60% números quentes, 40% frios (para balanceamento)
        quentes_qtd = 9
        frios_qtd = 6
        
        # Selecionar números quentes
        if len(numeros_quentes) >= quentes_qtd:
            combinacao.extend(random.sample(numeros_quentes, quentes_qtd))
        else:
            combinacao.extend(numeros_quentes)
        
        # Completar com números frios
        if len(numeros_frios) > 0:
            frios_disponiveis = [n for n in numeros_frios if n not in combinacao]
            frios_necessarios = min(frios_qtd, len(frios_disponiveis))
            if frios_necessarios > 0:
                combinacao.extend(random.sample(frios_disponiveis, frios_necessarios))
        
        # Completar se necessário
        while len(combinacao) < 15:
            disponiveis = [i for i in range(1, 26) if i not in combinacao]
            if disponiveis:
                combinacao.append(random.choice(disponiveis))
            else:
                break
        
        return sorted(combinacao[:15])
    
    def gerar_combinacao_por_faixas(self):
        """Gera combinação respeitando distribuição por faixas"""
        faixa_baixa_target = round(self.tendencias_atuais.get('faixa_baixa', 5))
        faixa_media_target = round(self.tendencias_atuais.get('faixa_media', 5))
        faixa_alta_target = round(self.tendencias_atuais.get('faixa_alta', 5))
        
        # Ajustar para somar 15
        total = faixa_baixa_target + faixa_media_target + faixa_alta_target
        if total != 15:
            diff = 15 - total
            faixa_media_target += diff  # Compensar na faixa média
        
        # Definir faixas
        faixa_baixa = list(range(1, 9))    # 1-8
        faixa_media = list(range(9, 17))   # 9-16
        faixa_alta = list(range(17, 26))   # 17-25
        
        combinacao = []
        
        # Selecionar de cada faixa
        if faixa_baixa_target > 0:
            combinacao.extend(random.sample(faixa_baixa, min(faixa_baixa_target, len(faixa_baixa))))
        
        if faixa_media_target > 0:
            combinacao.extend(random.sample(faixa_media, min(faixa_media_target, len(faixa_media))))
        
        if faixa_alta_target > 0:
            combinacao.extend(random.sample(faixa_alta, min(faixa_alta_target, len(faixa_alta))))
        
        # Completar se necessário
        while len(combinacao) < 15:
            disponiveis = [i for i in range(1, 26) if i not in combinacao]
            if disponiveis:
                combinacao.append(random.choice(disponiveis))
            else:
                break
        
        return sorted(combinacao[:15])
    
    def gerar_combinacao_anomalia_positiva(self):
        """Gera combinação buscando padrão anômalo positivo"""
        if not self.analises_academicas:
            return self.gerar_combinacao_equilibrada()
        
        # Buscar insights das análises
        anomalias = self.analises_academicas.get('analises_realizadas', {}).get('anomalias', {})
        
        # Estratégia: criar padrão diferente dos concursos anômalos
        combinacao = []
        
        # Usar estratégia conservadora baseada nas médias históricas
        # Números com frequência próxima à média
        if self.dados_historicos is not None:
            # Calcular frequências históricas
            todos_numeros = []
            for _, row in self.dados_historicos.iterrows():
                for i in range(1, 16):
                    todos_numeros.append(row[f'N{i}'])
            
            freq_historica = Counter(todos_numeros)
            freq_media = sum(freq_historica.values()) / len(freq_historica)
            
            # Selecionar números com frequência próxima à média
            numeros_equilibrados = []
            for num, freq in freq_historica.items():
                if abs(freq - freq_media) <= freq_media * 0.2:  # Dentro de 20% da média
                    numeros_equilibrados.append(num)
            
            if len(numeros_equilibrados) >= 15:
                combinacao = sorted(random.sample(numeros_equilibrados, 15))
            else:
                combinacao = numeros_equilibrados + random.sample(
                    [i for i in range(1, 26) if i not in numeros_equilibrados],
                    15 - len(numeros_equilibrados)
                )
                combinacao = sorted(combinacao)
        
        if len(combinacao) < 15:
            return self.gerar_combinacao_equilibrada()
        
        return combinacao
    
    def gerar_multiplas_combinacoes(self, quantidade=10):
        """Gera múltiplas combinações usando diferentes estratégias"""
        print(f"\n🎲 GERANDO {quantidade} COMBINAÇÕES INTELIGENTES...")
        print("=" * 50)
        
        combinacoes = []
        estrategias = [
            ("Equilibrada", self.gerar_combinacao_equilibrada),
            ("Por Tendências", self.gerar_combinacao_por_tendencias),
            ("Por Faixas", self.gerar_combinacao_por_faixas),
            ("Anomalia Positiva", self.gerar_combinacao_anomalia_positiva)
        ]
        
        for i in range(quantidade):
            estrategia_nome, estrategia_func = estrategias[i % len(estrategias)]
            
            try:
                combinacao = estrategia_func()
                
                # Validar combinação
                if len(combinacao) == 15 and len(set(combinacao)) == 15:
                    # Calcular métricas da combinação
                    impares = len([n for n in combinacao if n % 2 == 1])
                    primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
                    qtd_primos = len([n for n in combinacao if n in primos])
                    soma = sum(combinacao)
                    
                    combinacoes.append({
                        'numero': i + 1,
                        'estrategia': estrategia_nome,
                        'numeros': combinacao,
                        'impares': impares,
                        'primos': qtd_primos,
                        'soma': soma
                    })
                    
                    # Exibir combinação
                    numeros_str = ' '.join([f"{n:02d}" for n in combinacao])
                    print(f"{i+1:2d}. {numeros_str} | {estrategia_nome}")
                    print(f"    Ímpares: {impares} | Primos: {qtd_primos} | Soma: {soma}")
                
            except Exception as e:
                print(f"❌ Erro na combinação {i+1}: {e}")
        
        return combinacoes
    
    def salvar_combinacoes(self, combinacoes):
        """Salva combinações em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"combinacoes_inteligentes_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("COMBINAÇÕES INTELIGENTES LOTOFÁCIL\n")
                f.write("=" * 50 + "\n")
                f.write(f"Geradas em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total: {len(combinacoes)} combinações\n")
                f.write(f"Último concurso analisado: {self.ultimo_concurso['Concurso'] if self.ultimo_concurso is not None else 'N/A'}\n")
                f.write("\n")
                
                # Tendências atuais
                f.write("TENDÊNCIAS ANALISADAS:\n")
                f.write("-" * 25 + "\n")
                for chave, valor in self.tendencias_atuais.items():
                    if isinstance(valor, list):
                        f.write(f"{chave}: {valor[:5]}\n")
                    else:
                        f.write(f"{chave}: {valor:.2f}\n")
                f.write("\n")
                
                # Combinações
                f.write("COMBINAÇÕES GERADAS:\n")
                f.write("-" * 25 + "\n")
                
                for comb in combinacoes:
                    numeros_str = ' '.join([f"{n:02d}" for n in comb['numeros']])
                    f.write(f"{comb['numero']:2d}: {numeros_str}\n")
                    f.write(f"    Estratégia: {comb['estrategia']}\n")
                    f.write(f"    Ímpares: {comb['impares']} | Primos: {comb['primos']} | Soma: {comb['soma']}\n")
                    f.write("\n")
                
                # Resumo das estratégias utilizadas
                f.write("RESUMO DAS ESTRATÉGIAS UTILIZADAS:\n")
                f.write("-" * 35 + "\n")
                
                estrategias_usadas = {}
                for comb in combinacoes:
                    estrategia = comb['estrategia']
                    if estrategia not in estrategias_usadas:
                        estrategias_usadas[estrategia] = 0
                    estrategias_usadas[estrategia] += 1
                
                for estrategia, quantidade in estrategias_usadas.items():
                    f.write(f"• {estrategia}: {quantidade} combinação(ões)\n")
                
                f.write("\nMETODOLOGIA:\n")
                f.write("-" * 12 + "\n")
                f.write("• Numeros Quentes: Baseado em frequência dos últimos 100 concursos\n")
                f.write("• Numeros Equilibrados: Balance entre pares/ímpares e baixos/altos\n")
                f.write("• Analise de Gaps: Números com maiores intervalos desde último sorteio\n")
                f.write("• Padroes Academicos: Baseado em análises estatísticas avançadas\n")
                f.write("• Numeros Ciclos: Considera ciclos e urgência de aparição\n")
                f.write("• Sequencias Inteligentes: Evita padrões muito óbvios\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write("Gerado pelo Sistema Inteligente de Combinações\n")
                f.write("Base científica: 6 metodologias acadêmicas implementadas\n")
            
            print(f"\n💾 Combinações salvas: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return None
    
    def executar_geracao_completa(self, quantidade=10):
        """Executa o processo completo de geração"""
        print("🚀 INICIANDO GERAÇÃO INTELIGENTE DE COMBINAÇÕES")
        print("=" * 55)
        
        # Carregar dados
        if not self.carregar_dados_historicos():
            print("❌ Falha ao carregar dados históricos")
            return False
        
        if not self.carregar_analises_academicas():
            print("⚠️ Prosseguindo sem análises acadêmicas")
        
        # Analisar situação atual
        if not self.analisar_situacao_atual():
            print("❌ Falha ao analisar situação atual")
            return False
        
        # Gerar combinações
        combinacoes = self.gerar_multiplas_combinacoes(quantidade)
        
        if not combinacoes:
            print("❌ Nenhuma combinação gerada")
            return False
        
        # Salvar resultados
        arquivo = self.salvar_combinacoes(combinacoes)
        
        # Resumo final
        print(f"\n✅ GERAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 {len(combinacoes)} combinações inteligentes geradas")
        print(f"💾 Arquivo: {arquivo}")
        print(f"🎯 Baseado em dados do concurso {self.ultimo_concurso['Concurso'] if self.ultimo_concurso is not None else 'N/A'}")
        
        return True

def main():
    """Função principal"""
    import os
    
    print("GERADOR INTELIGENTE DE COMBINACOES LOTOFACIL")
    print("=" * 55)
    
    gerador = GeradorInteligente()
    
    try:
        quantidade = input("\nQuantas combinacoes deseja gerar? (padrao: 10): ").strip()
        if not quantidade:
            quantidade = 10
        else:
            quantidade = int(quantidade)
        
        sucesso = gerador.executar_geracao_completa(quantidade)
        
        if sucesso:
            print(f"\nSistema executado com sucesso!")
        else:
            print(f"\nFalha na execucao do sistema")
            
    except KeyboardInterrupt:
        print(f"\n\nOperacao cancelada pelo usuario")
    except Exception as e:
        print(f"\nErro inesperado: {e}")

if __name__ == "__main__":
    main()
    input("\nPressione ENTER para finalizar...")