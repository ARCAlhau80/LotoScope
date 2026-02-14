#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 MONITOR DE APRENDIZADO DA IA
Sistema para rastrear e visualizar o progresso de aprendizado dos modelos de IA
- Histórico de treinamento
- Métricas de performance
- Evolução da precisão
- Comparação entre versões
- Dados de retroalimentação

Autor: AR CALHAU
Data: 22 de Agosto de 2025
"""

import json
import os
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any
import statistics
from collections import defaultdict, Counter
import numpy as np

class MonitorAprendizadoIA:
    """Monitor para rastrear o progresso de aprendizado da IA"""
    
    def __init__(self):
        self.pasta_base = "ia_repetidos"
        self.arquivo_historico = f"{self.pasta_base}/historico_aprendizado.json"
        self.arquivo_metricas = f"{self.pasta_base}/metricas_evolucao.json"
        self.arquivo_feedback = f"{self.pasta_base}/feedback_resultados.json"
        
        # Cria arquivos base se não existirem
        self._inicializar_arquivos()
    
    def _inicializar_arquivos(self):
        """Inicializa arquivos de monitoramento se não existirem"""
        os.makedirs(self.pasta_base, exist_ok=True)
        
        # Histórico de treinamento
        if not os.path.exists(self.arquivo_historico):
            historico_inicial = {
                "versao": "1.0",
                "data_criacao": datetime.now().isoformat(),
                "treinamentos": [],
                "modelo_atual": {
                    "data_treino": None,
                    "amostras_treinamento": 0,
                    "precisao_qtde": 0.0,
                    "precisao_posicao": 0.0
                }
            }
            self._salvar_json(self.arquivo_historico, historico_inicial)
        
        # Métricas de evolução
        if not os.path.exists(self.arquivo_metricas):
            metricas_inicial = {
                "evolucao_precisao": [],
                "evolucao_amostras": [],
                "marcos_importantes": [],
                "performance_por_periodo": {}
            }
            self._salvar_json(self.arquivo_metricas, metricas_inicial)
        
        # Feedback de resultados
        if not os.path.exists(self.arquivo_feedback):
            feedback_inicial = {
                "resultados_testados": [],
                "acertos_por_quantidade": {},
                "padroes_descobertos": [],
                "melhorias_identificadas": []
            }
            self._salvar_json(self.arquivo_feedback, feedback_inicial)
    
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
    
    def registrar_treinamento(self, dados_treinamento: Dict):
        """Registra um novo treinamento da IA"""
        historico = self._carregar_json(self.arquivo_historico)
        
        registro_treino = {
            "data": datetime.now().isoformat(),
            "amostras": dados_treinamento.get('amostras', 0),
            "precisao_qtde": dados_treinamento.get('precisao_qtde', 0.0),
            "precisao_posicao": dados_treinamento.get('precisao_posicao', 0.0),
            "tempo_treinamento": dados_treinamento.get('tempo_treinamento', 0),
            "versao_dados": dados_treinamento.get('versao_dados', '1.0'),
            "melhorias": dados_treinamento.get('melhorias', [])
        }
        
        historico["treinamentos"].append(registro_treino)
        historico["modelo_atual"] = registro_treino
        
        self._salvar_json(self.arquivo_historico, historico)
        self._atualizar_metricas(registro_treino)
        
        print(f"✅ Treinamento registrado: {registro_treino['precisao_qtde']:.1%} precisão (Qtde)")
    
    def _atualizar_metricas(self, registro_treino: Dict):
        """Atualiza métricas de evolução"""
        metricas = self._carregar_json(self.arquivo_metricas)
        
        # Evolução da precisão
        metricas["evolucao_precisao"].append({
            "data": registro_treino["data"],
            "precisao_qtde": registro_treino["precisao_qtde"],
            "precisao_posicao": registro_treino["precisao_posicao"]
        })
        
        # Evolução das amostras
        metricas["evolucao_amostras"].append({
            "data": registro_treino["data"],
            "amostras": registro_treino["amostras"]
        })
        
        # Marcos importantes (melhorias significativas)
        if len(metricas["evolucao_precisao"]) > 1:
            precisao_anterior = metricas["evolucao_precisao"][-2]["precisao_qtde"]
            precisao_atual = registro_treino["precisao_qtde"]
            
            if precisao_atual > precisao_anterior + 0.05:  # Melhoria de 5%+
                marco = {
                    "data": registro_treino["data"],
                    "tipo": "melhoria_significativa",
                    "descricao": f"Precisão aumentou de {precisao_anterior:.1%} para {precisao_atual:.1%}",
                    "ganho": precisao_atual - precisao_anterior
                }
                metricas["marcos_importantes"].append(marco)
        
        self._salvar_json(self.arquivo_metricas, metricas)
    
    def registrar_resultado_teste(self, dados_teste: Dict):
        """Registra resultado de um teste real das combinações"""
        feedback = self._carregar_json(self.arquivo_feedback)
        
        resultado = {
            "data_teste": datetime.now().isoformat(),
            "concurso": dados_teste.get('concurso'),
            "combinacoes_testadas": dados_teste.get('combinacoes_testadas', 0),
            "acertos_por_combinacao": dados_teste.get('acertos_por_combinacao', []),
            "meta_atingida": dados_teste.get('meta_11_acertos', False),
            "percentual_11_acertos": dados_teste.get('percentual_11_acertos', 0.0),
            "melhor_combinacao": dados_teste.get('melhor_combinacao', []),
            "max_acertos": dados_teste.get('max_acertos', 0)
        }
        
        feedback["resultados_testados"].append(resultado)
        
        # Atualiza estatísticas por quantidade de acertos
        qtd_acertos = str(resultado["max_acertos"])
        if qtd_acertos not in feedback["acertos_por_quantidade"]:
            feedback["acertos_por_quantidade"][qtd_acertos] = 0
        feedback["acertos_por_quantidade"][qtd_acertos] += 1
        
        self._salvar_json(self.arquivo_feedback, feedback)
        print(f"✅ Resultado teste registrado: {resultado['max_acertos']} acertos máximo")
    
    def analisar_arquivos_modelos(self) -> Dict:
        """Analisa os arquivos de modelo para extrair informações"""
        info_modelos = {}
        
        arquivos_modelo = [
            "modelo_qtde_repetidos.pkl",
            "modelo_mesma_posicao.pkl", 
            "estatisticas.pkl",
            "padroes_historicos.pkl",
            "scaler_features.pkl"
        ]
        
        for arquivo in arquivos_modelo:
            caminho = f"{self.pasta_base}/{arquivo}"
            if os.path.exists(caminho):
                stat = os.stat(caminho)
                info_modelos[arquivo] = {
                    "tamanho_mb": round(stat.st_size / (1024*1024), 2),
                    "ultima_modificacao": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "idade_horas": round((datetime.now().timestamp() - stat.st_mtime) / 3600, 1)
                }
        
        return info_modelos
    
    def gerar_relatorio_aprendizado(self) -> str:
        """Gera relatório completo do estado de aprendizado"""
        historico = self._carregar_json(self.arquivo_historico)
        metricas = self._carregar_json(self.arquivo_metricas)
        feedback = self._carregar_json(self.arquivo_feedback)
        info_modelos = self.analisar_arquivos_modelos()
        
        relatorio = []
        relatorio.append("🧠 RELATÓRIO DE APRENDIZADO DA IA")
        relatorio.append("=" * 60)
        relatorio.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        relatorio.append("")
        
        # Estado atual dos modelos
        relatorio.append("📊 ESTADO ATUAL DOS MODELOS:")
        relatorio.append("-" * 40)
        modelo_atual = historico.get("modelo_atual", {})
        if modelo_atual.get("data_treino"):
            data_treino = datetime.fromisoformat(modelo_atual["data_treino"])
            idade_modelo = datetime.now() - data_treino
            relatorio.append(f"• Último treinamento: {data_treino.strftime('%d/%m/%Y %H:%M')}")
            relatorio.append(f"• Idade do modelo: {idade_modelo.days} dias, {idade_modelo.seconds//3600} horas")
            relatorio.append(f"• Amostras de treinamento: {modelo_atual.get('amostras_treinamento', 0):,}")
            relatorio.append(f"• Precisão Qtde Repetidos: {modelo_atual.get('precisao_qtde', 0):.1%}")
            relatorio.append(f"• Precisão Mesma Posição: {modelo_atual.get('precisao_posicao', 0):.1%}")
        else:
            relatorio.append("• ⚠️ Nenhum treinamento registrado")
        
        relatorio.append("")
        
        # Informações dos arquivos
        relatorio.append("💾 ARQUIVOS DE MODELO:")
        relatorio.append("-" * 30)
        for arquivo, info in info_modelos.items():
            relatorio.append(f"• {arquivo}:")
            relatorio.append(f"  - Tamanho: {info['tamanho_mb']} MB")
            relatorio.append(f"  - Modificado: há {info['idade_horas']} horas")
        
        relatorio.append("")
        
        # Evolução do aprendizado
        relatorio.append("📈 EVOLUÇÃO DO APRENDIZADO:")
        relatorio.append("-" * 35)
        treinamentos = historico.get("treinamentos", [])
        if len(treinamentos) >= 2:
            primeiro = treinamentos[0]
            ultimo = treinamentos[-1]
            
            melhoria_qtde = ultimo["precisao_qtde"] - primeiro["precisao_qtde"]
            melhoria_pos = ultimo["precisao_posicao"] - primeiro["precisao_posicao"]
            
            relatorio.append(f"• Total de treinamentos: {len(treinamentos)}")
            relatorio.append(f"• Melhoria Precisão Qtde: {melhoria_qtde:+.1%}")
            relatorio.append(f"• Melhoria Precisão Posição: {melhoria_pos:+.1%}")
            
            # Últimos 5 treinamentos
            relatorio.append("\n🔍 ÚLTIMOS TREINAMENTOS:")
            for treino in treinamentos[-5:]:
                data = datetime.fromisoformat(treino["data"]).strftime("%d/%m %H:%M")
                relatorio.append(f"  {data}: {treino['precisao_qtde']:.1%} | {treino['precisao_posicao']:.1%}")
        else:
            relatorio.append("• Dados insuficientes para análise de evolução")
        
        relatorio.append("")
        
        # Marcos importantes
        marcos = metricas.get("marcos_importantes", [])
        if marcos:
            relatorio.append("🏆 MARCOS IMPORTANTES:")
            relatorio.append("-" * 25)
            for marco in marcos[-3:]:  # Últimos 3 marcos
                data = datetime.fromisoformat(marco["data"]).strftime("%d/%m %H:%M")
                relatorio.append(f"• {data}: {marco['descricao']}")
        
        relatorio.append("")
        
        # Resultados de testes
        resultados = feedback.get("resultados_testados", [])
        if resultados:
            relatorio.append("🎯 RESULTADOS DE TESTES REAIS:")
            relatorio.append("-" * 35)
            relatorio.append(f"• Total de testes: {len(resultados)}")
            
            acertos_max = [r["max_acertos"] for r in resultados if r.get("max_acertos")]
            if acertos_max:
                relatorio.append(f"• Máximo de acertos: {max(acertos_max)}")
                relatorio.append(f"• Média de acertos: {statistics.mean(acertos_max):.1f}")
            
            # Distribuição de acertos
            dist_acertos = feedback.get("acertos_por_quantidade", {})
            if dist_acertos:
                relatorio.append("\n📊 Distribuição de acertos:")
                for qtd, freq in sorted(dist_acertos.items(), key=lambda x: int(x[0]), reverse=True):
                    relatorio.append(f"  {qtd} acertos: {freq}x")
        
        relatorio.append("")
        
        # Recomendações
        relatorio.append("💡 RECOMENDAÇÕES:")
        relatorio.append("-" * 20)
        
        if modelo_atual.get("data_treino"):
            idade_modelo = (datetime.now() - datetime.fromisoformat(modelo_atual["data_treino"])).days
            if idade_modelo > 7:
                relatorio.append("• ⚠️ Modelo com mais de 7 dias - considere retreinamento")
            
            precisao_media = (modelo_atual.get("precisao_qtde", 0) + modelo_atual.get("precisao_posicao", 0)) / 2
            if precisao_media < 0.6:
                relatorio.append("• 📚 Precisão baixa - adicione mais dados de treinamento")
            elif precisao_media > 0.8:
                relatorio.append("• ✅ Modelo com boa precisão - continue monitorando")
        
        if len(resultados) < 5:
            relatorio.append("• 🧪 Poucos testes reais - execute mais validações")
        
        relatorio.append("")
        relatorio.append("=" * 60)
        
        return "\n".join(relatorio)
    
    def salvar_relatorio_aprendizado(self, nome_arquivo: Optional[str] = None) -> str:
        """Salva relatório de aprendizado em arquivo"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_aprendizado_ia_{timestamp}.txt"
        
        relatorio = self.gerar_relatorio_aprendizado()
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            
            print(f"✅ Relatório salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return ""
    
    def mostrar_status_aprendizado(self):
        """Mostra status resumido do aprendizado"""
        print("\n🧠 STATUS DE APRENDIZADO DA IA")
        print("=" * 50)
        
        historico = self._carregar_json(self.arquivo_historico)
        modelo_atual = historico.get("modelo_atual", {})
        
        if modelo_atual.get("data_treino"):
            data_treino = datetime.fromisoformat(modelo_atual["data_treino"])
            idade = datetime.now() - data_treino
            
            print(f"📅 Último treinamento: {data_treino.strftime('%d/%m/%Y %H:%M')}")
            print(f"⏰ Idade do modelo: {idade.days} dias, {idade.seconds//3600} horas")
            print(f"📊 Amostras de treinamento: {modelo_atual.get('amostras_treinamento', 0):,}")
            print(f"🎯 Precisão Qtde Repetidos: {modelo_atual.get('precisao_qtde', 0):.1%}")
            print(f"🎯 Precisão Mesma Posição: {modelo_atual.get('precisao_posicao', 0):.1%}")
            
            # Status baseado na precisão
            precisao_media = (modelo_atual.get("precisao_qtde", 0) + modelo_atual.get("precisao_posicao", 0)) / 2
            if precisao_media >= 0.8:
                print("✅ Status: MODELO EXCELENTE")
            elif precisao_media >= 0.6:
                print("🟡 Status: MODELO BOM")
            else:
                print("🔴 Status: MODELO PRECISA MELHORAR")
            
        else:
            print("⚠️ Nenhum modelo treinado encontrado")
            print("💡 Execute um treinamento para começar o aprendizado")
        
        # Informações dos arquivos
        info_modelos = self.analisar_arquivos_modelos()
        if info_modelos:
            print(f"\n💾 {len(info_modelos)} arquivos de modelo encontrados")
            tamanho_total = sum(info['tamanho_mb'] for info in info_modelos.values())
            print(f"📁 Tamanho total: {tamanho_total:.1f} MB")
        
        print("=" * 50)

def main():
    """Função principal para demonstrar o monitor"""
    print("📊 MONITOR DE APRENDIZADO DA IA")
    print("=" * 50)
    
    monitor = MonitorAprendizadoIA()
    
    try:
        opcao = input("\nEscolha uma opção:\n1 - Status resumido\n2 - Relatório completo\n3 - Salvar relatório\nOpção: ")
        
        if opcao == "1":
            monitor.mostrar_status_aprendizado()
            
        elif opcao == "2":
            relatorio = monitor.gerar_relatorio_aprendizado()
            print("\n" + relatorio)
            
        elif opcao == "3":
            arquivo = monitor.salvar_relatorio_aprendizado()
            if arquivo:
                print(f"\n✅ Relatório salvo em: {arquivo}")
            
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
