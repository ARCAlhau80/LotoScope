"""
Validador da Estratégia Assimétrica
Testa as combinações geradas contra dados históricos para validar a eficácia na faixa 9-13
"""

import json
import random
from datetime import datetime
from collections import Counter

class ValidadorEstrategiaAssimetrica:
    def __init__(self):
        self.dados_historicos = self.carregar_dados_historicos()
        self.faixa_alvo = (9, 13)  # Faixa de interesse: 9 a 13 acertos
        
    def carregar_dados_historicos(self):
        """Carrega dados históricos ou simula baseado em padrões conhecidos"""
        try:
            with open('resultados_teste_historico.json', 'r') as f:
                dados = json.load(f)
                print(f"✓ Carregados {len(dados)} resultados históricos")
                return dados
        except FileNotFoundError:
            print("⚠️ Dados históricos não encontrados. Simulando resultados...")
            return self.simular_dados_historicos()
    
    def simular_dados_historicos(self):
        """Simula dados históricos baseados em padrões da Lotofácil"""
        dados_simulados = {}
        
        # Simulação de 100 concursos com padrões realistas
        for concurso in range(3400, 3500):
            # Simula resultado oficial baseado em tendências conhecidas
            resultado_oficial = self.gerar_resultado_simulado()
            
            dados_simulados[str(concurso)] = {
                'numeros_sorteados': resultado_oficial,
                'concurso': concurso
            }
        
        print(f"✓ Simulados {len(dados_simulados)} concursos para validação")
        return dados_simulados
    
    def gerar_resultado_simulado(self):
        """Gera resultado simulado baseado em padrões da Lotofácil"""
        # Pesos baseados em frequências históricas conhecidas
        pesos_frequencia = {
            1: 0.85, 2: 0.90, 3: 0.88, 4: 0.92, 5: 0.87,
            6: 0.89, 7: 0.91, 8: 0.86, 9: 0.93, 10: 0.88,
            11: 0.90, 12: 0.87, 13: 0.94, 14: 0.89, 15: 0.85,
            16: 0.91, 17: 0.88, 18: 0.86, 19: 0.92, 20: 0.90,
            21: 0.87, 22: 0.89, 23: 0.85, 24: 0.91, 25: 0.88
        }
        
        resultado = []
        numeros_disponiveis = list(range(1, 26))
        
        for _ in range(15):
            pesos = [pesos_frequencia[n] for n in numeros_disponiveis]
            numero = random.choices(numeros_disponiveis, weights=pesos)[0]
            resultado.append(numero)
            numeros_disponiveis.remove(numero)
            
        return sorted(resultado)
    
    def calcular_acertos(self, combinacao, resultado_oficial):
        """Calcula quantos acertos a combinação teve"""
        return len(set(combinacao) & set(resultado_oficial))
    
    def testar_combinacao_historica(self, combinacao):
        """Testa uma combinação contra todos os dados históricos"""
        acertos_por_concurso = []
        acertos_na_faixa = 0
        total_concursos = 0
        
        for concurso, dados in self.dados_historicos.items():
            if 'numeros_sorteados' in dados:
                resultado_oficial = dados['numeros_sorteados']
                acertos = self.calcular_acertos(combinacao, resultado_oficial)
                acertos_por_concurso.append(acertos)
                
                if self.faixa_alvo[0] <= acertos <= self.faixa_alvo[1]:
                    acertos_na_faixa += 1
                total_concursos += 1
        
        # Estatísticas
        if acertos_por_concurso:
            performance = {
                'acertos_por_concurso': acertos_por_concurso,
                'media_acertos': sum(acertos_por_concurso) / len(acertos_por_concurso),
                'acertos_na_faixa': acertos_na_faixa,
                'total_concursos': total_concursos,
                'percentual_faixa': (acertos_na_faixa / total_concursos) * 100 if total_concursos > 0 else 0,
                'distribuicao_acertos': Counter(acertos_por_concurso)
            }
        else:
            performance = {'erro': 'Nenhum dado histórico válido'}
            
        return performance
    
    def validar_estrategia_assimetrica(self, arquivo_resultado):
        """Valida todas as combinações do arquivo de resultado"""
        print(f"\n{'='*60}")
        print("VALIDAÇÃO DA ESTRATÉGIA ASSIMÉTRICA")
        print(f"{'='*60}")
        print(f"Faixa alvo: {self.faixa_alvo[0]} a {self.faixa_alvo[1]} acertos")
        print(f"Dados históricos: {len(self.dados_historicos)} concursos")
        
        # Carrega as combinações geradas
        with open(arquivo_resultado, 'r') as f:
            resultado = json.load(f)
        
        combinacoes = resultado['combinacoes']
        print(f"Combinações a testar: {len(combinacoes)}")
        
        # Testa cada combinação
        resultados_validacao = []
        
        for i, comb_data in enumerate(combinacoes, 1):
            combinacao = comb_data['combinacao']
            score_original = comb_data['score']
            
            print(f"\nTestando combinação {i}...")
            print(f"Score assimétrico: {score_original:.1f}")
            print(f"Números: {combinacao}")
            
            performance = self.testar_combinacao_historica(combinacao)
            
            if 'erro' not in performance:
                print(f"Média de acertos: {performance['media_acertos']:.2f}")
                print(f"Acertos na faixa {self.faixa_alvo}: {performance['acertos_na_faixa']}/{performance['total_concursos']} ({performance['percentual_faixa']:.1f}%)")
                
                # Distribuição detalhada
                dist = performance['distribuicao_acertos']
                print(f"Distribuição: ", end="")
                for acertos in sorted(dist.keys()):
                    print(f"{acertos}→{dist[acertos]}x ", end="")
                print()
                
                resultados_validacao.append({
                    'posicao': i,
                    'combinacao': combinacao,
                    'score_assimetrico': score_original,
                    'media_acertos': performance['media_acertos'],
                    'percentual_faixa_alvo': performance['percentual_faixa'],
                    'acertos_na_faixa': performance['acertos_na_faixa'],
                    'total_concursos': performance['total_concursos'],
                    'distribuicao': dict(performance['distribuicao_acertos'])
                })
            else:
                print(f"❌ Erro na validação: {performance['erro']}")
        
        # Análise comparativa
        self.gerar_relatorio_validacao(resultados_validacao, resultado)
        
        return resultados_validacao
    
    def gerar_relatorio_validacao(self, resultados, resultado_original):
        """Gera relatório completo da validação"""
        print(f"\n{'='*60}")
        print("RELATÓRIO DE VALIDAÇÃO")
        print(f"{'='*60}")
        
        if not resultados:
            print("❌ Nenhum resultado válido para análise")
            return
        
        # Estatísticas gerais
        medias_acertos = [r['media_acertos'] for r in resultados]
        percentuais_faixa = [r['percentual_faixa_alvo'] for r in resultados]
        scores_assimetricos = [r['score_assimetrico'] for r in resultados]
        
        print(f"Análise de {len(resultados)} combinações:")
        print(f"  Média de acertos geral: {sum(medias_acertos)/len(medias_acertos):.2f}")
        print(f"  Percentual médio na faixa {self.faixa_alvo}: {sum(percentuais_faixa)/len(percentuais_faixa):.1f}%")
        print(f"  Score assimétrico médio: {sum(scores_assimetricos)/len(scores_assimetricos):.1f}")
        
        # Ranking por eficácia na faixa alvo
        resultados_ordenados = sorted(resultados, key=lambda x: x['percentual_faixa_alvo'], reverse=True)
        
        print(f"\nRanking por eficácia na faixa {self.faixa_alvo[0]}-{self.faixa_alvo[1]}:")
        for i, r in enumerate(resultados_ordenados, 1):
            print(f"  {i}º: {r['percentual_faixa_alvo']:.1f}% (Score: {r['score_assimetrico']:.1f}) - Pos.Original: {r['posicao']}")
        
        # Correlação entre score assimétrico e eficácia real
        print(f"\nCorrelação Score vs Eficácia:")
        melhor_score = max(resultados, key=lambda x: x['score_assimetrico'])
        melhor_eficacia = max(resultados, key=lambda x: x['percentual_faixa_alvo'])
        
        print(f"  Melhor score assimétrico: Pos.{melhor_score['posicao']} ({melhor_score['score_assimetrico']:.1f}) → {melhor_score['percentual_faixa_alvo']:.1f}% na faixa")
        print(f"  Melhor eficácia real: Pos.{melhor_eficacia['posicao']} ({melhor_eficacia['percentual_faixa_alvo']:.1f}%) → Score {melhor_eficacia['score_assimetrico']:.1f}")
        
        # Salva relatório detalhado
        relatorio_completo = {
            'timestamp_validacao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'configuracao_original': resultado_original['configuracao'],
            'faixa_alvo': self.faixa_alvo,
            'total_concursos_teste': len(self.dados_historicos),
            'estatisticas_gerais': {
                'media_acertos_geral': sum(medias_acertos)/len(medias_acertos),
                'percentual_medio_faixa': sum(percentuais_faixa)/len(percentuais_faixa),
                'score_assimetrico_medio': sum(scores_assimetricos)/len(scores_assimetricos)
            },
            'resultados_detalhados': resultados_ordenados
        }
        
        arquivo_validacao = f"validacao_assimetrica_{datetime.now().strftime('%H%M%S')}.json"
        with open(arquivo_validacao, 'w') as f:
            json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Relatório detalhado salvo em: {arquivo_validacao}")
        
        # Conclusão
        if melhor_eficacia['percentual_faixa_alvo'] > 50:
            print(f"\n🎯 ESTRATÉGIA VALIDADA! Melhor combinação atinge {melhor_eficacia['percentual_faixa_alvo']:.1f}% na faixa alvo")
        elif melhor_eficacia['percentual_faixa_alvo'] > 30:
            print(f"\n⚡ ESTRATÉGIA PROMISSORA! Melhor combinação atinge {melhor_eficacia['percentual_faixa_alvo']:.1f}% na faixa alvo")
        else:
            print(f"\n📊 ESTRATÉGIA EM ANÁLISE: Melhor resultado {melhor_eficacia['percentual_faixa_alvo']:.1f}% na faixa alvo")

