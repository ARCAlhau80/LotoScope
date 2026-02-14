#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 VALIDADOR DE SUPER-COMBINAÇÕES IA
Sistema que testa super-combinações geradas pela IA contra resultados reais
e aprende com os erros para melhorar futuras predições.

Features:
- Validação automática contra resultados históricos
- Aprendizado contínuo com feedback real
- Análise de performance e ajustes automáticos
- Relatórios detalhados de acurácia

Autor: AR CALHAU
Data: 20 de Agosto de 2025
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import pyodbc
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from collections import defaultdict
from database_config import db_config

class ValidadorSuperCombinacoes:
    """Sistema de validação e aprendizado contínuo para super-combinações"""
    
    def __init__(self, db_path: str = "lotofacil.db"):
        self.db_path = db_path
        self.pasta_validacao = "combin_ia/validacao"
        self.pasta_super_combinacoes = "combin_ia/super_combinacoes"
        self.pasta_aprendizado = "combin_ia/aprendizado"
        
        # Cria pastas se não existirem
        for pasta in [self.pasta_validacao, self.pasta_aprendizado]:
            os.makedirs(pasta, exist_ok=True)
        
        # Histórico de validações
        self.historico_validacoes = []
        self.metricas_aprendizado = {
            'acertos_por_faixa': defaultdict(int),
            'erros_por_tipo': defaultdict(int),
            'evolucao_performance': [],
            'padroes_identificados': []
        }
    
    def conectar_base(self) -> Optional[pyodbc.Connection]:
        """Conecta à base de dados"""
        try:
            conn_str = f"""
            DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={db_config.server};
            DATABASE={db_config.database};
            Trusted_Connection=yes;
            """
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def obter_resultado_concurso(self, numero_concurso: int) -> Optional[List[int]]:
        """Obtém resultado de um concurso específico do banco"""
        try:
            conn = self.conectar_base()
            if not conn:
                return None
                
            cursor = conn.cursor()
            
            # Busca o resultado do concurso
            query = """
            SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15
            FROM Resultados_INT 
            WHERE Concurso = ?
            """
            
            cursor.execute(query, (numero_concurso,))
            resultado = cursor.fetchone()
            
            conn.close()
            
            if resultado:
                # Os números já vêm como inteiros diretamente das colunas N1-N15
                dezenas = [int(n) for n in resultado if n is not None and n > 0]
                return sorted(dezenas)
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar concurso {numero_concurso}: {e}")
            return None
    
    def obter_ultimos_concursos(self, quantidade: int = 10) -> List[Dict]:
        """Obtém os últimos concursos para validação"""
        try:
            conn = self.conectar_base()
            if not conn:
                return []
                
            cursor = conn.cursor()
            
            query = """
            SELECT TOP (?) Concurso, Data_Sorteio,
                   N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
                   N11, N12, N13, N14, N15
            FROM Resultados_INT 
            ORDER BY Concurso DESC 
            """
            
            cursor.execute(query, (quantidade,))
            resultados = cursor.fetchall()
            
            conn.close()
            
            concursos = []
            for row in resultados:
                concurso = row[0]
                data_sorteio = row[1] 
                dezenas = [int(n) for n in row[2:17] if n is not None and n > 0]  # N1 a N15
                
                concursos.append({
                    'concurso': concurso,
                    'dezenas': sorted(dezenas),
                    'data_sorteio': data_sorteio.strftime('%Y-%m-%d') if data_sorteio else 'N/A'
                })
            
            return concursos
            
        except Exception as e:
            print(f"❌ Erro ao buscar últimos concursos: {e}")
            return []
    
    def calcular_acertos_combinacao(self, combinacao: List[int], 
                                   resultado_oficial: List[int]) -> int:
        """Calcula quantos números uma combinação acertou"""
        combinacao_set = set(combinacao)
        resultado_set = set(resultado_oficial)
        return len(combinacao_set & resultado_set)
    
    def validar_super_combinacao(self, super_combinacao: List[int], 
                               concurso_teste: int) -> Dict:
        """Valida uma super-combinação contra um resultado real"""
        resultado_oficial = self.obter_resultado_concurso(concurso_teste)
        
        if not resultado_oficial:
            return {'erro': f'Concurso {concurso_teste} não encontrado'}
        
        acertos = self.calcular_acertos_combinacao(super_combinacao, resultado_oficial)
        
        # Análise detalhada
        validacao = {
            'concurso': concurso_teste,
            'super_combinacao': super_combinacao,
            'resultado_oficial': resultado_oficial,
            'acertos': acertos,
            'taxa_acerto': acertos / len(super_combinacao),
            'numeros_acertados': list(set(super_combinacao) & set(resultado_oficial)),
            'numeros_errados': list(set(super_combinacao) - set(resultado_oficial)),
            'numeros_nao_jogados': list(set(resultado_oficial) - set(super_combinacao)),
            'performance_faixa': self._classificar_performance(acertos),
            'validado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return validacao
    
    def _classificar_performance(self, acertos: int) -> str:
        """Classifica a performance baseada no número de acertos"""
        if acertos >= 15:
            return "EXCEPCIONAL"
        elif acertos >= 13:
            return "EXCELENTE"
        elif acertos >= 11:
            return "BOA"
        elif acertos >= 9:
            return "REGULAR"
        else:
            return "BAIXA"
    
    def validar_arquivo_super_combinacoes(self, arquivo_path: str,
                                        concursos_teste: List[int] = None) -> Dict:
        """Valida todas as super-combinações de um arquivo"""
        
        if not os.path.exists(arquivo_path):
            return {'erro': f'Arquivo {arquivo_path} não encontrado'}
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            super_combinacoes = dados.get('super_combinacoes', [])
            
            if not super_combinacoes:
                return {'erro': 'Nenhuma super-combinação encontrada no arquivo'}
            
            # Se concursos não especificados, usa os últimos
            if not concursos_teste:
                ultimos_concursos = self.obter_ultimos_concursos(5)
                concursos_teste = [c['concurso'] for c in ultimos_concursos]
            
            print(f"🎯 Validando {len(super_combinacoes)} super-combinação(ões)")
            print(f"🔍 Testando contra concursos: {concursos_teste}")
            
            validacoes_completas = []
            
            for i, super_info in enumerate(super_combinacoes):
                super_combinacao = super_info['super_combinacao']
                
                print(f"   Validando super-combinação {i+1}...")
                
                validacoes_concurso = []
                for concurso in concursos_teste:
                    validacao = self.validar_super_combinacao(super_combinacao, concurso)
                    if 'erro' not in validacao:
                        validacoes_concurso.append(validacao)
                
                if validacoes_concurso:
                    # Estatísticas consolidadas
                    acertos_totais = [v['acertos'] for v in validacoes_concurso]
                    
                    validacao_consolidada = {
                        'super_combinacao_info': super_info,
                        'validacoes_individuais': validacoes_concurso,
                        'estatisticas': {
                            'acertos_maximo': max(acertos_totais),
                            'acertos_minimo': min(acertos_totais),
                            'acertos_medio': np.mean(acertos_totais),
                            'acertos_mediano': np.median(acertos_totais),
                            'desvio_padrao': np.std(acertos_totais),
                            'concursos_testados': len(concursos_teste),
                            'melhor_performance': max(v['performance_faixa'] for v in validacoes_concurso),
                            'performances_por_faixa': self._contar_performances(validacoes_concurso)
                        }
                    }
                    
                    validacoes_completas.append(validacao_consolidada)
            
            # Análise geral
            resultado_geral = self._analisar_validacoes_gerais(validacoes_completas)
            
            # Salva resultados
            self.salvar_validacao(validacoes_completas, resultado_geral, arquivo_path)
            
            return {
                'validacoes': validacoes_completas,
                'analise_geral': resultado_geral,
                'arquivo_origem': arquivo_path,
                'concursos_testados': concursos_teste
            }
            
        except Exception as e:
            return {'erro': f'Erro durante validação: {e}'}
    
    def _contar_performances(self, validacoes: List[Dict]) -> Dict:
        """Conta performances por faixa"""
        contador = defaultdict(int)
        for validacao in validacoes:
            contador[validacao['performance_faixa']] += 1
        return dict(contador)
    
    def _analisar_validacoes_gerais(self, validacoes: List[Dict]) -> Dict:
        """Análise geral de todas as validações"""
        if not validacoes:
            return {}
        
        # Coleta todas as estatísticas
        todos_acertos_maximos = []
        todos_acertos_medios = []
        todas_performances = []
        
        for val in validacoes:
            stats = val['estatisticas']
            todos_acertos_maximos.append(stats['acertos_maximo'])
            todos_acertos_medios.append(stats['acertos_medio'])
            
            for validacao_ind in val['validacoes_individuais']:
                todas_performances.append(validacao_ind['performance_faixa'])
        
        # Análise consolidada
        analise = {
            'total_super_combinacoes': len(validacoes),
            'performance_geral': {
                'melhor_acerto_geral': max(todos_acertos_maximos) if todos_acertos_maximos else 0,
                'acerto_maximo_medio': np.mean(todos_acertos_maximos) if todos_acertos_maximos else 0,
                'acerto_medio_geral': np.mean(todos_acertos_medios) if todos_acertos_medios else 0,
                'consistencia': np.std(todos_acertos_medios) if todos_acertos_medios else 0,
            },
            'distribuicao_performances': self._contar_performances_lista(todas_performances),
            'super_combinacao_destaque': self._identificar_melhor_super_combinacao(validacoes),
            'recomendacoes_ia': self._gerar_recomendacoes_aprendizado(validacoes)
        }
        
        return analise
    
    def _contar_performances_lista(self, performances: List[str]) -> Dict:
        """Conta performances de uma lista simples"""
        contador = defaultdict(int)
        for perf in performances:
            contador[perf] += 1
        return dict(contador)
    
    def _identificar_melhor_super_combinacao(self, validacoes: List[Dict]) -> Dict:
        """Identifica a super-combinação com melhor performance"""
        if not validacoes:
            return {}
        
        melhor = max(validacoes, 
                    key=lambda x: x['estatisticas']['acertos_maximo'])
        
        return {
            'combinacao': melhor['super_combinacao_info']['super_combinacao'],
            'acerto_maximo': melhor['estatisticas']['acertos_maximo'],
            'acerto_medio': melhor['estatisticas']['acertos_medio'],
            'performance_prevista': melhor['super_combinacao_info'].get('performance_prevista', 0),
            'confianca_ia': melhor['super_combinacao_info'].get('confianca_ia', 0)
        }
    
    def _gerar_recomendacoes_aprendizado(self, validacoes: List[Dict]) -> List[str]:
        """Gera recomendações baseadas nos resultados da validação"""
        recomendacoes = []
        
        if not validacoes:
            return recomendacoes
        
        # Análise dos resultados
        acertos_maximos = [v['estatisticas']['acertos_maximo'] for v in validacoes]
        acertos_medios = [v['estatisticas']['acertos_medio'] for v in validacoes]
        
        media_maximos = np.mean(acertos_maximos)
        media_medios = np.mean(acertos_medios)
        
        # Recomendações baseadas na performance
        if media_maximos < 10:
            recomendacoes.append("Performance baixa detectada. Considere retreinar o modelo com mais dados históricos.")
        
        if media_medios < 8:
            recomendacoes.append("Consistência baixa. Ajustar parâmetros de otimização da IA.")
        
        if np.std(acertos_maximos) > 3:
            recomendacoes.append("Alta variabilidade nos resultados. Revisar estratégia de geração de super-combinações.")
        
        # Análise de padrões
        todas_combinacoes = [v['super_combinacao_info']['super_combinacao'] for v in validacoes]
        if self._detectar_padrao_numeros_baixos(todas_combinacoes):
            recomendacoes.append("Detectado viés para números baixos. Balancear distribuição numérica.")
        
        if not recomendacoes:
            recomendacoes.append("Performance satisfatória. Continuar monitoramento.")
        
        return recomendacoes
    
    def _detectar_padrao_numeros_baixos(self, combinacoes: List[List[int]]) -> bool:
        """Detecta se há viés para números baixos"""
        todos_numeros = []
        for combinacao in combinacoes:
            todos_numeros.extend(combinacao)
        
        numeros_baixos = [n for n in todos_numeros if n <= 12]
        return len(numeros_baixos) / len(todos_numeros) > 0.6
    
    def salvar_validacao(self, validacoes: List[Dict], analise_geral: Dict,
                        arquivo_origem: str):
        """Salva resultados da validação"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"validacao_{timestamp}.json"
        arquivo_completo = os.path.join(self.pasta_validacao, nome_arquivo)
        
        dados_validacao = {
            'validado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'arquivo_origem': arquivo_origem,
            'validacoes_detalhadas': validacoes,
            'analise_geral': analise_geral,
            'configuracao_teste': {
                'total_super_combinacoes': len(validacoes),
                'concursos_testados': validacoes[0]['validacoes_individuais'] if validacoes else []
            }
        }
        
        try:
            # Salva JSON detalhado
            with open(arquivo_completo, 'w', encoding='utf-8') as f:
                json.dump(dados_validacao, f, indent=2, ensure_ascii=False)
            
            # Salva relatório em texto
            arquivo_txt = arquivo_completo.replace('.json', '_relatorio.txt')
            self._gerar_relatorio_texto(dados_validacao, arquivo_txt)
            
            print(f"✅ Validação salva:")
            print(f"   📄 Dados: {arquivo_completo}")
            print(f"   📄 Relatório: {arquivo_txt}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar validação: {e}")
    
    def _gerar_relatorio_texto(self, dados: Dict, arquivo_txt: str):
        """Gera relatório em texto legível"""
        with open(arquivo_txt, 'w', encoding='utf-8') as f:
            f.write("🎯 RELATÓRIO DE VALIDAÇÃO - SUPER-COMBINAÇÕES IA\n")
            f.write("=" * 65 + "\n")
            f.write(f"Validado em: {dados['validado_em']}\n")
            f.write(f"Arquivo origem: {dados['arquivo_origem']}\n\n")
            
            analise = dados['analise_geral']
            
            if analise:
                f.write("📊 PERFORMANCE GERAL:\n")
                f.write("-" * 30 + "\n")
                perf = analise['performance_geral']
                f.write(f"Melhor acerto geral: {perf.get('melhor_acerto_geral', 0)} números\n")
                f.write(f"Média dos máximos: {perf.get('acerto_maximo_medio', 0):.1f}\n")
                f.write(f"Média geral: {perf.get('acerto_medio_geral', 0):.1f}\n")
                f.write(f"Consistência: {perf.get('consistencia', 0):.2f}\n\n")
                
                f.write("🏆 SUPER-COMBINAÇÃO DESTAQUE:\n")
                f.write("-" * 35 + "\n")
                destaque = analise.get('super_combinacao_destaque', {})
                if destaque:
                    f.write(f"Combinação: {','.join(map(str, destaque.get('combinacao', [])))}\n")
                    f.write(f"Melhor acerto: {destaque.get('acerto_maximo', 0)}\n")
                    f.write(f"Média: {destaque.get('acerto_medio', 0):.1f}\n")
                    f.write(f"Performance prevista: {destaque.get('performance_prevista', 0):.1f}\n")
                    f.write(f"Confiança IA: {destaque.get('confianca_ia', 0):.1%}\n\n")
                
                f.write("💡 RECOMENDAÇÕES:\n")
                f.write("-" * 20 + "\n")
                for i, rec in enumerate(analise.get('recomendacoes_ia', []), 1):
                    f.write(f"{i}. {rec}\n")
                f.write("\n")
            
            # Detalhes por super-combinação
            f.write("📋 RESULTADOS DETALHADOS:\n")
            f.write("-" * 30 + "\n")
            
            for i, validacao in enumerate(dados['validacoes_detalhadas'], 1):
                stats = validacao['estatisticas']
                f.write(f"Super-combinação {i}:\n")
                f.write(f"  Máximo: {stats['acertos_maximo']} | ")
                f.write(f"Médio: {stats['acertos_medio']:.1f} | ")
                f.write(f"Mínimo: {stats['acertos_minimo']}\n")
                
                # Performances
                perfs = stats.get('performances_por_faixa', {})
                if perfs:
                    f.write(f"  Performances: ")
                    for faixa, count in perfs.items():
                        f.write(f"{faixa}({count}) ")
                    f.write("\n")
                
                f.write("\n")

def main():
    """Função principal"""
    print("🎯 VALIDADOR DE SUPER-COMBINAÇÕES IA")
    print("=" * 45)
    
    validador = ValidadorSuperCombinacoes()
    
    try:
        print("⚙️ OPÇÕES DISPONÍVEIS:")
        print("1. Validar arquivo de super-combinações")
        print("2. Validar super-combinação específica")
        print("3. Análise de tendências históricas")
        
        opcao = input("\nEscolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            print("\n🔍 VALIDAÇÃO DE ARQUIVO")
            
            # Lista arquivos disponíveis
            pasta_super = "combin_ia/super_combinacoes"
            if os.path.exists(pasta_super):
                arquivos = [f for f in os.listdir(pasta_super) if f.endswith('.json')]
                if arquivos:
                    print("📁 Arquivos disponíveis:")
                    for i, arq in enumerate(arquivos, 1):
                        print(f"   {i}. {arq}")
                    
                    idx = int(input("Escolha o arquivo (número): ")) - 1
                    if 0 <= idx < len(arquivos):
                        arquivo_path = os.path.join(pasta_super, arquivos[idx])
                    else:
                        print("❌ Opção inválida")
                        return
                else:
                    arquivo_path = input("Caminho completo do arquivo: ").strip()
            else:
                arquivo_path = input("Caminho completo do arquivo: ").strip()
            
            # Opção de concursos específicos
            usar_ultimos = input("Usar últimos 5 concursos? (s/n): ").lower().startswith('s')
            concursos_teste = None
            
            if not usar_ultimos:
                concursos_input = input("Números dos concursos (separados por vírgula): ").strip()
                if concursos_input:
                    concursos_teste = [int(x.strip()) for x in concursos_input.split(',')]
            
            # Executa validação
            resultado = validador.validar_arquivo_super_combinacoes(arquivo_path, concursos_teste)
            
            if 'erro' in resultado:
                print(f"❌ {resultado['erro']}")
            else:
                analise = resultado['analise_geral']
                print(f"\n🎉 VALIDAÇÃO CONCLUÍDA!")
                print(f"✅ {analise['total_super_combinacoes']} super-combinação(ões) testada(s)")
                
                perf = analise['performance_geral']
                print(f"🎯 Melhor acerto: {perf['melhor_acerto_geral']} números")
                print(f"📊 Média geral: {perf['acerto_medio_geral']:.1f}")
                
                destaque = analise.get('super_combinacao_destaque', {})
                if destaque:
                    print(f"\n🏆 MELHOR COMBINAÇÃO:")
                    print(f"   {','.join(map(str, destaque['combinacao']))}")
                    print(f"   Acerto máximo: {destaque['acerto_maximo']}")
        
        elif opcao == "2":
            print("\n🎯 VALIDAÇÃO ESPECÍFICA")
            combinacao_input = input("Digite a combinação (números separados por vírgula): ").strip()
            concurso = int(input("Número do concurso para testar: "))
            
            combinacao = [int(x.strip()) for x in combinacao_input.split(',')]
            
            validacao = validador.validar_super_combinacao(combinacao, concurso)
            
            if 'erro' in validacao:
                print(f"❌ {validacao['erro']}")
            else:
                print(f"\n📋 RESULTADO DA VALIDAÇÃO:")
                print(f"Combinação testada: {','.join(map(str, validacao['super_combinacao']))}")
                print(f"Resultado oficial: {','.join(map(str, validacao['resultado_oficial']))}")
                print(f"Acertos: {validacao['acertos']} ({validacao['performance_faixa']})")
                print(f"Taxa de acerto: {validacao['taxa_acerto']:.1%}")
                
                if validacao['numeros_acertados']:
                    print(f"Números acertados: {validacao['numeros_acertados']}")
                if validacao['numeros_errados']:
                    print(f"Números errados: {validacao['numeros_errados']}")
        
        elif opcao == "3":
            print("\n📈 ANÁLISE DE TENDÊNCIAS")
            print("Funcionalidade em desenvolvimento...")
        
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
