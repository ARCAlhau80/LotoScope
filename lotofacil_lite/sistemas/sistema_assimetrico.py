"""
Sistema de Geração Assimétrica - LotoScope
Combina o gerador original (filtro 1) com avaliador de faixa média (filtro 2)
Estratégia: Gerar com alta precisão, filtrar para faixa 9-13
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
from avaliador_faixa_media import AvaliadorFaixaMedia
from datetime import datetime
import json
import random

class SistemaGeracaoAssimetrica:
    def __init__(self):
        print("Inicializando Sistema de Geração Assimétrica...")
        self.gerador_principal = GeradorAcademicoDinamico()
        self.avaliador_faixa_media = AvaliadorFaixaMedia()
        self.configuracao = {
            'combinacoes_iniciais': 50,  # Quantas o gerador principal vai gerar
            'filtro_final': 10,          # Quantas passam pelo segundo filtro
            'score_minimo': 30           # Score mínimo para faixa 9-13
        }
        
    def gerar_combinacoes_otimizadas(self, quantidade_final=5):
        """
        Processo de geração em duas etapas:
        1. Gerador principal produz N combinações com alta precisão geral
        2. Avaliador filtra as melhores para faixa 9-13
        """
        print(f"\n{'='*60}")
        print("SISTEMA DE GERAÇÃO ASSIMÉTRICA - LOTOFÁCIL")
        print(f"{'='*60}")
        print(f"Objetivo: {quantidade_final} combinações otimizadas para faixa 9-13")
        print(f"Processo: {self.configuracao['combinacoes_iniciais']} → filtro → {quantidade_final}")
        
        # ETAPA 1: Geração inicial com gerador principal
        print(f"\nETAPA 1: Gerando {self.configuracao['combinacoes_iniciais']} combinações com gerador principal...")
        combinacoes_iniciais = []
        
        for i in range(self.configuracao['combinacoes_iniciais']):
            combinacao = self.gerador_principal.gerar_combinacao_academica(15)
            combinacoes_iniciais.append(combinacao)
            if (i + 1) % 10 == 0:
                print(f"  Geradas: {i + 1}/{self.configuracao['combinacoes_iniciais']}")
        
        print(f"✓ Etapa 1 concluída: {len(combinacoes_iniciais)} combinações geradas")
        
        # ETAPA 2: Filtro assimétrico para faixa 9-13
        print(f"\nETAPA 2: Aplicando filtro assimétrico para faixa 9-13...")
        combinacoes_com_score = self.avaliador_faixa_media.filtrar_melhores_para_faixa_media(
            combinacoes_iniciais, 
            top_n=min(self.configuracao['filtro_final'], len(combinacoes_iniciais))
        )
        
        # ETAPA 3: Seleção final
        print(f"\nETAPA 3: Seleção final de {quantidade_final} combinações...")
        
        # Filtra por score mínimo
        combinacoes_qualificadas = [
            (comb, score) for comb, score in combinacoes_com_score 
            if score >= self.configuracao['score_minimo']
        ]
        
        if len(combinacoes_qualificadas) < quantidade_final:
            print(f"⚠️  Apenas {len(combinacoes_qualificadas)} combinações atingiram score mínimo {self.configuracao['score_minimo']}")
            print("Incluindo combinações com scores menores...")
            combinacoes_qualificadas = combinacoes_com_score
        
        # Seleciona as melhores
        combinacoes_finais = combinacoes_qualificadas[:quantidade_final]
        
        # RELATÓRIO FINAL
        self.gerar_relatorio_completo(
            combinacoes_iniciais, 
            combinacoes_com_score, 
            combinacoes_finais
        )
        
        return combinacoes_finais
    
    def gerar_relatorio_completo(self, iniciais, com_score, finais):
        """Gera relatório completo do processo"""
        print(f"\n{'='*60}")
        print("RELATÓRIO COMPLETO - GERAÇÃO ASSIMÉTRICA")
        print(f"{'='*60}")
        
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print(f"Data/Hora: {timestamp}")
        
        print(f"\nEstatísticas do processo:")
        print(f"  Combinações iniciais geradas: {len(iniciais)}")
        print(f"  Combinações avaliadas: {len(com_score)}")
        print(f"  Combinações finais selecionadas: {len(finais)}")
        
        # Análise dos scores
        if com_score:
            scores = [score for _, score in com_score]
            print(f"\nAnálise dos scores (faixa 9-13):")
            print(f"  Score máximo: {max(scores):.1f}")
            print(f"  Score mínimo: {min(scores):.1f}")
            print(f"  Score médio: {sum(scores)/len(scores):.1f}")
            print(f"  Score mínimo configurado: {self.configuracao['score_minimo']}")
        
        print(f"\nCombinações finais selecionadas:")
        for i, (combinacao, score) in enumerate(finais, 1):
            soma = sum(combinacao)
            pares = sum(1 for n in combinacao if n % 2 == 0)
            impares = 15 - pares
            
            print(f"\n{i}. SCORE: {score:.1f}")
            print(f"   Números: {sorted(combinacao)}")
            print(f"   Soma: {soma} | Pares: {pares} | Ímpares: {impares}")
            
            # Análise de distribuição por região
            regioes = [0] * 5
            for num in combinacao:
                regiao = (num - 1) // 5
                regioes[regiao] += 1
            print(f"   Distribuição: {'-'.join(map(str, regioes))} (por região 1-5, 6-10, etc.)")
        
        # Salva resultado
        resultado = {
            'timestamp': timestamp,
            'configuracao': self.configuracao,
            'estatisticas': {
                'combinacoes_iniciais': len(iniciais),
                'combinacoes_avaliadas': len(com_score),
                'combinacoes_finais': len(finais),
                'score_maximo': max(scores) if com_score else 0,
                'score_medio': sum(scores)/len(scores) if com_score else 0
            },
            'combinacoes_finais': [
                {
                    'posicao': i,
                    'combinacao': sorted(combinacao),
                    'score': score,
                    'soma': sum(combinacao),
                    'pares': sum(1 for n in combinacao if n % 2 == 0)
                }
                for i, (combinacao, score) in enumerate(finais, 1)
            ]
        }
        
        arquivo_resultado = f"resultado_assimetrico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(arquivo_resultado, 'w') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Relatório salvo em: {arquivo_resultado}")
        
        return resultado
    
    def ajustar_configuracao(self, combinacoes_iniciais=None, filtro_final=None, score_minimo=None):
        """Permite ajustar parâmetros do sistema"""
        if combinacoes_iniciais is not None:
            self.configuracao['combinacoes_iniciais'] = combinacoes_iniciais
        if filtro_final is not None:
            self.configuracao['filtro_final'] = filtro_final  
        if score_minimo is not None:
            self.configuracao['score_minimo'] = score_minimo
            
        print(f"Configuração atualizada: {self.configuracao}")
    
    def modo_analise_rapida(self, n_testes=5):
        """Modo para análise rápida com menos combinações"""
        print(f"\n🔍 MODO ANÁLISE RÁPIDA - {n_testes} testes")
        
        configuracao_original = self.configuracao.copy()
        
        # Configuração para análise rápida
        self.configuracao['combinacoes_iniciais'] = 20
        self.configuracao['filtro_final'] = 10
        self.configuracao['score_minimo'] = 20
        
        resultados = []
        for i in range(n_testes):
            print(f"\nTeste {i+1}/{n_testes}:")
            resultado = self.gerar_combinacoes_otimizadas(quantidade_final=3)
            resultados.append(resultado)
        
        # Restaura configuração original
        self.configuracao = configuracao_original
        
        print(f"\n📊 RESUMO DOS {n_testes} TESTES:")
        scores_medios = []
        for i, resultado in enumerate(resultados):
            if resultado:
                scores = [score for _, score in resultado]
                score_medio = sum(scores) / len(scores)
                scores_medios.append(score_medio)
                print(f"  Teste {i+1}: Score médio {score_medio:.1f}")
        
        if scores_medios:
            print(f"Score médio geral: {sum(scores_medios)/len(scores_medios):.1f}")
        
        return resultados

def main():
    """Função principal para teste do sistema"""
    sistema = SistemaGeracaoAssimetrica()
    
    print("Escolha o modo de operação:")
    print("1. Geração normal (5 combinações)")
    print("2. Análise rápida (5 testes com 3 combinações cada)")
    print("3. Modo personalizado")
    
    try:
        opcao = input("\nOpção (1-3): ").strip()
        
        if opcao == "1":
            combinacoes = sistema.gerar_combinacoes_otimizadas(5)
            print(f"\n✅ Processo concluído! {len(combinacoes)} combinações geradas.")
            
        elif opcao == "2":
            resultados = sistema.modo_analise_rapida(5)
            print(f"\n✅ Análise rápida concluída! {len(resultados)} testes realizados.")
            
        elif opcao == "3":
            iniciais = int(input("Combinações iniciais (padrão 50): ") or "50")
            finais = int(input("Combinações finais (padrão 5): ") or "5")
            score_min = float(input("Score mínimo (padrão 30): ") or "30")
            
            sistema.ajustar_configuracao(iniciais, min(iniciais, 20), score_min)
            combinacoes = sistema.gerar_combinacoes_otimizadas(finais)
            print(f"\n✅ Processo personalizado concluído! {len(combinacoes)} combinações geradas.")
            
        else:
            print("Opção inválida. Executando modo padrão...")
            combinacoes = sistema.gerar_combinacoes_otimizadas(5)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("Executando modo padrão...")
        combinacoes = sistema.gerar_combinacoes_otimizadas(3)

if __name__ == "__main__":
    main()
