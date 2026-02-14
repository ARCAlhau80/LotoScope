#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 SISTEMA DE APRENDIZADO INTELIGENTE - LOTOFACIL
=================================================
Auto-ajuste contínuo baseado em padrões estatísticos
Foco em: menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo
"""

import random
import logging
from datetime import datetime
from database_optimizer import get_optimized_connection
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SistemaAprendizadoInteligente:
    """
    🧠 Sistema de IA adaptativa para previsão da Lotofácil
    """
    
    def __init__(self):
        self.conn = None
        self.concurso_atual = None
        self.concurso_alvo = None
        self.historico_estatisticas = []
        self.melhor_resultado = {
            'acertos': 0,
            'tentativas': 0,
            'combinacao': [],
            'concurso_previsto': 0,
            'padroes_usados': {}
        }
        self.padroes_aprendidos = {
            'menor_que_ultimo': {'peso': 1.0, 'eficacia': 0.0, 'usos': 0},
            'maior_que_ultimo': {'peso': 1.0, 'eficacia': 0.0, 'usos': 0},
            'igual_ao_ultimo': {'peso': 1.0, 'eficacia': 0.0, 'usos': 0},
            'numeros_frequentes': {'peso': 0.8, 'eficacia': 0.0, 'usos': 0},
            'numeros_raros': {'peso': 0.6, 'eficacia': 0.0, 'usos': 0},
            'soma_range': {'peso': 0.7, 'eficacia': 0.0, 'usos': 0}
        }
        self.tentativas_maximas = 1000
        self.historico_aprendizado = []
        
    def conectar_banco(self):
        """🔌 Conecta ao banco de dados"""
        try:
            self.conn = get_optimized_connection()
            if self.conn:
                logger.info("✅ Conectado ao banco de dados")
                return True
            else:
                logger.error("❌ Falha na conexão")
                return False
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            return False
    
    def escolher_concurso_atual(self, concurso=None):
        """🎯 Escolhe concurso atual ou usa o mais recente"""
        try:
            if concurso:
                self.concurso_atual = concurso
            else:
                # Pega o concurso mais recente
                cursor = self.conn.cursor()
                cursor.execute("SELECT MAX(Concurso) FROM resultados_int")
                max_concurso = cursor.fetchone()[0]
                self.concurso_atual = max_concurso - 1  # Usa o penúltimo para ter o próximo para validar
            
            self.concurso_alvo = self.concurso_atual + 1
            
            # Verifica se o concurso alvo existe (para validação)
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resultados_int WHERE Concurso = ?", (self.concurso_alvo,))
            existe = cursor.fetchone()[0] > 0
            
            if existe:
                logger.info(f"🎯 Concurso atual: {self.concurso_atual} | Alvo: {self.concurso_alvo}")
                return True
            else:
                logger.warning(f"⚠️ Concurso alvo {self.concurso_alvo} não existe ainda")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao escolher concurso: {e}")
            return False
    
    def analisar_estatisticas_completas(self):
        """📊 Analisa TODAS as estatísticas dos concursos 1 até atual"""
        try:
            cursor = self.conn.cursor()
            
            # Query para pegar todas as estatísticas relevantes
            query = """
            SELECT 
                Concurso,
                N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                menor_que_ultimo,
                maior_que_ultimo,
                igual_ao_ultimo,
                SomaTotal,
                QtdeImpares,
                SEQ,
                QtdeGaps,
                QtdeRepetidos
            FROM resultados_int 
            WHERE Concurso BETWEEN 1 AND ?
            ORDER BY Concurso
            """
            
            cursor.execute(query, (self.concurso_atual,))
            resultados = cursor.fetchall()
            
            # Processa estatísticas
            self.historico_estatisticas = []
            for row in resultados:
                concurso = row[0]
                numeros = list(row[1:16])  # N1 a N15
                
                estatisticas = {
                    'concurso': concurso,
                    'numeros': numeros,
                    'menor_que_ultimo': row[16],
                    'maior_que_ultimo': row[17],
                    'igual_ao_ultimo': row[18],
                    'soma_total': row[19],
                    'qtde_impares': row[20],
                    'sequencia': row[21],
                    'qtde_gaps': row[22],
                    'qtde_repetidos': row[23]
                }
                
                self.historico_estatisticas.append(estatisticas)
            
            logger.info(f"📊 Analisadas estatísticas de {len(self.historico_estatisticas)} concursos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar estatísticas: {e}")
            return False
    
    def calcular_padroes_previsiveis(self):
        """🎯 Calcula padrões baseados nos campos mais previsíveis"""
        if len(self.historico_estatisticas) < 10:
            return {}
        
        # Analisa os últimos 50 concursos para padrões recentes
        ultimos = self.historico_estatisticas[-50:]
        
        padroes = {
            'menor_que_ultimo_tendencia': sum(1 for x in ultimos if x['menor_que_ultimo'] > 0) / len(ultimos),
            'maior_que_ultimo_tendencia': sum(1 for x in ultimos if x['maior_que_ultimo'] > 0) / len(ultimos),
            'igual_ao_ultimo_tendencia': sum(1 for x in ultimos if x['igual_ao_ultimo'] > 0) / len(ultimos),
            
            'menor_que_ultimo_media': sum(x['menor_que_ultimo'] for x in ultimos) / len(ultimos),
            'maior_que_ultimo_media': sum(x['maior_que_ultimo'] for x in ultimos) / len(ultimos),
            'igual_ao_ultimo_media': sum(x['igual_ao_ultimo'] for x in ultimos) / len(ultimos),
            
            'soma_media': sum(x['soma_total'] for x in ultimos) / len(ultimos),
            'impares_media': sum(x['qtde_impares'] for x in ultimos) / len(ultimos),
            'gaps_media': sum(x['qtde_gaps'] for x in ultimos) / len(ultimos),
        }
        
        # Números mais frequentes nos últimos concursos
        numeros_freq = {}
        for est in ultimos:
            for num in est['numeros']:
                numeros_freq[num] = numeros_freq.get(num, 0) + 1
        
        padroes['numeros_frequentes'] = sorted(numeros_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        padroes['numeros_raros'] = sorted(numeros_freq.items(), key=lambda x: x[1])[:10]
        
        return padroes
    
    def gerar_combinacao_inteligente(self, padroes):
        """🧠 Gera combinação baseada nos padrões e pesos aprendidos"""
        try:
            combinacao = []
            
            # Aplica estratégia baseada nos pesos aprendidos
            ultimo_concurso = self.historico_estatisticas[-1]
            numeros_ultimo = ultimo_concurso['numeros']
            
            # 1. Números baseados em menor_que_ultimo
            peso_menor = self.padroes_aprendidos['menor_que_ultimo']['peso']
            qtd_menor = int(padroes['menor_que_ultimo_media'] * peso_menor)
            
            # 2. Números baseados em maior_que_ultimo  
            peso_maior = self.padroes_aprendidos['maior_que_ultimo']['peso']
            qtd_maior = int(padroes['maior_que_ultimo_media'] * peso_maior)
            
            # 3. Números iguais ao último
            peso_igual = self.padroes_aprendidos['igual_ao_ultimo']['peso']
            qtd_igual = int(padroes['igual_ao_ultimo_media'] * peso_igual)
            
            # Garante que não exceda 15
            total_previstos = qtd_menor + qtd_maior + qtd_igual
            if total_previstos > 15:
                fator = 15 / total_previstos
                qtd_menor = int(qtd_menor * fator)
                qtd_maior = int(qtd_maior * fator)
                qtd_igual = int(qtd_igual * fator)
            
            # Gera números baseados nas estratégias
            numeros_candidatos = set()
            
            # Números menores que o último
            for _ in range(qtd_menor):
                num = random.randint(1, min(numeros_ultimo) - 1) if min(numeros_ultimo) > 1 else 1
                numeros_candidatos.add(num)
            
            # Números maiores que o último
            for _ in range(qtd_maior):
                num = random.randint(max(numeros_ultimo) + 1, 25) if max(numeros_ultimo) < 25 else 25
                numeros_candidatos.add(num)
            
            # Números iguais (repetidos do último)
            if qtd_igual > 0:
                numeros_repetir = random.sample(numeros_ultimo, min(qtd_igual, len(numeros_ultimo)))
                numeros_candidatos.update(numeros_repetir)
            
            # Completa com números frequentes
            peso_freq = self.padroes_aprendidos['numeros_frequentes']['peso']
            numeros_freq = [num for num, freq in padroes['numeros_frequentes']]
            
            while len(numeros_candidatos) < 15:
                if random.random() < peso_freq:
                    num = random.choice(numeros_freq)
                else:
                    num = random.randint(1, 25)
                numeros_candidatos.add(num)
                
                if len(numeros_candidatos) >= 15:
                    break
            
            # Converte para lista ordenada
            combinacao = sorted(list(numeros_candidatos))[:15]
            
            # Se ainda não tem 15, completa aleatoriamente
            while len(combinacao) < 15:
                num = random.randint(1, 25)
                if num not in combinacao:
                    combinacao.append(num)
            
            return sorted(combinacao)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar combinação: {e}")
            # Fallback: combinação aleatória
            return sorted(random.sample(range(1, 26), 15))
    
    def validar_combinacao(self, combinacao):
        """✅ Valida combinação contra resultado real"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 
                FROM resultados_int 
                WHERE Concurso = ?
            """, (self.concurso_alvo,))
            
            resultado = cursor.fetchone()
            if not resultado:
                return 0
            
            numeros_reais = list(resultado)
            acertos = len(set(combinacao) & set(numeros_reais))
            
            return acertos
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return 0
    
    def atualizar_pesos_aprendizado(self, acertos, padroes_usados):
        """🎓 Atualiza pesos baseado no sucesso/falha"""
        # Fator de aprendizado baseado no sucesso
        fator_sucesso = acertos / 15.0
        
        # Atualiza eficácia de cada padrão usado
        for padrao, uso in padroes_usados.items():
            if padrao in self.padroes_aprendidos:
                self.padroes_aprendidos[padrao]['usos'] += 1
                
                # Média móvel da eficácia
                eficacia_atual = self.padroes_aprendidos[padrao]['eficacia']
                usos = self.padroes_aprendidos[padrao]['usos']
                
                nova_eficacia = ((eficacia_atual * (usos - 1)) + fator_sucesso) / usos
                self.padroes_aprendidos[padrao]['eficacia'] = nova_eficacia
                
                # Ajusta peso baseado na eficácia
                if nova_eficacia > 0.6:  # Boa eficácia
                    self.padroes_aprendidos[padrao]['peso'] *= 1.1  # Aumenta peso
                elif nova_eficacia < 0.3:  # Baixa eficácia
                    self.padroes_aprendidos[padrao]['peso'] *= 0.9  # Diminui peso
                
                # Limita pesos
                self.padroes_aprendidos[padrao]['peso'] = max(0.1, min(2.0, self.padroes_aprendidos[padrao]['peso']))
        
        logger.info(f"🎓 Pesos atualizados baseado em {acertos} acertos")
    
    def executar_sessao_aprendizado(self, concurso=None, max_tentativas=None):
        """🚀 Executa sessão completa de aprendizado"""
        if max_tentativas:
            self.tentativas_maximas = max_tentativas
        
        logger.info(f"🚀 Iniciando sessão de aprendizado inteligente")
        
        # Conecta e prepara
        if not self.conectar_banco():
            return False
        
        if not self.escolher_concurso_atual(concurso):
            return False
        
        if not self.analisar_estatisticas_completas():
            return False
        
        # Calcula padrões iniciais
        padroes = self.calcular_padroes_previsiveis()
        
        melhor_acertos = 0
        tentativa = 0
        
        print(f"\n🎯 SESSÃO DE APRENDIZADO INTELIGENTE")
        print(f"=" * 50)
        print(f"Concurso atual: {self.concurso_atual}")
        print(f"Prevendo concurso: {self.concurso_alvo}")
        print(f"Tentativas máximas: {self.tentativas_maximas}")
        print(f"Objetivo: 15 acertos")
        
        while tentativa < self.tentativas_maximas:
            tentativa += 1
            
            # Gera combinação inteligente
            combinacao = self.gerar_combinacao_inteligente(padroes)
            
            # Valida
            acertos = self.validar_combinacao(combinacao)
            
            # Registra padrões usados (simplificado)
            padroes_usados = {
                'menor_que_ultimo': 1,
                'maior_que_ultimo': 1,
                'igual_ao_ultimo': 1,
                'numeros_frequentes': 1
            }
            
            # Atualiza aprendizado
            self.atualizar_pesos_aprendizado(acertos, padroes_usados)
            
            # Verifica se é melhor resultado
            if acertos > melhor_acertos:
                melhor_acertos = acertos
                self.melhor_resultado = {
                    'acertos': acertos,
                    'tentativas': tentativa,
                    'combinacao': combinacao,
                    'concurso_previsto': self.concurso_alvo,
                    'padroes_usados': padroes_usados.copy()
                }
                
                print(f"🎉 NOVO MELHOR RESULTADO!")
                print(f"   Tentativa: {tentativa}")
                print(f"   Acertos: {acertos}/15")
                print(f"   Combinação: {combinacao}")
                
                # Se conseguiu 15, para
                if acertos == 15:
                    print(f"🏆 PERFEITO! 15 acertos em {tentativa} tentativas!")
                    break
            
            # A cada 100 tentativas, mostra progresso
            if tentativa % 100 == 0:
                print(f"⏳ Tentativa {tentativa}: melhor resultado = {melhor_acertos} acertos")
        
        # Relatório final
        print(f"\n📊 RELATÓRIO FINAL DA SESSÃO")
        print(f"=" * 50)
        print(f"Tentativas realizadas: {tentativa}")
        print(f"Melhor resultado: {melhor_acertos} acertos")
        print(f"Tentativa do melhor: {self.melhor_resultado['tentativas']}")
        print(f"Melhor combinação: {self.melhor_resultado['combinacao']}")
        
        # Mostra pesos aprendidos
        print(f"\n🧠 PESOS APRENDIDOS:")
        for padrao, dados in self.padroes_aprendidos.items():
            print(f"   {padrao}: peso={dados['peso']:.2f}, eficácia={dados['eficacia']:.2f}, usos={dados['usos']}")
        
        return True
    
    def salvar_aprendizado(self):
        """💾 Salva estado do aprendizado"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dados = {
            'timestamp': timestamp,
            'melhor_resultado': self.melhor_resultado,
            'padroes_aprendidos': self.padroes_aprendidos,
            'concurso_atual': self.concurso_atual,
            'concurso_alvo': self.concurso_alvo
        }
        
        nome_arquivo = f"aprendizado_{timestamp}.json"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Aprendizado salvo em: {nome_arquivo}")
        return nome_arquivo
    
    def carregar_aprendizado(self, arquivo):
        """📂 Carrega estado do aprendizado"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.melhor_resultado = dados['melhor_resultado']
            self.padroes_aprendidos = dados['padroes_aprendidos']
            self.concurso_atual = dados['concurso_atual']
            self.concurso_alvo = dados['concurso_alvo']
            
            print(f"📂 Aprendizado carregado de: {arquivo}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao carregar aprendizado: {e}")
            return False

def main():
    """Interface principal"""
    sistema = SistemaAprendizadoInteligente()
    
    print("🧠 SISTEMA DE APRENDIZADO INTELIGENTE - LOTOFACIL")
    print("=" * 60)
    print("Auto-ajuste contínuo baseado em padrões estatísticos")
    print("Foco: menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo")
    print()
    
    while True:
        print("OPÇÕES:")
        print("1️⃣  🚀 Iniciar sessão de aprendizado")
        print("2️⃣  🎯 Escolher concurso específico")
        print("3️⃣  ⚙️  Configurar tentativas máximas")
        print("4️⃣  💾 Salvar aprendizado atual")
        print("5️⃣  📂 Carregar aprendizado anterior")
        print("6️⃣  📊 Ver status dos pesos")
        print("0️⃣  🚪 Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            sistema.executar_sessao_aprendizado()
        elif opcao == "2":
            concurso = input("Digite o número do concurso atual: ").strip()
            try:
                concurso = int(concurso)
                sistema.executar_sessao_aprendizado(concurso)
            except ValueError:
                print("❌ Número inválido!")
        elif opcao == "3":
            tentativas = input("Digite o máximo de tentativas (padrão 1000): ").strip()
            try:
                sistema.tentativas_maximas = int(tentativas)
                print(f"✅ Configurado para {sistema.tentativas_maximas} tentativas máximas")
            except ValueError:
                print("❌ Número inválido!")
        elif opcao == "4":
            sistema.salvar_aprendizado()
        elif opcao == "5":
            arquivo = input("Digite o nome do arquivo: ").strip()
            sistema.carregar_aprendizado(arquivo)
        elif opcao == "6":
            print("\n🧠 PESOS ATUAIS:")
            for padrao, dados in sistema.padroes_aprendidos.items():
                print(f"   {padrao}: peso={dados['peso']:.2f}, eficácia={dados['eficacia']:.2f}, usos={dados['usos']}")
            print()
        elif opcao == "0":
            print("🚪 Saindo...")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()