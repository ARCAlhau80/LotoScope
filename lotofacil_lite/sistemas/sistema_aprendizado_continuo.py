#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 SISTEMA DE APRENDIZADO CONTÍNUO
Sistema que integra registro, feedback e evolução em um ciclo contínuo
- Auto-registro de treinamentos
- Validação automática contra resultados reais  
- Evolução documentada automaticamente
- Dashboard consolidado de progresso

Autor: AR CALHAU
Data: 22 de Agosto de 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import statistics
from pathlib import Path

# Importa os sistemas especializados
try:
    from monitor_aprendizado_ia import MonitorAprendizadoIA
    from sistema_feedback_resultados import SistemaFeedbackResultados  
    from sistema_evolucao_documentada import SistemaEvolucaoDocumentada
except ImportError as e:
    print(f"⚠️ Erro ao importar sistemas: {e}")

class SistemaAprendizadoContinuo:
    """Sistema integrado de aprendizado contínuo"""
    
    def __init__(self):
        self.pasta_base = "ia_repetidos"
        self.arquivo_config = f"{self.pasta_base}/config_aprendizado_continuo.json"
        
        # Inicializa subsistemas
        try:
            self.monitor = MonitorAprendizadoIA()
            self.feedback = SistemaFeedbackResultados()
            self.evolucao = SistemaEvolucaoDocumentada()
        except:
            print("⚠️ Alguns subsistemas não puderam ser inicializados")
            self.monitor = None
            self.feedback = None
            self.evolucao = None
        
        self._inicializar_sistema()
    
    def _inicializar_sistema(self):
        """Inicializa configurações do sistema contínuo"""
        os.makedirs(self.pasta_base, exist_ok=True)
        
        if not os.path.exists(self.arquivo_config):
            config_inicial = {
                "sistema_ativo": True,
                "auto_backup": True,
                "auto_validacao": True,
                "intervalo_relatorios_dias": 7,
                "meta_precisao": 0.75,
                "meta_11_acertos_percentual": 0.30,
                "ultima_execucao": datetime.now().isoformat(),
                "configuracoes_avancadas": {
                    "max_backups": 10,
                    "dias_validacao": 30,
                    "threshold_melhoria": 0.05
                }
            }
            self._salvar_json(self.arquivo_config, config_inicial)
    
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
    
    def registrar_ciclo_completo_treinamento(self, dados_treinamento: Dict):
        """
        Registra um ciclo completo de treinamento em todos os sistemas
        dados_treinamento = {
            'versao_modelo': '1.2.0',
            'descricao_melhorias': 'Algoritmo X implementado',
            'metricas_performance': {...},
            'dados_treinamento': {...},
            'combinacoes_geradas': [...],  # Para futura validação
            'concurso_alvo': 3475
        }
        """
        print("🔄 Iniciando registro completo do ciclo de aprendizado...")
        
        sucesso_monitor = False
        sucesso_evolucao = False
        sucesso_previsao = False
        
        try:
            # 1. Registra no monitor básico
            if self.monitor:
                dados_monitor = {
                    'amostras': dados_treinamento.get('dados_treinamento', {}).get('total_amostras', 0),
                    'precisao_qtde': dados_treinamento.get('metricas_performance', {}).get('precisao_qtde', 0),
                    'precisao_posicao': dados_treinamento.get('metricas_performance', {}).get('precisao_posicao', 0),
                    'tempo_treinamento': dados_treinamento.get('metricas_performance', {}).get('tempo_treinamento', 0),
                    'melhorias': dados_treinamento.get('melhorias_implementadas', [])
                }
                self.monitor.registrar_treinamento(dados_monitor)
                sucesso_monitor = True
                print("   ✅ Registrado no sistema de monitoramento")
        except Exception as e:
            print(f"   ❌ Erro no monitor: {e}")
        
        try:
            # 2. Registra nova versão no sistema de evolução
            if self.evolucao:
                dados_versao = {
                    'versao': dados_treinamento.get('versao_modelo', f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    'descricao': dados_treinamento.get('descricao_melhorias', 'Treinamento automático'),
                    'melhorias': dados_treinamento.get('melhorias_implementadas', []),
                    'metricas_performance': dados_treinamento.get('metricas_performance', {}),
                    'arquivos_modelo': ['modelo_qtde_repetidos.pkl', 'modelo_mesma_posicao.pkl'],
                    'descobertas_associadas': dados_treinamento.get('descobertas', [])
                }
                self.evolucao.registrar_nova_versao(dados_versao)
                sucesso_evolucao = True
                print("   ✅ Nova versão registrada no sistema de evolução")
        except Exception as e:
            print(f"   ❌ Erro na evolução: {e}")
        
        try:
            # 3. Registra previsão para futura validação
            if self.feedback and dados_treinamento.get('combinacoes_geradas'):
                dados_previsao = {
                    'data_previsao': datetime.now().strftime('%Y-%m-%d'),
                    'concurso_alvo': dados_treinamento.get('concurso_alvo'),
                    'combinacoes_previstas': dados_treinamento.get('combinacoes_geradas', [])[:50], # Max 50 para teste
                    'modelo_usado': dados_treinamento.get('versao_modelo', 'ia_numeros_repetidos'),
                    'confianca': dados_treinamento.get('metricas_performance', {}).get('precisao_qtde', 0),
                    'parametros': dados_treinamento.get('parametros_modelo', {})
                }
                self.feedback.registrar_teste_previsao(dados_previsao)
                sucesso_previsao = True
                print("   ✅ Previsão registrada para validação futura")
        except Exception as e:
            print(f"   ❌ Erro no feedback: {e}")
        
        # Atualiza configurações
        config = self._carregar_json(self.arquivo_config)
        config["ultima_execucao"] = datetime.now().isoformat()
        self._salvar_json(self.arquivo_config, config)
        
        print(f"\n🎯 Ciclo completo registrado:")
        print(f"   Monitor: {'✅' if sucesso_monitor else '❌'}")
        print(f"   Evolução: {'✅' if sucesso_evolucao else '❌'}")  
        print(f"   Previsão: {'✅' if sucesso_previsao else '❌'}")
        
        return {
            "sucesso_geral": all([sucesso_monitor, sucesso_evolucao, sucesso_previsao]),
            "detalhes": {
                "monitor": sucesso_monitor,
                "evolucao": sucesso_evolucao,
                "previsao": sucesso_previsao
            }
        }
    
    def executar_validacao_automatica(self):
        """Executa validação automática de todas as previsões pendentes"""
        print("🔍 Executando validação automática...")
        
        try:
            if self.feedback:
                self.feedback.validar_previsoes_pendentes()
                print("   ✅ Validação de previsões concluída")
            else:
                print("   ❌ Sistema de feedback não disponível")
        except Exception as e:
            print(f"   ❌ Erro na validação: {e}")
    
    def gerar_dashboard_aprendizado(self) -> str:
        """Gera dashboard consolidado do estado do aprendizado"""
        dashboard = []
        dashboard.append("🎯 DASHBOARD DE APRENDIZADO CONTÍNUO")
        dashboard.append("=" * 55)
        dashboard.append(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        dashboard.append("")
        
        try:
            # Status dos sistemas
            dashboard.append("🔧 STATUS DOS SISTEMAS:")
            dashboard.append("-" * 30)
            dashboard.append(f"• Monitor IA: {'🟢 Ativo' if self.monitor else '🔴 Indisponível'}")
            dashboard.append(f"• Sistema Feedback: {'🟢 Ativo' if self.feedback else '🔴 Indisponível'}")
            dashboard.append(f"• Sistema Evolução: {'🟢 Ativo' if self.evolucao else '🔴 Indisponível'}")
            dashboard.append("")
            
            # Métricas do monitor
            if self.monitor:
                try:
                    # Carrega dados do monitor
                    historico_monitor = self.monitor._carregar_json(self.monitor.arquivo_historico)
                    modelo_atual = historico_monitor.get("modelo_atual", {})
                    
                    dashboard.append("🧠 STATUS DO MODELO ATUAL:")
                    dashboard.append("-" * 35)
                    if modelo_atual.get("data_treino"):
                        data_treino = datetime.fromisoformat(modelo_atual["data_treino"])
                        idade = datetime.now() - data_treino
                        dashboard.append(f"• Último treino: {data_treino.strftime('%d/%m/%Y %H:%M')}")
                        dashboard.append(f"• Idade: {idade.days} dias, {idade.seconds//3600}h")
                        dashboard.append(f"• Precisão Qtde: {modelo_atual.get('precisao_qtde', 0):.1%}")
                        dashboard.append(f"• Precisão Posição: {modelo_atual.get('precisao_posicao', 0):.1%}")
                        
                        # Análise da precisão
                        precisao_media = (modelo_atual.get('precisao_qtde', 0) + modelo_atual.get('precisao_posicao', 0)) / 2
                        if precisao_media >= 0.75:
                            status_modelo = "🟢 EXCELENTE"
                        elif precisao_media >= 0.6:
                            status_modelo = "🟡 BOM"
                        else:
                            status_modelo = "🔴 PRECISA MELHORAR"
                        dashboard.append(f"• Status: {status_modelo}")
                    else:
                        dashboard.append("• ⚠️ Nenhum modelo treinado")
                    dashboard.append("")
                    
                except Exception as e:
                    dashboard.append(f"• ❌ Erro ao ler dados do monitor: {e}")
                    dashboard.append("")
            
            # Estatísticas de feedback
            if self.feedback:
                try:
                    feedback_dados = self.feedback._carregar_json(self.feedback.arquivo_feedback)
                    estatisticas = feedback_dados.get("estatisticas_acertos", {})
                    testes = [t for t in feedback_dados.get("teste_previsoes", []) if t["status"] == "validado"]
                    
                    dashboard.append("📊 RESULTADOS DE VALIDAÇÃO:")
                    dashboard.append("-" * 35)
                    dashboard.append(f"• Testes validados: {len(testes)}")
                    dashboard.append(f"• Combinações testadas: {estatisticas.get('total_combinacoes_testadas', 0):,}")
                    
                    if estatisticas:
                        dashboard.append(f"• Precisão média: {estatisticas.get('precisao_media_geral', 0):.1%}")
                        dashboard.append(f"• Meta 11+ acertos: {estatisticas.get('percentual_11_acertos_medio', 0):.1%}")
                        
                        # Últimos resultados
                        if testes:
                            ultimos_3 = sorted(testes, key=lambda x: x.get("data_validacao", ""), reverse=True)[:3]
                            dashboard.append("• Últimos resultados:")
                            for teste in ultimos_3:
                                concurso = teste.get("concurso_alvo", "N/A")
                                precisao = teste.get("precisao_obtida", {})
                                melhor = precisao.get("melhor_combinacao", 0)
                                dashboard.append(f"  - Concurso {concurso}: {melhor} acertos max")
                    
                    # Previsões pendentes
                    pendentes = [t for t in feedback_dados.get("teste_previsoes", []) if t["status"] == "aguardando_resultado"]
                    dashboard.append(f"• Previsões pendentes: {len(pendentes)}")
                    dashboard.append("")
                    
                except Exception as e:
                    dashboard.append(f"• ❌ Erro ao ler dados de feedback: {e}")
                    dashboard.append("")
            
            # Evolução histórica
            if self.evolucao:
                try:
                    evolucao_dados = self.evolucao._carregar_json(self.evolucao.arquivo_evolucao)
                    metricas_evolucao = evolucao_dados.get("metricas_evolucao", {})
                    versoes = evolucao_dados.get("versoes_historico", [])
                    
                    dashboard.append("📈 EVOLUÇÃO HISTÓRICA:")
                    dashboard.append("-" * 30)
                    dashboard.append(f"• Versão atual: {evolucao_dados.get('versao_atual', 'N/A')}")
                    dashboard.append(f"• Total de versões: {len(versoes)}")
                    dashboard.append(f"• Total descobertas: {metricas_evolucao.get('total_descobertas', 0)}")
                    
                    # Progresso da precisão
                    precisao_inicial = metricas_evolucao.get('precisao_inicial', 0)
                    precisao_atual = metricas_evolucao.get('precisao_atual', 0)
                    if precisao_inicial > 0:
                        melhoria = ((precisao_atual - precisao_inicial) / precisao_inicial) * 100
                        dashboard.append(f"• Melhoria total: {melhoria:+.1f}%")
                    
                    dashboard.append(f"• Melhor precisão: {metricas_evolucao.get('melhor_precisao', 0):.1%}")
                    dashboard.append("")
                    
                except Exception as e:
                    dashboard.append(f"• ❌ Erro ao ler dados de evolução: {e}")
                    dashboard.append("")
            
            # Configurações do sistema
            config = self._carregar_json(self.arquivo_config)
            dashboard.append("⚙️ CONFIGURAÇÕES:")
            dashboard.append("-" * 20)
            dashboard.append(f"• Sistema ativo: {'🟢 Sim' if config.get('sistema_ativo', True) else '🔴 Não'}")
            dashboard.append(f"• Auto-backup: {'✅' if config.get('auto_backup', True) else '❌'}")
            dashboard.append(f"• Auto-validação: {'✅' if config.get('auto_validacao', True) else '❌'}")
            dashboard.append(f"• Meta precisão: {config.get('meta_precisao', 0.75):.1%}")
            dashboard.append(f"• Meta 11+ acertos: {config.get('meta_11_acertos_percentual', 0.30):.1%}")
            
            ultima_exec = config.get("ultima_execucao", "")
            if ultima_exec:
                data_exec = datetime.fromisoformat(ultima_exec)
                dashboard.append(f"• Última execução: {data_exec.strftime('%d/%m/%Y %H:%M')}")
            dashboard.append("")
            
            # Recomendações automáticas
            dashboard.append("💡 RECOMENDAÇÕES AUTOMÁTICAS:")
            dashboard.append("-" * 35)
            
            # Verifica idade do modelo
            if self.monitor:
                try:
                    historico_monitor = self.monitor._carregar_json(self.monitor.arquivo_historico)
                    modelo_atual = historico_monitor.get("modelo_atual", {})
                    if modelo_atual.get("data_treino"):
                        idade = datetime.now() - datetime.fromisoformat(modelo_atual["data_treino"])
                        if idade.days > 7:
                            dashboard.append("• 🔄 Modelo com mais de 7 dias - considere retreinamento")
                        elif idade.days > 3:
                            dashboard.append("• 🟡 Modelo com alguns dias - monitore performance")
                except:
                    pass
            
            # Verifica precisão
            try:
                if self.monitor:
                    historico_monitor = self.monitor._carregar_json(self.monitor.arquivo_historico)
                    modelo_atual = historico_monitor.get("modelo_atual", {})
                    precisao_atual = (modelo_atual.get('precisao_qtde', 0) + modelo_atual.get('precisao_posicao', 0)) / 2
                    
                    meta_precisao = config.get('meta_precisao', 0.75)
                    if precisao_atual < meta_precisao:
                        dashboard.append(f"• 📈 Precisão atual ({precisao_atual:.1%}) abaixo da meta ({meta_precisao:.1%})")
                    elif precisao_atual >= meta_precisao * 1.1:
                        dashboard.append("• ✅ Precisão excelente - continue estratégias atuais")
            except:
                pass
            
            # Verifica previsões pendentes
            try:
                if self.feedback:
                    feedback_dados = self.feedback._carregar_json(self.feedback.arquivo_feedback)
                    pendentes = [t for t in feedback_dados.get("teste_previsoes", []) if t["status"] == "aguardando_resultado"]
                    if len(pendentes) > 10:
                        dashboard.append(f"• 🔍 {len(pendentes)} previsões pendentes - execute validação")
            except:
                pass
            
            dashboard.append("")
            dashboard.append("=" * 55)
            
        except Exception as e:
            dashboard.append(f"❌ Erro ao gerar dashboard: {e}")
        
        return "\n".join(dashboard)
    
    def executar_manutencao_automatica(self):
        """Executa manutenção automática do sistema"""
        print("🔧 Executando manutenção automática...")
        
        config = self._carregar_json(self.arquivo_config)
        
        # 1. Validação automática se habilitada
        if config.get("auto_validacao", True):
            try:
                self.executar_validacao_automatica()
            except Exception as e:
                print(f"   ❌ Erro na validação automática: {e}")
        
        # 2. Limpeza de backups antigos
        if config.get("auto_backup", True):
            try:
                max_backups = config.get("configuracoes_avancadas", {}).get("max_backups", 10)
                self._limpar_backups_antigos(max_backups)
            except Exception as e:
                print(f"   ❌ Erro na limpeza de backups: {e}")
        
        # 3. Atualiza timestamp
        config["ultima_execucao"] = datetime.now().isoformat()
        self._salvar_json(self.arquivo_config, config)
        
        print("✅ Manutenção automática concluída")
    
    def _limpar_backups_antigos(self, max_backups: int):
        """Remove backups mais antigos mantendo apenas os últimos N"""
        if not self.evolucao or not os.path.exists(self.evolucao.pasta_backups):
            return
        
        backups = []
        for item in os.listdir(self.evolucao.pasta_backups):
            caminho = os.path.join(self.evolucao.pasta_backups, item)
            if os.path.isdir(caminho):
                # Obtém data de modificação
                stat_info = os.stat(caminho)
                backups.append((item, stat_info.st_mtime, caminho))
        
        # Ordena por data (mais recentes primeiro)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Remove backups excedentes
        removidos = 0
        for i, (nome, _, caminho) in enumerate(backups):
            if i >= max_backups:
                try:
                    import shutil
                    shutil.rmtree(caminho)
                    removidos += 1
                except Exception as e:
                    print(f"   ⚠️ Erro ao remover backup {nome}: {e}")
        
        if removidos > 0:
            print(f"   🗑️ {removidos} backups antigos removidos")
    
    def salvar_dashboard(self, nome_arquivo: Optional[str] = None) -> str:
        """Salva dashboard em arquivo"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"dashboard_aprendizado_{timestamp}.txt"
        
        dashboard = self.gerar_dashboard_aprendizado()
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(dashboard)
            
            print(f"✅ Dashboard salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar dashboard: {e}")
            return ""

def main():
    """Função principal para teste do sistema contínuo"""
    print("🔄 SISTEMA DE APRENDIZADO CONTÍNUO")
    print("=" * 50)
    
    sistema = SistemaAprendizadoContinuo()
    
    try:
        print("\nOpções disponíveis:")
        print("1 - Dashboard de aprendizado")
        print("2 - Salvar dashboard")
        print("3 - Executar validação automática")
        print("4 - Executar manutenção automática")
        print("5 - Registrar ciclo de treinamento (exemplo)")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            dashboard = sistema.gerar_dashboard_aprendizado()
            print("\n" + dashboard)
            
        elif opcao == "2":
            arquivo = sistema.salvar_dashboard()
            if arquivo:
                print(f"\n✅ Dashboard salvo: {arquivo}")
                
        elif opcao == "3":
            sistema.executar_validacao_automatica()
            
        elif opcao == "4":
            sistema.executar_manutencao_automatica()
            
        elif opcao == "5":
            # Exemplo de registro completo
            dados_exemplo = {
                'versao_modelo': '1.3.0',
                'descricao_melhorias': 'Implementação de aprendizado contínuo',
                'melhorias_implementadas': ['Sistema de feedback', 'Validação automática'],
                'metricas_performance': {
                    'precisao_qtde': 0.78,
                    'precisao_posicao': 0.71,
                    'tempo_treinamento': 95,
                    'total_amostras': 6000
                },
                'combinacoes_geradas': [[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]] * 20,  # Exemplo
                'concurso_alvo': 3476,
                'descobertas': ['Padrão contínuo confirmado']
            }
            resultado = sistema.registrar_ciclo_completo_treinamento(dados_exemplo)
            print(f"\nResultado: {resultado}")
        
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
