#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 SISTEMA DE FEEDBACK DE RESULTADOS
Sistema para registrar e analisar resultados das previsões da IA
- Validação automática contra concursos reais
- Cálculo de precisão das previsões
- Feedback contínuo para melhoria dos modelos
- Histórico completo de performance

Autor: AR CALHAU
Data: 22 de Agosto de 2025
"""

import json
import os
import sys
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

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
from collections import defaultdict, Counter
import numpy as np
from database_config import db_config

class SistemaFeedbackResultados:
    """Sistema para registrar e analisar feedback de resultados das previsões da IA"""
    
    def __init__(self):
        self.pasta_base = "ia_repetidos"
        self.arquivo_feedback = f"{self.pasta_base}/feedback_detalhado.json"
        self.arquivo_evolucao = f"{self.pasta_base}/evolucao_performance.json"
        self.arquivo_padroes = f"{self.pasta_base}/padroes_descobertos.json"
        
        # Cria estrutura
        self._inicializar_sistema()
    
    def _inicializar_sistema(self):
        """Inicializa sistema de feedback"""
        os.makedirs(self.pasta_base, exist_ok=True)
        
        # Arquivo de feedback detalhado
        if not os.path.exists(self.arquivo_feedback):
            feedback_inicial = {
                "versao": "1.0",
                "data_criacao": datetime.now().isoformat(),
                "teste_previsoes": [],
                "estatisticas_acertos": {},
                "precisao_por_periodo": {},
                "melhorias_identificadas": []
            }
            self._salvar_json(self.arquivo_feedback, feedback_inicial)
        
        # Arquivo de evolução
        if not os.path.exists(self.arquivo_evolucao):
            evolucao_inicial = {
                "marcos_evolucao": [],
                "graficos_performance": {
                    "precisao_temporal": [],
                    "acertos_por_mes": [],
                    "melhoria_continua": []
                },
                "comparativo_modelos": []
            }
            self._salvar_json(self.arquivo_evolucao, evolucao_inicial)
        
        # Arquivo de padrões descobertos
        if not os.path.exists(self.arquivo_padroes):
            padroes_inicial = {
                "padroes_validados": [],
                "hipoteses_testadas": [],
                "descobertas_importantes": [],
                "correlacoes_confirmadas": []
            }
            self._salvar_json(self.arquivo_padroes, padroes_inicial)
    
    def _salvar_json(self, arquivo: str, dados: Dict):
        """Salva dados em JSON"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"❌ Erro ao salvar {arquivo}: {e}")
    
    def _carregar_json(self, arquivo: str) -> Dict:
        """Carrega dados de JSON"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar {arquivo}: {e}")
            return {}
    
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
    
    def obter_concursos_recentes(self, dias_atras: int = 30) -> List[Dict]:
        """Obtém concursos dos últimos X dias para validação"""
        conn = self.conectar_base()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Data limite
            data_limite = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
            
            query = """
            SELECT Concurso, Data_Sorteio, N1, N2, N3, N4, N5, N6, N7, N8, 
                   N9, N10, N11, N12, N13, N14, N15
            FROM Resultados_INT 
            WHERE Data_Sorteio >= ?
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query, data_limite)
            resultados = cursor.fetchall()
            
            concursos = []
            for row in resultados:
                concurso = {
                    'concurso': row[0],
                    'data': row[1].strftime('%Y-%m-%d') if row[1] else None,
                    'numeros': [row[i] for i in range(2, 17) if row[i] is not None]
                }
                concursos.append(concurso)
            
            return concursos
            
        except Exception as e:
            print(f"❌ Erro ao obter concursos: {e}")
            return []
        finally:
            conn.close()
    
    def registrar_teste_previsao(self, dados_previsao: Dict):
        """
        Registra um teste de previsão para validação futura
        dados_previsao = {
            'data_previsao': '2025-08-22',
            'concurso_alvo': 3475,
            'combinacoes_previstas': [[1,2,3...], [4,5,6...]],
            'modelo_usado': 'ia_numeros_repetidos',
            'confianca': 0.85,
            'parametros': {...}
        }
        """
        feedback = self._carregar_json(self.arquivo_feedback)
        
        teste = {
            "id": len(feedback["teste_previsoes"]) + 1,
            "data_registro": datetime.now().isoformat(),
            "data_previsao": dados_previsao.get('data_previsao'),
            "concurso_alvo": dados_previsao.get('concurso_alvo'),
            "combinacoes_previstas": dados_previsao.get('combinacoes_previstas', []),
            "modelo_usado": dados_previsao.get('modelo_usado'),
            "confianca_previsao": dados_previsao.get('confianca', 0.0),
            "parametros_modelo": dados_previsao.get('parametros', {}),
            "status": "aguardando_resultado",
            "resultado_real": None,
            "precisao_obtida": None,
            "acertos_por_combinacao": [],
            "analise_pos_resultado": {}
        }
        
        feedback["teste_previsoes"].append(teste)
        self._salvar_json(self.arquivo_feedback, feedback)
        
        print(f"✅ Previsão registrada: Concurso {teste['concurso_alvo']} com {len(teste['combinacoes_previstas'])} combinações")
    
    def validar_previsoes_pendentes(self):
        """Valida previsões contra resultados reais disponíveis"""
        print("🔍 Verificando previsões pendentes...")
        
        feedback = self._carregar_json(self.arquivo_feedback)
        concursos_recentes = self.obter_concursos_recentes(60)  # 2 meses
        
        concursos_dict = {c['concurso']: c for c in concursos_recentes}
        
        validacoes_realizadas = 0
        
        for teste in feedback["teste_previsoes"]:
            if teste["status"] == "aguardando_resultado":
                concurso_alvo = teste["concurso_alvo"]
                
                if concurso_alvo in concursos_dict:
                    resultado = concursos_dict[concurso_alvo]
                    self._validar_previsao_individual(teste, resultado)
                    validacoes_realizadas += 1
        
        if validacoes_realizadas > 0:
            self._salvar_json(self.arquivo_feedback, feedback)
            self._atualizar_estatisticas_globais()
            print(f"✅ {validacoes_realizadas} previsões validadas!")
        else:
            print("ℹ️ Nenhuma previsão pendente para validar")
    
    def _validar_previsao_individual(self, teste: Dict, resultado_real: Dict):
        """Valida uma previsão individual contra o resultado real"""
        numeros_sorteados = set(resultado_real['numeros'])
        combinacoes_previstas = teste["combinacoes_previstas"]
        
        acertos_por_combinacao = []
        total_acertos = 0
        melhor_resultado = 0
        
        for combinacao in combinacoes_previstas:
            numeros_combinacao = set(combinacao)
            acertos = len(numeros_combinacao.intersection(numeros_sorteados))
            acertos_por_combinacao.append(acertos)
            total_acertos += acertos
            melhor_resultado = max(melhor_resultado, acertos)
        
        # Calcula precisão
        if combinacoes_previstas:
            precisao_media = total_acertos / (len(combinacoes_previstas) * 15)
            precisao_melhor = melhor_resultado / 15
        else:
            precisao_media = 0.0
            precisao_melhor = 0.0
        
        # Meta de 11+ acertos
        combinacoes_11_acertos = sum(1 for a in acertos_por_combinacao if a >= 11)
        percentual_11_acertos = combinacoes_11_acertos / len(combinacoes_previstas) if combinacoes_previstas else 0
        
        # Atualiza o teste
        teste["status"] = "validado"
        teste["resultado_real"] = resultado_real['numeros']
        teste["precisao_obtida"] = {
            "precisao_media": precisao_media,
            "precisao_melhor": precisao_melhor,
            "media_acertos": statistics.mean(acertos_por_combinacao) if acertos_por_combinacao else 0,
            "melhor_combinacao": melhor_resultado,
            "combinacoes_11_acertos": combinacoes_11_acertos,
            "percentual_11_acertos": percentual_11_acertos
        }
        teste["acertos_por_combinacao"] = acertos_por_combinacao
        teste["data_validacao"] = datetime.now().isoformat()
        
        # Análise pós-resultado
        teste["analise_pos_resultado"] = self._analisar_resultado_detalhado(
            combinacoes_previstas, resultado_real['numeros'], teste["parametros_modelo"]
        )
        
        print(f"   Concurso {teste['concurso_alvo']}: Melhor resultado {melhor_resultado} acertos")
    
    def _analisar_resultado_detalhado(self, combinacoes: List, resultado: List, parametros: Dict) -> Dict:
        """Análise detalhada do resultado para identificar padrões"""
        analise = {
            "numeros_mais_acertados": {},
            "posicoes_mais_certeiras": {},
            "padroes_identificados": [],
            "sugestoes_melhoria": []
        }
        
        # Análise de números mais acertados
        contador_acertos = Counter()
        resultado_set = set(resultado)
        
        for combinacao in combinacoes:
            for numero in combinacao:
                if numero in resultado_set:
                    contador_acertos[numero] += 1
        
        analise["numeros_mais_acertados"] = dict(contador_acertos.most_common(10))
        
        # Análise de posições
        for i, num_resultado in enumerate(resultado):
            posicao_ordenada = i + 1
            acertos_posicao = 0
            
            for combinacao in combinacoes:
                combinacao_ordenada = sorted(combinacao)
                if posicao_ordenada <= len(combinacao_ordenada):
                    if combinacao_ordenada[posicao_ordenada - 1] == num_resultado:
                        acertos_posicao += 1
            
            analise["posicoes_mais_certeiras"][f"posicao_{posicao_ordenada}"] = acertos_posicao
        
        # Identifica padrões específicos
        if contador_acertos:
            numeros_frequentes = [num for num, freq in contador_acertos.items() if freq >= len(combinacoes) * 0.3]
            if numeros_frequentes:
                analise["padroes_identificados"].append({
                    "tipo": "numeros_frequentes_acertados",
                    "numeros": numeros_frequentes,
                    "importancia": "alta"
                })
        
        # Sugestões de melhoria
        if len(contador_acertos) < 5:
            analise["sugestoes_melhoria"].append("Diversificar mais os números nas combinações")
        
        acertos_medio = statistics.mean([len(set(comb).intersection(resultado_set)) for comb in combinacoes])
        if acertos_medio < 8:
            analise["sugestoes_melhoria"].append("Revisar pesos dos números nos modelos preditivos")
        
        return analise
    
    def _atualizar_estatisticas_globais(self):
        """Atualiza estatísticas globais baseadas nos resultados validados"""
        feedback = self._carregar_json(self.arquivo_feedback)
        
        testes_validados = [t for t in feedback["teste_previsoes"] if t["status"] == "validado"]
        
        if not testes_validados:
            return
        
        # Estatísticas de acertos
        distribuicao_acertos = Counter()
        precisoes_medias = []
        precisoes_melhores = []
        percentuais_11_acertos = []
        
        for teste in testes_validados:
            precisao = teste.get("precisao_obtida", {})
            
            # Distribuição de acertos
            for acertos in teste.get("acertos_por_combinacao", []):
                distribuicao_acertos[acertos] += 1
            
            # Métricas de precisão
            if "precisao_media" in precisao:
                precisoes_medias.append(precisao["precisao_media"])
            if "precisao_melhor" in precisao:
                precisoes_melhores.append(precisao["precisao_melhor"])
            if "percentual_11_acertos" in precisao:
                percentuais_11_acertos.append(precisao["percentual_11_acertos"])
        
        # Calcula estatísticas agregadas
        estatisticas = {
            "total_testes_validados": len(testes_validados),
            "total_combinacoes_testadas": sum(len(t["combinacoes_previstas"]) for t in testes_validados),
            "distribuicao_acertos": dict(distribuicao_acertos),
            "precisao_media_geral": statistics.mean(precisoes_medias) if precisoes_medias else 0,
            "precisao_melhor_geral": statistics.mean(precisoes_melhores) if precisoes_melhores else 0,
            "percentual_11_acertos_medio": statistics.mean(percentuais_11_acertos) if percentuais_11_acertos else 0,
            "data_ultima_atualizacao": datetime.now().isoformat()
        }
        
        feedback["estatisticas_acertos"] = estatisticas
        self._salvar_json(self.arquivo_feedback, feedback)
    
    def gerar_relatorio_evolucao(self) -> str:
        """Gera relatório detalhado da evolução da IA"""
        feedback = self._carregar_json(self.arquivo_feedback)
        evolucao = self._carregar_json(self.arquivo_evolucao)
        padroes = self._carregar_json(self.arquivo_padroes)
        
        relatorio = []
        relatorio.append("📊 RELATÓRIO DE EVOLUÇÃO DO APRENDIZADO DA IA")
        relatorio.append("=" * 65)
        relatorio.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        relatorio.append("")
        
        # Estatísticas gerais
        estatisticas = feedback.get("estatisticas_acertos", {})
        if estatisticas:
            relatorio.append("📈 ESTATÍSTICAS GERAIS:")
            relatorio.append("-" * 30)
            relatorio.append(f"• Testes validados: {estatisticas.get('total_testes_validados', 0)}")
            relatorio.append(f"• Combinações testadas: {estatisticas.get('total_combinacoes_testadas', 0):,}")
            relatorio.append(f"• Precisão média geral: {estatisticas.get('precisao_media_geral', 0):.1%}")
            relatorio.append(f"• Meta 11+ acertos: {estatisticas.get('percentual_11_acertos_medio', 0):.1%}")
            relatorio.append("")
        
        # Distribuição de acertos
        distribuicao = estatisticas.get("distribuicao_acertos", {})
        if distribuicao:
            relatorio.append("🎯 DISTRIBUIÇÃO DE ACERTOS:")
            relatorio.append("-" * 35)
            total_combinacoes = sum(distribuicao.values())
            
            for acertos in sorted(distribuicao.keys(), key=int, reverse=True):
                freq = distribuicao[acertos]
                percentual = (freq / total_combinacoes) * 100 if total_combinacoes > 0 else 0
                relatorio.append(f"• {acertos} acertos: {freq:,} vezes ({percentual:.1f}%)")
            relatorio.append("")
        
        # Testes recentes
        testes_validados = [t for t in feedback.get("teste_previsoes", []) if t["status"] == "validado"]
        if testes_validados:
            relatorio.append("🔍 ÚLTIMOS TESTES VALIDADOS:")
            relatorio.append("-" * 35)
            
            for teste in sorted(testes_validados, key=lambda x: x.get("data_validacao", ""), reverse=True)[:5]:
                concurso = teste.get("concurso_alvo", "N/A")
                precisao = teste.get("precisao_obtida", {})
                melhor = precisao.get("melhor_combinacao", 0)
                media = precisao.get("media_acertos", 0)
                data_val = teste.get("data_validacao", "")
                
                if data_val:
                    data_formatada = datetime.fromisoformat(data_val).strftime("%d/%m")
                    relatorio.append(f"• {data_formatada} - Concurso {concurso}: {melhor} max, {media:.1f} média")
            relatorio.append("")
        
        # Padrões descobertos
        padroes_validados = padroes.get("padroes_validados", [])
        if padroes_validados:
            relatorio.append("🧩 PADRÕES DESCOBERTOS E VALIDADOS:")
            relatorio.append("-" * 40)
            for padrao in padroes_validados[-3:]:  # Últimos 3
                relatorio.append(f"• {padrao.get('descricao', 'Padrão sem descrição')}")
                relatorio.append(f"  Confiança: {padrao.get('confianca', 0):.1%}")
            relatorio.append("")
        
        # Melhorias identificadas
        melhorias = feedback.get("melhorias_identificadas", [])
        if melhorias:
            relatorio.append("💡 MELHORIAS IDENTIFICADAS:")
            relatorio.append("-" * 30)
            for melhoria in melhorias[-5:]:  # Últimas 5
                relatorio.append(f"• {melhoria}")
            relatorio.append("")
        
        # Recomendações baseadas nos dados
        relatorio.append("🎯 RECOMENDAÇÕES PARA PRÓXIMAS ITERAÇÕES:")
        relatorio.append("-" * 45)
        
        if estatisticas.get("precisao_media_geral", 0) < 0.5:
            relatorio.append("• 🔴 Precisão baixa - Revisar algoritmos de predição")
            relatorio.append("• 📚 Adicionar mais dados históricos ao treinamento")
        elif estatisticas.get("precisao_media_geral", 0) < 0.7:
            relatorio.append("• 🟡 Precisão moderada - Ajustar pesos dos fatores")
            relatorio.append("• ⚙️ Implementar fine-tuning nos modelos")
        else:
            relatorio.append("• ✅ Precisão boa - Manter estratégias atuais")
            relatorio.append("• 🚀 Explorar técnicas avançadas para otimização")
        
        if estatisticas.get("percentual_11_acertos_medio", 0) < 0.3:
            relatorio.append("• 🎯 Focar em estratégias para atingir meta de 11+ acertos")
            
        relatorio.append("")
        relatorio.append("=" * 65)
        
        return "\n".join(relatorio)
    
    def salvar_relatorio_evolucao(self, nome_arquivo: Optional[str] = None) -> str:
        """Salva relatório de evolução"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"evolucao_aprendizado_ia_{timestamp}.txt"
        
        relatorio = self.gerar_relatorio_evolucao()
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            
            print(f"✅ Relatório de evolução salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return ""
    
    def descobrir_padrao(self, descricao: str, dados_suporte: Dict, confianca: float = 0.5):
        """Registra um novo padrão descoberto"""
        padroes = self._carregar_json(self.arquivo_padroes)
        
        padrao = {
            "data_descoberta": datetime.now().isoformat(),
            "descricao": descricao,
            "dados_suporte": dados_suporte,
            "confianca": confianca,
            "status": "descoberto",
            "testes_validacao": []
        }
        
        padroes["padroes_validados"].append(padrao)
        self._salvar_json(self.arquivo_padroes, padroes)
        
        print(f"✅ Padrão registrado: {descricao} (Confiança: {confianca:.1%})")

def main():
    """Função principal para teste do sistema"""
    print("📊 SISTEMA DE FEEDBACK DE RESULTADOS")
    print("=" * 50)
    
    sistema = SistemaFeedbackResultados()
    
    try:
        print("\nOpções disponíveis:")
        print("1 - Validar previsões pendentes")
        print("2 - Gerar relatório de evolução")
        print("3 - Salvar relatório de evolução")
        print("4 - Listar concursos recentes")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            sistema.validar_previsoes_pendentes()
            
        elif opcao == "2":
            relatorio = sistema.gerar_relatorio_evolucao()
            print("\n" + relatorio)
            
        elif opcao == "3":
            arquivo = sistema.salvar_relatorio_evolucao()
            if arquivo:
                print(f"\n✅ Relatório salvo: {arquivo}")
                
        elif opcao == "4":
            concursos = sistema.obter_concursos_recentes(30)
            print(f"\n📅 {len(concursos)} concursos dos últimos 30 dias:")
            for c in concursos[:10]:
                print(f"   Concurso {c['concurso']}: {c['data']} - {c['numeros'][:5]}...")
        
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
