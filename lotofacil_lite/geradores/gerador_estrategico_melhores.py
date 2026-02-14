#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR ESTRATÉGICO BASEADO NOS 10 MELHORES
==============================================
Usa análise histórica para criar estratégias otimizadas
==============================================
"""

import sys
import os
import random
from pathlib import Path
from datetime import datetime

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class GeradorEstrategicoMelhores:
    """Gerador que usa estratégias baseadas na análise dos 10 melhores"""
    
    def __init__(self):
        self.nucleo_atual = []
        self.complementares = []
        self.estrategias_disponiveis = {
            1: "Núcleo Fixo + Complementares Rotativos",
            2: "Escalonamento por Performance",
            3: "Complementação Inteligente Total",
            4: "Híbrido: Núcleo + Expansão Científica"
        }
    
    def executar_menu_estrategico(self):
        """Menu principal do gerador estratégico"""
        while True:
            self._mostrar_menu()
            
            try:
                opcao = input("\nEscolha uma opção (0-6): ").strip()
                
                if opcao == "0":
                    print("👋 Até logo!")
                    break
                elif opcao == "1":
                    self._atualizar_nucleo_atual()
                elif opcao == "2":
                    self._executar_estrategia_nucleo_fixo()
                elif opcao == "3":
                    self._executar_estrategia_escalonada()
                elif opcao == "4":
                    self._executar_estrategia_complementacao_total()
                elif opcao == "5":
                    self._executar_estrategia_hibrida()
                elif opcao == "6":
                    self._relatorio_estrategias()
                else:
                    print("❌ Opção inválida")
                    
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def _mostrar_menu(self):
        """Exibe o menu principal"""
        nucleo_str = ','.join(map(str, self.nucleo_atual)) if self.nucleo_atual else "⚠️ Não definido"
        
        print("\n" + "="*70)
        print("🎯 GERADOR ESTRATÉGICO DOS 10 MELHORES")
        print("="*70)
        print("🧠 Baseado em análise histórica de performance")
        print("="*70)
        print(f"🔥 NÚCLEO ATUAL: {nucleo_str}")
        print("="*70)
        print("1️⃣  🧠 Atualizar Núcleo Atual (10 Melhores)")
        print("2️⃣  🎯 Estratégia 1: Núcleo Fixo + Complementares")
        print("3️⃣  📊 Estratégia 2: Escalonamento por Performance")  
        print("4️⃣  🔬 Estratégia 3: Complementação Inteligente Total")
        print("5️⃣  ⭐ Estratégia 4: Híbrido - Núcleo + Expansão")
        print("6️⃣  📋 Relatório de Todas as Estratégias")
        print("0️⃣  🚪 Sair")
        print("="*70)
    
    def _atualizar_nucleo_atual(self):
        """Atualiza o núcleo dos 10 melhores números"""
        print("\n🧠 ATUALIZANDO NÚCLEO DOS 10 MELHORES...")
        print("🔄 Analisando últimos 100 concursos...")
        
        try:
            # Buscar últimos 100 concursos
            query = """
            SELECT MAX(Concurso) FROM Resultados_INT
            """
            resultado = db_config.execute_query(query)
            
            if not resultado:
                print("❌ Erro ao buscar dados")
                return
            
            max_concurso = resultado[0][0]
            inicio_analise = max_concurso - 99  # Últimos 100
            
            print(f"📊 Analisando concursos {inicio_analise} a {max_concurso}")
            
            # Calcular scores para cada número
            scores = {}
            for numero in range(1, 26):
                scores[numero] = self._calcular_score_numero(numero, inicio_analise, max_concurso)
            
            # Selecionar os 10 melhores
            ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            self.nucleo_atual = [numero for numero, score in ranking[:10]]
            self.complementares = [numero for numero, score in ranking[10:]]
            
            print("\n🏆 NOVO NÚCLEO DOS 10 MELHORES:")
            print("="*50)
            for i, (numero, score) in enumerate(ranking[:10], 1):
                print(f"   {i:2d}º lugar: Número {numero:2d} - Score: {score:.1f}")
            
            print(f"\n🎯 NÚCLEO DEFINIDO: {','.join(map(str, self.nucleo_atual))}")
            print(f"📦 Complementares: {len(self.complementares)} números disponíveis")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            # Fallback para núcleo padrão
            self.nucleo_atual = [1, 4, 7, 9, 10, 11, 13, 14, 19, 22]
            self.complementares = [n for n in range(1, 26) if n not in self.nucleo_atual]
    
    def _calcular_score_numero(self, numero, inicio, fim):
        """Calcula score de um número em um período"""
        try:
            score = 0
            
            # 1. Ausência atual (40% peso)
            ausencia = self._calcular_ausencia_atual(numero, fim)
            score += min(ausencia * 5, 100) * 0.40
            
            # 2. Frequência no período (30% peso)
            frequencia = self._calcular_frequencia_periodo_numero(numero, inicio, fim)
            score += min(frequencia * 3, 100) * 0.30
            
            # 3. Tendência crescente (20% peso)
            tendencia = self._calcular_tendencia_numero(numero, inicio, fim)
            score += tendencia * 0.20
            
            # 4. Fatores especiais (10% peso)
            especiais = self._calcular_fatores_especiais(numero)
            score += especiais * 0.10
            
            return score
            
        except:
            return 50.0  # Score neutro
    
    def _calcular_ausencia_atual(self, numero, ultimo_concurso):
        """Calcula quantos concursos o número não aparece"""
        try:
            query = """
            SELECT MAX(Concurso) FROM Resultados_INT 
            WHERE (N1=? OR N2=? OR N3=? OR N4=? OR N5=? OR N6=? OR N7=? OR N8=? OR 
                   N9=? OR N10=? OR N11=? OR N12=? OR N13=? OR N14=? OR N15=?)
            AND Concurso <= ?
            """
            
            params = [numero] * 15 + [ultimo_concurso]
            resultado = db_config.execute_query(query, tuple(params))
            
            if resultado and resultado[0][0]:
                ultima_aparicao = resultado[0][0]
                return ultimo_concurso - ultima_aparicao
            
            return 20  # Muito ausente
            
        except:
            return 5
    
    def _calcular_frequencia_periodo_numero(self, numero, inicio, fim):
        """Calcula frequência de aparição no período"""
        try:
            query = """
            SELECT COUNT_BIG(*) FROM Resultados_INT 
            WHERE (N1=? OR N2=? OR N3=? OR N4=? OR N5=? OR N6=? OR N7=? OR N8=? OR 
                   N9=? OR N10=? OR N11=? OR N12=? OR N13=? OR N14=? OR N15=?)
            AND Concurso BETWEEN ? AND ?
            """
            
            params = [numero] * 15 + [inicio, fim]
            resultado = db_config.execute_query(query, tuple(params))
            
            return resultado[0][0] if resultado else 0
            
        except:
            return 0
    
    def _calcular_tendencia_numero(self, numero, inicio, fim):
        """Calcula se o número está em tendência de alta"""
        try:
            meio = inicio + (fim - inicio) // 2
            
            freq1 = self._calcular_frequencia_periodo_numero(numero, inicio, meio)
            freq2 = self._calcular_frequencia_periodo_numero(numero, meio + 1, fim)
            
            if freq1 > 0:
                tendencia = ((freq2 - freq1) / freq1) * 100
                return max(0, min(tendencia + 50, 100))
            
            return 50
            
        except:
            return 50
    
    def _calcular_fatores_especiais(self, numero):
        """Calcula fatores especiais (primos, centrais, etc.)"""
        score = 0
        
        # Primos
        if numero in {2, 3, 5, 7, 11, 13, 17, 19, 23}:
            score += 30
        
        # Centrais (8-18)
        if 8 <= numero <= 18:
            score += 25
        
        # Fibonacci
        if numero in {1, 2, 3, 5, 8, 13, 21}:
            score += 20
        
        # Extremos evitar
        if numero in {1, 25}:
            score -= 15
        
        return max(0, min(score, 100))
    
    def _executar_estrategia_nucleo_fixo(self):
        """Estratégia 1: Núcleo fixo + complementares rotativos"""
        if not self.nucleo_atual:
            print("⚠️ Defina o núcleo primeiro (opção 1)")
            return
        
        print("\n🎯 ESTRATÉGIA 1: NÚCLEO FIXO + COMPLEMENTARES ROTATIVOS")
        print("="*60)
        print("💡 Conceito: 10 melhores sempre + 5 complementares variados")
        print()
        
        try:
            qtd = int(input("Quantas combinações gerar (padrão 10): ") or "10")
        except:
            qtd = 10
        
        combinacoes = []
        
        for i in range(qtd):
            # Núcleo sempre presente (10 números)
            combinacao = self.nucleo_atual.copy()
            
            # Adicionar 5 complementares aleatórios
            complementares_escolhidos = random.sample(self.complementares, 5)
            combinacao.extend(complementares_escolhidos)
            
            # Ordenar
            combinacao.sort()
            combinacoes.append(combinacao)
        
        # Mostrar resultados
        print(f"\n🎯 {qtd} COMBINAÇÕES GERADAS (ESTRATÉGIA NÚCLEO FIXO):")
        print("="*60)
        print(f"🔥 Núcleo sempre presente: {','.join(map(str, self.nucleo_atual))}")
        print()
        
        for i, comb in enumerate(combinacoes, 1):
            complementares_usados = [n for n in comb if n not in self.nucleo_atual]
            print(f"Jogo {i:2d}: {','.join(map(str, comb))}")
            print(f"         Complementares: {','.join(map(str, complementares_usados))}")
        
        # Salvar arquivo
        self._salvar_combinacoes(combinacoes, "nucleo_fixo")
    
    def _executar_estrategia_escalonada(self):
        """Estratégia 2: Escalonamento por performance"""
        if not self.nucleo_atual:
            print("⚠️ Defina o núcleo primeiro (opção 1)")
            return
        
        print("\n📊 ESTRATÉGIA 2: ESCALONAMENTO POR PERFORMANCE")
        print("="*60)
        print("💡 Conceito: Peso maior nos 5 primeiros, rotação dos 5 últimos")
        print()
        
        try:
            qtd = int(input("Quantas combinações gerar (padrão 8): ") or "8")
        except:
            qtd = 8
        
        combinacoes = []
        
        # Dividir núcleo em prioridades
        nucleo_prioritario = self.nucleo_atual[:5]  # Top 5
        nucleo_rotativo = self.nucleo_atual[5:]     # Últimos 5
        
        for i in range(qtd):
            combinacao = []
            
            # Sempre usar os 5 prioritários
            combinacao.extend(nucleo_prioritario)
            
            # Usar 3-4 dos rotativos
            qtd_rotativos = random.choice([3, 4])
            rotativos_escolhidos = random.sample(nucleo_rotativo, qtd_rotativos)
            combinacao.extend(rotativos_escolhidos)
            
            # Completar com complementares
            faltam = 15 - len(combinacao)
            complementares_escolhidos = random.sample(self.complementares, faltam)
            combinacao.extend(complementares_escolhidos)
            
            # Ordenar
            combinacao.sort()
            combinacoes.append(combinacao)
        
        # Mostrar resultados
        print(f"\n📊 {qtd} COMBINAÇÕES GERADAS (ESTRATÉGIA ESCALONADA):")
        print("="*60)
        print(f"🏆 Núcleo prioritário (sempre): {','.join(map(str, nucleo_prioritario))}")
        print(f"🔄 Núcleo rotativo: {','.join(map(str, nucleo_rotativo))}")
        print()
        
        for i, comb in enumerate(combinacoes, 1):
            rotativos_usados = [n for n in comb if n in nucleo_rotativo]
            complementares_usados = [n for n in comb if n not in self.nucleo_atual]
            
            print(f"Jogo {i:2d}: {','.join(map(str, comb))}")
            print(f"         Rotativos: {','.join(map(str, rotativos_usados))} | "
                  f"Complementares: {','.join(map(str, complementares_usados))}")
        
        # Salvar arquivo
        self._salvar_combinacoes(combinacoes, "escalonada")
    
    def _executar_estrategia_complementacao_total(self):
        """Estratégia 3: Complementação inteligente total"""
        if not self.nucleo_atual:
            print("⚠️ Defina o núcleo primeiro (opção 1)")
            return
        
        print("\n🔬 ESTRATÉGIA 3: COMPLEMENTAÇÃO INTELIGENTE TOTAL")
        print("="*60)
        print("💡 Conceito: Análise matemática dos 15 restantes para otimizar")
        print()
        
        try:
            qtd = int(input("Quantas combinações gerar (padrão 6): ") or "6")
        except:
            qtd = 6
        
        combinacoes = []
        
        # Análise inteligente dos complementares
        complementares_inteligentes = self._analisar_complementares_inteligentes()
        
        for i in range(qtd):
            combinacao = []
            
            # Usar 8-12 números do núcleo (variável)
            qtd_nucleo = random.randint(int(8), int(12))
            nucleo_escolhido = random.sample(self.nucleo_atual, qtd_nucleo)
            combinacao.extend(nucleo_escolhido)
            
            # Completar com complementares inteligentes
            faltam = 15 - len(combinacao)
            complementares_escolhidos = random.sample(complementares_inteligentes[:10], 
                                                    min(faltam, len(complementares_inteligentes)))
            combinacao.extend(complementares_escolhidos)
            
            # Se ainda falta, usar complementares normais
            if len(combinacao) < 15:
                faltam = 15 - len(combinacao)
                extras = [n for n in self.complementares if n not in combinacao]
                combinacao.extend(random.sample(extras, min(faltam, len(extras))))
            
            # Ordenar
            combinacao.sort()
            combinacoes.append(combinacao)
        
        # Mostrar resultados
        print(f"\n🔬 {qtd} COMBINAÇÕES GERADAS (ESTRATÉGIA COMPLEMENTAÇÃO TOTAL):")
        print("="*60)
        print(f"🧠 Complementares inteligentes: {','.join(map(str, complementares_inteligentes[:8]))}")
        print()
        
        for i, comb in enumerate(combinacoes, 1):
            nucleo_usado = [n for n in comb if n in self.nucleo_atual]
            complementares_usados = [n for n in comb if n not in self.nucleo_atual]
            
            print(f"Jogo {i:2d}: {','.join(map(str, comb))}")
            print(f"         Núcleo ({len(nucleo_usado)}): {','.join(map(str, nucleo_usado))} | "
                  f"Compl.: {','.join(map(str, complementares_usados))}")
        
        # Salvar arquivo
        self._salvar_combinacoes(combinacoes, "complementacao_total")
    
    def _analisar_complementares_inteligentes(self):
        """Analisa os 15 complementares para escolher os melhores"""
        try:
            # Score simples baseado em ausência e frequência recente
            scores = {}
            
            for numero in self.complementares:
                score = 0
                
                # Ausência (quanto maior, melhor para complementar)
                ausencia = self._calcular_ausencia_atual(numero, 9999)  # Último concurso
                score += min(ausencia * 2, 50)
                
                # Não deve estar muito ausente (equilíbrio)
                if ausencia > 15:
                    score -= 20
                
                # Fatores especiais
                score += self._calcular_fatores_especiais(numero) * 0.3
                
                scores[numero] = score
            
            # Ordenar por score
            ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [numero for numero, score in ranking]
            
        except:
            return self.complementares.copy()
    
    def _executar_estrategia_hibrida(self):
        """Estratégia 4: Híbrido - Núcleo + Expansão científica"""
        if not self.nucleo_atual:
            print("⚠️ Defina o núcleo primeiro (opção 1)")
            return
        
        print("\n⭐ ESTRATÉGIA 4: HÍBRIDO - NÚCLEO + EXPANSÃO CIENTÍFICA")
        print("="*60)
        print("💡 Conceito: Combina todas as estratégias anteriores")
        print()
        
        try:
            qtd = int(input("Quantas combinações gerar (padrão 12): ") or "12")
        except:
            qtd = 12
        
        combinacoes = []
        
        for i in range(qtd):
            # Escolher estratégia para esta combinação
            estrategia_tipo = (i % 4) + 1
            
            if estrategia_tipo == 1:
                # Núcleo completo + 5 complementares
                combinacao = self.nucleo_atual.copy()
                complementares_escolhidos = random.sample(self.complementares, 5)
                combinacao.extend(complementares_escolhidos)
                tipo = "Núcleo completo"
                
            elif estrategia_tipo == 2:
                # Núcleo prioritário + mix
                combinacao = self.nucleo_atual[:7].copy()  # Top 7
                mix = random.sample(self.nucleo_atual[7:] + self.complementares[:8], 8)
                combinacao.extend(mix)
                tipo = "Prioritário+mix"
                
            elif estrategia_tipo == 3:
                # Balanceado
                combinacao = random.sample(self.nucleo_atual, 9)
                complementares_escolhidos = random.sample(self.complementares[:10], 6)
                combinacao.extend(complementares_escolhidos)
                tipo = "Balanceado"
                
            else:
                # Científico - baseado em análise
                complementares_intel = self._analisar_complementares_inteligentes()
                combinacao = random.sample(self.nucleo_atual, 8)
                combinacao.extend(random.sample(complementares_intel[:7], 7))
                tipo = "Científico"
            
            # Garantir 15 números únicos
            combinacao = list(set(combinacao))
            while len(combinacao) < 15:
                candidatos = [n for n in range(1, 26) if n not in combinacao]
                combinacao.extend(random.sample(candidatos, min(15 - len(combinacao), len(candidatos))))
            
            combinacao = combinacao[:15]  # Garantir exatamente 15
            combinacao.sort()
            combinacoes.append((combinacao, tipo))
        
        # Mostrar resultados
        print(f"\n⭐ {qtd} COMBINAÇÕES GERADAS (ESTRATÉGIA HÍBRIDA):")
        print("="*60)
        
        for i, (comb, tipo) in enumerate(combinacoes, 1):
            nucleo_usado = [n for n in comb if n in self.nucleo_atual]
            
            print(f"Jogo {i:2d}: {','.join(map(str, comb))}")
            print(f"         Tipo: {tipo} | Núcleo usado: {len(nucleo_usado)}/10")
        
        # Salvar arquivo
        self._salvar_combinacoes([comb for comb, tipo in combinacoes], "hibrida")
    
    def _relatorio_estrategias(self):
        """Relatório detalhado de todas as estratégias"""
        print("\n📋 RELATÓRIO COMPLETO DAS ESTRATÉGIAS")
        print("="*60)
        
        if not self.nucleo_atual:
            print("⚠️ Defina o núcleo primeiro (opção 1)")
            return
        
        print(f"🎯 NÚCLEO ATUAL: {','.join(map(str, self.nucleo_atual))}")
        print(f"📦 COMPLEMENTARES: {len(self.complementares)} números disponíveis")
        print()
        
        for num, desc in self.estrategias_disponiveis.items():
            print(f"📊 ESTRATÉGIA {num}: {desc}")
            
            if num == 1:
                print("   • Núcleo: 10 números fixos sempre presentes")
                print("   • Complementares: 5 rotativos aleatórios")
                print("   • Vantagem: Máxima concentração nos melhores")
                print("   • Expectativa: 6-8 acertos do núcleo por jogo")
                
            elif num == 2:
                print("   • Núcleo prioritário: 5 sempre + 3-4 rotativos")
                print("   • Complementares: Completam para 15")
                print("   • Vantagem: Equilibrio entre concentração e variação")
                print("   • Expectativa: 5-7 acertos, maior diversidade")
                
            elif num == 3:
                print("   • Núcleo variável: 8-12 números por jogo")
                print("   • Complementares inteligentes: Análise científica")
                print("   • Vantagem: Adaptação dinâmica e cobertura ampla")
                print("   • Expectativa: Performance consistente 4-6 acertos")
                
            elif num == 4:
                print("   • Híbrido: Combina todas as estratégias")
                print("   • Variação: Cada jogo usa estratégia diferente")
                print("   • Vantagem: Máxima cobertura e flexibilidade")
                print("   • Expectativa: Performance equilibrada geral")
            
            print()
    
    def _salvar_combinacoes(self, combinacoes, tipo_estrategia):
        """Salva as combinações em arquivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"combinacoes_estrategia_{tipo_estrategia}_{timestamp}.txt"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(f"🎯 GERADOR ESTRATÉGICO - {tipo_estrategia.upper()}\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Núcleo usado: {','.join(map(str, self.nucleo_atual))}\n")
                f.write("="*60 + "\n\n")
                
                for i, comb in enumerate(combinacoes, 1):
                    f.write(f"Jogo {i:2d}: {','.join(map(str, comb))}\n")
                
                # Seção CHAVE DE OURO
                f.write("\n" + "="*60 + "\n")
                f.write("🔑 CHAVE DE OURO - APENAS AS COMBINAÇÕES:\n")
                f.write("="*60 + "\n")
                for comb in combinacoes:
                    f.write(f"{','.join(map(str, comb))}\n")
            
            print(f"\n💾 Arquivo salvo: {nome_arquivo}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

def main():
    """Função principal"""
    print("🎯 GERADOR ESTRATÉGICO BASEADO NOS 10 MELHORES")
    print("="*60)
    
    gerador = GeradorEstrategicoMelhores()
    gerador.executar_menu_estrategico()

if __name__ == "__main__":
    main()
