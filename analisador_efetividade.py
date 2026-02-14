#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 ANALISADOR DE EFETIVIDADE DO AUTO-TREINO
===========================================
Analisa a efetividade do aprendizado e performance real do sistema
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter

class AnalisadorEfetividade:
    """Analisa efetividade do sistema de auto-treino"""
    
    def __init__(self):
        self.conhecimentos = []
        self.carregar_conhecimentos()
    
    def carregar_conhecimentos(self):
        """Carrega todos os arquivos de conhecimento"""
        arquivos = [f for f in os.listdir('.') if f.startswith('conhecimento_')]
        
        for arquivo in sorted(arquivos):
            try:
                with open(arquivo, 'r') as f:
                    dados = json.load(f)
                    self.conhecimentos.append({
                        'arquivo': arquivo,
                        'dados': dados,
                        'timestamp': arquivo.split('_')[-1].replace('.json', '')
                    })
                print(f"✅ Carregado: {arquivo}")
            except Exception as e:
                print(f"❌ Erro ao carregar {arquivo}: {e}")
    
    def analisar_acertos_15(self):
        """Analisa quantas vezes o sistema acertou 15 números"""
        print("\n🎯 ANÁLISE DE ACERTOS PERFEITOS (15/15)")
        print("="*60)
        
        total_tentativas = 0
        acertos_15 = 0
        acertos_14 = 0
        acertos_13_plus = 0
        
        melhor_resultado = 0
        historico_acertos = []
        
        for conhecimento in self.conhecimentos:
            dados = conhecimento['dados']
            
            # Analisa padrões vencedores
            if 'padroes_vencedores' in dados:
                for padrao in dados['padroes_vencedores']:
                    acertos = padrao.get('acertos', 0)
                    historico_acertos.append(acertos)
                    total_tentativas += 1
                    
                    if acertos == 15:
                        acertos_15 += 1
                    elif acertos == 14:
                        acertos_14 += 1
                    elif acertos >= 13:
                        acertos_13_plus += 1
                    
                    if acertos > melhor_resultado:
                        melhor_resultado = acertos
        
        # Estatísticas
        if total_tentativas > 0:
            taxa_15 = (acertos_15 / total_tentativas) * 100
            taxa_14_plus = ((acertos_15 + acertos_14) / total_tentativas) * 100
            taxa_13_plus = (acertos_13_plus / total_tentativas) * 100
            media_acertos = sum(historico_acertos) / len(historico_acertos) if historico_acertos else 0
        else:
            taxa_15 = taxa_14_plus = taxa_13_plus = media_acertos = 0
        
        print(f"Total de tentativas analisadas: {total_tentativas:,}")
        print(f"Melhor resultado obtido: {melhor_resultado}/15")
        print(f"")
        print(f"🏆 ACERTOS 15/15: {acertos_15} ({taxa_15:.2f}%)")
        print(f"🥈 ACERTOS 14+/15: {acertos_15 + acertos_14} ({taxa_14_plus:.2f}%)")
        print(f"🥉 ACERTOS 13+/15: {acertos_13_plus} ({taxa_13_plus:.2f}%)")
        print(f"📊 Média de acertos: {media_acertos:.2f}")
        
        return {
            'total_tentativas': total_tentativas,
            'acertos_15': acertos_15,
            'acertos_14': acertos_14,
            'acertos_13_plus': acertos_13_plus,
            'melhor_resultado': melhor_resultado,
            'media_acertos': media_acertos,
            'historico': historico_acertos
        }
    
    def analisar_evolucao_aprendizado(self):
        """Analisa como o sistema evoluiu ao longo do tempo"""
        print("\n📈 EVOLUÇÃO DO APRENDIZADO")
        print("="*60)
        
        evolucao = []
        
        for i, conhecimento in enumerate(self.conhecimentos):
            dados = conhecimento['dados']
            timestamp = conhecimento['timestamp']
            
            # Conta números eficazes descobertos
            nums_eficazes = len(dados.get('numeros_mais_eficazes', {}))
            padroes = len(dados.get('padroes_vencedores', []))
            
            # Calcula score médio dos números eficazes
            if 'numeros_mais_eficazes' in dados:
                scores = list(dados['numeros_mais_eficazes'].values())
                score_medio = sum(scores) / len(scores) if scores else 0
                score_max = max(scores) if scores else 0
            else:
                score_medio = score_max = 0
            
            evolucao.append({
                'sessao': i + 1,
                'timestamp': timestamp,
                'numeros_eficazes': nums_eficazes,
                'padroes_descobertos': padroes,
                'score_medio': score_medio,
                'score_max': score_max
            })
            
            print(f"Sessão {i+1:2d}: {nums_eficazes:2d} números eficazes, "
                  f"{padroes:2d} padrões, score médio: {score_medio:.1f}")
        
        return evolucao
    
    def identificar_numeros_mais_eficazes(self):
        """Identifica os números mais eficazes consolidados"""
        print("\n🔢 NÚMEROS MAIS EFICAZES CONSOLIDADOS")
        print("="*60)
        
        contador_numeros = defaultdict(list)
        
        # Consolida scores de todos os conhecimentos
        for conhecimento in self.conhecimentos:
            dados = conhecimento['dados']
            if 'numeros_mais_eficazes' in dados:
                for num, score in dados['numeros_mais_eficazes'].items():
                    contador_numeros[int(num)].append(score)
        
        # Calcula médias e estatísticas
        stats_numeros = {}
        for num, scores in contador_numeros.items():
            stats_numeros[num] = {
                'aparicoes': len(scores),
                'score_total': sum(scores),
                'score_medio': sum(scores) / len(scores),
                'score_max': max(scores),
                'consistencia': len(scores) / len(self.conhecimentos)
            }
        
        # Ordena por eficácia
        top_numeros = sorted(stats_numeros.items(), 
                           key=lambda x: (x[1]['score_medio'], x[1]['consistencia']), 
                           reverse=True)
        
        print("TOP 15 NÚMEROS MAIS EFICAZES:")
        print("Num | Score Médio | Aparições | Consistência | Score Max")
        print("-"*55)
        
        for i, (num, stats) in enumerate(top_numeros[:15]):
            print(f"{num:2d}  | {stats['score_medio']:8.1f} | "
                  f"{stats['aparicoes']:8d} | {stats['consistencia']:9.1%} | "
                  f"{stats['score_max']:7.0f}")
        
        return top_numeros
    
    def gerar_combinacao_para_futuro(self):
        """Gera combinação otimizada para concurso futuro"""
        print("\n🔮 COMBINAÇÃO PARA PRÓXIMO CONCURSO")
        print("="*60)
        
        # Pega os números mais eficazes
        top_numeros = self.identificar_numeros_mais_eficazes()
        
        # Estratégia: Top 12 + balanceamento
        combinacao = []
        
        # Adiciona top 12 números mais eficazes
        for num, stats in top_numeros[:12]:
            combinacao.append(num)
        
        # Balanceamento por distribuição
        faltam = 15 - len(combinacao)
        restantes = [n for n in range(1, 26) if n not in combinacao]
        
        # Prioriza números com boa consistência que sobraram
        candidatos_restantes = []
        for num in restantes:
            if num in dict(top_numeros):
                stats = dict(top_numeros)[num]
                candidatos_restantes.append((num, stats['consistencia']))
        
        # Ordena por consistência e pega os melhores
        candidatos_restantes.sort(key=lambda x: x[1], reverse=True)
        for num, _ in candidatos_restantes[:faltam]:
            combinacao.append(num)
        
        # Se ainda faltam, completa com distribuição balanceada
        if len(combinacao) < 15:
            remaining = [n for n in range(1, 26) if n not in combinacao]
            # Balanceia por faixas: baixos (1-8), médios (9-17), altos (18-25)
            baixos = [n for n in remaining if n <= 8]
            medios = [n for n in remaining if 9 <= n <= 17]
            altos = [n for n in remaining if n >= 18]
            
            while len(combinacao) < 15 and (baixos or medios or altos):
                if baixos:
                    combinacao.append(baixos.pop(0))
                if len(combinacao) < 15 and medios:
                    combinacao.append(medios.pop(0))
                if len(combinacao) < 15 and altos:
                    combinacao.append(altos.pop(0))
        
        combinacao = sorted(combinacao[:15])
        
        # Análise da combinação
        pares = sum(1 for n in combinacao if n % 2 == 0)
        impares = 15 - pares
        baixos = sum(1 for n in combinacao if n <= 8)
        medios = sum(1 for n in combinacao if 9 <= n <= 17)
        altos = sum(1 for n in combinacao if n >= 18)
        
        print(f"COMBINAÇÃO RECOMENDADA: {combinacao}")
        print(f"")
        print(f"Análise da combinação:")
        print(f"• Pares: {pares}, Ímpares: {impares}")
        print(f"• Baixos (1-8): {baixos}, Médios (9-17): {medios}, Altos (18-25): {altos}")
        print(f"• Baseada em {len(self.conhecimentos)} sessões de aprendizado")
        
        # Calcula confiança
        nums_conhecidos = len([n for n in combinacao if n in dict(top_numeros)])
        confianca = (nums_conhecidos / 15) * 100
        print(f"• Confiança: {confianca:.1f}% ({nums_conhecidos}/15 números com histórico)")
        
        return combinacao
    
    def relatorio_completo(self):
        """Gera relatório completo de efetividade"""
        print("🧠 RELATÓRIO COMPLETO DE EFETIVIDADE DO AUTO-TREINO")
        print("="*70)
        
        # Análises
        stats_acertos = self.analisar_acertos_15()
        evolucao = self.analisar_evolucao_aprendizado()
        top_numeros = self.identificar_numeros_mais_eficazes()
        combinacao_futura = self.gerar_combinacao_para_futuro()
        
        # Resumo executivo
        print(f"\n📋 RESUMO EXECUTIVO")
        print("="*60)
        print(f"• Arquivos de conhecimento analisados: {len(self.conhecimentos)}")
        print(f"• Total de tentativas registradas: {stats_acertos['total_tentativas']:,}")
        print(f"• Melhor resultado obtido: {stats_acertos['melhor_resultado']}/15")
        print(f"• Taxa de sucesso 15/15: {(stats_acertos['acertos_15']/max(1,stats_acertos['total_tentativas'])*100):.2f}%")
        print(f"• Média de acertos: {stats_acertos['media_acertos']:.2f}")
        
        if evolucao:
            print(f"• Números eficazes descobertos: {evolucao[-1]['numeros_eficazes']}")
            print(f"• Padrões vencedores identificados: {evolucao[-1]['padroes_descobertos']}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES PARA PRÓXIMOS CONCURSOS")
        print("="*60)
        print(f"1. Use a combinação recomendada baseada no aprendizado")
        print(f"2. Foque nos top 15 números mais eficazes identificados")
        print(f"3. Mantenha o balanceamento pares/ímpares e distribuição")
        print(f"4. Continue o auto-treino para refinamento contínuo")
        
        return {
            'stats_acertos': stats_acertos,
            'evolucao': evolucao,
            'top_numeros': top_numeros[:15],
            'combinacao_futura': combinacao_futura
        }

