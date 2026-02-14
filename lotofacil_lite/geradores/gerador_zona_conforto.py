"""
🎯 GERADOR ZONA DE CONFORTO - V2.0 CORRIGIDO
Data: 06 de outubro de 2025
Estratégia: 80% zona 1-17, permite sequências longas, usa IA existente

CONCEITO:
- 80% dos números na zona de conforto (1-17)
- Permite sequências consecutivas de até 12 números
- Integra aprendizado das redes neurais existentes
- Simplicidade > Complexidade algorítmica
"""

import random
import os
from datetime import datetime
from collections import Counter

class GeradorZonaConforto:
    def __init__(self):
        self.zona_conforto = list(range(1, 18))  # 1-17
        self.zona_complementar = list(range(18, 26))  # 18-25
        
        # 🚀 INTEGRAÇÃO DAS DESCOBERTAS DOS CAMPOS DE COMPARAÇÃO
        try:
            from integracao_descobertas_comparacao import IntegracaoDescobertasComparacao
            self.descobertas = IntegracaoDescobertasComparacao()
            print("🔬 Descobertas dos campos de comparação aplicadas")
        except ImportError:
            self.descobertas = None
            print("⚠️ Módulo de descobertas não encontrado - funcionamento normal")
        
        # 🔧 INTEGRAÇÃO COM SISTEMA DE CALIBRAÇÃO AUTOMÁTICA
        try:
            from aplicador_calibracao import aplicador_calibracao
            self.aplicador_calibracao = aplicador_calibracao
            print("🔧 Sistema de calibração automática integrado")
        except ImportError:
            self.aplicador_calibracao = None
            print("⚠️ Sistema de calibração não disponível")
        
        print("🎯 Gerador Zona de Conforto V2.0 - CORRIGIDO + CALIBRAÇÃO AUTOMÁTICA")
        print("📊 Estratégia: 80% zona 1-17 + Sequências longas permitidas")
        
    def gerar_combinacao_zona_conforto(self, qtd_numeros=15):
        """Gera uma combinação focada na zona de conforto com calibração automática"""
        # 🔧 Aplica calibração automática se disponível
        config = {}
        if self.aplicador_calibracao:
            config = self.aplicador_calibracao.aplicar_configuracao_zona_conforto(qtd_numeros=qtd_numeros)
            if config.get('calibracao_ativa'):
                print("🔧 Aplicando calibração automática ao gerador")
        
        # Usa configurações calibradas ou padrão
        zona_inicio = config.get('zona_inicio', 1)
        zona_fim = config.get('zona_fim', 17)
        peso_zona = config.get('peso_zona', 0.8)
        
        # Atualiza zonas baseado na calibração
        self.zona_conforto = list(range(zona_inicio, zona_fim + 1))
        self.zona_complementar = [x for x in range(1, 26) if x not in self.zona_conforto]
        
        # Calcula quantidades baseado no peso calibrado
        qtd_zona_conforto = int(qtd_numeros * peso_zona)
        qtd_zona_complementar = qtd_numeros - qtd_zona_conforto
        
        # Verifica se há números suficientes nas zonas
        if len(self.zona_conforto) < qtd_zona_conforto:
            qtd_zona_conforto = len(self.zona_conforto)
            qtd_zona_complementar = qtd_numeros - qtd_zona_conforto
        
        # Seleciona números da zona de conforto
        numeros_zona = random.sample(self.zona_conforto, qtd_zona_conforto)
        
        # Seleciona números da zona complementar (se houver)
        numeros_complementar = []
        if qtd_zona_complementar > 0 and self.zona_complementar:
            qtd_complementar_real = min(qtd_zona_complementar, len(self.zona_complementar))
            numeros_complementar = random.sample(self.zona_complementar, qtd_complementar_real)
        
        # Combina e ordena
        combinacao = sorted(numeros_zona + numeros_complementar)
        
        # Completa se necessário
        while len(combinacao) < qtd_numeros:
            numero_adicional = random.randint(1, 25)
            if numero_adicional not in combinacao:
                combinacao.append(numero_adicional)
        
        combinacao = sorted(combinacao[:qtd_numeros])
        
        if config.get('calibracao_ativa'):
            print(f"🎯 Zona calibrada: {zona_inicio}-{zona_fim} (peso: {peso_zona:.1%})")
        
        return combinacao
    
    def gerar_com_sequencias(self, qtd_numeros=15):
        """Gera combinação permitindo sequências longas"""
        combinacao = []
        numeros_disponiveis = list(range(1, 26))
        
        # Aplica descobertas se disponível
        if self.descobertas:
            # Simula estado atual para demonstração
            estado_atual = (5, 6, 4)  # menor, maior, igual
            proximo_estado = self.descobertas.prever_proximo_estado(estado_atual)
            soma_estimada = self.descobertas.estimar_soma_por_estado(*estado_atual)
            
            print(f"🔮 Estado previsto: {proximo_estado}")
            print(f"📊 Soma estimada: {soma_estimada}")
            
            # Ajusta estratégia baseado na soma estimada
            if soma_estimada < 200:
                # Soma baixa - favorece números menores
                preferidos = list(range(1, 15))
            elif soma_estimada > 250:
                # Soma alta - favorece números maiores  
                preferidos = list(range(10, 26))
            else:
                # Soma média - estratégia padrão
                preferidos = list(range(5, 20))
        else:
            # Estratégia padrão sem descobertas
            preferidos = self.zona_conforto
        
        # Cria sequência inicial na zona de preferência
        inicio_seq = random.choice(preferidos[:10])
        tamanho_seq = min(random.randint(3, 8), qtd_numeros // 2)
        
        # Adiciona sequência
        for i in range(tamanho_seq):
            if inicio_seq + i <= 25 and len(combinacao) < qtd_numeros:
                combinacao.append(inicio_seq + i)
        
        # Completa com números aleatórios da zona de conforto
        while len(combinacao) < qtd_numeros:
            candidatos = [n for n in self.zona_conforto if n not in combinacao]
            if not candidatos:
                candidatos = [n for n in range(1, 26) if n not in combinacao]
            
            if candidatos:
                combinacao.append(random.choice(candidatos))
        
        return sorted(combinacao[:qtd_numeros])
    
    def gerar_multiplas_combinacoes(self, qtd_jogos=10, qtd_numeros=15):
        """Gera múltiplas combinações usando estratégia zona de conforto"""
        print(f"\n🎲 Gerando {qtd_jogos} combinações de {qtd_numeros} números...")
        print("📊 Estratégia: 80% zona conforto (1-17) + sequências permitidas")
        
        combinacoes = []
        
        for i in range(qtd_jogos):
            if i % 2 == 0:
                # Intercala estratégias
                combinacao = self.gerar_combinacao_zona_conforto(qtd_numeros)
            else:
                combinacao = self.gerar_com_sequencias(qtd_numeros)
            
            combinacoes.append(combinacao)
            
            # Análise da distribuição
            zona_conforto_count = len([n for n in combinacao if n in self.zona_conforto])
            perc_zona = (zona_conforto_count / len(combinacao)) * 100
            
            print(f"🎯 Jogo {i+1:2d}: {combinacao}")
            print(f"   📊 Zona conforto: {zona_conforto_count}/{len(combinacao)} ({perc_zona:.0f}%)")
        
        # Salva arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"combinacoes_zona_conforto_{qtd_numeros}nums_{timestamp}.txt"
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("🎯 COMBINAÇÕES ZONA DE CONFORTO\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data/Hora: {datetime.now()}\n")
            f.write(f"Estratégia: 80% zona 1-17 + sequências longas\n")
            f.write(f"Quantidade: {qtd_jogos} jogos de {qtd_numeros} números\n\n")
            
            for i, combinacao in enumerate(combinacoes, 1):
                zona_count = len([n for n in combinacao if n in self.zona_conforto])
                perc = (zona_count / len(combinacao)) * 100
                f.write(f"Jogo {i:2d}: {' '.join(f'{n:2d}' for n in combinacao)} | Zona: {zona_count}/{len(combinacao)} ({perc:.0f}%)\n")
        
        print(f"\n💾 Arquivo salvo: {arquivo}")
        return combinacoes

def menu_zona_conforto():
    """Menu principal do gerador zona de conforto"""
    gerador = GeradorZonaConforto()
    
    while True:
        print("\n🎯 GERADOR ZONA DE CONFORTO")
        print("=" * 50)
        print("1️⃣  🎲 Gerar Combinações (Padrão)")
        print("2️⃣  🔄 Gerar com Sequências Longas")
        print("3️⃣  📊 Gerar Múltiplas Combinações")
        print("4️⃣  🧠 Modo com Descobertas IA")
        print("0️⃣  🚪 Voltar")
        print("=" * 50)
        
        try:
            opcao = input("Escolha uma opção (0-4): ").strip()
            
            if opcao == "1":
                qtd = int(input("Quantos números por jogo (15-20)? [15]: ") or "15")
                jogos = int(input("Quantas combinações? [5]: ") or "5")
                gerador.gerar_multiplas_combinacoes(jogos, qtd)
                
            elif opcao == "2":
                qtd = int(input("Quantos números por jogo (15-20)? [15]: ") or "15")
                jogos = int(input("Quantas combinações? [5]: ") or "5")
                
                print(f"\n🔄 Gerando {jogos} combinações com sequências longas...")
                for i in range(jogos):
                    combinacao = gerador.gerar_com_sequencias(qtd)
                    print(f"🎯 Jogo {i+1}: {combinacao}")
                    
            elif opcao == "3":
                qtd = int(input("Quantos números por jogo (15-20)? [15]: ") or "15")
                jogos = int(input("Quantas combinações? [10]: ") or "10")
                gerador.gerar_multiplas_combinacoes(jogos, qtd)
                
            elif opcao == "4":
                if gerador.descobertas:
                    print("\n🧠 Modo com Descobertas IA Ativado")
                    qtd = int(input("Quantos números por jogo (15-20)? [15]: ") or "15")
                    jogos = int(input("Quantas combinações? [5]: ") or "5")
                    
                    for i in range(jogos):
                        combinacao = gerador.gerar_com_sequencias(qtd)
                        print(f"🎯 Jogo {i+1}: {combinacao}")
                else:
                    print("❌ Descobertas IA não disponíveis")
                    
            elif opcao == "0":
                print("👋 Voltando ao menu principal...")
                break
                
            else:
                print("❌ Opção inválida!")
                
            if opcao != "0":
                input("\n⏸️ Pressione ENTER para continuar...")
                
        except (ValueError, KeyboardInterrupt, EOFError):
            print("\n🔙 Voltando...")
            break

if __name__ == "__main__":
    menu_zona_conforto()