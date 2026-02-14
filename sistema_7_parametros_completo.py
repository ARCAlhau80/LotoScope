#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA INTEGRADO DOS 7 PARÂMETROS DINÂMICOS
===============================================
Sistema completo que analisa histórico, calcula parâmetros otimizados
e executa estratégia dinâmica no sistema de auto-treino
"""

from estrategia_dinamica import EstrategiaParametrosDinamicos
from analisador_parametros_dinamicos import AnalisadorParametrosDinamicos
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class SistemaParametrosDinamicosCompleto:
    """
    Sistema completo que integra análise histórica com estratégia dinâmica
    """
    
    def __init__(self):
        self.estrategia = EstrategiaParametrosDinamicos()
        self.configuracao = self._carregar_configuracao()
        self.historico_evolucao = []
        self.metricas = {
            'sessoes_executadas': 0,
            'total_combinacoes': 0,
            'melhor_performance': 0,
            'parametros_evoluidos': 0,
            'tempo_total': 0
        }
    
    def _carregar_configuracao(self) -> Dict:
        """Carrega configuração específica para os 7 parâmetros"""
        config_padrao = {
            'intervalo_atualizacao_parametros': 300,  # 5 minutos
            'limite_tentativas_por_combinacao': 3268760,  # Como solicitado
            'threshold_sucesso': 13,  # Mínimo de acertos para sucesso
            'janelas_analise': [3, 5, 10, 15, 30, 'total'],
            'pesos_janelas': {
                3: 0.35,
                5: 0.25,
                10: 0.20,
                15: 0.10,
                30: 0.07,
                'total': 0.03
            },
            'salvar_evolucao_a_cada': 10,  # Sessões
            'parametros_target': {
                'n1': {'min': 1, 'max': 5, 'otimo': 2},
                'n15': {'min': 22, 'max': 25, 'otimo': 25},
                'maior_que_ultimo': {'min': 5, 'max': 12, 'otimo': 8},
                'menor_que_ultimo': {'min': 3, 'max': 10, 'otimo': 6},
                'qtde_6_a_25': {'min': 10, 'max': 15, 'otimo': 13},
                'qtde_6_a_20': {'min': 7, 'max': 12, 'otimo': 9},
                'melhores_posicoes': {'min': 5, 'max': 10, 'otimo': 7}
            }
        }
        
        # Tenta carregar configuração existente
        try:
            with open('config_7_parametros.json', 'r') as f:
                config_salva = json.load(f)
                config_padrao.update(config_salva)
        except FileNotFoundError:
            # Salva configuração padrão
            self._salvar_configuracao(config_padrao)
        
        return config_padrao
    
    def _salvar_configuracao(self, config: Dict):
        """Salva configuração"""
        with open('config_7_parametros.json', 'w') as f:
            json.dump(config, f, indent=2, default=str)
    
    def carregar_dados_historicos(self, dados: List[Dict] = None):
        """Carrega dados históricos no sistema"""
        self.estrategia.carregar_dados_historicos(dados)
        print(f"[SISTEMA] Dados históricos carregados")
    
    def executar_sessao_otimizada(self, concurso_alvo: int = None) -> Dict[str, Any]:
        """
        Executa uma sessão otimizada com os 7 parâmetros dinâmicos
        """
        inicio_sessao = time.time()
        
        print(f"\n[SESSAO] Iniciando sessão otimizada...")
        
        # 1. Atualiza parâmetros se necessário
        self.estrategia.atualizar_parametros()
        parametros_usados = self.estrategia.parametros_atuais.copy()
        
        print(f"[PARAMETROS] Usando:")
        for param, valor in parametros_usados.items():
            print(f"   {param}: {valor}")
        
        # 2. Executa tentativas com limite configurado
        limite_tentativas = self.configuracao['limite_tentativas_por_combinacao']
        melhor_combinacao = None
        melhor_resultado = 0
        tentativas_usadas = 0
        
        print(f"[TREINANDO] Limite: {limite_tentativas:,} tentativas")
        
        # Simula treino intensivo
        inicio_treino = time.time()
        
        while tentativas_usadas < limite_tentativas:
            tentativas_usadas += 1
            
            # Gera combinação com estratégia otimizada
            combinacao = self.estrategia.gerar_combinacao(concurso_alvo)
            
            # Simula avaliação (em produção seria contra resultado real)
            resultado_simulado = self._gerar_resultado_simulado()
            acertos = len(set(combinacao) & set(resultado_simulado))
            
            if acertos > melhor_resultado:
                melhor_resultado = acertos
                melhor_combinacao = combinacao
                
                print(f"[MELHORIA] {acertos} acertos em {tentativas_usadas:,} tentativas")
                
                # Se atingiu 15 acertos, para
                if acertos == 15:
                    print(f"[PERFEITO] 15 acertos encontrados!")
                    break
            
            # Progresso a cada 500k tentativas
            if tentativas_usadas % 500000 == 0:
                print(f"[PROGRESSO] {tentativas_usadas:,} tentativas, melhor: {melhor_resultado}")
        
        tempo_treino = time.time() - inicio_treino
        
        # 3. Avalia resultado
        sucesso = melhor_resultado >= self.configuracao['threshold_sucesso']
        
        resultado_sessao = {
            'concurso_alvo': concurso_alvo,
            'parametros_usados': parametros_usados,
            'melhor_combinacao': melhor_combinacao,
            'melhor_resultado': melhor_resultado,
            'tentativas_usadas': tentativas_usadas,
            'tempo_treino': tempo_treino,
            'sucesso': sucesso,
            'timestamp': datetime.now().isoformat()
        }
        
        # 4. Atualiza métricas
        self._atualizar_metricas(resultado_sessao)
        
        # 5. Registra evolução
        self.historico_evolucao.append(resultado_sessao)
        
        print(f"[RESULTADO] {melhor_resultado} acertos, {tentativas_usadas:,} tentativas, {tempo_treino:.1f}s")
        
        return resultado_sessao
    
    def _gerar_resultado_simulado(self) -> List[int]:
        """Gera resultado simulado (em produção seria o resultado real)"""
        import random
        return sorted(random.sample(range(1, 26), 15))
    
    def _atualizar_metricas(self, resultado: Dict):
        """Atualiza métricas do sistema"""
        self.metricas['sessoes_executadas'] += 1
        self.metricas['total_combinacoes'] += resultado['tentativas_usadas']
        self.metricas['tempo_total'] += resultado['tempo_treino']
        
        if resultado['melhor_resultado'] > self.metricas['melhor_performance']:
            self.metricas['melhor_performance'] = resultado['melhor_resultado']
        
        if resultado['sucesso']:
            self.metricas['parametros_evoluidos'] += 1
    
    def executar_ciclo_continuo(self, num_sessoes: int = 10):
        """Executa ciclo contínuo de otimização"""
        print(f"\n🎯 EXECUTANDO CICLO CONTÍNUO - {num_sessoes} SESSÕES")
        print("=" * 60)
        
        for i in range(num_sessoes):
            print(f"\n--- SESSÃO {i+1}/{num_sessoes} ---")
            
            # Executa sessão otimizada
            resultado = self.executar_sessao_otimizada(concurso_alvo=3500+i)
            
            # Salva evolução periodicamente
            if (i + 1) % self.configuracao['salvar_evolucao_a_cada'] == 0:
                self._salvar_evolucao()
            
            # Exibe progresso
            if (i + 1) % 3 == 0:
                self._exibir_relatorio_progresso()
        
        # Relatório final
        self._exibir_relatorio_final()
    
    def _salvar_evolucao(self):
        """Salva evolução para arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"evolucao_7_parametros_{timestamp}.json"
        
        dados = {
            'configuracao': self.configuracao,
            'metricas': self.metricas,
            'historico_evolucao': self.historico_evolucao,
            'parametros_atuais': self.estrategia.parametros_atuais
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"[SALVO] Evolução salva: {arquivo}")
    
    def _exibir_relatorio_progresso(self):
        """Exibe relatório de progresso"""
        if not self.metricas['sessoes_executadas']:
            return
        
        taxa_sucesso = (self.metricas['parametros_evoluidos'] / self.metricas['sessoes_executadas']) * 100
        media_tentativas = self.metricas['total_combinacoes'] / self.metricas['sessoes_executadas']
        tempo_medio = self.metricas['tempo_total'] / self.metricas['sessoes_executadas']
        
        print(f"\n📊 PROGRESSO ATUAL:")
        print(f"   Sessões: {self.metricas['sessoes_executadas']}")
        print(f"   Taxa de sucesso: {taxa_sucesso:.1f}%")
        print(f"   Melhor performance: {self.metricas['melhor_performance']} acertos")
        print(f"   Média tentativas: {media_tentativas:,.0f}")
        print(f"   Tempo médio: {tempo_medio:.1f}s")
    
    def _exibir_relatorio_final(self):
        """Exibe relatório final completo"""
        print(f"\n🏆 RELATÓRIO FINAL - 7 PARÂMETROS DINÂMICOS")
        print("=" * 60)
        
        self._exibir_relatorio_progresso()
        
        print(f"\n🎯 PARÂMETROS FINAIS:")
        for param, valor in self.estrategia.parametros_atuais.items():
            target = self.configuracao['parametros_target'][param]['otimo']
            status = "✅" if valor == target else "⚡"
            print(f"   {status} {param}: {valor} (target: {target})")
        
        # Últimas 3 sessões
        if len(self.historico_evolucao) >= 3:
            print(f"\n📈 ÚLTIMAS 3 SESSÕES:")
            for i, sessao in enumerate(self.historico_evolucao[-3:], 1):
                print(f"   {i}. {sessao['melhor_resultado']} acertos, {sessao['tentativas_usadas']:,} tentativas")
        
        print(f"\n✅ Sistema dos 7 parâmetros dinâmicos em operação!")
    
    def gerar_query_otimizada_atual(self) -> str:
        """Gera query SQL com parâmetros atuais otimizados"""
        return self.estrategia.analisador.gerar_query_dinamica(self.estrategia.parametros_atuais)

def main():
    """Execução principal do sistema"""
    print("🎯 SISTEMA COMPLETO DOS 7 PARÂMETROS DINÂMICOS")
    print("=" * 60)
    
    # Cria sistema
    sistema = SistemaParametrosDinamicosCompleto()
    
    # Carrega dados
    sistema.carregar_dados_historicos()
    
    # Executa ciclo de otimização
    sistema.executar_ciclo_continuo(num_sessoes=5)
    
    # Gera query final otimizada
    print(f"\n📝 QUERY SQL OTIMIZADA:")
    query = sistema.gerar_query_otimizada_atual()
    print(query[:300] + "...")
    
    # Salva estado final
    sistema._salvar_evolucao()
    
    print(f"\n🎉 Sistema completo executado com sucesso!")

if __name__ == "__main__":
    main()