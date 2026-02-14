#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 ANALISADOR DE PREDIÇÕES - SISTEMA DE APRENDIZADO CONTÍNUO
Sistema que demonstra como os arquivos JSON de predições são fundamentais 
para o aprendizado e evolução contínua dos modelos de IA

FUNCIONALIDADE PRINCIPAL:
- Análise automática dos arquivos de predição JSON
- Validação contra resultados reais quando disponíveis
- Feedback para melhoria dos modelos
- Evolução documentada do sistema
- Aprendizado baseado em resultados

Autor: AR CALHAU
Data: 20 de Setembro de 2025
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics

class AnalisadorPredicoes:
    """Sistema que analisa predições e realiza aprendizado contínuo"""
    
    def __init__(self):
        self.versao = "1.0"
        self.pasta_predicoes = "."
        self.arquivo_aprendizado = "aprendizado_continuo.json"
        self.arquivo_evolucao = "evolucao_modelos.json"
        
    def analisar_arquivos_predicao(self) -> Dict:
        """Analisa todos os arquivos de predição JSON disponíveis"""
        print("📊 ANALISADOR DE PREDIÇÕES - APRENDIZADO CONTÍNUO")
        print("=" * 60)
        
        # Busca todos os arquivos de predição
        arquivos_predicao = glob.glob("predicao_temporal_79_*.json")
        
        if not arquivos_predicao:
            return {"erro": "Nenhum arquivo de predição encontrado"}
        
        print(f"📁 Encontrados {len(arquivos_predicao)} arquivos de predição:")
        print("-" * 50)
        
        analise_completa = {
            "total_arquivos": len(arquivos_predicao),
            "data_analise": datetime.now().isoformat(),
            "predicoes_analisadas": [],
            "estatisticas_gerais": {},
            "oportunidades_aprendizado": [],
            "feedback_modelo": {}
        }
        
        # Analisa cada arquivo
        for arquivo in sorted(arquivos_predicao):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    predicao = json.load(f)
                
                # Análise individual
                analise_individual = self._analisar_predicao_individual(arquivo, predicao)
                analise_completa["predicoes_analisadas"].append(analise_individual)
                
                print(f"✅ {arquivo}")
                print(f"   🎯 Números: {predicao['numeros_preditos']}")
                print(f"   📊 Concurso alvo: {predicao['concurso_alvo']}")
                print(f"   🔢 Soma: {predicao['soma_prevista']}")
                print(f"   🎯 Confiança: {predicao['confianca']:.1%}")
                print(f"   🪟 Janela: {predicao.get('janela_usada', 'N/A')} concursos")
                print()
                
            except Exception as e:
                print(f"❌ Erro ao ler {arquivo}: {e}")
        
        # Gera estatísticas gerais
        analise_completa["estatisticas_gerais"] = self._calcular_estatisticas_gerais(analise_completa["predicoes_analisadas"])
        
        # Identifica oportunidades de aprendizado
        analise_completa["oportunidades_aprendizado"] = self._identificar_oportunidades_aprendizado(analise_completa["predicoes_analisadas"])
        
        # Gera feedback para o modelo
        analise_completa["feedback_modelo"] = self._gerar_feedback_modelo(analise_completa["predicoes_analisadas"])
        
        # Mostra análise completa
        self._mostrar_analise_completa(analise_completa)
        
        return analise_completa
    
    def _analisar_predicao_individual(self, arquivo: str, predicao: Dict) -> Dict:
        """Analisa uma predição individual"""
        analise = {
            "arquivo": arquivo,
            "timestamp": predicao.get("timestamp", ""),
            "concurso_alvo": predicao.get("concurso_alvo", 0),
            "numeros_preditos": predicao.get("numeros_preditos", []),
            "soma_prevista": predicao.get("soma_prevista", 0),
            "qtde_pares": predicao.get("qtde_pares", 0),
            "qtde_altos": predicao.get("qtde_altos", 0),
            "janela_usada": predicao.get("janela_usada", 0),
            "variacao_id": predicao.get("variacao_id", 0),
            "modelo_usado": predicao.get("modelo_usado", ""),
            "confianca": predicao.get("confianca", 0)
        }
        
        # Análise de distribuição
        numeros = analise["numeros_preditos"]
        if numeros:
            analise["distribuicao"] = {
                "baixos_1_12": sum(1 for n in numeros if 1 <= n <= 12),
                "medios_13_13": sum(1 for n in numeros if n == 13),
                "altos_14_25": sum(1 for n in numeros if 14 <= n <= 25),
                "sequencias": self._contar_sequencias(numeros),
                "gaps_grandes": self._contar_gaps_grandes(numeros)
            }
        
        return analise
    
    def _contar_sequencias(self, numeros: List[int]) -> int:
        """Conta sequências consecutivas"""
        if len(numeros) < 2:
            return 0
        
        sequencias = 0
        for i in range(len(numeros) - 1):
            if numeros[i+1] == numeros[i] + 1:
                sequencias += 1
        
        return sequencias
    
    def _contar_gaps_grandes(self, numeros: List[int]) -> int:
        """Conta gaps maiores que 3"""
        if len(numeros) < 2:
            return 0
        
        gaps_grandes = 0
        for i in range(len(numeros) - 1):
            if numeros[i+1] - numeros[i] > 3:
                gaps_grandes += 1
        
        return gaps_grandes
    
    def _calcular_estatisticas_gerais(self, predicoes: List[Dict]) -> Dict:
        """Calcula estatísticas gerais de todas as predições"""
        if not predicoes:
            return {}
        
        # Extrai dados para análise
        somas = [p["soma_prevista"] for p in predicoes if p["soma_prevista"]]
        qtdes_pares = [p["qtde_pares"] for p in predicoes if p["qtde_pares"] is not None]
        qtdes_altos = [p["qtde_altos"] for p in predicoes if p["qtde_altos"] is not None]
        janelas = [p["janela_usada"] for p in predicoes if p["janela_usada"]]
        
        estatisticas = {
            "soma_total": {
                "media": statistics.mean(somas) if somas else 0,
                "mediana": statistics.median(somas) if somas else 0,
                "min": min(somas) if somas else 0,
                "max": max(somas) if somas else 0,
                "desvio": statistics.stdev(somas) if len(somas) > 1 else 0
            },
            "distribuicao_pares": {
                "media": statistics.mean(qtdes_pares) if qtdes_pares else 0,
                "mais_comum": max(set(qtdes_pares), key=qtdes_pares.count) if qtdes_pares else 0
            },
            "distribuicao_altos": {
                "media": statistics.mean(qtdes_altos) if qtdes_altos else 0,
                "mais_comum": max(set(qtdes_altos), key=qtdes_altos.count) if qtdes_altos else 0
            },
            "janelas_temporais": {
                "media": statistics.mean(janelas) if janelas else 0,
                "variacoes": len(set(janelas)) if janelas else 0
            }
        }
        
        return estatisticas
    
    def _identificar_oportunidades_aprendizado(self, predicoes: List[Dict]) -> List[str]:
        """Identifica oportunidades de melhoria e aprendizado"""
        oportunidades = []
        
        if not predicoes:
            return ["Nenhuma predição para analisar"]
        
        # Análise de diversidade
        somas = [p["soma_prevista"] for p in predicoes if p["soma_prevista"]]
        if somas:
            desvio_soma = statistics.stdev(somas) if len(somas) > 1 else 0
            if desvio_soma < 10:
                oportunidades.append("🔍 BAIXA DIVERSIDADE: Somas muito similares - considerar maior variação")
        
        # Análise de janelas temporais
        janelas = [p["janela_usada"] for p in predicoes if p["janela_usada"]]
        if janelas:
            variacoes_janela = len(set(janelas))
            if variacoes_janela < 3:
                oportunidades.append("📊 JANELAS LIMITADAS: Poucas variações de janela temporal - expandir range")
        
        # Análise de distribuição
        qtdes_altos = [p["qtde_altos"] for p in predicoes if p["qtde_altos"] is not None]
        if qtdes_altos:
            media_altos = statistics.mean(qtdes_altos)
            if media_altos > 8:
                oportunidades.append("⚠️ VIÉS NÚMEROS ALTOS: Muitos números altos - balancear distribuição")
            elif media_altos < 5:
                oportunidades.append("⚠️ VIÉS NÚMEROS BAIXOS: Poucos números altos - balancear distribuição")
        
        # Análise temporal
        timestamps = [p["timestamp"] for p in predicoes if p["timestamp"]]
        if len(timestamps) > 5:
            oportunidades.append("✅ DADOS SUFICIENTES: Volume adequado para análise de aprendizado")
        else:
            oportunidades.append("📈 COLETAR MAIS DADOS: Gerar mais predições para melhor aprendizado")
        
        return oportunidades
    
    def _gerar_feedback_modelo(self, predicoes: List[Dict]) -> Dict:
        """Gera feedback específico para melhoria do modelo"""
        feedback = {
            "pontos_fortes": [],
            "areas_melhoria": [],
            "recomendacoes": [],
            "parametros_otimos": {}
        }
        
        if not predicoes:
            return feedback
        
        # Análise de pontos fortes
        janelas = [p["janela_usada"] for p in predicoes if p["janela_usada"]]
        if janelas:
            janela_mais_usada = max(set(janelas), key=janelas.count)
            feedback["pontos_fortes"].append(f"Janela temporal {janela_mais_usada} é preferida pelo modelo")
        
        somas = [p["soma_prevista"] for p in predicoes if p["soma_prevista"]]
        if somas:
            soma_media = statistics.mean(somas)
            if 180 <= soma_media <= 200:
                feedback["pontos_fortes"].append("Somas previstas estão no range histórico ideal (180-200)")
        
        # Análise de áreas de melhoria
        qtdes_pares = [p["qtde_pares"] for p in predicoes if p["qtde_pares"] is not None]
        if qtdes_pares:
            desvio_pares = statistics.stdev(qtdes_pares) if len(qtdes_pares) > 1 else 0
            if desvio_pares > 2:
                feedback["areas_melhoria"].append("Distribuição pares/ímpares muito variável")
        
        # Recomendações
        if len(predicoes) >= 5:
            feedback["recomendacoes"].append("Implementar validação cruzada com resultados reais")
            feedback["recomendacoes"].append("Analisar padrões de acerto quando concursos saírem")
            feedback["recomendacoes"].append("Ajustar pesos dos features baseado em performance")
        
        # Parâmetros ótimos identificados
        if janelas:
            feedback["parametros_otimos"]["janela_recomendada"] = statistics.mode(janelas) if len(janelas) > 1 else janelas[0]
        
        if somas:
            feedback["parametros_otimos"]["soma_objetivo"] = statistics.median(somas)
        
        return feedback
    
    def _mostrar_analise_completa(self, analise: Dict):
        """Mostra análise completa formatada"""
        print("\n📊 ANÁLISE COMPLETA DE APRENDIZADO")
        print("=" * 60)
        
        est = analise["estatisticas_gerais"]
        print("📈 ESTATÍSTICAS GERAIS:")
        print(f"   📊 Soma média prevista: {est.get('soma_total', {}).get('media', 0):.1f}")
        print(f"   🎯 Range de somas: {est.get('soma_total', {}).get('min', 0)} - {est.get('soma_total', {}).get('max', 0)}")
        print(f"   ⚖️ Pares médios: {est.get('distribuicao_pares', {}).get('media', 0):.1f}")
        print(f"   📈 Altos médios: {est.get('distribuicao_altos', {}).get('media', 0):.1f}")
        
        print(f"\n🔍 OPORTUNIDADES DE APRENDIZADO:")
        for oportunidade in analise["oportunidades_aprendizado"]:
            print(f"   • {oportunidade}")
        
        feedback = analise["feedback_modelo"]
        print(f"\n💡 FEEDBACK PARA O MODELO:")
        print("   🏆 Pontos Fortes:")
        for ponto in feedback.get("pontos_fortes", []):
            print(f"     ✅ {ponto}")
        
        print("   🔧 Áreas de Melhoria:")
        for area in feedback.get("areas_melhoria", []):
            print(f"     🔄 {area}")
        
        print("   🎯 Recomendações:")
        for rec in feedback.get("recomendacoes", []):
            print(f"     💡 {rec}")
    
    def simular_aprendizado_futuro(self, concurso_real: int, numeros_reais: List[int]):
        """Simula como seria o aprendizado quando o concurso real sair"""
        print("\n🎯 SIMULAÇÃO DE APRENDIZADO FUTURO")
        print("=" * 50)
        print("📊 Quando o concurso real sair, o sistema irá:")
        print()
        
        # Busca predições para o concurso
        arquivos_predicao = glob.glob("predicao_temporal_79_*.json")
        predicoes_concurso = []
        
        for arquivo in arquivos_predicao:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    predicao = json.load(f)
                
                if predicao.get("concurso_alvo") == concurso_real:
                    predicoes_concurso.append((arquivo, predicao))
            except:
                continue
        
        if not predicoes_concurso:
            print(f"❌ Nenhuma predição encontrada para concurso {concurso_real}")
            return
        
        print(f"📋 Encontradas {len(predicoes_concurso)} predições para concurso {concurso_real}")
        print("=" * 50)
        
        # Simula validação para cada predição
        resultados_aprendizado = []
        
        for arquivo, predicao in predicoes_concurso:
            numeros_preditos = predicao["numeros_preditos"]
            acertos = len(set(numeros_preditos) & set(numeros_reais))
            precisao = (acertos / 15) * 100
            
            resultado = {
                "arquivo": arquivo,
                "acertos": acertos,
                "precisao": precisao,
                "janela_usada": predicao.get("janela_usada", 0),
                "soma_predita": predicao.get("soma_prevista", 0),
                "soma_real": sum(numeros_reais),
                "erro_soma": abs(predicao.get("soma_prevista", 0) - sum(numeros_reais))
            }
            
            resultados_aprendizado.append(resultado)
            
            print(f"🎯 {arquivo}:")
            print(f"   📊 Acertos: {acertos}/15 ({precisao:.1f}%)")
            print(f"   🔢 Soma predita: {predicao.get('soma_prevista', 0)} | Real: {sum(numeros_reais)} | Erro: {resultado['erro_soma']}")
            print(f"   🪟 Janela: {predicao.get('janela_usada', 0)} concursos")
            print(f"   ✅ Sucesso: {'SIM' if acertos >= 11 else 'NÃO'}")
            print()
        
        # Análise de aprendizado
        print("🧠 APRENDIZADO EXTRAÍDO:")
        print("-" * 30)
        
        # Melhor janela
        melhor_resultado = max(resultados_aprendizado, key=lambda x: x["acertos"])
        print(f"🏆 Melhor resultado: {melhor_resultado['acertos']} acertos (janela {melhor_resultado['janela_usada']})")
        
        # Análise de janelas
        janelas_performance = {}
        for resultado in resultados_aprendizado:
            janela = resultado["janela_usada"]
            if janela not in janelas_performance:
                janelas_performance[janela] = []
            janelas_performance[janela].append(resultado["acertos"])
        
        print("📊 Performance por janela temporal:")
        for janela, acertos_list in janelas_performance.items():
            media_acertos = statistics.mean(acertos_list)
            print(f"   🪟 Janela {janela}: {media_acertos:.1f} acertos médios")
        
        # Recomendações de ajuste
        print("\n💡 RECOMENDAÇÕES PARA PRÓXIMAS PREDIÇÕES:")
        melhor_janela = melhor_resultado["janela_usada"]
        print(f"   🎯 Usar preferencialmente janela {melhor_janela}")
        
        if melhor_resultado["erro_soma"] < 10:
            print(f"   ✅ Predição de soma está boa (erro {melhor_resultado['erro_soma']})")
        else:
            print(f"   🔧 Ajustar algoritmo de soma (erro {melhor_resultado['erro_soma']})")
        
        return resultados_aprendizado
    
    def demonstrar_ciclo_completo_aprendizado(self):
        """Demonstra o ciclo completo de aprendizado"""
        print("🎓 DEMONSTRAÇÃO: CICLO COMPLETO DE APRENDIZADO")
        print("=" * 60)
        print("📋 ETAPAS DO PROCESSO DE APRENDIZADO CONTÍNUO:")
        print()
        
        print("1️⃣ GERAÇÃO DE PREDIÇÕES:")
        print("   📊 Modelo gera predições (arquivos JSON)")
        print("   💾 Salva metadados: janela, soma, distribuição, confiança")
        print("   🎯 Cada predição é uma 'hipótese' do modelo")
        print()
        
        print("2️⃣ ARMAZENAMENTO ESTRUTURADO:")
        print("   📁 Arquivos JSON contêm dados estruturados")
        print("   🕐 Timestamp para rastreamento temporal")
        print("   🔢 Métricas quantificáveis para análise")
        print("   🏷️ Metadados para correlações futuras")
        print()
        
        print("3️⃣ VALIDAÇÃO CONTRA REALIDADE:")
        print("   ✅ Quando concurso sai, sistema compara automaticamente")
        print("   📊 Calcula precisão real vs. precisão esperada")
        print("   🎯 Identifica quais variações funcionaram melhor")
        print("   📈 Registra feedback para ajustes futuros")
        print()
        
        print("4️⃣ ANÁLISE E APRENDIZADO:")
        print("   🧠 Identifica padrões nas predições que acertaram mais")
        print("   🪟 Descobre janelas temporais mais eficazes")
        print("   ⚖️ Ajusta pesos de features baseado em performance")
        print("   🔄 Evolui algoritmos baseado em resultados reais")
        print()
        
        print("5️⃣ EVOLUÇÃO DO MODELO:")
        print("   📈 Incrementa precisão baseado em aprendizado")
        print("   🎯 Otimiza parâmetros automaticamente")
        print("   🔧 Ajusta estratégias que não funcionaram")
        print("   🏆 Documenta melhorias no sistema de evolução")
        print()
        
        print("🔄 CICLO CONTÍNUO:")
        print("   ♻️ Processo se repete a cada novo concurso")
        print("   📊 Base de conhecimento cresce constantemente")
        print("   🧠 Modelo fica mais inteligente com o tempo")
        print("   🎯 Precisão tende a aumentar progressivamente")