def main():
    """Função principal"""
    analisador = AnalisadorEfetividade()
    
    if not analisador.conhecimentos:
        print("❌ Nenhum arquivo de conhecimento encontrado!")
        print("Execute o sistema de auto-treino primeiro para gerar dados.")
        return
    
    print("📊 ANALISADOR DE EFETIVIDADE DO AUTO-TREINO")
    print("="*50)
    print("1. Análise de acertos 15/15")
    print("2. Evolução do aprendizado")
    print("3. Números mais eficazes")
    print("4. Combinação para futuro")
    print("5. Relatório completo")
    print("0. Sair")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "1":
        analisador.analisar_acertos_15()
    elif opcao == "2":
        analisador.analisar_evolucao_aprendizado()
    elif opcao == "3":
        analisador.identificar_numeros_mais_eficazes()
    elif opcao == "4":
        analisador.gerar_combinacao_para_futuro()
    elif opcao == "5":
        resultados = analisador.relatorio_completo()
        
        # Salva relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo = f"relatorio_efetividade_{timestamp}.json"
        with open(arquivo, 'w') as f:
            json.dump(resultados, f, indent=2, default=str)
        print(f"\n💾 Relatório salvo em: {arquivo}")
        
    elif opcao == "0":
        print("Saindo...")
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main()