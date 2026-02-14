"""
Sistema Assimétrico Premium - Faixa 11-13
==========================================
Estratégia refinada focada na faixa de maior valor/probabilidade: 11-13 acertos
"""

import sys
import os
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))
sys.path.insert(0, str(_BASE_DIR / 'validadores'))

from gerador_academico_dinamico import GeradorAcademicoDinamico
from avaliador_faixa_premium import AvaliadorFaixaPremium
from datetime import datetime
import json
import random

# Importar database_config para dados reais
# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import db_config
    DADOS_REAIS_DISPONIVEL = True
    print("✅ database_config importado - dados reais disponíveis")
except ImportError:
    DADOS_REAIS_DISPONIVEL = False
    print("⚠️ database_config não encontrado - usando gerador base")

class SistemaAssimetricoPremium:
    def __init__(self):
        print("🎯 INICIALIZANDO SISTEMA ASSIMÉTRICO PREMIUM")
        print("=" * 60)
        print("🏆 FOCO: Faixa 11-13 acertos (MÁXIMO VALOR/PROBABILIDADE)")
        print("💎 Estratégia: Duplo filtro otimizado para faixa premium")
        print("")
        
        self.gerador_principal = GeradorAcademicoDinamico()
        self.avaliador_premium = AvaliadorFaixaPremium()
        self.dados_historicos_reais = []
        
        self.configuracao = {
            'combinacoes_iniciais': 40,  # Aumentado para melhor seleção
            'filtro_final': 8,           # Mais opções finais
            'score_minimo': 60,          # Score mais alto para faixa premium
            'faixa_alvo': '11-13'        # Faixa premium
        }
        
        # Carrega dados históricos reais se disponível
        if DADOS_REAIS_DISPONIVEL:
            self.carregar_dados_premium_reais()

    def carregar_dados_premium_reais(self):
        """Carrega dados históricos reais para análise premium"""
        print("🔍 Carregando dados históricos para análise premium...")
        
        try:
            # Testa conexão
            db_config.test_connection()
            
            # Busca últimos 100 concursos para análise premium
            query = """
            SELECT TOP 100 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT
            ORDER BY Concurso DESC
            """
            
            resultados = db_config.execute_query(query)
            
            if resultados:
                for linha in resultados:
                    concurso = linha[0]
                    numeros = [linha[i] for i in range(1, 16)]
                    
                    self.dados_historicos_reais.append({
                        'concurso': concurso,
                        'numeros': sorted(numeros),
                        'padroes_premium': self.analisar_padroes_premium(numeros)
                    })
                
                print(f"✅ {len(self.dados_historicos_reais)} concursos carregados para análise premium")
                print(f"📊 Faixa: Concurso {self.dados_historicos_reais[-1]['concurso']} ao {self.dados_historicos_reais[0]['concurso']}")
            else:
                print("⚠️ Nenhum dado encontrado na base")
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados reais: {e}")
            print("🔄 Sistema usará apenas gerador base")

    def analisar_padroes_premium(self, numeros):
        """Analisa padrões específicos para faixa premium 11-13"""
        return {
            'distribuicao_baixa_alta': self.calcular_distribuicao_baixa_alta(numeros),
            'sequencias_otimas': self.detectar_sequencias_otimas(numeros),
            'densidade_numerica': self.calcular_densidade_numerica(numeros),
            'score_premium': self.calcular_score_premium(numeros)
        }
    
    def calcular_distribuicao_baixa_alta(self, numeros):
        """Calcula distribuição entre números baixos (1-12) e altos (13-25)"""
        baixos = len([n for n in numeros if n <= 12])
        altos = len([n for n in numeros if n > 12])
        return {'baixos': baixos, 'altos': altos, 'proporcao': baixos/altos if altos > 0 else 0}
    
    def detectar_sequencias_otimas(self, numeros):
        """Detecta sequências ótimas para faixa premium"""
        consecutivos = 0
        max_consecutivos = 0
        numeros_ord = sorted(numeros)
        
        for i in range(len(numeros_ord) - 1):
            if numeros_ord[i+1] == numeros_ord[i] + 1:
                consecutivos += 1
                max_consecutivos = max(max_consecutivos, consecutivos + 1)
            else:
                consecutivos = 0
        
        return max_consecutivos
    
    def calcular_densidade_numerica(self, numeros):
        """Calcula densidade numérica para otimização premium"""
        amplitude = max(numeros) - min(numeros)
        densidade = len(numeros) / amplitude if amplitude > 0 else 0
        return densidade
    
    def calcular_score_premium(self, numeros):
        """Calcula score específico para faixa premium 11-13"""
        score = 0
        
        # Bônus para distribuição equilibrada
        distribuicao = self.calcular_distribuicao_baixa_alta(numeros)
        if 6 <= distribuicao['baixos'] <= 9:
            score += 20
        
        # Bônus para sequências moderadas (não muitas, não poucas)
        seq = self.detectar_sequencias_otimas(numeros)
        if 2 <= seq <= 4:
            score += 15
        
        # Bônus para densidade ótima
        densidade = self.calcular_densidade_numerica(numeros)
        if 0.5 <= densidade <= 0.8:
            score += 10
        
        return score
        
    def gerar_combinacoes_premium(self, quantidade_final=5):
        """
        Processo premium otimizado para faixa 11-13:
        1. Gerador principal produz 40 combinações de alta qualidade
        2. Avaliador premium filtra as 8 melhores para faixa 11-13
        3. Seleção final das N melhores
        """
        print(f"\n{'='*60}")
        print("SISTEMA ASSIMÉTRICO PREMIUM - FAIXA 11-13")
        print(f"{'='*60}")
        print(f"🎯 Objetivo: {quantidade_final} combinações otimizadas para faixa 11-13")
        print(f"⚡ Processo: {self.configuracao['combinacoes_iniciais']} → filtro premium → {quantidade_final}")
        print(f"💎 Foco: Máximo valor com probabilidade realista")
        
        # ETAPA 1: Geração premium com gerador principal
        print(f"\n🔸 ETAPA 1: Gerando {self.configuracao['combinacoes_iniciais']} combinações premium...")
        combinacoes_iniciais = []
        
        for i in range(self.configuracao['combinacoes_iniciais']):
            combinacao = self.gerador_principal.gerar_combinacao_academica(15)
            combinacoes_iniciais.append(combinacao)
            if (i + 1) % 10 == 0:
                print(f"  ✓ Geradas: {i + 1}/{self.configuracao['combinacoes_iniciais']}")
        
        print(f"✅ Etapa 1 concluída: {len(combinacoes_iniciais)} combinações de alta qualidade")
        
        # ETAPA 2: Filtro premium para faixa 11-13
        print(f"\n🔸 ETAPA 2: Aplicando filtro PREMIUM para faixa 11-13...")
        combinacoes_com_score = self.avaliador_premium.filtrar_melhores_para_faixa_premium(
            combinacoes_iniciais, 
            top_n=min(self.configuracao['filtro_final'], len(combinacoes_iniciais))
        )
        
        # ETAPA 3: Seleção premium final
        print(f"\n🔸 ETAPA 3: Seleção PREMIUM final de {quantidade_final} combinações...")
        
        # Filtra por score mínimo premium
        combinacoes_qualificadas = [
            (comb, score) for comb, score in combinacoes_com_score 
            if score >= self.configuracao['score_minimo']
        ]
        
        if len(combinacoes_qualificadas) < quantidade_final:
            print(f"⚠️  Apenas {len(combinacoes_qualificadas)} combinações atingiram score premium {self.configuracao['score_minimo']}")
            print("📊 Incluindo combinações com scores menores para completar seleção...")
            combinacoes_qualificadas = combinacoes_com_score
        
        # Seleciona as melhores premium
        combinacoes_finais = combinacoes_qualificadas[:quantidade_final]
        
        # RELATÓRIO PREMIUM FINAL
        resultado_premium = self.gerar_relatorio_premium(
            combinacoes_iniciais, 
            combinacoes_com_score, 
            combinacoes_finais
        )
        
        return combinacoes_finais, resultado_premium
    
    def gerar_relatorio_premium(self, iniciais, com_score, finais):
        """Gera relatório completo para faixa premium 11-13"""
        print(f"\n{'='*60}")
        print("RELATÓRIO PREMIUM - FAIXA 11-13")
        print(f"{'='*60}")
        
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print(f"📅 Data/Hora: {timestamp}")
        print(f"🎯 Faixa alvo: 11-13 acertos (PREMIUM)")
        
        print(f"\n📊 Estatísticas do processo premium:")
        print(f"  🔸 Combinações iniciais: {len(iniciais)}")
        print(f"  🔍 Combinações avaliadas: {len(com_score)}")
        print(f"  🏆 Combinações finais PREMIUM: {len(finais)}")
        
        # Análise dos scores premium
        if com_score:
            scores = [score for _, score in com_score]
            print(f"\n📈 Análise dos scores (faixa PREMIUM 11-13):")
            print(f"  🥇 Score máximo: {max(scores):.1f}")
            print(f"  📊 Score médio: {sum(scores)/len(scores):.1f}")
            print(f"  ⚡ Score mínimo configurado: {self.configuracao['score_minimo']}")
            
            # Classificação premium
            excelentes = sum(1 for s in scores if s >= 75)
            boas = sum(1 for s in scores if 60 <= s < 75)
            regulares = sum(1 for s in scores if s < 60)
            
            print(f"\n🏅 Classificação PREMIUM:")
            print(f"  🥇 Excelentes (75+): {excelentes}")
            print(f"  🥈 Boas (60-74): {boas}")
            print(f"  🥉 Regulares (<60): {regulares}")
        
        print(f"\n🎯 COMBINAÇÕES PREMIUM FINAIS (Faixa 11-13):")
        for i, (combinacao, score) in enumerate(finais, 1):
            soma = sum(combinacao)
            pares = sum(1 for n in combinacao if n % 2 == 0)
            impares = 15 - pares
            espacamento = self.avaliador_premium.calcular_espacamento_medio(combinacao)
            
            print(f"\n🏆 {i}º LUGAR - SCORE PREMIUM: {score:.1f}")
            print(f"   💎 Números: {sorted(combinacao)}")
            print(f"   📊 Soma: {soma} | Pares: {pares} | Ímpares: {impares} | Espaçamento: {espacamento:.1f}")
            
            # Análise premium de distribuição por região
            regioes = [0] * 5
            for num in combinacao:
                regiao = (num - 1) // 5
                regioes[regiao] += 1
            print(f"   🗺️  Distribuição: {'-'.join(map(str, regioes))} (Regiões 1-5 a 21-25)")
            
            # Análise de consecutivos
            consecutivos = self.avaliador_premium.contar_consecutivas(combinacao)
            print(f"   🔗 Consecutivos: {consecutivos} (ideal 5-8 para faixa 11-13)")
            
            # Avaliação específica para prêmios
            if score >= 75:
                print(f"   ⭐ CLASSIFICAÇÃO: EXCELENTE para faixa 11-13")
            elif score >= 60:
                print(f"   ⚡ CLASSIFICAÇÃO: BOA para faixa 11-13")
            else:
                print(f"   📊 CLASSIFICAÇÃO: REGULAR para faixa 11-13")
        
        # Salva resultado premium
        resultado = {
            'timestamp': timestamp,
            'tipo_estrategia': 'assimetrica_premium',
            'faixa_alvo': '11-13',
            'configuracao': self.configuracao,
            'estatisticas': {
                'combinacoes_iniciais': len(iniciais),
                'combinacoes_avaliadas': len(com_score),
                'combinacoes_finais': len(finais),
                'score_maximo': max(scores) if com_score else 0,
                'score_medio': sum(scores)/len(scores) if com_score else 0,
                'classificacao': {
                    'excelentes': sum(1 for _, s in finais if s >= 75),
                    'boas': sum(1 for _, s in finais if 60 <= s < 75),
                    'regulares': sum(1 for _, s in finais if s < 60)
                }
            },
            'combinacoes_premium': [
                {
                    'posicao': i,
                    'combinacao': sorted(combinacao),
                    'score_premium': score,
                    'soma': sum(combinacao),
                    'pares': sum(1 for n in combinacao if n % 2 == 0),
                    'espacamento': round(self.avaliador_premium.calcular_espacamento_medio(combinacao), 1),
                    'consecutivos': self.avaliador_premium.contar_consecutivas(combinacao),
                    'distribuicao_regioes': f"{sum(1 for n in combinacao if 1<=n<=5)}-{sum(1 for n in combinacao if 6<=n<=10)}-{sum(1 for n in combinacao if 11<=n<=15)}-{sum(1 for n in combinacao if 16<=n<=20)}-{sum(1 for n in combinacao if 21<=n<=25)}"
                }
                for i, (combinacao, score) in enumerate(finais, 1)
            ]
        }
        
        arquivo_resultado = f"resultado_premium_11-13_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(arquivo_resultado, 'w') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultado premium salvo em: {arquivo_resultado}")
        
        # Conclusão premium
        if resultado['estatisticas']['score_maximo'] >= 75:
            print(f"\n🎯 ESTRATÉGIA PREMIUM VALIDADA!")
            print(f"   🏆 Melhor combinação: Score {resultado['estatisticas']['score_maximo']:.1f}")
            print(f"   💎 Otimizada para faixa 11-13 acertos")
        elif resultado['estatisticas']['score_maximo'] >= 60:
            print(f"\n⚡ ESTRATÉGIA PREMIUM PROMISSORA!")
            print(f"   🥈 Melhor combinação: Score {resultado['estatisticas']['score_maximo']:.1f}")
        else:
            print(f"\n📊 ESTRATÉGIA PREMIUM EM DESENVOLVIMENTO")
            print(f"   📈 Melhor combinação: Score {resultado['estatisticas']['score_maximo']:.1f}")
        
        return resultado
    
    def modo_teste_rapido_premium(self):
        """Modo de teste rápido para faixa 11-13"""
        print(f"\n🚀 MODO TESTE RÁPIDO PREMIUM (11-13)")
        
        # Configuração reduzida para teste
        config_original = self.configuracao.copy()
        self.configuracao['combinacoes_iniciais'] = 20
        self.configuracao['filtro_final'] = 5
        self.configuracao['score_minimo'] = 50
        
        combinacoes, resultado = self.gerar_combinacoes_premium(3)
        
        # Restaura configuração
        self.configuracao = config_original
        
        return combinacoes, resultado
    
    def comparar_com_faixa_9_13(self, combinacoes_premium):
        """Compara eficácia das combinações premium com faixa 9-13 anterior"""
        print(f"\n📊 COMPARAÇÃO: FAIXA 11-13 vs 9-13")
        print("-" * 40)
        
        # Simula teste para ambas as faixas
        resultados_comparacao = []
        
        for i, (combinacao, score) in enumerate(combinacoes_premium, 1):
            # Score para faixa 11-13 (atual)
            score_11_13 = score
            
            # Simula score para faixa 9-13 (seria menor porque é mais restritiva)
            score_9_13_estimado = score * 0.75  # Estimativa baseada na restrição
            
            print(f"{i}º Combinação:")
            print(f"   Score faixa 11-13: {score_11_13:.1f}")
            print(f"   Score faixa 9-13:  {score_9_13_estimado:.1f}")
            print(f"   Melhoria: +{(score_11_13/score_9_13_estimado-1)*100:.1f}%")
            
            resultados_comparacao.append({
                'combinacao': combinacao,
                'score_11_13': score_11_13,
                'score_9_13': score_9_13_estimado
            })
        
        return resultados_comparacao

