#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📈 SISTEMA DE REGISTRO DE EVOLUÇÃO DOCUMENTADA
Sistema para documentar completamente a evolução da IA e descobertas
- Histórico detalhado de todas as versões dos modelos
- Comparativo de performance entre versões
- Timeline de melhorias implementadas
- Documentação de descobertas importantes

Autor: AR CALHAU
Data: 22 de Agosto de 2025
"""

import json
import os
import pickle
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
import statistics
import hashlib
import numpy as np
from pathlib import Path

class SistemaEvolucaoDocumentada:
    """Sistema para documentar completamente a evolução da IA"""
    
    def __init__(self):
        self.pasta_base = "ia_repetidos"
        self.pasta_historico = f"{self.pasta_base}/historico_versoes"
        self.pasta_backups = f"{self.pasta_base}/backups_modelos"
        
        self.arquivo_evolucao = f"{self.pasta_base}/evolucao_documentada.json"
        self.arquivo_timeline = f"{self.pasta_base}/timeline_descobertas.json"
        self.arquivo_comparativo = f"{self.pasta_base}/comparativo_versoes.json"
        
        # Cria estrutura
        self._inicializar_sistema()
    
    def _inicializar_sistema(self):
        """Inicializa sistema de documentação"""
        for pasta in [self.pasta_base, self.pasta_historico, self.pasta_backups]:
            os.makedirs(pasta, exist_ok=True)
        
        # Arquivo de evolução documentada
        if not os.path.exists(self.arquivo_evolucao):
            evolucao_inicial = {
                "versao_atual": "1.0.0",
                "data_inicio": datetime.now().isoformat(),
                "versoes_historico": [],
                "melhorias_implementadas": [],
                "descobertas_importantes": [],
                "metricas_evolucao": {
                    "precisao_inicial": 0.0,
                    "precisao_atual": 0.0,
                    "melhor_precisao": 0.0,
                    "total_descobertas": 0
                }
            }
            self._salvar_json(self.arquivo_evolucao, evolucao_inicial)
        
        # Arquivo de timeline
        if not os.path.exists(self.arquivo_timeline):
            timeline_inicial = {
                "marcos_temporais": [],
                "descobertas_por_periodo": {},
                "evolucao_metricas": [],
                "eventos_importantes": []
            }
            self._salvar_json(self.arquivo_timeline, timeline_inicial)
        
        # Arquivo comparativo
        if not os.path.exists(self.arquivo_comparativo):
            comparativo_inicial = {
                "comparacoes_versoes": [],
                "graficos_performance": {
                    "precisao_por_versao": [],
                    "acertos_por_versao": [],
                    "tempo_treinamento": []
                },
                "decisoes_tecnicas": []
            }
            self._salvar_json(self.arquivo_comparativo, comparativo_inicial)
    
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
    
    def _gerar_hash_modelo(self, caminho_modelo: str) -> str:
        """Gera hash único para um modelo"""
        try:
            with open(caminho_modelo, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return "hash_indisponivel"
    
    def registrar_nova_versao(self, dados_versao: Dict):
        """
        Registra uma nova versão do modelo com backup automático
        dados_versao = {
            'versao': '1.1.0',
            'descricao': 'Melhoria no algoritmo de correlação',
            'melhorias': ['Novo algoritmo X', 'Otimização Y'],
            'metricas_performance': {
                'precisao_qtde': 0.75,
                'precisao_posicao': 0.68,
                'tempo_treinamento': 120,
                'amostras_treinamento': 5000
            },
            'arquivos_modelo': ['modelo_qtde_repetidos.pkl', 'modelo_mesma_posicao.pkl'],
            'descobertas_associadas': ['Padrão X confirmado', 'Correlação Y descoberta']
        }
        """
        print(f"📝 Registrando nova versão: {dados_versao.get('versao', 'N/A')}")
        
        evolucao = self._carregar_json(self.arquivo_evolucao)
        
        # Backup dos modelos atuais
        versao = dados_versao.get('versao', f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self._fazer_backup_modelos(versao)
        
        # Registra nova versão
        registro_versao = {
            "versao": versao,
            "data_lancamento": datetime.now().isoformat(),
            "descricao": dados_versao.get('descricao', ''),
            "melhorias": dados_versao.get('melhorias', []),
            "metricas_performance": dados_versao.get('metricas_performance', {}),
            "arquivos_modelo": dados_versao.get('arquivos_modelo', []),
            "descobertas_associadas": dados_versao.get('descobertas_associadas', []),
            "hash_modelos": {},
            "tamanho_total_mb": 0
        }
        
        # Calcula hashes e tamanhos
        tamanho_total = 0
        for arquivo in registro_versao["arquivos_modelo"]:
            caminho = f"{self.pasta_base}/{arquivo}"
            if os.path.exists(caminho):
                registro_versao["hash_modelos"][arquivo] = self._gerar_hash_modelo(caminho)
                tamanho_total += os.path.getsize(caminho)
        
        registro_versao["tamanho_total_mb"] = round(tamanho_total / (1024*1024), 2)
        
        # Adiciona ao histórico
        evolucao["versoes_historico"].append(registro_versao)
        evolucao["versao_atual"] = versao
        
        # Atualiza métricas de evolução
        metricas_performance = dados_versao.get('metricas_performance', {})
        if metricas_performance:
            precisao_atual = metricas_performance.get('precisao_qtde', 0)
            
            if evolucao["metricas_evolucao"]["precisao_inicial"] == 0:
                evolucao["metricas_evolucao"]["precisao_inicial"] = precisao_atual
            
            evolucao["metricas_evolucao"]["precisao_atual"] = precisao_atual
            evolucao["metricas_evolucao"]["melhor_precisao"] = max(
                evolucao["metricas_evolucao"]["melhor_precisao"], 
                precisao_atual
            )
        
        # Registra melhorias implementadas
        for melhoria in dados_versao.get('melhorias', []):
            registro_melhoria = {
                "data": datetime.now().isoformat(),
                "versao": versao,
                "descricao": melhoria,
                "impacto_esperado": "A definir"
            }
            evolucao["melhorias_implementadas"].append(registro_melhoria)
        
        # Registra descobertas
        for descoberta in dados_versao.get('descobertas_associadas', []):
            registro_descoberta = {
                "data": datetime.now().isoformat(),
                "versao": versao,
                "descoberta": descoberta,
                "validada": False
            }
            evolucao["descobertas_importantes"].append(registro_descoberta)
        
        evolucao["metricas_evolucao"]["total_descobertas"] = len(evolucao["descobertas_importantes"])
        
        self._salvar_json(self.arquivo_evolucao, evolucao)
        
        # Atualiza timeline
        self._atualizar_timeline(versao, dados_versao)
        
        # Atualiza comparativo
        self._atualizar_comparativo(registro_versao)
        
        print(f"✅ Versão {versao} registrada com sucesso!")
        print(f"   • {len(dados_versao.get('melhorias', []))} melhorias implementadas")
        print(f"   • {len(dados_versao.get('descobertas_associadas', []))} descobertas associadas")
        print(f"   • Backup salvo em: {self.pasta_backups}/v_{versao}")
    
    def _fazer_backup_modelos(self, versao: str):
        """Faz backup de todos os modelos da versão atual"""
        pasta_backup = f"{self.pasta_backups}/v_{versao}"
        os.makedirs(pasta_backup, exist_ok=True)
        
        arquivos_modelo = [
            "modelo_qtde_repetidos.pkl",
            "modelo_mesma_posicao.pkl",
            "scaler_features.pkl",
            "estatisticas.pkl",
            "padroes_historicos.pkl"
        ]
        
        arquivos_copiados = 0
        for arquivo in arquivos_modelo:
            origem = f"{self.pasta_base}/{arquivo}"
            destino = f"{pasta_backup}/{arquivo}"
            
            if os.path.exists(origem):
                try:
                    shutil.copy2(origem, destino)
                    arquivos_copiados += 1
                except Exception as e:
                    print(f"⚠️ Erro ao copiar {arquivo}: {e}")
        
        # Salva metadados do backup
        metadados_backup = {
            "data_backup": datetime.now().isoformat(),
            "versao": versao,
            "arquivos_backup": arquivos_copiados,
            "tamanho_total_mb": self._calcular_tamanho_pasta(pasta_backup)
        }
        
        with open(f"{pasta_backup}/metadados.json", 'w', encoding='utf-8') as f:
            json.dump(metadados_backup, f, indent=2, default=str)
        
        print(f"💾 Backup criado: {arquivos_copiados} arquivos em {pasta_backup}")
    
    def _calcular_tamanho_pasta(self, pasta: str) -> float:
        """Calcula tamanho total de uma pasta em MB"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(pasta):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total += os.path.getsize(filepath)
        except:
            pass
        return round(total / (1024*1024), 2)
    
    def _atualizar_timeline(self, versao: str, dados_versao: Dict):
        """Atualiza timeline de eventos"""
        timeline = self._carregar_json(self.arquivo_timeline)
        
        evento = {
            "data": datetime.now().isoformat(),
            "tipo": "nova_versao",
            "versao": versao,
            "titulo": f"Lançamento da versão {versao}",
            "descricao": dados_versao.get('descricao', ''),
            "impacto": "medio",
            "metricas_associadas": dados_versao.get('metricas_performance', {})
        }
        
        timeline["marcos_temporais"].append(evento)
        
        # Organiza descobertas por período (mês)
        periodo = datetime.now().strftime("%Y-%m")
        if periodo not in timeline["descobertas_por_periodo"]:
            timeline["descobertas_por_periodo"][periodo] = []
        
        for descoberta in dados_versao.get('descobertas_associadas', []):
            timeline["descobertas_por_periodo"][periodo].append({
                "descoberta": descoberta,
                "versao": versao,
                "data": datetime.now().isoformat()
            })
        
        self._salvar_json(self.arquivo_timeline, timeline)
    
    def _atualizar_comparativo(self, registro_versao: Dict):
        """Atualiza dados comparativos entre versões"""
        comparativo = self._carregar_json(self.arquivo_comparativo)
        
        metricas = registro_versao.get("metricas_performance", {})
        if metricas:
            # Precisão por versão
            comparativo["graficos_performance"]["precisao_por_versao"].append({
                "versao": registro_versao["versao"],
                "data": registro_versao["data_lancamento"],
                "precisao_qtde": metricas.get("precisao_qtde", 0),
                "precisao_posicao": metricas.get("precisao_posicao", 0)
            })
            
            # Tempo de treinamento
            if "tempo_treinamento" in metricas:
                comparativo["graficos_performance"]["tempo_treinamento"].append({
                    "versao": registro_versao["versao"],
                    "tempo_segundos": metricas["tempo_treinamento"],
                    "amostras": metricas.get("amostras_treinamento", 0)
                })
        
        self._salvar_json(self.arquivo_comparativo, comparativo)
    
    def registrar_descoberta_importante(self, descoberta: str, detalhes: Dict, impacto: str = "medio"):
        """Registra uma descoberta importante no timeline"""
        timeline = self._carregar_json(self.arquivo_timeline)
        
        evento_descoberta = {
            "data": datetime.now().isoformat(),
            "tipo": "descoberta",
            "titulo": descoberta,
            "detalhes": detalhes,
            "impacto": impacto,  # baixo, medio, alto, revolucionario
            "validada": False,
            "testes_confirmacao": []
        }
        
        timeline["eventos_importantes"].append(evento_descoberta)
        self._salvar_json(self.arquivo_timeline, timeline)
        
        print(f"🔬 Descoberta registrada: {descoberta}")
    
    def gerar_relatorio_evolucao_completo(self) -> str:
        """Gera relatório completo da evolução da IA"""
        evolucao = self._carregar_json(self.arquivo_evolucao)
        timeline = self._carregar_json(self.arquivo_timeline)
        comparativo = self._carregar_json(self.arquivo_comparativo)
        
        relatorio = []
        relatorio.append("📈 RELATÓRIO COMPLETO DE EVOLUÇÃO DA IA")
        relatorio.append("=" * 60)
        relatorio.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        relatorio.append("")
        
        # Visão geral da evolução
        metricas = evolucao.get("metricas_evolucao", {})
        relatorio.append("🎯 VISÃO GERAL DA EVOLUÇÃO:")
        relatorio.append("-" * 35)
        relatorio.append(f"• Versão atual: {evolucao.get('versao_atual', 'N/A')}")
        relatorio.append(f"• Total de versões: {len(evolucao.get('versoes_historico', []))}")
        relatorio.append(f"• Precisão inicial: {metricas.get('precisao_inicial', 0):.1%}")
        relatorio.append(f"• Precisão atual: {metricas.get('precisao_atual', 0):.1%}")
        relatorio.append(f"• Melhor precisão: {metricas.get('melhor_precisao', 0):.1%}")
        relatorio.append(f"• Total de descobertas: {metricas.get('total_descobertas', 0)}")
        
        # Calcula melhoria total
        precisao_inicial = metricas.get('precisao_inicial', 0)
        precisao_atual = metricas.get('precisao_atual', 0)
        if precisao_inicial > 0:
            melhoria = ((precisao_atual - precisao_inicial) / precisao_inicial) * 100
            relatorio.append(f"• Melhoria total: {melhoria:+.1f}%")
        relatorio.append("")
        
        # Histórico de versões
        versoes = evolucao.get("versoes_historico", [])
        if versoes:
            relatorio.append("📋 HISTÓRICO DE VERSÕES:")
            relatorio.append("-" * 30)
            
            for versao in versoes[-5:]:  # Últimas 5 versões
                data = datetime.fromisoformat(versao["data_lancamento"]).strftime("%d/%m/%Y")
                precisao = versao.get("metricas_performance", {}).get("precisao_qtde", 0)
                relatorio.append(f"• {versao['versao']} ({data}): {precisao:.1%}")
                relatorio.append(f"  - {versao.get('descricao', 'Sem descrição')}")
                if versao.get("melhorias"):
                    relatorio.append(f"  - Melhorias: {len(versao['melhorias'])}")
            relatorio.append("")
        
        # Timeline de eventos importantes
        eventos = timeline.get("eventos_importantes", [])
        if eventos:
            relatorio.append("⏱️ TIMELINE DE DESCOBERTAS:")
            relatorio.append("-" * 35)
            
            for evento in sorted(eventos, key=lambda x: x["data"], reverse=True)[:5]:
                data = datetime.fromisoformat(evento["data"]).strftime("%d/%m")
                impacto_emoji = {"baixo": "🔹", "medio": "🔸", "alto": "🔶", "revolucionario": "⭐"}.get(evento["impacto"], "📌")
                relatorio.append(f"{impacto_emoji} {data}: {evento['titulo']}")
            relatorio.append("")
        
        # Melhorias implementadas
        melhorias = evolucao.get("melhorias_implementadas", [])
        if melhorias:
            relatorio.append("🚀 MELHORIAS IMPLEMENTADAS:")
            relatorio.append("-" * 35)
            
            # Agrupa por versão
            melhorias_por_versao = {}
            for melhoria in melhorias:
                versao = melhoria.get("versao", "N/A")
                if versao not in melhorias_por_versao:
                    melhorias_por_versao[versao] = []
                melhorias_por_versao[versao].append(melhoria["descricao"])
            
            for versao, lista_melhorias in list(melhorias_por_versao.items())[-3:]:  # Últimas 3 versões
                relatorio.append(f"• Versão {versao}:")
                for melhoria in lista_melhorias[:3]:  # Max 3 melhorias por versão
                    relatorio.append(f"  - {melhoria}")
            relatorio.append("")
        
        # Descobertas importantes
        descobertas = evolucao.get("descobertas_importantes", [])
        if descobertas:
            relatorio.append("🔬 DESCOBERTAS IMPORTANTES:")
            relatorio.append("-" * 35)
            
            descobertas_recentes = sorted(descobertas, key=lambda x: x["data"], reverse=True)[:5]
            for descoberta in descobertas_recentes:
                data = datetime.fromisoformat(descoberta["data"]).strftime("%d/%m")
                status = "✅" if descoberta.get("validada", False) else "🔄"
                relatorio.append(f"{status} {data}: {descoberta['descoberta']}")
            relatorio.append("")
        
        # Comparativo de performance
        precisao_versoes = comparativo.get("graficos_performance", {}).get("precisao_por_versao", [])
        if len(precisao_versoes) > 1:
            relatorio.append("📊 COMPARATIVO DE PERFORMANCE:")
            relatorio.append("-" * 40)
            
            # Calcula tendência
            precisoes = [v["precisao_qtde"] for v in precisao_versoes if v.get("precisao_qtde")]
            if len(precisoes) > 1:
                tendencia = "📈 Crescente" if precisoes[-1] > precisoes[0] else "📉 Decrescente"
                variacao = abs(precisoes[-1] - precisoes[0])
                relatorio.append(f"• Tendência geral: {tendencia}")
                relatorio.append(f"• Variação total: {variacao:.1%}")
                
                if len(precisoes) > 2:
                    media_melhoria = statistics.mean([precisoes[i] - precisoes[i-1] for i in range(1, len(precisoes))])
                    relatorio.append(f"• Melhoria média por versão: {media_melhoria:+.1%}")
            relatorio.append("")
        
        # Estatísticas de backups
        if os.path.exists(self.pasta_backups):
            backups = [d for d in os.listdir(self.pasta_backups) if os.path.isdir(os.path.join(self.pasta_backups, d))]
            if backups:
                relatorio.append("💾 INFORMAÇÕES DE BACKUP:")
                relatorio.append("-" * 30)
                relatorio.append(f"• Total de backups: {len(backups)}")
                relatorio.append(f"• Espaço ocupado: {self._calcular_tamanho_pasta(self.pasta_backups)} MB")
                relatorio.append("")
        
        # Próximos passos recomendados
        relatorio.append("🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
        relatorio.append("-" * 40)
        
        if precisao_atual < 0.7:
            relatorio.append("• 🔴 Prioridade alta: Melhorar precisão geral")
            relatorio.append("• 📚 Adicionar mais dados de treinamento")
        elif precisao_atual < 0.8:
            relatorio.append("• 🟡 Foco em otimizações incrementais")
            relatorio.append("• ⚙️ Ajustar hiperparâmetros dos modelos")
        else:
            relatorio.append("• ✅ Manter estratégias atuais funcionando")
            relatorio.append("• 🚀 Explorar técnicas avançadas")
        
        descobertas_nao_validadas = sum(1 for d in descobertas if not d.get("validada", False))
        if descobertas_nao_validadas > 0:
            relatorio.append(f"• 🔄 Validar {descobertas_nao_validadas} descobertas pendentes")
        
        if len(versoes) > 5:
            relatorio.append("• 🧹 Considerar limpeza de backups antigos")
        
        relatorio.append("")
        relatorio.append("=" * 60)
        
        return "\n".join(relatorio)
    
    def salvar_relatorio_evolucao_completo(self, nome_arquivo: Optional[str] = None) -> str:
        """Salva relatório completo de evolução"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"evolucao_completa_ia_{timestamp}.txt"
        
        relatorio = self.gerar_relatorio_evolucao_completo()
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            
            print(f"✅ Relatório completo salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return ""
    
    def comparar_versoes(self, versao1: str, versao2: str) -> Dict:
        """Compara duas versões específicas"""
        evolucao = self._carregar_json(self.arquivo_evolucao)
        versoes = {v["versao"]: v for v in evolucao.get("versoes_historico", [])}
        
        if versao1 not in versoes or versao2 not in versoes:
            return {"erro": "Uma das versões não foi encontrada"}
        
        v1 = versoes[versao1]
        v2 = versoes[versao2]
        
        comparacao = {
            "versao_1": {
                "versao": versao1,
                "data": v1["data_lancamento"],
                "metricas": v1.get("metricas_performance", {}),
                "melhorias": len(v1.get("melhorias", []))
            },
            "versao_2": {
                "versao": versao2,
                "data": v2["data_lancamento"],
                "metricas": v2.get("metricas_performance", {}),
                "melhorias": len(v2.get("melhorias", []))
            },
            "diferencas": {}
        }
        
        # Calcula diferenças nas métricas
        m1 = v1.get("metricas_performance", {})
        m2 = v2.get("metricas_performance", {})
        
        for metrica in ["precisao_qtde", "precisao_posicao", "tempo_treinamento"]:
            if metrica in m1 and metrica in m2:
                diferenca = m2[metrica] - m1[metrica]
                percentual = (diferenca / m1[metrica]) * 100 if m1[metrica] > 0 else 0
                comparacao["diferencas"][metrica] = {
                    "diferenca_absoluta": diferenca,
                    "diferenca_percentual": percentual
                }
        
        return comparacao

def main():
    """Função principal para teste do sistema"""
    print("📈 SISTEMA DE EVOLUÇÃO DOCUMENTADA")
    print("=" * 50)
    
    sistema = SistemaEvolucaoDocumentada()
    
    try:
        print("\nOpções disponíveis:")
        print("1 - Gerar relatório completo de evolução")
        print("2 - Salvar relatório completo")
        print("3 - Registrar nova versão (exemplo)")
        print("4 - Registrar descoberta importante")
        print("5 - Listar backups disponíveis")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            relatorio = sistema.gerar_relatorio_evolucao_completo()
            print("\n" + relatorio)
            
        elif opcao == "2":
            arquivo = sistema.salvar_relatorio_evolucao_completo()
            if arquivo:
                print(f"\n✅ Relatório completo salvo: {arquivo}")
                
        elif opcao == "3":
            # Exemplo de registro de nova versão
            dados_exemplo = {
                'versao': '1.1.0',
                'descricao': 'Melhoria na precisão dos algoritmos',
                'melhorias': ['Otimização do algoritmo de correlação', 'Ajuste nos pesos'],
                'metricas_performance': {
                    'precisao_qtde': 0.75,
                    'precisao_posicao': 0.68,
                    'tempo_treinamento': 120,
                    'amostras_treinamento': 5000
                },
                'descobertas_associadas': ['Padrão de repetição confirmado']
            }
            sistema.registrar_nova_versao(dados_exemplo)
            
        elif opcao == "4":
            descoberta = "Correlação forte entre números repetidos e posição no sorteio"
            detalhes = {"confianca": 0.85, "dados_suporte": "Análise de 1000 concursos"}
            sistema.registrar_descoberta_importante(descoberta, detalhes, "alto")
            
        elif opcao == "5":
            if os.path.exists(sistema.pasta_backups):
                backups = [d for d in os.listdir(sistema.pasta_backups) if os.path.isdir(os.path.join(sistema.pasta_backups, d))]
                print(f"\n💾 {len(backups)} backups disponíveis:")
                for backup in sorted(backups):
                    tamanho = sistema._calcular_tamanho_pasta(os.path.join(sistema.pasta_backups, backup))
                    print(f"   {backup}: {tamanho} MB")
            else:
                print("\n⚠️ Pasta de backups não encontrada")
        
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n⏹️ Processo cancelado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
