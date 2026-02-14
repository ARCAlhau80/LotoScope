#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 PIPELINE INTEGRADO DE SUPER-COMBINAÇÕES IA
Sistema completo que integra:
1. Geração de dataset histórico
2. Treinamento da IA
3. Geração de super-combinações
4. Validação automática
5. Aprendizado contínuo

Autor: AR CALHAU
Data: 20 de Agosto de 2025
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'geradores'))
sys.path.insert(0, str(_BASE_DIR / 'validadores'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))

# Imports dos módulos locais
try:
    from gerador_dataset_historico import GeradorDatasetHistorico
    from super_combinacao_ia import SuperCombinacaoIA
    from validador_super_combinacoes import ValidadorSuperCombinacoes
    from gerador_academico_dinamico import GeradorAcademicoDinamico
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos estão no mesmo diretório")
    sys.exit(1)

class PipelineSuperCombinacoesIA:
    """Pipeline integrado para geração e validação de super-combinações"""
    
    def __init__(self, db_path: str = "lotofacil.db"):
        self.db_path = db_path
        self.pasta_pipeline = "combin_ia/pipeline"
        self.pasta_logs = "combin_ia/logs"
        
        # Cria pastas necessárias
        for pasta in [self.pasta_pipeline, self.pasta_logs]:
            os.makedirs(pasta, exist_ok=True)
        
        # Inicializa componentes
        self.gerador_dataset = GeradorDatasetHistorico()
        self.super_ia = SuperCombinacaoIA()
        self.validador = ValidadorSuperCombinacoes(db_path)
        self.gerador_dinamico = GeradorAcademicoDinamico()
        
        # Log de operações
        self.log_operacoes = []
        
    def log(self, mensagem: str, tipo: str = "INFO"):
        """Adiciona entrada ao log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada_log = {
            'timestamp': timestamp,
            'tipo': tipo,
            'mensagem': mensagem
        }
        self.log_operacoes.append(entrada_log)
        print(f"[{timestamp}] {tipo}: {mensagem}")
    
    def verificar_prerequisites(self) -> Dict[str, bool]:
        """Verifica se todos os pré-requisitos estão atendidos"""
        self.log("Verificando pré-requisitos do sistema...")
        
        # Testa conexão com banco usando database_config
        banco_ok = False
        try:
            from database_config import db_config
            banco_ok = db_config.test_connection()
        except Exception as e:
            self.log(f"Erro ao testar banco: {e}", "WARNING")
        
        status = {
            'banco_dados': banco_ok,
            'diretorios': all(os.path.exists(pasta) for pasta in [
                "combin_ia/datasets",
                "combin_ia/modelos", 
                "combin_ia/super_combinacoes",
                "combin_ia/validacao"
            ]),
            'modelo_treinado': os.path.exists("combin_ia/modelos/modelo_super_combinacao.pkl"),
            'datasets_historicos': len([f for f in os.listdir("combin_ia/datasets") 
                                      if f.endswith('.json')]) > 0 if os.path.exists("combin_ia/datasets") else False
        }
        
        for item, ok in status.items():
            status_str = "✅ OK" if ok else "❌ FALTANDO"
            self.log(f"  {item}: {status_str}")
        
        return status
    
    def preparar_ambiente(self, force_dataset: bool = False, 
                         force_treinamento: bool = False) -> bool:
        """Prepara o ambiente executando passos necessários"""
        self.log("🔧 PREPARANDO AMBIENTE", "SETUP")
        
        status = self.verificar_prerequisites()
        
        # Gera datasets históricos se necessário
        if not status['datasets_historicos'] or force_dataset:
            self.log("Gerando datasets históricos...")
            try:
                # Gera datasets para os últimos 250 concursos (otimizado pela análise de janela)
                self.gerador_dataset.processar_concursos_automatico(
                    quantidade_concursos=250,
                    qtd_combinacoes_por_concurso=50
                )
                self.log("✅ Datasets históricos gerados", "SUCCESS")
            except Exception as e:
                self.log(f"❌ Erro ao gerar datasets: {e}", "ERROR")
                return False
        
        # Treina modelo se necessário
        if not status['modelo_treinado'] or force_treinamento:
            self.log("Treinando modelo de IA...")
            try:
                self.super_ia.treinar_modelo(force_retrain=force_treinamento)
                self.log("✅ Modelo de IA treinado", "SUCCESS")
            except Exception as e:
                self.log(f"❌ Erro ao treinar modelo: {e}", "ERROR")
                return False
        
        self.log("✅ Ambiente preparado com sucesso", "SUCCESS")
        return True
    
    def executar_pipeline_completo(self, 
                                  origem_combinacoes: str = "dinamico",
                                  quantidade_combinacoes: int = 100,
                                  quantidade_super: int = 3,
                                  validar_automatico: bool = True) -> Dict:
        """Executa o pipeline completo"""
        
        self.log("🚀 INICIANDO PIPELINE COMPLETO DE SUPER-COMBINAÇÕES", "PIPELINE")
        
        resultado_pipeline = {
            'iniciado_em': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'configuracao': {
                'origem_combinacoes': origem_combinacoes,
                'quantidade_combinacoes': quantidade_combinacoes,
                'quantidade_super': quantidade_super,
                'validar_automatico': validar_automatico
            },
            'etapas_executadas': [],
            'arquivos_gerados': [],
            'resultados': {}
        }
        
        try:
            # ETAPA 1: Obter combinações base
            self.log("ETAPA 1: Obtendo combinações base...")
            
            if origem_combinacoes == "dinamico":
                # Gera combinações usando o sistema dinâmico
                combinacoes_base = self._gerar_combinacoes_dinamico(quantidade_combinacoes)
                arquivo_base = self._salvar_combinacoes_temporarias(combinacoes_base, "dinamico")
            else:
                # Usa arquivo fornecido
                arquivo_base = origem_combinacoes
                combinacoes_base = self.super_ia.ler_combinacoes_arquivo(arquivo_base)
            
            if not combinacoes_base:
                raise Exception("Nenhuma combinação base obtida")
            
            self.log(f"✅ {len(combinacoes_base)} combinações base obtidas")
            resultado_pipeline['etapas_executadas'].append("combinacoes_base")
            resultado_pipeline['resultados']['combinacoes_base'] = len(combinacoes_base)
            
            # ETAPA 2: Gerar super-combinações com IA
            self.log("ETAPA 2: Gerando super-combinações com IA...")
            
            super_combinacoes = self.super_ia.gerar_super_combinacao(
                combinacoes_base, quantidade_super
            )
            
            if not super_combinacoes:
                raise Exception("Falha na geração de super-combinações")
            
            # Salva super-combinações
            arquivo_super = self.super_ia.salvar_super_combinacoes(
                super_combinacoes, f"pipeline_{origem_combinacoes}"
            )
            
            self.log(f"✅ {len(super_combinacoes)} super-combinação(ões) gerada(s)")
            resultado_pipeline['etapas_executadas'].append("super_combinacoes")
            resultado_pipeline['arquivos_gerados'].append(arquivo_super)
            resultado_pipeline['resultados']['super_combinacoes'] = super_combinacoes
            
            # ETAPA 3: Validação automática (se solicitada)
            if validar_automatico:
                self.log("ETAPA 3: Validando super-combinações...")
                
                validacao = self.validador.validar_arquivo_super_combinacoes(arquivo_super)
                
                if 'erro' not in validacao:
                    self.log("✅ Validação concluída")
                    resultado_pipeline['etapas_executadas'].append("validacao")
                    resultado_pipeline['resultados']['validacao'] = validacao['analise_geral']
                    
                    # Mostra resultado da validação
                    analise = validacao['analise_geral']
                    perf = analise['performance_geral']
                    self.log(f"📊 Melhor acerto: {perf.get('melhor_acerto_geral', 0)} números")
                    self.log(f"📊 Média geral: {perf.get('acerto_medio_geral', 0):.1f}")
                else:
                    self.log(f"⚠️ Erro na validação: {validacao['erro']}", "WARNING")
            
            # ETAPA 4: Relatório final
            self.log("ETAPA 4: Gerando relatório final...")
            arquivo_relatorio = self._gerar_relatorio_pipeline(resultado_pipeline)
            resultado_pipeline['arquivos_gerados'].append(arquivo_relatorio)
            
            resultado_pipeline['concluido_em'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resultado_pipeline['status'] = "SUCESSO"
            
            self.log("🎉 PIPELINE CONCLUÍDO COM SUCESSO!", "SUCCESS")
            
            return resultado_pipeline
            
        except Exception as e:
            self.log(f"❌ Erro no pipeline: {e}", "ERROR")
            resultado_pipeline['status'] = "ERRO"
            resultado_pipeline['erro'] = str(e)
            resultado_pipeline['concluido_em'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return resultado_pipeline
    
    def _gerar_combinacoes_dinamico(self, quantidade: int) -> List[List[int]]:
        """Gera combinações usando o gerador dinâmico"""
        try:
            self.log(f"Gerando {quantidade} combinações usando o sistema dinâmico...")
            
            # Usa o método correto do gerador dinâmico 
            combinacoes = self.gerador_dinamico.gerar_multiplas_combinacoes(
                quantidade=quantidade, 
                qtd_numeros=15  # Padrão 15 números
            )
            
            if combinacoes:
                self.log(f"✅ {len(combinacoes)} combinações dinâmicas geradas")
                return combinacoes
            else:
                self.log("⚠️ Nenhuma combinação gerada pelo sistema dinâmico", "WARNING")
                return []
            
        except Exception as e:
            self.log(f"Erro ao gerar combinações dinâmicas: {e}", "ERROR")
            return []
    
    def _salvar_combinacoes_temporarias(self, combinacoes: List[List[int]], 
                                      origem: str) -> str:
        """Salva combinações temporárias para uso no pipeline"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"combin_ia/pipeline/combinacoes_base_{origem}_{timestamp}.txt"
        
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(f"# Combinações base - {origem}\n")
                f.write(f"# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"# Total: {len(combinacoes)} combinações\n\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    f.write(f"Combinação {i}: {','.join(map(str, combinacao))}\n")
            
            self.log(f"Combinações base salvas: {arquivo}")
            return arquivo
            
        except Exception as e:
            self.log(f"Erro ao salvar combinações temporárias: {e}", "ERROR")
            return ""
    
    def _gerar_relatorio_pipeline(self, resultado: Dict) -> str:
        """Gera relatório completo do pipeline"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"combin_ia/pipeline/relatorio_pipeline_{timestamp}.txt"
        
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write("🚀 RELATÓRIO DO PIPELINE DE SUPER-COMBINAÇÕES IA\n")
                f.write("=" * 65 + "\n\n")
                
                # Informações gerais
                f.write(f"Executado em: {resultado['iniciado_em']}\n")
                f.write(f"Status: {resultado['status']}\n")
                f.write(f"Duração: {resultado['concluido_em']}\n\n")
                
                # Configuração
                config = resultado['configuracao']
                f.write("⚙️ CONFIGURAÇÃO:\n")
                f.write("-" * 20 + "\n")
                for chave, valor in config.items():
                    f.write(f"{chave}: {valor}\n")
                f.write("\n")
                
                # Etapas executadas
                f.write("📋 ETAPAS EXECUTADAS:\n")
                f.write("-" * 25 + "\n")
                for i, etapa in enumerate(resultado['etapas_executadas'], 1):
                    f.write(f"{i}. {etapa}\n")
                f.write("\n")
                
                # Resultados
                if 'resultados' in resultado:
                    resultados = resultado['resultados']
                    
                    f.write("📊 RESULTADOS:\n")
                    f.write("-" * 15 + "\n")
                    
                    if 'combinacoes_base' in resultados:
                        f.write(f"Combinações base: {resultados['combinacoes_base']}\n")
                    
                    if 'super_combinacoes' in resultados:
                        super_comb = resultados['super_combinacoes']
                        f.write(f"Super-combinações geradas: {len(super_comb)}\n\n")
                        
                        for i, sc in enumerate(super_comb, 1):
                            f.write(f"🎯 Super-combinação {i}:\n")
                            f.write(f"   {','.join(map(str, sc['super_combinacao']))}\n")
                            f.write(f"   Performance prevista: {sc.get('performance_prevista', 0):.1f}\n")
                            f.write(f"   Confiança: {sc.get('confianca_ia', 0):.1%}\n\n")
                    
                    if 'validacao' in resultados:
                        val = resultados['validacao']
                        f.write("🔍 VALIDAÇÃO:\n")
                        if 'performance_geral' in val:
                            perf = val['performance_geral']
                            f.write(f"   Melhor acerto: {perf.get('melhor_acerto_geral', 0)}\n")
                            f.write(f"   Média geral: {perf.get('acerto_medio_geral', 0):.1f}\n")
                
                # Arquivos gerados
                f.write("\n📁 ARQUIVOS GERADOS:\n")
                f.write("-" * 22 + "\n")
                for arquivo_gen in resultado.get('arquivos_gerados', []):
                    f.write(f"• {arquivo_gen}\n")
                
                # Log de operações
                f.write("\n📝 LOG DE OPERAÇÕES:\n")
                f.write("-" * 22 + "\n")
                for log_entry in self.log_operacoes[-20:]:  # Últimas 20 entradas
                    f.write(f"[{log_entry['timestamp']}] {log_entry['tipo']}: {log_entry['mensagem']}\n")
            
            self.log(f"Relatório salvo: {arquivo}")
            return arquivo
            
        except Exception as e:
            self.log(f"Erro ao gerar relatório: {e}", "ERROR")
            return ""
    
    def salvar_log(self):
        """Salva log completo das operações"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_log = f"combin_ia/logs/pipeline_log_{timestamp}.json"
        
        try:
            with open(arquivo_log, 'w', encoding='utf-8') as f:
                json.dump({
                    'gerado_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_operacoes': len(self.log_operacoes),
                    'log_completo': self.log_operacoes
                }, f, indent=2, ensure_ascii=False)
            
            print(f"📝 Log salvo: {arquivo_log}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")

def main():
    """Função principal com menu interativo"""
    print("🚀 PIPELINE INTEGRADO DE SUPER-COMBINAÇÕES IA")
    print("=" * 55)
    print("Sistema completo: Dataset → Treinamento → Geração → Validação")
    print()
    
    pipeline = PipelineSuperCombinacoesIA()
    
    try:
        print("⚙️ OPÇÕES DISPONÍVEIS:")
        print("1. Executar pipeline completo (automático)")
        print("2. Preparar ambiente (datasets + treinamento)")
        print("3. Pipeline com arquivo personalizado")
        print("4. Verificar status do sistema")
        print("5. Pipeline rápido (50 combinações)")
        
        opcao = input("\nEscolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            print("\n🚀 PIPELINE COMPLETO AUTOMÁTICO")
            
            qtd_comb = int(input("Quantidade de combinações base (padrão 100): ") or "100")
            qtd_super = int(input("Quantidade de super-combinações (padrão 3): ") or "3")
            validar = input("Validar automaticamente? (s/n): ").lower().startswith('s') or True
            
            # Prepara ambiente primeiro
            if not pipeline.preparar_ambiente():
                print("❌ Falha na preparação do ambiente")
                return
            
            # Executa pipeline
            resultado = pipeline.executar_pipeline_completo(
                origem_combinacoes="dinamico",
                quantidade_combinacoes=qtd_comb,
                quantidade_super=qtd_super,
                validar_automatico=validar
            )
            
            if resultado['status'] == "SUCESSO":
                print(f"\n🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
                print(f"📊 Etapas executadas: {len(resultado['etapas_executadas'])}")
                print(f"📁 Arquivos gerados: {len(resultado.get('arquivos_gerados', []))}")
            else:
                print(f"\n❌ Pipeline falhou: {resultado.get('erro', 'Erro desconhecido')}")
        
        elif opcao == "2":
            print("\n🔧 PREPARAÇÃO DO AMBIENTE")
            force_dataset = input("Forçar regeneração de datasets? (s/n): ").lower().startswith('s')
            force_treino = input("Forçar retreinamento do modelo? (s/n): ").lower().startswith('s')
            
            sucesso = pipeline.preparar_ambiente(force_dataset, force_treino)
            
            if sucesso:
                print("✅ Ambiente preparado com sucesso!")
            else:
                print("❌ Falha na preparação do ambiente")
        
        elif opcao == "3":
            print("\n📂 PIPELINE COM ARQUIVO PERSONALIZADO")
            arquivo = input("Caminho do arquivo com combinações: ").strip()
            
            if not os.path.exists(arquivo):
                print("❌ Arquivo não encontrado")
                return
            
            qtd_super = int(input("Quantidade de super-combinações (padrão 3): ") or "3")
            validar = input("Validar automaticamente? (s/n): ").lower().startswith('s') or True
            
            resultado = pipeline.executar_pipeline_completo(
                origem_combinacoes=arquivo,
                quantidade_super=qtd_super,
                validar_automatico=validar
            )
            
            if resultado['status'] == "SUCESSO":
                print("🎉 Pipeline concluído com sucesso!")
            else:
                print(f"❌ Pipeline falhou: {resultado.get('erro')}")
        
        elif opcao == "4":
            print("\n🔍 STATUS DO SISTEMA")
            status = pipeline.verificar_prerequisites()
            
            todos_ok = all(status.values())
            print(f"\n📊 Status geral: {'✅ PRONTO' if todos_ok else '⚠️ NECESSITA PREPARAÇÃO'}")
            
            if not todos_ok:
                print("\n💡 Execute a opção 2 para preparar o ambiente")
        
        elif opcao == "5":
            print("\n⚡ PIPELINE RÁPIDO")
            print("Executando com 50 combinações para teste rápido...")
            
            if not pipeline.preparar_ambiente():
                print("❌ Falha na preparação")
                return
            
            resultado = pipeline.executar_pipeline_completo(
                origem_combinacoes="dinamico",
                quantidade_combinacoes=50,
                quantidade_super=2,
                validar_automatico=True
            )
            
            if resultado['status'] == "SUCESSO":
                print("🎉 Pipeline rápido concluído!")
            else:
                print(f"❌ Falha: {resultado.get('erro')}")
        
        else:
            print("❌ Opção inválida")
        
        # Salva log sempre
        pipeline.salvar_log()
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado pelo usuário")
        pipeline.salvar_log()
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        pipeline.salvar_log()

if __name__ == "__main__":
    main()