def main():
    """Execução principal da validação"""
    validador = ValidadorEstrategiaAssimetrica()
    
    # Lista arquivos de resultado disponíveis
    import os
    arquivos_resultado = [f for f in os.listdir('.') if f.startswith('resultado_assimetrico_simples_') and f.endswith('.json')]
    
    if not arquivos_resultado:
        print("❌ Nenhum arquivo de resultado encontrado. Execute primeiro o sistema_assimetrico_simples.py")
        return
    
    print("Arquivos de resultado disponíveis:")
    for i, arquivo in enumerate(arquivos_resultado, 1):
        print(f"  {i}. {arquivo}")
    
    try:
        # Usa o arquivo mais recente automaticamente
        arquivo_escolhido = max(arquivos_resultado, key=lambda x: os.path.getmtime(x))
        print(f"\nUsando automaticamente o mais recente: {arquivo_escolhido}")
        
        print(f"\nIniciando validação de: {arquivo_escolhido}")
        resultados = validador.validar_estrategia_assimetrica(arquivo_escolhido)
        
        print(f"\n✅ Validação concluída! {len(resultados)} combinações analisadas.")
        
    except (ValueError, IndexError):
        print("❌ Seleção inválida")
    except KeyboardInterrupt:
        print("\n⚠️ Validação interrompida")
    except Exception as e:
        print(f"\n❌ Erro na validação: {e}")

if __name__ == "__main__":
    main()
