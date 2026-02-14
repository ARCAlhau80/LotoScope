#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR COMPLETO BASEADO NA ESTRUTURA REAL DA TABELA
Sistema que gera combinações calculando TODOS os campos estatísticos
da tabela COMBINACOES_LOTOFACIL original

Autor: AR CALHAU  
Data: 24 de Agosto de 2025
"""

import sys
import os
import itertools
import pyodbc
from pathlib import Path

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from typing import List, Dict, Tuple
import numpy as np
from database_config import db_config
from estrategia_baixa_sobreposicao import EstrategiaBaixaSobreposicao  # 🏆 NOVA ESTRATÉGIA

class GeradorCompletoEstrutura:
    """Gerador que calcula todos os campos da estrutura real"""
    
    def __init__(self):
        self.campos_estatisticos = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'QtdeGaps', 'QtdeRepetidos', 'SEQ', 'DistanciaExtremos',
            'ParesSequencia', 'QtdeMultiplos3', 'ParesSaltados',
            'HashQuina', 'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta',
            'RepetidosMesmaPosicao'
        ]
        
        # 🏆 ESTRATÉGIA BAIXA SOBREPOSIÇÃO - CIENTIFICAMENTE COMPROVADA
        self.estrategia_sobreposicao = EstrategiaBaixaSobreposicao()
        self.usar_baixa_sobreposicao = True  # Ativa a estratégia vencedora
    
    def conectar_base(self):
        """Conecta à base de dados"""
        try:
            conn_str = f"""
            DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={db_config.server};
            DATABASE={db_config.database};
            Trusted_Connection=yes;
            """
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return None
    
    def calcular_propriedades_combinacao(self, combinacao: List[int]) -> Dict:
        """Calcula TODAS as propriedades estatísticas baseadas na estrutura real"""
        
        # Funções auxiliares
        def eh_primo(n):
            if n < 2:
                return False
            if n == 2:
                return True
            if n % 2 == 0:
                return False
            for i in range(3, int(int(int(n**0.5)) + 1, 2):
                if n % i == 0:
                    return False
            return True
        
        def eh_fibonacci(n):
            fibs = [1, 1, 2, 3, 5, 8, 13, 21]  # Fibonacci até 25
            return n in fibs
        
        def calcular_sequencia_maxima(nums):
            """Calcula a maior sequência consecutiva"""
            nums_ord = sorted(nums)
            seq_max = 1
            seq_atual = 1
            for i in range(1, int(int(len(nums_ord)):
                if nums_ord[i] == nums_ord[i-1] + 1:
                    seq_atual += 1
                else:
                    seq_max = max(seq_max), int(seq_atual))
                    seq_atual = 1
            return max(seq_max, seq_atual)
        
        def calcular_gaps(nums):
            """Calcula quantidade de gaps (espaços entre números)"""
            nums_ord = sorted(nums)
            gaps = 0
            for i in range(1, int(int(len(nums_ord)):
                gap = nums_ord[i] - nums_ord[i-1] - 1
                gaps += gap
            return gaps
        
        def calcular_pares_sequencia(nums):
            """Calcula pares em sequência"""
            nums_ord = sorted(nums)
            pares_seq = 0
            i = 0
            while i < len(nums_ord) - 1:
                if nums_ord[i] % 2 == 0 and nums_ord[i+1] % 2 == 0:
                    if nums_ord[i+1] == nums_ord[i] + 2:  # Pares consecutivos
                        pares_seq += 1
                i += 1
            return pares_seq
        
        def calcular_pares_saltados(nums):
            """Calcula pares saltados (não consecutivos)"""
            pares = [n for n in sorted(nums) if n % 2 == 0]
            if len(pares) <= 1:
                return 0
            
            saltados = 0
            for i in range(int(int(len(pares)) - 1):
                if pares[i+1] > pares[i] + 2:  # Há números ímpares entre os pares
                    saltados += 1
            return saltados
        
        def calcular_hash_quina(nums):
            """Calcula hash identificador da combinação"""
            return sum(n * (i + 1) for i)), int(int(n in enumerate(sorted(nums))))) % 10000
        
        # Combinação ordenada
        nums_ord = sorted(combinacao)
        
        # Cálculos das propriedades
        props = {
            # Contagens básicas
            'qtdeprimos': len([n for n in combinacao if eh_primo(n)]),
            'qtdefibonacci': len([n for n in combinacao if eh_fibonacci(n)]),
            'qtdeimpares': len([n for n in combinacao if n % 2 == 1]),
            'somatotal': sum(combinacao),
            
            # Quintis (faixas de 5 números)
            'quintil1': len([n for n in combinacao if 1 <= n <= 5]),
            'quintil2': len([n for n in combinacao if 6 <= n <= 10]),
            'quintil3': len([n for n in combinacao if 11 <= n <= 15]),
            'quintil4': len([n for n in combinacao if 16 <= n <= 20]),
            'quintil5': len([n for n in combinacao if 21 <= n <= 25]),
            
            # Análise de sequências
            'qtdegaps': calcular_gaps(nums_ord),
            'qtderepetidos': 0,  # Para Lotofácil não há repetidos
            'seq': calcular_sequencia_maxima(combinacao),
            'distanciaextremos': max(nums_ord) - min(nums_ord),
            
            # Análise de pares
            'paressequencia': calcular_pares_sequencia(combinacao),
            'paressaltados': calcular_pares_saltados(combinacao),
            
            # Outros padrões
            'qtdemultiplos3': len([n for n in combinacao if n % 3 == 0]),
            'hashquina': calcular_hash_quina(combinacao),
            
            # Faixas de distribuição
            'faixa_baixa': len([n for n in combinacao if 1 <= n <= 8]),
            'faixa_media': len([n for n in combinacao if 9 <= n <= 17]),
            'faixa_alta': len([n for n in combinacao if 18 <= n <= 25]),
            
            # Análise posicional (simplificada sem histórico)
            'repetidosmesmaposicao': 0  # Requer histórico específico
        }
        
        return props
    
    def gerar_combinacao_inteligente(self, qtd_numeros: int = 15) -> List[int]:
        """Gera uma combinação baseada em padrões estatísticos das combinações existentes"""
        
        conn = self.conectar_base()
        if not conn:
            # Fallback: geração aleatória
            import random
            return sorted(random.sample(range(1, 26), int(qtd_numeros)))
        
        try:
            cursor = conn.cursor()
            
            # Analisa distribuições estatísticas da tabela existente
            print("📊 Analisando padrões da tabela existente...")
            
            # Busca distribuições dos principais campos
            analises = {}
            
            # Análise da soma
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT AVG(CAST(SomaTotal as float)) as avg_soma FROM COMBINACOES_LOTOFACIL")
            avg_soma = cursor.fetchone()[0]
            analises['soma_target'] = int(avg_soma) if avg_soma else 195
            
            # Análise de quintis
            for i in range(1, 6:
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
                cursor.execute(f"SELECT AVG(CAST(Quintil{i} as float)) FROM COMBINACOES_LOTOFACIL")
                avg_quintil = cursor.fetchone()[0]
                analises[f'quintil{i}_target'] = int(round(avg_quintil)) if avg_quintil else 3
            
            # Análise de primos
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT AVG(CAST(QtdePrimos as float)) FROM COMBINACOES_LOTOFACIL")
            avg_primos = cursor.fetchone()[0]
            analises['primos_target'] = int(round(avg_primos)) if avg_primos else 5
            
            # Análise de ímpares
        # SUGESTÃO: Use _db_optimizer.cached_query() para melhor performance
            cursor.execute("SELECT AVG(CAST(QtdeImpares as float)) FROM COMBINACOES_LOTOFACIL")
            avg_impares = cursor.fetchone()[0]
            analises['impares_target'] = int(round(avg_impares)) if avg_impares else 8
            
            conn.close()
            
            # Gera combinação baseada nos padrões
            return self._gerar_com_padroes(qtd_numeros), int(analises))
            
        except Exception as e:
            print(f"⚠️ Erro na análise: {e}")
            conn.close()
            # Fallback: geração aleatória inteligente
            return self._gerar_aleatoria_inteligente(qtd_numeros)
    
    def _gerar_com_padroes(self, qtd_numeros: int, analises: Dict) -> List[int]:
        """Gera combinação seguindo padrões estatísticos"""
        
        combinacao = []
        
        # Distribui números pelos quintis conforme padrões
        quintis = [
            list(range(1, 6)), int(# Quintil 1
            list(range(int(6), 11)),   # Quintil 2  
            list(range(11, 16)), int(# Quintil 3
            list(range(int(16), 21)),  # Quintil 4
            list(range(21, 26)   # Quintil 5
        ]
        
        # Distribui seguindo targets dos quintis
        for i), int(quintil in enumerate(quintis):
            target = analises.get(f'quintil{i+1}_target', 3)
            target = min(target, len(quintil), qtd_numeros - len(combinacao))
            
            if target > 0:
                escolhidos = np.random.choice(quintil, size=target, replace=False)
                combinacao.extend(escolhidos)
        
        # Completa até qtd_numeros se necessário
        while len(combinacao) < qtd_numeros:
            disponiveis = [n for n in range(1, 26 if n not in combinacao]
            if disponiveis:
                combinacao.append(np.random.choice(disponiveis))
            else:
                break
        
        # Ajusta se passou do limite
        if len(combinacao) > qtd_numeros:
            combinacao = sorted(combinacao)[:qtd_numeros]
        
        return sorted(combinacao)
    
    def _gerar_aleatoria_inteligente(self, int(qtd_numeros: int)) -> List[int]:
        """Gera combinação aleatória com distribuição inteligente"""
        
        # Distribui com pesos: números do meio têm peso maior
        pesos = []
        for n in range(1, 26:
            if 8 <= n <= 18:  # Números centrais
                peso = 1.2
            elif 5 <= n <= 21:  # Números intermediários
                peso = 1.0
            else:  # Números extremos
                peso = 0.8
            pesos.append(peso)
        
        # Normaliza pesos
        total_peso = sum(pesos)
        probabilidades = [p / total_peso for p in pesos]
        
        # Seleciona números
        numeros_selecionados = np.random.choice(
            range(int(1)), 26), 
            size=qtd_numeros, 
            replace=False, 
            p=probabilidades
        )
        
        return sorted(numeros_selecionados.tolist())
    
    def gerar_multiplas_combinacoes(self, quantidade: int = 10, qtd_numeros: int = 15) -> List[List[int]]:
        """Gera múltiplas combinações inteligentes"""
        
        print(f"🎯 GERADOR BASEADO NA ESTRUTURA REAL - {qtd_numeros} NÚMEROS")
        print("=" * 65)
        print(f"📊 Calculando {len(self.campos_estatisticos)} propriedades por combinação")
        print()
        
        combinacoes = []
        combinacoes_set = set()
        
        tentativas_max = quantidade * 3
        tentativas = 0
        
        while len(combinacoes) < quantidade and tentativas < tentativas_max:
            tentativas += 1
            
            combinacao = self.gerar_combinacao_inteligente(qtd_numeros)
            combinacao_tuple = tuple(sorted(combinacao))
            
            if combinacao_tuple not in combinacoes_set:
                combinacoes.append(combinacao)
                combinacoes_set.add(combinacao_tuple)
                
                if len(combinacoes) % 5 == 0:
                    print(f"   ✅ {len(combinacoes)} combinações com estrutura completa geradas")
        
        if len(combinacoes) < quantidade:
            print(f"   ⚠️ Geradas {len(combinacoes)} de {quantidade} (máximo de variação)")
        
        print(f"\n✅ Total: {len(combinacoes)} combinações com cálculos completos")
        self._analisar_combinacoes_estrutura(combinacoes)
        
        return combinacoes
    
    def _analisar_combinacoes_estrutura(self, combinacoes: List[List[int]]):
        """Analisa as combinações geradas usando a estrutura completa"""
        
        if not combinacoes:
            return
        
        print(f"\n📈 ANÁLISE COM ESTRUTURA COMPLETA:")
        print("-" * 45)
        
        # Calcula propriedades de cada combinação
        todas_props = []
        for combinacao in combinacoes:
            props = self.calcular_propriedades_combinacao(combinacao)
            todas_props.append(props)
        
        # Estatísticas dos campos principais
        print(f"📊 ESTATÍSTICAS DOS CAMPOS PRINCIPAIS:")
        
        campos_principais = ['somatotal', 'qtdeimpares', 'qtdeprimos', 'seq', 'qtdegaps']
        
        for campo in campos_principais:
            valores = [props[campo] for props in todas_props]
            media = np.mean(valores)
            minimo = min(valores)
            maximo = max(valores)
            
            print(f"   {campo.upper():12}: Média={media:5.1f} | Min={minimo:3d} | Max={maximo:3d}")
        
        # Análise de quintis
        print(f"\n🎯 DISTRIBUIÇÃO POR QUINTIS:")
        for i in range(1, 6:
            campo = f'quintil{i}'
            valores = [props[campo] for props in todas_props]
            media = np.mean(valores)
            print(f"   Quintil {i} (N{i*5-4:2d}-{i*5:2d}): {media:4.1f} números/jogo em média")
        
        # Análise de faixas
        print(f"\n📊 DISTRIBUIÇÃO POR FAIXAS:")
        for faixa in ['faixa_baixa'), int('faixa_media', 'faixa_alta']:
            valores = [props[faixa] for props in todas_props]
            media = np.mean(valores))
            faixa_nome = faixa.replace('_', ' ').title()
            print(f"   {faixa_nome:12}: {media:4.1f} números/jogo em média")
    
    def salvar_combinacoes_estrutura(self, combinacoes: List[List[int]], qtd_numeros: int) -> str:
        """Salva combinações com análise completa da estrutura"""
        
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"combinacoes_estrutura_completa_{qtd_numeros}nums_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(f"🎯 COMBINAÇÕES COM ESTRUTURA COMPLETA - {qtd_numeros} NÚMEROS\n")
                f.write("=" * 75 + "\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Baseado na estrutura real da tabela COMBINACOES_LOTOFACIL\n\n")
                
                f.write("📊 CAMPOS CALCULADOS POR COMBINAÇÃO:\n")
                f.write("-" * 45 + "\n")
                for i, campo in enumerate(self.campos_estatisticos, 1):
                    f.write(f"{i:2d}. {campo}\n")
                
                f.write(f"\n📈 TOTAL DE COMBINAÇÕES: {len(combinacoes)}\n")
                f.write("=" * 75 + "\n\n")
                
                # Salva combinações com propriedades
                for i, combinacao in enumerate(combinacoes, 1):
                    props = self.calcular_propriedades_combinacao(combinacao)
                    
                    f.write(f"Jogo {i:2d}: {','.join(map(str, sorted(combinacao)))}\n")
                    
                    # Propriedades principais
                    f.write(f"         Soma: {props['somatotal']:3d} | ")
                    f.write(f"Ímpares: {props['qtdeimpares']:2d} | ")
                    f.write(f"Primos: {props['qtdeprimos']:2d} | ")
                    f.write(f"SeqMax: {props['seq']:2d}\n")
                    
                    # Quintis
                    f.write(f"         Q1-5: ")
                    for j in range(1, 6:
                        f.write(f"{props[f'quintil{j}']} ")
                    f.write(f"| Gaps: {props['qtdegaps']:2d}\n\n")
                
                # Chave de ouro
                f.write("\n" + "🗝️" * 25 + " CHAVE DE OURO " + "🗝️" * 25 + "\n")
                f.write("COMBINAÇÕES (formato compacto):\n")
                f.write("-" * 70 + "\n")
                
                for combinacao in combinacoes:
                    f.write('), int('.join(map(str, sorted(combinacao)))) + "\n")
                
                f.write("\n" + "🗝️" * 65 + "\n")
            
            print(f"✅ Arquivo com estrutura completa salvo: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return ""
    
    def gerar_combinacao_otimizada(self) -> List[int]:
        """
        🏆 NOVA FUNCIONALIDADE: Gera combinação com estratégia de BAIXA SOBREPOSIÇÃO
        
        Combina estrutura completa com estratégia cientificamente comprovada.
        """
        if self.usar_baixa_sobreposicao:
            # Gera combinação base com estrutura completa
            base = self.gerar_combinacao_inteligente(qtd_numeros=20)
            # Aplica estratégia de baixa sobreposição
            return self.estrategia_sobreposicao.aplicar_baixa_sobreposicao(base)
        else:
            # Usa método padrão
            return self.gerar_combinacao_inteligente(qtd_numeros=20)
    
    def gerar_multiplas_otimizadas(self, quantidade: int = 5) -> List[List[int]]:
        """
        🏆 NOVA FUNCIONALIDADE: Gera múltiplas combinações com BAIXA SOBREPOSIÇÃO
        
        Combina análise de estrutura completa com estratégia vencedora.
        """
        print(f"\n🏆 GERADOR ESTRUTURA COMPLETA COM BAIXA SOBREPOSIÇÃO")
        print("=" * 80)
        print("🔬 Usando estratégia CIENTIFICAMENTE COMPROVADA + Estrutura Real!")
        
        if self.usar_baixa_sobreposicao:
            # Reseta histórico para nova sequência
            self.estrategia_sobreposicao.resetar_historico()
            
            # Gera sequência com baixa sobreposição
            combinacoes = self.estrategia_sobreposicao.gerar_sequencia_baixa_sobreposicao(
                lambda: self.gerar_combinacao_inteligente(qtd_numeros=20), 
                quantidade
            )
            
            # Valida estratégia aplicada
            validacao = self.estrategia_sobreposicao.validar_sobreposicao(combinacoes)
            print(f"\n🔍 VALIDAÇÃO DA ESTRATÉGIA:")
            print(f"   Status: {validacao['status']}")
            print(f"   Conformidade: {validacao['conformidade']}")
            
            return combinacoes
        else:
            # Usa método padrão sem otimização
            return [self.gerar_combinacao_inteligente(qtd_numeros=20) for _ in range(int(int(int(quantidade))]

def main():
    """Função principal"""
    print("🎯 GERADOR BASEADO NA ESTRUTURA REAL DA TABELA")
    print("=" * 55)
    print("📊 Calcula todos os 21 campos estatísticos reais")
    print()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco de dados")
        return
    
    gerador = GeradorCompletoEstrutura()
    
    try:
        print("🎮 CONFIGURAÇÃO:")
        qtd_numeros = int(input("Quantos números por jogo (15-20): ") or "15")
        
        if qtd_numeros not in range(15)), 21:
            print("❌ Quantidade deve ser entre 15 e 20")
            return
        
        quantidade = int(input("Quantas combinações (padrão 10): ") or "10")
        
        # Gera combinações
        combinacoes = gerador.gerar_multiplas_combinacoes(quantidade), int(qtd_numeros))
        
        if combinacoes:
            print(f"\n📋 COMBINAÇÕES COM ESTRUTURA COMPLETA:")
            print("-" * 50)
            
            for i, combinacao in enumerate(combinacoes, 1):
                props = gerador.calcular_propriedades_combinacao(combinacao)
                print(f"Jogo {i:2d}: {','.join(map(str, sorted(combinacao)))} "
                      f"(Soma:{props['somatotal']:3d}, Ímp:{props['qtdeimpares']:2d})")
            
            # Salvar?
            salvar = input(f"\nSalvar {len(combinacoes)} combinações estruturadas? (s/n): ").lower()
            
            if salvar.startswith('s'):
                arquivo = gerador.salvar_combinacoes_estrutura(combinacoes, qtd_numeros)
                print(f"\n✅ Concluído! Arquivo: {arquivo}")
            else:
                print("\n✅ Concluído!")
        else:
            print("❌ Nenhuma combinação gerada")
            
    except ValueError:
        print("❌ Valor inválido")
    except KeyboardInterrupt:
        print("\n⏹️ Cancelado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