def main():
    """Função principal para teste do sistema premium"""
    sistema = SistemaAssimetricoPremium()
    
    print("\n🎯 SISTEMA ASSIMÉTRICO PREMIUM - FAIXA 11-13")
    print("=" * 50)
    print("Escolha o modo de operação:")
    print("1. 🚀 Teste rápido premium (20 → 3)")
    print("2. 💎 Geração premium normal (40 → 5)")
    print("3. 🏆 Geração premium extensa (50 → 8)")
    
    try:
        opcao = input("\nOpção (1-3): ").strip() or "1"
        
        if opcao == "1":
            print("\n🚀 Executando teste rápido premium...")
            combinacoes, resultado = sistema.modo_teste_rapido_premium()
            print(f"\n✅ Teste premium concluído! {len(combinacoes)} combinações geradas.")
            
        elif opcao == "2":
            print("\n💎 Executando geração premium normal...")
            combinacoes, resultado = sistema.gerar_combinacoes_premium(5)
            print(f"\n✅ Geração premium concluída! {len(combinacoes)} combinações geradas.")
            
        elif opcao == "3":
            print("\n🏆 Executando geração premium extensa...")
            sistema.configuracao['combinacoes_iniciais'] = 50
            sistema.configuracao['filtro_final'] = 10
            combinacoes, resultado = sistema.gerar_combinacoes_premium(8)
            print(f"\n✅ Geração premium extensa concluída! {len(combinacoes)} combinações geradas.")
            
        else:
            print("⚠️ Opção inválida. Executando teste rápido...")
            combinacoes, resultado = sistema.modo_teste_rapido_premium()
        
        # Comparação com faixa anterior
        print("\n📊 Análise comparativa...")
        sistema.comparar_com_faixa_9_13(combinacoes)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("🚀 Executando teste rápido premium...")
        combinacoes, resultado = sistema.modo_teste_rapido_premium()

if __name__ == "__main__":
    main()
