#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALISADOR DE CORRELAÇÃO ENTRE PARÂMETROS E POSIÇÕES
Identifica posições específicas (N1-N15) que atuam como "divisores" 
baseado na relação entre maior_que, menor_que e igual_ao_ultimo.

Conceito: Descobrir qual posição é o "termômetro" que indica
se a distribuição será alta ou baixa.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalisadorCorrelacaoPosicoes:
    """Analisa correlações entre parâmetros e posições específicas"""
    
    def __init__(self):
        self.dados_historicos = []
        self.padroes_descobertos = {}
        self.correlacoes_posicoes = {}
        
    def carregar_dados_simulados(self, quantidade=100):
        """Carrega dados históricos simulados para análise"""
        import random
        
        logger.info(f"Carregando {quantidade} concursos simulados...")
        
        for concurso in range(3400, 3400 + quantidade):
            # Simula resultado de 15 números ordenados
            numeros = sorted(random.sample(range(1, 26), 15))
            
            # Calcula parâmetros baseados no concurso anterior
            if concurso > 3400:
                # Simula concurso anterior
                anterior = sorted(random.sample(range(1, 26), 15))
                
                maior_que = sum(1 for n in numeros if n > max(anterior))
                menor_que = sum(1 for n in numeros if n < min(anterior))
                igual = sum(1 for n in numeros if n in anterior)
                
                # Garante que soma = 15 (alguns números podem não se encaixar perfeitamente)
                diferenca = 15 - (maior_que + menor_que + igual)
                if diferenca > 0:
                    igual += diferenca
                elif diferenca < 0:
                    if maior_que >= abs(diferenca):
                        maior_que += diferenca
                    else:
                        menor_que += diferenca
            else:
                # Primeiro concurso: valores aleatórios que somem 15
                total = 15
                maior_que = random.randint(3, 8)
                menor_que = random.randint(3, 8)
                igual = total - maior_que - menor_que
                
                if igual < 0:
                    igual = random.randint(1, 4)
                    maior_que = random.randint(1, 8)
                    menor_que = 15 - maior_que - igual
            
            # Dados do concurso
            dados_concurso = {
                'concurso': concurso,
                'numeros': numeros,
                'maior_que': maior_que,
                'menor_que': menor_que,
                'igual': igual,
                'N1': numeros[0],
                'N2': numeros[1],
                'N3': numeros[2],
                'N4': numeros[3],
                'N5': numeros[4],
                'N6': numeros[5],
                'N7': numeros[6],
                'N8': numeros[7],
                'N9': numeros[8],
                'N10': numeros[9],
                'N11': numeros[10],
                'N12': numeros[11],
                'N13': numeros[12],
                'N14': numeros[13],
                'N15': numeros[14],
                'soma_total': sum(numeros)
            }
            
            self.dados_historicos.append(dados_concurso)
        
        logger.info(f"✅ {len(self.dados_historicos)} concursos carregados")
        return True
    
    def analisar_padroes_correlacao(self):
        """Analisa padrões de correlação entre parâmetros e posições"""
        logger.info("🔍 Analisando padrões de correlação...")
        
        # Separar concursos por padrão de parâmetros
        padrao_menor_maior = []  # menor_que > igual > maior_que
        padrao_maior_menor = []  # maior_que > menor_que > igual
        padrao_equilibrado = []  # outros padrões
        
        for dados in self.dados_historicos:
            maior = dados['maior_que']
            menor = dados['menor_que']
            igual = dados['igual']
            
            if menor > igual and igual > maior:
                padrao_menor_maior.append(dados)
            elif maior > menor and menor > igual:
                padrao_maior_menor.append(dados)
            else:
                padrao_equilibrado.append(dados)
        
        logger.info(f"📊 Padrões encontrados:")
        logger.info(f"   Menor > Igual > Maior: {len(padrao_menor_maior)} concursos")
        logger.info(f"   Maior > Menor > Igual: {len(padrao_maior_menor)} concursos")
        logger.info(f"   Outros padrões: {len(padrao_equilibrado)} concursos")
        
        # Analisar cada posição para cada padrão
        self.padroes_descobertos = {
            'padrao_menor_maior': self._analisar_posicoes_por_padrao(padrao_menor_maior, "Menor > Igual > Maior"),
            'padrao_maior_menor': self._analisar_posicoes_por_padrao(padrao_maior_menor, "Maior > Menor > Igual"),
            'padrao_equilibrado': self._analisar_posicoes_por_padrao(padrao_equilibrado, "Outros Padrões")
        }
        
        return self.padroes_descobertos
    
    def _analisar_posicoes_por_padrao(self, dados_padrao: List[Dict], nome_padrao: str) -> Dict:
        """Analisa estatísticas de cada posição para um padrão específico"""
        if not dados_padrao:
            return {}
        
        posicoes_stats = {}
        
        for pos in range(1, 16):  # N1 a N15
            coluna = f'N{pos}'
            valores = [d[coluna] for d in dados_padrao if coluna in d]
            
            if valores:
                posicoes_stats[coluna] = {
                    'media': round(statistics.mean(valores), 2),
                    'mediana': statistics.median(valores),
                    'moda': statistics.mode(valores) if valores else None,
                    'min': min(valores),
                    'max': max(valores),
                    'range': max(valores) - min(valores),
                    'desvio_padrao': round(statistics.stdev(valores) if len(valores) > 1 else 0, 2),
                    'quartil_25': round(statistics.quantiles(valores, n=4)[0], 1) if len(valores) >= 4 else min(valores),
                    'quartil_75': round(statistics.quantiles(valores, n=4)[2], 1) if len(valores) >= 4 else max(valores),
                    'total_amostras': len(valores)
                }
        
        # Identificar posições com maior variação (potenciais divisores)
        posicoes_ordenadas = []
        for pos, stats in posicoes_stats.items():
            variacao_coef = stats['desvio_padrao'] / stats['media'] if stats['media'] > 0 else 0
            posicoes_ordenadas.append((pos, variacao_coef, stats))
        
        # Ordenar por coeficiente de variação (maior variação = maior importância como divisor)
        posicoes_ordenadas.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'nome_padrao': nome_padrao,
            'total_concursos': len(dados_padrao),
            'posicoes_stats': posicoes_stats,
            'posicoes_mais_variaveis': posicoes_ordenadas[:5],  # Top 5 mais variáveis
            'posicao_divisor_principal': posicoes_ordenadas[0][0] if posicoes_ordenadas else None
        }
    
    def descobrir_correlacoes_especificas(self):
        """Descobre correlações específicas entre parâmetros e posições centrais"""
        logger.info("🎯 Descobrindo correlações específicas...")
        
        correlacoes = {}
        
        # Analisar posições centrais (N7-N10) como potenciais divisores
        posicoes_centrais = ['N7', 'N8', 'N9', 'N10']
        
        for posicao in posicoes_centrais:
            correlacoes[posicao] = self._analisar_correlacao_posicao(posicao)
        
        # Encontrar a posição com correlação mais forte
        melhor_correlacao = None
        melhor_score = 0
        
        for pos, dados in correlacoes.items():
            score = dados.get('score_correlacao', 0)
            if score > melhor_score:
                melhor_score = score
                melhor_correlacao = pos
        
        self.correlacoes_posicoes = {
            'correlacoes_por_posicao': correlacoes,
            'posicao_divisor_principal': melhor_correlacao,
            'score_maximo': melhor_score
        }
        
        return self.correlacoes_posicoes
    
    def _analisar_correlacao_posicao(self, posicao: str) -> Dict:
        """Analisa correlação específica de uma posição com os parâmetros"""
        
        # Separar dados por tipo de dominância de parâmetro
        quando_menor_domina = []  # menor_que é o maior dos 3
        quando_maior_domina = []  # maior_que é o maior dos 3
        
        for dados in self.dados_historicos:
            maior = dados['maior_que']
            menor = dados['menor_que']
            igual = dados['igual']
            valor_posicao = dados[posicao]
            
            if menor >= maior and menor >= igual:
                quando_menor_domina.append(valor_posicao)
            elif maior >= menor and maior >= igual:
                quando_maior_domina.append(valor_posicao)
        
        # Calcular estatísticas
        stats_menor_domina = {}
        stats_maior_domina = {}
        
        if quando_menor_domina:
            stats_menor_domina = {
                'media': round(statistics.mean(quando_menor_domina), 2),
                'mediana': statistics.median(quando_menor_domina),
                'min': min(quando_menor_domina),
                'max': max(quando_menor_domina),
                'amostras': len(quando_menor_domina)
            }
        
        if quando_maior_domina:
            stats_maior_domina = {
                'media': round(statistics.mean(quando_maior_domina), 2),
                'mediana': statistics.median(quando_maior_domina),
                'min': min(quando_maior_domina),
                'max': max(quando_maior_domina),
                'amostras': len(quando_maior_domina)
            }
        
        # Calcular diferença significativa (score de correlação)
        score_correlacao = 0
        diferenca_medias = 0
        
        if stats_menor_domina and stats_maior_domina:
            diferenca_medias = abs(stats_menor_domina['media'] - stats_maior_domina['media'])
            score_correlacao = diferenca_medias * min(stats_menor_domina['amostras'], stats_maior_domina['amostras'])
        
        return {
            'posicao': posicao,
            'quando_menor_domina': stats_menor_domina,
            'quando_maior_domina': stats_maior_domina,
            'diferenca_medias': round(diferenca_medias, 2),
            'score_correlacao': round(score_correlacao, 2),
            'interpretacao': self._interpretar_correlacao(stats_menor_domina, stats_maior_domina, posicao)
        }
    
    def _interpretar_correlacao(self, stats_menor: Dict, stats_maior: Dict, posicao: str) -> str:
        """Interpreta a correlação encontrada"""
        if not stats_menor or not stats_maior:
            return f"Dados insuficientes para {posicao}"
        
        media_menor = stats_menor['media']
        media_maior = stats_maior['media']
        
        diferenca = abs(media_menor - media_maior)
        
        if diferenca < 1:
            return f"{posicao}: Pouca correlação (diferença: {diferenca:.1f})"
        elif media_menor > media_maior:
            return f"{posicao}: Quando 'menor_que' domina → {posicao} ≥ {media_menor:.1f} | Quando 'maior_que' domina → {posicao} ≤ {media_maior:.1f}"
        else:
            return f"{posicao}: Quando 'menor_que' domina → {posicao} ≤ {media_menor:.1f} | Quando 'maior_que' domina → {posicao} ≥ {media_maior:.1f}"
    
    def gerar_relatorio_completo(self) -> str:
        """Gera relatório completo das análises"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"relatorio_correlacao_posicoes_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("🎯 RELATÓRIO DE CORRELAÇÃO: PARÂMETROS × POSIÇÕES\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"📊 Total de concursos analisados: {len(self.dados_historicos)}\n\n")
            
            # Padrões descobertos
            f.write("🔍 PADRÕES DESCOBERTOS POR TIPO:\n")
            f.write("-" * 50 + "\n")
            
            for chave, dados in self.padroes_descobertos.items():
                if dados:
                    f.write(f"\n📋 {dados['nome_padrao']}:\n")
                    f.write(f"   Total de concursos: {dados['total_concursos']}\n")
                    
                    if dados['posicao_divisor_principal']:
                        f.write(f"   🎯 Posição divisor principal: {dados['posicao_divisor_principal']}\n")
                    
                    f.write(f"   📊 Top 3 posições mais variáveis:\n")
                    for i, (pos, coef_var, stats) in enumerate(dados['posicoes_mais_variaveis'][:3], 1):
                        f.write(f"      {i}. {pos}: média {stats['media']:.1f}, desvio {stats['desvio_padrao']:.1f}\n")
            
            # Correlações específicas
            if self.correlacoes_posicoes:
                f.write(f"\n🎯 CORRELAÇÕES ESPECÍFICAS (POSIÇÕES CENTRAIS):\n")
                f.write("-" * 50 + "\n")
                
                if self.correlacoes_posicoes['posicao_divisor_principal']:
                    f.write(f"🏆 POSIÇÃO DIVISOR PRINCIPAL: {self.correlacoes_posicoes['posicao_divisor_principal']}\n")
                    f.write(f"📊 Score máximo: {self.correlacoes_posicoes['score_maximo']:.1f}\n\n")
                
                for pos, dados in self.correlacoes_posicoes['correlacoes_por_posicao'].items():
                    f.write(f"{pos}:\n")
                    f.write(f"   {dados['interpretacao']}\n")
                    f.write(f"   Score correlação: {dados['score_correlacao']:.1f}\n\n")
            
            # Conclusões e recomendações
            f.write("💡 CONCLUSÕES E RECOMENDAÇÕES:\n")
            f.write("-" * 50 + "\n")
            
            if self.correlacoes_posicoes and self.correlacoes_posicoes['posicao_divisor_principal']:
                pos_principal = self.correlacoes_posicoes['posicao_divisor_principal']
                f.write(f"1. A posição {pos_principal} demonstrou ser o melhor 'divisor' entre os padrões\n")
                f.write(f"2. Use {pos_principal} como referência para identificar se a distribuição será alta ou baixa\n")
                f.write(f"3. Monitore a relação entre maior_que/menor_que e o valor de {pos_principal}\n")
                
                # Buscar dados específicos da posição principal
                if pos_principal in self.correlacoes_posicoes['correlacoes_por_posicao']:
                    dados_principal = self.correlacoes_posicoes['correlacoes_por_posicao'][pos_principal]
                    f.write(f"4. Regra prática: {dados_principal['interpretacao']}\n")
            else:
                f.write("1. Análise inconclusiva - mais dados necessários\n")
                f.write("2. Considere expandir a amostra de concursos\n")
                f.write("3. Verifique se os padrões são consistentes ao longo do tempo\n")
            
            f.write(f"\n📁 Dados detalhados salvos em formato JSON para análise posterior\n")
        
        # Salvar dados em JSON para análise posterior
        dados_json = {
            'timestamp': timestamp,
            'total_concursos': len(self.dados_historicos),
            'padroes_descobertos': self.padroes_descobertos,
            'correlacoes_posicoes': self.correlacoes_posicoes,
            'dados_historicos': self.dados_historicos
        }
        
        nome_json = f"dados_correlacao_posicoes_{timestamp}.json"
        with open(nome_json, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Relatório salvo: {nome_arquivo}")
        logger.info(f"✅ Dados JSON salvos: {nome_json}")
        
        return nome_arquivo
    
    def executar_analise_completa(self):
        """Executa análise completa de correlações"""
        logger.info("🚀 Iniciando análise completa de correlações...")
        
        print("🎯 ANALISADOR DE CORRELAÇÃO PARÂMETROS × POSIÇÕES")
        print("=" * 60)
        print("🔍 Descobrindo qual posição (N1-N15) atua como 'divisor'")
        print("📊 Baseado na relação entre maior_que, menor_que e igual_ao_ultimo")
        print()
        
        # 1. Carregar dados
        if not self.carregar_dados_simulados(150):
            print("❌ Erro ao carregar dados")
            return None
        
        # 2. Analisar padrões
        print("🔍 Analisando padrões de correlação...")
        self.analisar_padroes_correlacao()
        
        # 3. Descobrir correlações específicas
        print("🎯 Descobrindo correlações específicas...")
        self.descobrir_correlacoes_especificas()
        
        # 4. Gerar relatório
        print("📝 Gerando relatório completo...")
        arquivo_relatorio = self.gerar_relatorio_completo()
        
        # 5. Mostrar resultados principais
        print("\n🏆 RESULTADOS PRINCIPAIS:")
        print("-" * 40)
        
        if self.correlacoes_posicoes and self.correlacoes_posicoes['posicao_divisor_principal']:
            pos_principal = self.correlacoes_posicoes['posicao_divisor_principal']
            score = self.correlacoes_posicoes['score_maximo']
            
            print(f"🎯 POSIÇÃO DIVISOR PRINCIPAL: {pos_principal}")
            print(f"📊 Score de correlação: {score:.1f}")
            
            if pos_principal in self.correlacoes_posicoes['correlacoes_por_posicao']:
                dados = self.correlacoes_posicoes['correlacoes_por_posicao'][pos_principal]
                print(f"💡 Interpretação: {dados['interpretacao']}")
                
                print(f"\n📋 REGRA PRÁTICA DESCOBERTA:")
                if dados['quando_menor_domina'] and dados['quando_maior_domina']:
                    menor_media = dados['quando_menor_domina']['media']
                    maior_media = dados['quando_maior_domina']['media']
                    
                    if menor_media > maior_media:
                        print(f"   • Quando 'menor_que' for dominante → Espere {pos_principal} ≥ {menor_media:.0f}")
                        print(f"   • Quando 'maior_que' for dominante → Espere {pos_principal} ≤ {maior_media:.0f}")
                    else:
                        print(f"   • Quando 'menor_que' for dominante → Espere {pos_principal} ≤ {menor_media:.0f}")
                        print(f"   • Quando 'maior_que' for dominante → Espere {pos_principal} ≥ {maior_media:.0f}")
        else:
            print("❌ Nenhuma correlação significativa encontrada")
            print("💡 Sugere-se aumentar a amostra ou refinar os critérios")
        
        print(f"\n📁 Relatório completo: {arquivo_relatorio}")
        print("✅ Análise de correlação concluída!")
        
        return arquivo_relatorio

def main():
    """Função principal"""
    analisador = AnalisadorCorrelacaoPosicoes()
    analisador.executar_analise_completa()

if __name__ == "__main__":
    main()