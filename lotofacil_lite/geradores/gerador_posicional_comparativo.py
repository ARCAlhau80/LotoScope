#!/usr/bin/env python3
"""
🎯 GERADOR POSICIONAL COMPARATIVO
=================================
Gera combinações comparando POSIÇÃO POR POSIÇÃO com o último sorteio.
Para cenário RESET EXTREMO: gera números MENORES em cada posição.

Exemplo:
- Último sorteio: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
- Para RESET (menores): [1,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
"""

import sqlite3
import random
from typing import List, Tuple, Dict
from datetime import datetime
import os

class GeradorPosicionalComparativo:
    def __init__(self):
        self.db_path = r"c:\Users\AR CALHAU\source\repos\LotoScope\Lotofacil.db"
        print("🎯 GERADOR POSICIONAL COMPARATIVO INICIALIZADO")
        print("📊 Estratégia: Comparação posição por posição com último sorteio")
        
    def obter_ultimo_sorteio(self) -> List[int]:
        """Obtém o último sorteio da base de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Bola1, Bola2, Bola3, Bola4, Bola5, Bola6, Bola7, Bola8, 
                           Bola9, Bola10, Bola11, Bola12, Bola13, Bola14, Bola15
                    FROM Resultados_INT 
                    ORDER BY Concurso DESC 
                    LIMIT 1
                """)
                
                resultado = cursor.fetchone()
                if resultado:
                    ultimo_sorteio = list(resultado)
                    print(f"📊 Último sorteio obtido: {ultimo_sorteio}")
                    return ultimo_sorteio
                else:
                    print("⚠️ Nenhum sorteio encontrado na base")
                    return list(range(1, 16))  # Fallback
                    
        except Exception as e:
            print(f"❌ Erro ao obter último sorteio: {e}")
            # Fallback baseado no concurso 3504 conhecido do contexto
            # Baseado nas imagens dos attachments
            return [1, 2, 6, 7, 8, 10, 11, 12, 19, 20, 21, 22, 23, 24, 25]
    
    def gerar_combinacao_menores(self, ultimo_sorteio: List[int], tentativa: int = 0) -> List[int]:
        """
        Gera combinação com números MENORES que o último sorteio em cada posição
        """
        print(f"\n🔄 Tentativa {tentativa + 1} - Gerando números MENORES por posição")
        print(f"📊 Referência: {ultimo_sorteio}")
        
        nova_combinacao = []
        numeros_usados = set()
        
        for pos in range(15):
            numero_anterior = ultimo_sorteio[pos]
            
            # Para reset extremo: buscar números significativamente menores
            if tentativa == 0:
                # Primeira tentativa: muito agressivo (2-4 números abaixo)
                limite_superior = max(1, numero_anterior - 2)
                limite_inferior = max(1, numero_anterior - 4)
            elif tentativa == 1:
                # Segunda tentativa: moderado (1-3 números abaixo)
                limite_superior = max(1, numero_anterior - 1)
                limite_inferior = max(1, numero_anterior - 3)
            else:
                # Tentativas subsequentes: qualquer número menor
                limite_superior = max(1, numero_anterior - 1)
                limite_inferior = 1
            
            # Busca número disponível na faixa
            candidatos = []
            for num in range(limite_inferior, limite_superior + 1):
                if num not in numeros_usados and 1 <= num <= 25:
                    candidatos.append(num)
            
            # Se não há candidatos menores, pega o menor disponível maior
            if not candidatos:
                for num in range(numero_anterior, 26):
                    if num not in numeros_usados:
                        candidatos.append(num)
                        break
            
            # Se ainda não há candidatos, pega qualquer disponível
            if not candidatos:
                for num in range(1, 26):
                    if num not in numeros_usados:
                        candidatos.append(num)
                        break
            
            if candidatos:
                numero_escolhido = random.choice(candidatos)
                nova_combinacao.append(numero_escolhido)
                numeros_usados.add(numero_escolhido)
                
                if numero_escolhido < numero_anterior:
                    status = "✅ MENOR"
                elif numero_escolhido > numero_anterior:
                    status = "⚠️ MAIOR"
                else:
                    status = "🔄 IGUAL"
                print(f"   Pos {pos+1:2d}: {numero_anterior:2d} → {numero_escolhido:2d} {status}")
            else:
                print(f"   ❌ Pos {pos+1}: Não foi possível encontrar número válido")
                break
        
        # Ordena a combinação final
        nova_combinacao.sort()
        
        # Calcula estatísticas de comparação
        menores = 0
        maiores = 0
        iguais = 0
        
        for i in range(15):
            if nova_combinacao[i] < ultimo_sorteio[i]:
                menores += 1
            elif nova_combinacao[i] > ultimo_sorteio[i]:
                maiores += 1
            else:
                iguais += 1
        
        print(f"\n📊 RESULTADO DA COMPARAÇÃO POSICIONAL:")
        print(f"   ✅ Menores: {menores}")
        print(f"   ⚠️ Maiores: {maiores}")
        print(f"   🔄 Iguais: {iguais}")
        print(f"   🎯 Combinação: {nova_combinacao}")
        
        return nova_combinacao, (menores, maiores, iguais)
    
    def gerar_multiplas_combinacoes(self, quantidade: int = 6) -> List[List[int]]:
        """Gera múltiplas combinações otimizadas para RESET EXTREMO"""
        print(f"\n🎲 Gerando {quantidade} combinações para RESET EXTREMO")
        print("🎯 Objetivo: Maximizar números MENORES por posição")
        
        ultimo_sorteio = self.obter_ultimo_sorteio()
        combinacoes = []
        estatisticas = []
        
        for i in range(quantidade):
            print(f"\n{'='*50}")
            print(f"🎲 COMBINAÇÃO {i+1}/{quantidade}")
            print(f"{'='*50}")
            
            # Múltiplas tentativas para otimizar
            melhor_combinacao = None
            melhor_score = -1
            melhor_stats = None
            
            for tentativa in range(3):
                try:
                    combinacao, stats = self.gerar_combinacao_menores(ultimo_sorteio, tentativa)
                    score = stats[0] - stats[1]  # menores - maiores
                    
                    if score > melhor_score:
                        melhor_combinacao = combinacao
                        melhor_score = score
                        melhor_stats = stats
                        
                except Exception as e:
                    print(f"❌ Erro na tentativa {tentativa}: {e}")
                    continue
            
            if melhor_combinacao:
                combinacoes.append(melhor_combinacao)
                estatisticas.append(melhor_stats)
                print(f"🏆 MELHOR: {melhor_combinacao}")
                print(f"📊 Score: {melhor_score} (menores-maiores)")
            else:
                print("❌ Falha ao gerar combinação válida")
        
        return combinacoes, estatisticas
    
    def salvar_combinacoes(self, combinacoes: List[List[int]], estatisticas: List[Tuple[int, int, int]]):
        """Salva as combinações em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"combinacoes_posicional_comparativo_{timestamp}.txt"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("🎯 COMBINAÇÕES POSICIONAIS COMPARATIVAS\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data/Hora: {datetime.now()}\n")
            f.write("Estratégia: Reset extremo - números menores por posição\n")
            f.write(f"Quantidade: {len(combinacoes)} jogos de 15 números\n\n")
            
            ultimo_sorteio = self.obter_ultimo_sorteio()
            f.write(f"🔗 Referência (último sorteio): {ultimo_sorteio}\n\n")
            
            for i, (combinacao, stats) in enumerate(zip(combinacoes, estatisticas)):
                menores, maiores, iguais = stats
                score = menores - maiores
                f.write(f"Jogo {i+1:2d}: {' '.join(f'{n:2d}' for n in combinacao)} | ")
                f.write(f"Score: {score:+2d} (M:{menores} m:{maiores} =:{iguais})\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("COMBINAÇÕES FORMATO VÍRGULAS (PARA APOSTAS):\n")
            f.write("=" * 50 + "\n")
            for combinacao in combinacoes:
                f.write(','.join(map(str, combinacao)) + "\n")
        
        print(f"💾 Arquivo salvo: {nome_arquivo}")
        return nome_arquivo

def main():
    """Função principal interativa"""
    gerador = GeradorPosicionalComparativo()
    
    while True:
        print("\n" + "="*50)
        print("🎯 GERADOR POSICIONAL COMPARATIVO")
        print("="*50)
        print("1️⃣  🎲 Gerar Combinações Reset Extremo")
        print("2️⃣  📊 Ver Último Sorteio")
        print("3️⃣  🧪 Teste de Combinação Única")
        print("0️⃣  🚪 Sair")
        print("="*50)
        
        opcao = input("Escolha uma opção (0-3): ").strip()
        
        if opcao == "1":
            try:
                quantidade = int(input("Quantas combinações? [6]: ") or "6")
                combinacoes, estatisticas = gerador.gerar_multiplas_combinacoes(quantidade)
                
                if combinacoes:
                    gerador.salvar_combinacoes(combinacoes, estatisticas)
                    
                    print(f"\n🎉 {len(combinacoes)} combinações geradas com sucesso!")
                    print("\n📊 RESUMO ESTATÍSTICO:")
                    for i, stats in enumerate(estatisticas):
                        menores, maiores, iguais = stats
                        score = menores - maiores
                        print(f"   Jogo {i+1}: Score {score:+2d} (M:{menores} m:{maiores} =:{iguais})")
                        
            except ValueError:
                print("❌ Quantidade inválida")
                
        elif opcao == "2":
            ultimo = gerador.obter_ultimo_sorteio()
            print(f"\n📊 ÚLTIMO SORTEIO: {ultimo}")
            
        elif opcao == "3":
            ultimo = gerador.obter_ultimo_sorteio()
            combinacao, stats = gerador.gerar_combinacao_menores(ultimo)
            print(f"\n🎯 Combinação teste gerada: {combinacao}")
            
        elif opcao == "0":
            print("👋 Encerrando gerador posicional...")
            break
            
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()