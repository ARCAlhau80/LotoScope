#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR DOS 10 MELHORES NÚMEROS - NÚCLEO DINÂMICO
================================================================
ESTRATÉGIA: Núcleo fixo com os 10 MELHORES números do momento
- Baseado em viradas de ciclo, ausências, números em alta
- Pirâmide invertida e análise de padrões dinâmicos  
- Complementares otimizados conforme tamanho (15-20 números)
================================================================
"""

import os
import sys
import random
from datetime import datetime
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import db_config
    DATABASE_DISPONIVEL = True
    print("✅ Database Config carregado - usando dados REAIS da base")
except ImportError:
    DATABASE_DISPONIVEL = False
    print("⚠️ Database Config não disponível - usando análise estática SIMULADA")

class GeradaDez10MelhoresNucleo:
    """Gerador com núcleo fixo dos 10 MELHORES números dinâmicos"""
    
    def __init__(self):
        self.nucleo_10_melhores = []  # Os 10 melhores do momento
        self.candidatos_complementares = []  # Outros 15 números
        self.database_config = None
        
        if DATABASE_DISPONIVEL:
            try:
                self.database_config = db_config
                print("✅ Conexão com base de dados ativa")
            except:
                print("⚠️ Base de dados indisponível - modo estático")
    
    def analisar_10_melhores_momento(self):
        """
        ANÁLISE INTELIGENTE DOS 10 MELHORES NÚMEROS
        Critérios dinâmicos baseados no estado atual
        """
        print("🧠 ANALISANDO OS 10 MELHORES NÚMEROS DO MOMENTO...")
        print("🎯 Critérios: Ciclos + Ausências + Alta + Pirâmide + Padrões")
        
        scores_dinamicos = {}
        
        # Inicializar todos os números
        for numero in range(1, 26):
            scores_dinamicos[numero] = 0.0
        
        try:
            if self.database_config and DATABASE_DISPONIVEL:
                print("📊 Usando análise dinâmica com base de dados...")
                self._calcular_scores_dinamicos(scores_dinamicos)
            else:
                print("📊 Usando análise estática inteligente...")
                self._calcular_scores_estaticos_inteligentes(scores_dinamicos)
                
        except Exception as e:
            print(f"⚠️ Erro na análise: {e}")
            self._calcular_scores_estaticos_inteligentes(scores_dinamicos)
        
        # Selecionar os 10 MELHORES
        ranking_melhores = sorted(scores_dinamicos.items(), 
                                key=lambda x: x[1], reverse=True)
        
        self.nucleo_10_melhores = [numero for numero, score in ranking_melhores[:10]]
        self.candidatos_complementares = [n for n in range(1, 26) 
                                        if n not in self.nucleo_10_melhores]
        
        print("\n🏆 OS 10 MELHORES NÚMEROS IDENTIFICADOS:")
        print("=" * 50)
        for i, (numero, score) in enumerate(ranking_melhores[:10], 1):
            print(f"   {i:2d}º lugar: Número {numero:2d} - Score: {score:.1f}")
        
        print(f"\n🎯 NÚCLEO DOS 10 MELHORES: {','.join(map(str, sorted(self.nucleo_10_melhores)))}")
        print(f"📦 Candidatos complementares: {len(self.candidatos_complementares)} números")
        
        return self.nucleo_10_melhores
    
    def _calcular_scores_dinamicos(self, scores):
        """Cálculo com dados reais da base"""
        print("🔄 Análise dinâmica em progresso...")
        
        # 1. VIRADAS DE CICLO (40% - mais crítico)
        print("   🔄 Analisando viradas de ciclo...")
        for numero in range(1, 26):
            score_ciclo = self._avaliar_virada_ciclo(numero)
            scores[numero] += score_ciclo * 0.40
        
        # 2. AUSÊNCIAS PROLONGADAS (30%)
        print("   ⏰ Analisando ausências prolongadas...")
        for numero in range(1, 26):
            score_ausencia = self._avaliar_ausencia_prolongada(numero)
            scores[numero] += score_ausencia * 0.30
        
        # 3. NÚMEROS EM ALTA (20%)
        print("   📈 Analisando números em alta...")
        for numero in range(1, 26):
            score_alta = self._avaliar_numero_em_alta(numero)
            scores[numero] += score_alta * 0.20
        
        # 4. FATORES ESPECIAIS (10%)
        print("   🎯 Analisando fatores especiais...")
        for numero in range(1, 26):
            score_especial = self._avaliar_fatores_especiais(numero)
            scores[numero] += score_especial * 0.10
    
    def _calcular_scores_estaticos_inteligentes(self, scores):
        """Cálculo estático baseado em padrões conhecidos"""
        print("🔄 Análise estática inteligente em progresso...")
        
        # PADRÃO 1: Pirâmide invertida - centro forte
        piramide_scores = {
            13: 100, 14: 95, 12: 90, 15: 85, 11: 80,
            16: 75, 10: 70, 17: 65, 9: 60, 18: 55,
            8: 45, 19: 40, 7: 35, 20: 30, 6: 25
        }
        
        # PADRÃO 2: Números primos (força especial)
        primos_fortes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        
        # PADRÃO 3: Fibonacci (sequência mágica)
        fibonacci_numeros = [1, 2, 3, 5, 8, 13, 21]
        
        # PADRÃO 4: Múltiplos estratégicos
        multiplos_5 = [5, 10, 15, 20, 25]
        
        for numero in range(1, 26):
            score_total = 0
            
            # Score base da pirâmide
            if numero in piramide_scores:
                score_total += piramide_scores[numero]
            else:
                score_total += 20  # Score mínimo
            
            # Bônus para primos
            if numero in primos_fortes:
                score_total += 30
            
            # Bônus para Fibonacci
            if numero in fibonacci_numeros:
                score_total += 25
            
            # Bônus para múltiplos de 5
            if numero in multiplos_5:
                score_total += 15
            
            # Penalidade para extremos (muito baixos ou altos)
            if numero <= 3 or numero >= 23:
                score_total -= 20
            
            scores[numero] = score_total
    
    def _avaliar_virada_ciclo(self, numero):
        """Avalia se número está próximo de virar ciclo"""
        try:
            if self.database_config and DATABASE_DISPONIVEL:
                # ANÁLISE REAL COM DADOS DA BASE
                print(f"      🔄 Analisando ciclo real do número {numero}...")
                
                # Buscar ausência atual do número
                ausencia_atual = self._obter_ausencia_atual_real(numero)
                
                # Buscar ciclo médio histórico do número  
                ciclo_medio_real = self._obter_ciclo_medio_real(numero)
                
                if ciclo_medio_real == 0:
                    return 50  # Score neutro
                
                # Calcular proximidade da virada baseada em dados reais
                proximidade = min((ausencia_atual / ciclo_medio_real) * 100, 100)
                
                # Bônus extra se está muito próximo do ciclo médio
                if ausencia_atual >= ciclo_medio_real * 0.8:  # 80% do ciclo
                    proximidade += 20  # Bônus de virada iminente
                
                # Bônus máximo se ultrapassou o ciclo médio
                if ausencia_atual >= ciclo_medio_real:
                    proximidade += 30  # Bônus de "devendo sair"
                
                return min(proximidade, 100)
                
            else:
                # Fallback: simulação inteligente
                return self._simular_analise_ciclo(numero)
            
        except Exception as e:
            print(f"      ⚠️ Erro na análise de ciclo do {numero}: {e}")
            return self._simular_analise_ciclo(numero)
    
    def _avaliar_ausencia_prolongada(self, numero):
        """Avalia ausência prolongada do número"""
        try:
            ausencia = self._simular_ausencia_atual(numero)
            
            # Números com muita ausência ganham pontos
            if ausencia > 15:
                return min(ausencia * 4, 100)
            elif ausencia > 8:
                return ausencia * 2
            else:
                return ausencia
                
        except:
            return 30  # Score neutro
    
    def _avaliar_numero_em_alta(self, numero):
        """Avalia se número está em alta (frequência recente)"""
        try:
            # Simulação - em implementação real verificaria últimos 20 concursos
            freq_recente = self._simular_frequencia_recente(numero)
            return min(freq_recente * 20, 100)
            
        except:
            return 40  # Score neutro
    
    def _avaliar_fatores_especiais(self, numero):
        """Avalia características especiais do número"""
        score = 0
        
        # Primos
        if self._eh_primo(numero):
            score += 40
        
        # Fibonacci
        if numero in [1, 2, 3, 5, 8, 13, 21]:
            score += 30
            
        # Centro da pirâmide
        if 11 <= numero <= 15:
            score += 25
            
        # Múltiplos de 5
        if numero % 5 == 0:
            score += 15
        
        return min(score, 100)
    
    # Métodos de simulação (substituir por dados reais quando disponíveis)
    def _simular_ausencia_atual(self, numero):
        """Simula ausência atual do número"""
        # Simulação baseada em padrões conhecidos
        if 10 <= numero <= 16:  # Centro
            return random.randint(int(3), int(12))
        elif numero <= 8 or numero >= 18:  # Extremos
            return random.randint(int(8), int(20))
        else:
            return random.randint(int(5), int(15))
    
    def _simular_ciclo_medio(self, numero):
        """Simula ciclo médio do número"""
        # Simulação - em média números saem a cada 6-12 jogos
        if 11 <= numero <= 15:  # Centro sai mais
            return random.uniform(5, 8)
        else:
            return random.uniform(7, 11)
    
    def _simular_frequencia_recente(self, numero):
        """Simula frequência nos últimos jogos"""
        # Simulação 0-1 (percentual de aparição recente)
        if 10 <= numero <= 16:
            return random.uniform(0.2, 0.8)  # Centro aparece mais
        else:
            return random.uniform(0.1, 0.5)  # Extremos menos
    
    def _eh_primo(self, numero):
        """Verifica se número é primo"""
        if numero < 2:
            return False
        for i in range(2, int(numero ** 0.5) + 1):
            if numero % i == 0:
                return False
        return True
    
    def gerar_combinacoes_nucleo_10_melhores(self, tamanho=15, quantidade=5):
        """
        Gera combinações com núcleo fixo dos 10 melhores
        """
        print(f"\n🚀 GERANDO COMBINAÇÕES COM NÚCLEO DOS 10 MELHORES")
        print(f"🎯 Tamanho: {tamanho} números | Quantidade: {quantidade}")
        print(f"🔥 Núcleo fixo: {len(self.nucleo_10_melhores)} melhores")
        print(f"📊 Complementares necessários: {tamanho - 10}")
        
        if not self.nucleo_10_melhores:
            print("❌ Núcleo não definido! Execute analisar_10_melhores_momento() primeiro")
            return []
        
        if tamanho < 10 or tamanho > 20:
            print("❌ Tamanho deve ser entre 10 e 20 números")
            return []
        
        complementares_necessarios = tamanho - 10
        combinacoes_geradas = []
        
        print(f"\n{'='*60}")
        print(f"🎯 NÚCLEO FIXO: {','.join(map(str, sorted(self.nucleo_10_melhores)))}")
        print(f"{'='*60}")
        
        for i in range(quantidade):
            # Selecionar complementares aleatórios
            complementares = random.sample(self.candidatos_complementares, 
                                         complementares_necessarios)
            
            # Formar combinação completa
            combinacao_completa = sorted(self.nucleo_10_melhores + complementares)
            combinacoes_geradas.append(combinacao_completa)
            
            print(f"   ✅ Jogo {i+1:2d}: {','.join(map(str, combinacao_completa))}")
        
        print(f"\n🎉 {quantidade} combinações geradas com sucesso!")
        print(f"🔥 Todas contêm os 10 MELHORES números do momento")
        
        return combinacoes_geradas
    
    def salvar_combinacoes_arquivo(self, combinacoes, tamanho):
        """Salva combinações em arquivo com timestamp"""
        if not combinacoes:
            print("❌ Nenhuma combinação para salvar")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"combinacoes_10_melhores_{tamanho}nums_{timestamp}.txt"
        caminho_completo = os.path.join(os.path.dirname(__file__), nome_arquivo)
        
        try:
            with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
                arquivo.write("🎯 COMBINAÇÕES NÚCLEO DOS 10 MELHORES NÚMEROS\n")
                arquivo.write("="*60 + "\n")
                arquivo.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                arquivo.write(f"Núcleo fixo: {','.join(map(str, sorted(self.nucleo_10_melhores)))}\n")
                arquivo.write(f"Tamanho: {tamanho} números | Total: {len(combinacoes)} combinações\n")
                arquivo.write("="*60 + "\n\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    # Formato expandido
                    arquivo.write(f"Jogo {i:3d}: {','.join(map(str, combinacao))}\n")
                
                arquivo.write("\n" + "="*60 + "\n")
                arquivo.write("🗝️ CHAVE DE OURO (formato compacto):\n")
                arquivo.write("-"*40 + "\n")
                
                for i, combinacao in enumerate(combinacoes, 1):
                    # Formato compacto para apostas
                    arquivo.write(f"{','.join(map(str, combinacao))}\n")
            
            print(f"💾 Arquivo salvo: {nome_arquivo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def executar_menu_10_melhores(self):
        """Menu interativo para geração com os 10 melhores"""
        while True:
            print("\n" + "="*70)
            print("🎯 GERADOR NÚCLEO DOS 10 MELHORES NÚMEROS")
            print("="*70)
            print("🧠 Estratégia: Os 10 melhores do momento + complementares")
            print("="*70)
            
            if self.nucleo_10_melhores:
                print(f"🔥 NÚCLEO ATUAL: {','.join(map(str, sorted(self.nucleo_10_melhores)))}")
            else:
                print("⚠️ Núcleo não definido")
                
            print("="*70)
            print("1️⃣  🧠 Analisar os 10 Melhores do Momento")
            print("2️⃣  🚀 Gerar Combinações (Núcleo + Complementares)")
            print("3️⃣  🎯 Teste Rápido (3 combinações de 15 números)")
            print("4️⃣  📊 Relatório dos 10 Melhores")
            print("0️⃣  🚪 Sair")
            print("="*70)
            
            try:
                opcao = input("Escolha uma opção (0-4): ").strip()
                
                if opcao == "0":
                    print("👋 Até logo!")
                    break
                    
                elif opcao == "1":
                    print("\n🧠 INICIANDO ANÁLISE DOS 10 MELHORES...")
                    self.analisar_10_melhores_momento()
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
                elif opcao == "2":
                    if not self.nucleo_10_melhores:
                        print("❌ Execute primeiro a análise dos 10 melhores (opção 1)")
                        input("⏸️ Pressione ENTER para continuar...")
                        continue
                        
                    try:
                        tamanho = int(input("Quantos números por jogo (10-20) [15]: ") or "15")
                        if tamanho < 10 or tamanho > 20:
                            print("❌ Tamanho deve ser entre 10 e 20")
                            continue
                            
                        quantidade = int(input("Quantas combinações deseja (1-50) [5]: ") or "5")
                        if quantidade < 1 or quantidade > 50:
                            print("❌ Quantidade deve ser entre 1 e 50")
                            continue
                        
                        combinacoes = self.gerar_combinacoes_nucleo_10_melhores(tamanho, quantidade)
                        
                        if combinacoes:
                            salvar = input("💾 Salvar em arquivo? (s/N): ").strip().lower()
                            if salvar in ['s', 'sim', 'y', 'yes']:
                                self.salvar_combinacoes_arquivo(combinacoes, tamanho)
                                
                    except ValueError:
                        print("❌ Digite apenas números")
                        
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
                elif opcao == "3":
                    if not self.nucleo_10_melhores:
                        print("❌ Execute primeiro a análise dos 10 melhores (opção 1)")
                        input("⏸️ Pressione ENTER para continuar...")
                        continue
                    
                    print("\n🎯 TESTE RÁPIDO - 10 MELHORES")
                    combinacoes = self.gerar_combinacoes_nucleo_10_melhores(15, 3)
                    
                    if combinacoes:
                        print(f"\n🎯 Análise rápida dos jogos:")
                        for i, comb in enumerate(combinacoes, 1):
                            nucleos_presentes = sum(1 for n in comb if n in self.nucleo_10_melhores)
                            soma = sum(comb)
                            print(f"   {i}. Núcleo: {nucleos_presentes}/10 | Soma: {soma}")
                    
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
                elif opcao == "4":
                    if not self.nucleo_10_melhores:
                        print("❌ Execute primeiro a análise dos 10 melhores (opção 1)")
                        input("⏸️ Pressione ENTER para continuar...")
                        continue
                    
                    print("\n📊 RELATÓRIO DOS 10 MELHORES")
                    print("="*50)
                    print(f"🎯 Núcleo: {','.join(map(str, sorted(self.nucleo_10_melhores)))}")
                    print(f"📦 Complementares: {len(self.candidatos_complementares)} disponíveis")
                    print(f"🔢 Range complementares: {min(self.candidatos_complementares)}-{max(self.candidatos_complementares)}")
                    
                    # Análise dos tipos no núcleo
                    primos_nucleo = [n for n in self.nucleo_10_melhores if self._eh_primo(n)]
                    fibonacci_nucleo = [n for n in self.nucleo_10_melhores if n in [1,2,3,5,8,13,21]]
                    
                    print(f"🔷 Primos no núcleo: {len(primos_nucleo)} → {primos_nucleo}")
                    print(f"🌀 Fibonacci no núcleo: {len(fibonacci_nucleo)} → {fibonacci_nucleo}")
                    
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
                else:
                    print("❌ Opção inválida")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                input("⏸️ Pressione ENTER para continuar...")

    def _obter_ausencia_atual_real(self, numero):
        """Obter ausência atual real do número da base de dados"""
        try:
            # Query para contar ausência desde última aparição
            query = """
            SELECT COUNT_BIG(*) FROM Resultados_INT r
            WHERE r.Concurso > (
                SELECT ISNULL(MAX(Concurso), 0) FROM Resultados_INT 
                WHERE N1 = ? OR N2 = ? OR N3 = ? OR N4 = ? OR N5 = ? OR
                      N6 = ? OR N7 = ? OR N8 = ? OR N9 = ? OR N10 = ? OR
                      N11 = ? OR N12 = ? OR N13 = ? OR N14 = ? OR N15 = ?
            )
            """
            
            params = [numero] * 15
            resultado = self.database_config.execute_query(query, tuple(params))
            
            if resultado and resultado[0][0] is not None:
                ausencia = resultado[0][0]
                print(f"         📊 Número {numero}: {ausencia} concursos sem aparecer")
                return ausencia
            else:
                return 0
            
        except Exception as e:
            print(f"         ⚠️ Erro ao buscar ausência real: {e}")
            return self._simular_ausencia_atual(numero)
            
        except Exception as e:
            print(f"         ⚠️ Erro ao buscar ausência real: {e}")
            return self._simular_ausencia_atual(numero)
    
    def _obter_ciclo_medio_real(self, numero):
        """Obter ciclo médio real do número da base de dados"""
        try:
            # Query corrigida - sem ORDER BY na CTE, usando subconsulta
            query = """
            SELECT AVG(CAST(diferenca AS FLOAT)) as ciclo_medio
            FROM (
                SELECT 
                    Concurso - LAG(Concurso) OVER (ORDER BY Concurso) as diferenca
                FROM Resultados_INT 
                WHERE N1 = ? OR N2 = ? OR N3 = ? OR N4 = ? OR N5 = ? OR
                      N6 = ? OR N7 = ? OR N8 = ? OR N9 = ? OR N10 = ? OR
                      N11 = ? OR N12 = ? OR N13 = ? OR N14 = ? OR N15 = ?
            ) AS intervalos
            WHERE diferenca IS NOT NULL
            """
            
            params = [numero] * 15
            resultado = self.database_config.execute_query(query, tuple(params))
            
            if resultado and resultado[0][0] is not None:
                ciclo_medio = resultado[0][0]
                print(f"         🔄 Número {numero}: ciclo médio de {ciclo_medio:.1f} concursos")
                return ciclo_medio
            else:
                return 7.0  # Valor padrão se não há dados
            
        except Exception as e:
            print(f"         ⚠️ Erro ao buscar ciclo real: {e}")
            return self._simular_ciclo_medio(numero)
    
    def _simular_analise_ciclo(self, numero):
        """Simulação inteligente da análise de ciclo"""
        ausencia_atual = self._simular_ausencia_atual(numero)
        ciclo_medio_numero = self._simular_ciclo_medio(numero)
        
        if ciclo_medio_numero == 0:
            return 50
        
        # Proximidade da virada (0 a 100)
        proximidade = min((ausencia_atual / ciclo_medio_numero) * 100, 100)
        return proximidade

def main():
    """Função principal"""
    print("🎯 SISTEMA DE NÚCLEO DOS 10 MELHORES NÚMEROS")
    print("🧠 Análise inteligente baseada em padrões dinâmicos")
    print("="*60)
    
    gerador = GeradaDez10MelhoresNucleo()
    gerador.executar_menu_10_melhores()

if __name__ == "__main__":
    main()