def main():
    """Função principal"""
    analisador = AnalisadorPredicoes()
    
    while True:
        print("\n📊 ANALISADOR DE PREDIÇÕES - APRENDIZADO CONTÍNUO")
        print("=" * 60)
        print("📋 OPÇÕES:")
        print("1️⃣  📁 Analisar Arquivos de Predição Existentes")
        print("2️⃣  🎯 Simular Aprendizado Futuro")
        print("3️⃣  🎓 Demonstrar Ciclo Completo de Aprendizado")
        print("4️⃣  📊 Explicar Importância dos Arquivos JSON")
        print("0️⃣  🔙 Sair")
        print()
        
        try:
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                analisador.analisar_arquivos_predicao()
            
            elif opcao == "2":
                print("\n🎯 SIMULAÇÃO DE APRENDIZADO:")
                try:
                    concurso = int(input("Concurso para simular (ex: 3491): "))
                    numeros_str = input("Números do resultado (separados por vírgula): ")
                    numeros = [int(x.strip()) for x in numeros_str.split(",")]
                    
                    if len(numeros) == 15:
                        analisador.simular_aprendizado_futuro(concurso, sorted(numeros))
                    else:
                        print("❌ Deve informar exatamente 15 números")
                except:
                    print("❌ Erro nos dados informados")
            
            elif opcao == "3":
                analisador.demonstrar_ciclo_completo_aprendizado()
            
            elif opcao == "4":
                print("\n📊 IMPORTÂNCIA DOS ARQUIVOS JSON DE PREDIÇÃO")
                print("=" * 60)
                print("🎯 OS ARQUIVOS JSON SÃO FUNDAMENTAIS PORQUE:")
                print()
                print("1️⃣ REGISTRO HISTÓRICO:")
                print("   📝 Cada arquivo é um 'experimento' documentado")
                print("   🕐 Timestamp permite análise temporal")
                print("   🎯 Rastreia evolução das predições")
                print()
                print("2️⃣ DADOS ESTRUTURADOS:")
                print("   📊 Formato padronizado para análise automática")
                print("   🔢 Métricas quantificáveis (soma, pares, altos)")
                print("   🏷️ Metadados ricos (janela, confiança, modelo)")
                print()
                print("3️⃣ FEEDBACK LOOP:")
                print("   ✅ Base para validação contra resultados reais")
                print("   🧠 Permite identificar o que funciona melhor")
                print("   🔄 Ciclo de melhoria contínua")
                print()
                print("4️⃣ MACHINE LEARNING:")
                print("   📈 Dataset para treinar modelos futuros")
                print("   🎯 Correlações entre parâmetros e sucesso")
                print("   🧠 Aprendizado supervisionado baseado em resultados")
                print()
                print("5️⃣ AUDITORIA E TRANSPARÊNCIA:")
                print("   🔍 Permite auditoria completa do processo")
                print("   📊 Transparência nas decisões do modelo")
                print("   🏆 Comprovação de melhorias ao longo do tempo")
                print()
                print("💡 CONCLUSÃO:")
                print("Sem esses arquivos, o sistema seria 'burro' - apenas geraria")
                print("predições sem aprender com erros e acertos. Com eles, temos")
                print("um sistema que evolui e fica mais inteligente a cada concurso!")
            
            elif opcao == "0":
                break
            
            else:
                print("❌ Opção inválida!")
            
            input("\n⏸️ Pressione ENTER para continuar...")
            
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            input("⏸️ Pressione ENTER para continuar...")

if __name__ == "__main__":
    main()