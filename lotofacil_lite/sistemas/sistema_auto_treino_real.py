#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA DE AUTO-TREINO REAL - LOTOFACIL
==========================================
Sistema que aprende usando dados REAIS da tabela resultados_int
"""

import pyodbc
import json
import random
import time
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os

# Importa configuração de banco existente
try:
    from database_optimizer import get_optimized_connection
    USE_OPTIMIZER = True
except ImportError:
    try:
        from database_config import db_config
        USE_OPTIMIZER = False
    except ImportError:
        USE_OPTIMIZER = None

class SistemaAutoTreinoReal:
    """
    🧠 Sistema de auto-treino que usa dados reais para aprender
    """
    
    def __init__(self):
        self.setup_logging()
        self.conhecimento = self._carregar_conhecimento()
        self.estatisticas = {
            'tentativas_total': 0,
            'acertos_15': 0,
            'acertos_14': 0,
            'acertos_13': 0,
            'melhor_resultado': 0,
            'concursos_testados': [],
            'padroes_eficazes': {},
            'ultima_sessao': datetime.now().isoformat()
        }
        
    def setup_logging(self):
        """🔧 Configura logging para acompanhar o aprendizado"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('auto_treino_real.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_connection(self):
        """🔌 Obtém conexão usando o sistema otimizado existente"""
        if USE_OPTIMIZER:
            return get_optimized_connection()
        elif USE_OPTIMIZER is False:
            return db_config.get_connection()
        else:
            # Fallback para conexão direta
            connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=VADER\\SQLEXPRESS;"
                "DATABASE=LotofacilDB;"
                "Trusted_Connection=yes;"
                "MARS_Connection=Yes;"
            )
            return pyodbc.connect(connection_string)
    
    def _carregar_conhecimento(self) -> Dict:
        """📚 Carrega conhecimento acumulado ou cria novo"""
        arquivo_conhecimento = 'conhecimento_real.json'
        
        if os.path.exists(arquivo_conhecimento):
            try:
                with open(arquivo_conhecimento, 'r') as f:
                    conhecimento = json.load(f)
                    self.logger.info(f"Conhecimento carregado: {len(conhecimento.get('padroes_testados', []))} padrões")
                    return conhecimento
            except Exception as e:
                self.logger.warning(f"Erro ao carregar conhecimento: {e}")
        
        # Cria conhecimento inicial
        return {
            'padroes_testados': [],
            'numeros_eficazes': {},
            'estrategias_sucesso': [],
            'historico_aprendizado': [],
            'concursos_analisados': [],
            'versao': '2.0_real',
            'criado_em': datetime.now().isoformat()
        }
    
    def _salvar_conhecimento(self):
        """💾 Salva conhecimento acumulado"""
        self.conhecimento['ultima_atualizacao'] = datetime.now().isoformat()
        self.conhecimento['estatisticas'] = self.estatisticas
        
        with open('conhecimento_real.json', 'w') as f:
            json.dump(self.conhecimento, f, indent=2)
        
        # Backup de segurança
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'conhecimento_real_backup_{timestamp}.json', 'w') as f:
            json.dump(self.conhecimento, f, indent=2)
    
    def buscar_concursos_disponiveis(self) -> List[int]:
        """🔍 Busca concursos disponíveis na tabela resultados_int"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT Concurso 
                    FROM resultados_int 
                    WHERE Concurso IS NOT NULL 
                    ORDER BY Concurso
                """)
                
                concursos = [row[0] for row in cursor.fetchall()]
                self.logger.info(f"Encontrados {len(concursos)} concursos: {concursos[0]} a {concursos[-1]}")
                return concursos
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar concursos: {e}")
            return []
    
    def obter_resultado_oficial(self, concurso: int) -> Optional[List[int]]:
        """🎯 Obtém resultado oficial de um concurso específico"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT N1, N2, N3, N4, N5, N6, N7, N8, 
                           N9, N10, N11, N12, N13, N14, N15
                    FROM resultados_int 
                    WHERE Concurso = ?
                """, concurso)
                
                resultado = cursor.fetchone()
                if resultado:
                    numeros = [int(n) for n in resultado if n is not None]
                    return sorted(numeros)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter resultado do concurso {concurso}: {e}")
            return None
    
    def escolher_concurso_treino(self, concursos_disponiveis: List[int]) -> Tuple[int, int]:
        """🎲 Escolhe par de concursos: treino + validação"""
        # Remove concursos já testados recentemente
        concursos_nao_testados = [c for c in concursos_disponiveis 
                                 if c not in self.estatisticas['concursos_testados'][-20:]]
        
        if len(concursos_nao_testados) < 2:
            concursos_nao_testados = concursos_disponiveis
        
        # Escolhe concurso aleatório que tenha um subsequente
        for _ in range(100):  # Máximo 100 tentativas
            concurso_treino = random.choice(concursos_nao_testados[:-1])
            concurso_validacao = concurso_treino + 1
            
            if concurso_validacao in concursos_disponiveis:
                return concurso_treino, concurso_validacao
        
        # Fallback: pega dois concursos consecutivos
        idx = random.randint(0, len(concursos_disponiveis) - 2)
        return concursos_disponiveis[idx], concursos_disponiveis[idx + 1]
    
    def gerar_combinacao_inteligente(self, resultado_treino: List[int]) -> List[int]:
        """🧠 Gera combinação baseada no aprendizado anterior"""
        
        # Analisa números mais eficazes do conhecimento
        nums_eficazes = self.conhecimento.get('numeros_eficazes', {})
        
        # Combina estratégias:
        # 1. Usa alguns números do resultado de treino (aprendizado)
        # 2. Usa números historicamente eficazes
        # 3. Adiciona alguns aleatórios para exploração
        
        combinacao = []
        
        # 40% dos números do resultado de treino (6 números)
        nums_treino = random.sample(resultado_treino, min(6, len(resultado_treino)))
        combinacao.extend(nums_treino)
        
        # 40% de números eficazes conhecidos (6 números)
        if nums_eficazes:
            nums_ordenados = sorted(nums_eficazes.items(), key=lambda x: x[1], reverse=True)
            nums_top = [int(n) for n, _ in nums_ordenados[:10]]
            nums_eficazes_sample = random.sample(nums_top, min(6, len(nums_top)))
            
            for num in nums_eficazes_sample:
                if num not in combinacao and len(combinacao) < 12:
                    combinacao.append(num)
        
        # Completa com números aleatórios até 15
        todos_numeros = list(range(1, 26))
        nums_restantes = [n for n in todos_numeros if n not in combinacao]
        
        while len(combinacao) < 15 and nums_restantes:
            num_aleatorio = random.choice(nums_restantes)
            combinacao.append(num_aleatorio)
            nums_restantes.remove(num_aleatorio)
        
        return sorted(combinacao)
    
    def contar_acertos(self, combinacao: List[int], resultado_oficial: List[int]) -> int:
        """🎯 Conta acertos entre combinação e resultado oficial"""
        return len(set(combinacao).intersection(set(resultado_oficial)))
    
    def atualizar_conhecimento(self, combinacao: List[int], acertos: int, 
                             concurso_treino: int, concurso_validacao: int):
        """📚 Atualiza conhecimento baseado no resultado"""
        
        # Registra padrão testado
        padrao = {
            'combinacao': combinacao,
            'acertos': acertos,
            'concurso_treino': concurso_treino,
            'concurso_validacao': concurso_validacao,
            'timestamp': datetime.now().isoformat(),
            'eficacia': acertos / 15.0
        }
        
        self.conhecimento['padroes_testados'].append(padrao)
        
        # Atualiza eficácia dos números
        for numero in combinacao:
            str_num = str(numero)
            if str_num not in self.conhecimento['numeros_eficazes']:
                self.conhecimento['numeros_eficazes'][str_num] = 0
            
            # Pontuação baseada nos acertos
            self.conhecimento['numeros_eficazes'][str_num] += acertos
        
        # Se foi um bom resultado, registra como estratégia de sucesso
        if acertos >= 13:
            estrategia = {
                'combinacao': combinacao,
                'acertos': acertos,
                'concursos': f"{concurso_treino}->{concurso_validacao}",
                'data': datetime.now().isoformat()
            }
            self.conhecimento['estrategias_sucesso'].append(estrategia)
        
        # Registra concursos analisados
        if concurso_treino not in self.conhecimento['concursos_analisados']:
            self.conhecimento['concursos_analisados'].append(concurso_treino)
        if concurso_validacao not in self.conhecimento['concursos_analisados']:
            self.conhecimento['concursos_analisados'].append(concurso_validacao)
        
        # Histórico de aprendizado
        self.conhecimento['historico_aprendizado'].append({
            'acertos': acertos,
            'timestamp': datetime.now().isoformat(),
            'concursos': f"{concurso_treino}->{concurso_validacao}"
        })
    
    def executar_ciclo_aprendizado(self) -> Dict:
        """🔄 Executa um ciclo completo de aprendizado"""
        
        # 1. Busca concursos disponíveis
        concursos = self.buscar_concursos_disponiveis()
        if len(concursos) < 2:
            return {'erro': 'Não há concursos suficientes na base'}
        
        # 2. Escolhe par de concursos
        concurso_treino, concurso_validacao = self.escolher_concurso_treino(concursos)
        
        # 3. Obtém resultados oficiais
        resultado_treino = self.obter_resultado_oficial(concurso_treino)
        resultado_validacao = self.obter_resultado_oficial(concurso_validacao)
        
        if not resultado_treino or not resultado_validacao:
            return {'erro': f'Não foi possível obter resultados dos concursos {concurso_treino}/{concurso_validacao}'}
        
        # 4. Gera combinação inteligente
        combinacao = self.gerar_combinacao_inteligente(resultado_treino)
        
        # 5. Testa contra resultado de validação
        acertos = self.contar_acertos(combinacao, resultado_validacao)
        
        # 6. Atualiza conhecimento
        self.atualizar_conhecimento(combinacao, acertos, concurso_treino, concurso_validacao)
        
        # 7. Atualiza estatísticas
        self.estatisticas['tentativas_total'] += 1
        self.estatisticas['concursos_testados'].append(concurso_validacao)
        
        if acertos == 15:
            self.estatisticas['acertos_15'] += 1
        elif acertos == 14:
            self.estatisticas['acertos_14'] += 1
        elif acertos == 13:
            self.estatisticas['acertos_13'] += 1
        
        if acertos > self.estatisticas['melhor_resultado']:
            self.estatisticas['melhor_resultado'] = acertos
        
        # 8. Log do resultado
        self.logger.info(f"Ciclo {self.estatisticas['tentativas_total']}: "
                        f"Treino={concurso_treino} -> Validação={concurso_validacao} "
                        f"| Acertos: {acertos}/15")
        
        if acertos >= 14:
            self.logger.info(f"🎯 EXCELENTE! {acertos} acertos com: {combinacao}")
            self.logger.info(f"🎯 Resultado oficial: {resultado_validacao}")
        
        return {
            'ciclo': self.estatisticas['tentativas_total'],
            'concurso_treino': concurso_treino,
            'concurso_validacao': concurso_validacao,
            'combinacao_gerada': combinacao,
            'resultado_oficial': resultado_validacao,
            'acertos': acertos,
            'resultado_treino': resultado_treino
        }
    
    def executar_sessao_aprendizado(self, max_ciclos: int = 50):
        """🚀 Executa múltiplos ciclos de aprendizado"""
        
        self.logger.info(f"🚀 Iniciando sessão de {max_ciclos} ciclos de aprendizado REAL")
        
        resultados_sessao = []
        inicio = time.time()
        
        for ciclo in range(max_ciclos):
            try:
                resultado = self.executar_ciclo_aprendizado()
                resultados_sessao.append(resultado)
                
                # Para se conseguir 15 acertos!
                if resultado.get('acertos') == 15:
                    self.logger.info(f"🏆 JACKPOT! 15 acertos no ciclo {ciclo + 1}!")
                    break
                
                # Pausa entre ciclos
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Erro no ciclo {ciclo + 1}: {e}")
                continue
        
        fim = time.time()
        
        # Salva conhecimento
        self._salvar_conhecimento()
        
        # Relatório da sessão
        acertos_15_sessao = sum(1 for r in resultados_sessao if r.get('acertos') == 15)
        acertos_14_sessao = sum(1 for r in resultados_sessao if r.get('acertos') == 14)
        melhor_sessao = max([r.get('acertos', 0) for r in resultados_sessao], default=0)
        
        self.logger.info(f"📊 SESSÃO FINALIZADA:")
        self.logger.info(f"   Ciclos executados: {len(resultados_sessao)}")
        self.logger.info(f"   Tempo total: {fim - inicio:.1f}s")
        self.logger.info(f"   Acertos 15: {acertos_15_sessao}")
        self.logger.info(f"   Acertos 14: {acertos_14_sessao}")
        self.logger.info(f"   Melhor resultado: {melhor_sessao}/15")
        self.logger.info(f"   Conhecimento salvo em: conhecimento_real.json")
        
        return {
            'sessao_completa': True,
            'ciclos_executados': len(resultados_sessao),
            'acertos_15': acertos_15_sessao,
            'acertos_14': acertos_14_sessao,
            'melhor_resultado': melhor_sessao,
            'tempo_total': fim - inicio,
            'resultados': resultados_sessao
        }
    
    def gerar_relatorio_aprendizado(self):
        """📊 Gera relatório do aprendizado atual"""
        
        total_padroes = len(self.conhecimento.get('padroes_testados', []))
        estrategias_sucesso = len(self.conhecimento.get('estrategias_sucesso', []))
        
        print("📊 RELATÓRIO DE APRENDIZADO REAL")
        print("=" * 50)
        print(f"Padrões testados: {total_padroes}")
        print(f"Estratégias de sucesso (13+): {estrategias_sucesso}")
        print(f"Acertos 15: {self.estatisticas['acertos_15']}")
        print(f"Acertos 14: {self.estatisticas['acertos_14']}")
        print(f"Acertos 13: {self.estatisticas['acertos_13']}")
        print(f"Melhor resultado: {self.estatisticas['melhor_resultado']}/15")
        
        # Top números eficazes
        nums_eficazes = self.conhecimento.get('numeros_eficazes', {})
        if nums_eficazes:
            print(f"\n🎯 Top 10 números mais eficazes:")
            sorted_nums = sorted(nums_eficazes.items(), key=lambda x: x[1], reverse=True)
            for i, (num, pontos) in enumerate(sorted_nums[:10], 1):
                print(f"   {i}. Número {num}: {pontos} pontos")

def main():
    """Função principal"""
    sistema = SistemaAutoTreinoReal()
    
    print("🎯 SISTEMA DE AUTO-TREINO REAL - LOTOFACIL")
    print("Aprendizado baseado em dados REAIS da tabela resultados_int")
    print()
    
    opcao = input("Escolha: (1) Ciclo único (2) Sessão de 50 ciclos (3) Relatório: ").strip()
    
    if opcao == "1":
        resultado = sistema.executar_ciclo_aprendizado()
        print(f"Resultado: {resultado}")
    
    elif opcao == "2":
        sistema.executar_sessao_aprendizado(50)
    
    elif opcao == "3":
        sistema.gerar_relatorio_aprendizado()
    
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main()