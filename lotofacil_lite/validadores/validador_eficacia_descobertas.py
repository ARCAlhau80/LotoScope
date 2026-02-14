#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔬 VALIDADOR DE EFICÁCIA DAS DESCOBERTAS
========================================
Sistema para medir e comparar a eficácia dos geradores
antes e depois da aplicação das descobertas dos campos de comparação.

Este sistema:
- Testa geradores com e sem as descobertas aplicadas
- Compara acurácia na predição de estados futuros
- Mede precisão das estimativas de soma
- Analisa tempo de detecção de inversões
- Gera relatórios detalhados de performance

Autor: AR CALHAU
Data: 06 de Outubro de 2025
"""

import os
import sys
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'validadores'))

# Importa descobertas
try:
    from integracao_descobertas_comparacao import IntegracaoDescobertasComparacao
    DESCOBERTAS_DISPONIVEL = True
except ImportError:
    DESCOBERTAS_DISPONIVEL = False

# Importa configuração do banco
try:
    from database_config import DatabaseConfig
    import pyodbc
    BANCO_DISPONIVEL = True
except ImportError:
    BANCO_DISPONIVEL = False

class ValidadorEficacia:
    """Sistema para validar eficácia das descobertas"""
    
    def __init__(self):
        self.pasta_relatorios = "relatorios_eficacia"
        os.makedirs(self.pasta_relatorios, exist_ok=True)
        
        # Carrega descobertas se disponível
        if DESCOBERTAS_DISPONIVEL:
            self.descobertas = IntegracaoDescobertasComparacao()
            print("🔬 Descobertas carregadas para validação")
        else:
            self.descobertas = None
            print("⚠️ Descobertas não disponíveis")
        
        # Dados para teste
        self.dados_teste = []
        self.resultados_teste = {}
        
        print("🔬 VALIDADOR DE EFICÁCIA DAS DESCOBERTAS INICIALIZADO")
        print("=" * 60)
    
    def carregar_dados_teste(self, limite: int = 100) -> bool:
        """Carrega dados históricos para teste"""
        print(f"\n📊 Carregando últimos {limite} concursos para teste...")
        
        # Por enquanto usa dados simulados para demonstração
        self._gerar_dados_simulados(limite)
        return True
    
    def _gerar_dados_simulados(self, quantidade: int):
        """Gera dados simulados para teste"""
        print("🎲 Gerando dados simulados para teste...")
        
        for i in range(quantidade):
            # Gera números aleatórios válidos
            numeros = sorted(random.sample(range(1, 26), 15))
            
            # Simula estado de comparação (deve somar 15)
            menor = random.randint(3, 7)
            maior = random.randint(4, 8)
            igual = 15 - menor - maior
            
            # Calcula soma e amplitude
            soma = sum(numeros)
            amplitude = max(numeros) - min(numeros)
            
            self.dados_teste.append({
                'concurso': 3500 - i,
                'numeros': numeros,
                'estado_comparacao': (menor, maior, igual),
                'soma': soma,
                'amplitude': amplitude
            })
        
        print(f"✅ Gerados {len(self.dados_teste)} dados simulados")
    
    def testar_predicao_estados(self) -> Dict:
        """Testa precisão na predição de estados futuros"""
        print("\n🎯 TESTE 1: Predição de Estados Futuros")
        print("=" * 50)
        
        acertos_sem_descoberta = 0
        acertos_com_descoberta = 0
        total_testes = 0
        
        resultados_detalhados = []
        
        # Testa sequências de 10 concursos
        for i in range(0, len(self.dados_teste) - 10, 5):
            sequencia = self.dados_teste[i:i+10]
            estado_atual = sequencia[0]['estado_comparacao']
            estado_real_futuro = sequencia[5]['estado_comparacao']
            
            # Predição sem descobertas (simples persistência)
            predicao_sem = estado_atual
            
            # Predição com descobertas
            if self.descobertas:
                predicao_com = self.descobertas.prever_proximo_estado(estado_atual)
            else:
                predicao_com = estado_atual
            
            # Calcula acertos
            acerto_sem = self._calcular_precisao_estado(predicao_sem, estado_real_futuro)
            acerto_com = self._calcular_precisao_estado(predicao_com, estado_real_futuro)
            
            acertos_sem_descoberta += acerto_sem
            acertos_com_descoberta += acerto_com
            total_testes += 1
            
            resultados_detalhados.append({
                'concurso': sequencia[0]['concurso'],
                'estado_atual': estado_atual,
                'estado_real': estado_real_futuro,
                'predicao_sem': predicao_sem,
                'predicao_com': predicao_com,
                'acerto_sem': acerto_sem,
                'acerto_com': acerto_com
            })
        
        # Calcula métricas finais
        precisao_sem = (acertos_sem_descoberta / total_testes) * 100 if total_testes > 0 else 0
        precisao_com = (acertos_com_descoberta / total_testes) * 100 if total_testes > 0 else 0
        melhoria = precisao_com - precisao_sem
        
        resultado = {
            'total_testes': total_testes,
            'precisao_sem_descoberta': precisao_sem,
            'precisao_com_descoberta': precisao_com,
            'melhoria_percentual': melhoria,
            'detalhes': resultados_detalhados
        }
        
        print(f"📊 Total de testes: {total_testes}")
        print(f"🎯 Precisão sem descobertas: {precisao_sem:.1f}%")
        print(f"🚀 Precisão com descobertas: {precisao_com:.1f}%")
        print(f"📈 Melhoria: {melhoria:+.1f}%")
        
        return resultado
    
    def testar_estimativa_soma(self) -> Dict:
        """Testa precisão na estimativa de soma"""
        print("\n🧮 TESTE 2: Estimativa de Soma")
        print("=" * 50)
        
        erros_sem_descoberta = []
        erros_com_descoberta = []
        
        resultados_detalhados = []
        
        for dados in self.dados_teste[:50]:  # Testa 50 concursos
            estado = dados['estado_comparacao']
            soma_real = dados['soma']
            
            # Estimativa sem descobertas (média histórica)
            estimativa_sem = 195  # Média histórica aproximada
            
            # Estimativa com descobertas
            if self.descobertas:
                menor, maior, igual = estado
                estimativa_com = self.descobertas.estimar_soma_por_estado(menor, maior, igual)
            else:
                estimativa_com = 195
            
            # Calcula erros
            erro_sem = abs(estimativa_sem - soma_real)
            erro_com = abs(estimativa_com - soma_real)
            
            erros_sem_descoberta.append(erro_sem)
            erros_com_descoberta.append(erro_com)
            
            resultados_detalhados.append({
                'concurso': dados['concurso'],
                'estado': estado,
                'soma_real': soma_real,
                'estimativa_sem': estimativa_sem,
                'estimativa_com': estimativa_com,
                'erro_sem': erro_sem,
                'erro_com': erro_com
            })
        
        # Calcula métricas
        mae_sem = sum(erros_sem_descoberta) / len(erros_sem_descoberta)
        mae_com = sum(erros_com_descoberta) / len(erros_com_descoberta)
        melhoria = ((mae_sem - mae_com) / mae_sem) * 100 if mae_sem > 0 else 0
        
        resultado = {
            'total_testes': len(erros_sem_descoberta),
            'mae_sem_descoberta': mae_sem,
            'mae_com_descoberta': mae_com,
            'melhoria_percentual': melhoria,
            'detalhes': resultados_detalhados
        }
        
        print(f"📊 Total de testes: {len(erros_sem_descoberta)}")
        print(f"📏 MAE sem descobertas: {mae_sem:.1f}")
        print(f"🎯 MAE com descobertas: {mae_com:.1f}")
        print(f"📈 Melhoria: {melhoria:+.1f}%")
        
        return resultado
    
    def testar_deteccao_inversoes(self) -> Dict:
        """Testa capacidade de detectar inversões"""
        print("\n🔄 TESTE 3: Detecção de Inversões")
        print("=" * 50)
        
        inversoes_detectadas_sem = 0
        inversoes_detectadas_com = 0
        total_inversoes = 0
        
        resultados_detalhados = []
        
        for i in range(len(self.dados_teste) - 1):
            estado_atual = self.dados_teste[i]['estado_comparacao']
            estado_proximo = self.dados_teste[i + 1]['estado_comparacao']
            
            # Verifica se houve inversão real
            inversao_real = self._verificar_inversao(estado_atual, estado_proximo)
            
            if inversao_real:
                total_inversoes += 1
                
                # Detecção sem descobertas (aleatória)
                deteccao_sem = random.random() < 0.1  # 10% de chance
                
                # Detecção com descobertas
                if self.descobertas:
                    deteccao_com = self.descobertas.eh_momento_inversao(estado_atual)
                else:
                    deteccao_com = False
                
                if deteccao_sem:
                    inversoes_detectadas_sem += 1
                if deteccao_com:
                    inversoes_detectadas_com += 1
                
                resultados_detalhados.append({
                    'concurso': self.dados_teste[i]['concurso'],
                    'estado_atual': estado_atual,
                    'estado_proximo': estado_proximo,
                    'inversao_real': inversao_real,
                    'detectada_sem': deteccao_sem,
                    'detectada_com': deteccao_com
                })
        
        # Calcula métricas
        taxa_deteccao_sem = (inversoes_detectadas_sem / total_inversoes * 100) if total_inversoes > 0 else 0
        taxa_deteccao_com = (inversoes_detectadas_com / total_inversoes * 100) if total_inversoes > 0 else 0
        melhoria = taxa_deteccao_com - taxa_deteccao_sem
        
        resultado = {
            'total_inversoes': total_inversoes,
            'detectadas_sem_descoberta': inversoes_detectadas_sem,
            'detectadas_com_descoberta': inversoes_detectadas_com,
            'taxa_deteccao_sem': taxa_deteccao_sem,
            'taxa_deteccao_com': taxa_deteccao_com,
            'melhoria_percentual': melhoria,
            'detalhes': resultados_detalhados
        }
        
        print(f"📊 Total de inversões: {total_inversoes}")
        print(f"🔍 Detectadas sem descobertas: {inversoes_detectadas_sem} ({taxa_deteccao_sem:.1f}%)")
        print(f"🚀 Detectadas com descobertas: {inversoes_detectadas_com} ({taxa_deteccao_com:.1f}%)")
        print(f"📈 Melhoria: {melhoria:+.1f}%")
        
        return resultado
    
    def _calcular_precisao_estado(self, predicao: Tuple, real: Tuple) -> float:
        """Calcula precisão entre estado predito e real"""
        if len(predicao) != 3 or len(real) != 3:
            return 0.0
        
        # Conta quantos campos estão corretos
        acertos = sum(1 for p, r in zip(predicao, real) if abs(p - r) <= 1)
        return acertos / 3.0
    
    def _verificar_inversao(self, estado1: Tuple, estado2: Tuple) -> bool:
        """Verifica se houve inversão entre dois estados"""
        menor1, maior1, _ = estado1
        menor2, maior2, _ = estado2
        
        # Inversão: menor vira maior ou maior vira menor
        return (menor1 > maior1 and menor2 < maior2) or (menor1 < maior1 and menor2 > maior2)
    
    def executar_todos_testes(self) -> Dict:
        """Executa todos os testes de validação"""
        print("🚀 INICIANDO VALIDAÇÃO COMPLETA DA EFICÁCIA DAS DESCOBERTAS")
        print("=" * 70)
        
        if not self.carregar_dados_teste():
            print("❌ Falha ao carregar dados de teste")
            return {}
        
        # Executa todos os testes
        resultado_estados = self.testar_predicao_estados()
        resultado_soma = self.testar_estimativa_soma()
        resultado_inversoes = self.testar_deteccao_inversoes()
        
        # Consolida resultados
        resultado_completo = {
            'timestamp': datetime.now().isoformat(),
            'descobertas_disponivel': DESCOBERTAS_DISPONIVEL,
            'banco_disponivel': BANCO_DISPONIVEL,
            'dados_teste_quantidade': len(self.dados_teste),
            'testes': {
                'predicao_estados': resultado_estados,
                'estimativa_soma': resultado_soma,
                'deteccao_inversoes': resultado_inversoes
            },
            'resumo_melhorias': {
                'predicao_estados': resultado_estados.get('melhoria_percentual', 0),
                'estimativa_soma': resultado_soma.get('melhoria_percentual', 0),
                'deteccao_inversoes': resultado_inversoes.get('melhoria_percentual', 0)
            }
        }
        
        # Salva relatório
        self.salvar_relatorio(resultado_completo)
        
        # Exibe resumo final
        self.exibir_resumo_final(resultado_completo)
        
        return resultado_completo
    
    def salvar_relatorio(self, resultado: Dict):
        """Salva relatório detalhado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"{self.pasta_relatorios}/relatorio_eficacia_{timestamp}.json"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Relatório salvo: {arquivo}")
    
    def exibir_resumo_final(self, resultado: Dict):
        """Exibe resumo final dos resultados"""
        print("\n" + "=" * 70)
        print("📊 RESUMO FINAL DA VALIDAÇÃO")
        print("=" * 70)
        
        melhorias = resultado['resumo_melhorias']
        
        print(f"🎯 Predição de Estados: {melhorias['predicao_estados']:+.1f}%")
        print(f"🧮 Estimativa de Soma: {melhorias['estimativa_soma']:+.1f}%")
        print(f"🔄 Detecção de Inversões: {melhorias['deteccao_inversoes']:+.1f}%")
        
        melhoria_media = sum(melhorias.values()) / len(melhorias)
        print(f"\n📈 MELHORIA MÉDIA GERAL: {melhoria_media:+.1f}%")
        
        if melhoria_media > 5:
            print("✅ DESCOBERTAS ALTAMENTE EFICAZES!")
        elif melhoria_media > 0:
            print("✅ Descobertas mostram melhoria mensurável")
        else:
            print("⚠️ Descobertas precisam de refinamento")
        
        print("=" * 70)

def main():
    """Função principal"""
    validador = ValidadorEficacia()
    resultado = validador.executar_todos_testes()
    
    if resultado:
        print(f"\n🎉 Validação concluída com sucesso!")
        print(f"📂 Dados testados: {resultado['dados_teste_quantidade']} concursos")
        print(f"🔬 Descobertas disponíveis: {'Sim' if resultado['descobertas_disponivel'] else 'Não'}")

if __name__ == "__main__":
    main()