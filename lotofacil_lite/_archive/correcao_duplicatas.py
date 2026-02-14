#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 CORREÇÃO: GERADOR ACADÊMICO SEM DUPLICATAS
===========================================

Modifica o gerador acadêmico para garantir que APENAS
combinações únicas sejam geradas, eliminando completamente
o problema das duplicatas massivas.

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

import os
import sys

def aplicar_correcao_duplicatas():
    """
    Aplica a correção no gerador acadêmico para eliminar duplicatas
    """
    print("🔧 APLICANDO CORREÇÃO PARA ELIMINAR DUPLICATAS")
    print("=" * 50)
    
    arquivo_gerador = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\gerador_academico_dinamico.py"
    
    if not os.path.exists(arquivo_gerador):
        print(f"❌ Arquivo não encontrado: {arquivo_gerador}")
        return False
    
    # Lê o arquivo atual
    with open(arquivo_gerador, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Aplica as correções necessárias
    conteudo_corrigido = aplicar_modificacoes_duplicatas(conteudo)
    
    # Cria backup
    backup_arquivo = arquivo_gerador.replace('.py', '_backup_sem_duplicatas.py')
    with open(backup_arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    # Salva arquivo corrigido
    with open(arquivo_gerador, 'w', encoding='utf-8') as f:
        f.write(conteudo_corrigido)
    
    print(f"✅ Correção aplicada!")
    print(f"📁 Backup salvo em: {backup_arquivo}")
    print(f"🔧 Arquivo corrigido: {arquivo_gerador}")
    
    return True

def aplicar_modificacoes_duplicatas(conteudo: str) -> str:
    """
    Aplica as modificações necessárias para eliminar duplicatas
    """
    print("🔧 Aplicando modificações...")
    
    # 1. Adiciona controle de combinações únicas no construtor
    if "self.combinacoes_geradas = set()" not in conteudo:
        conteudo = conteudo.replace(
            "# Dados dinâmicos serão calculados",
            """# Dados dinâmicos serão calculados
        
        # 🎯 CONTROLE DE DUPLICATAS
        self.combinacoes_unicas = set()  # Armazena combinações já geradas
        self.max_tentativas_globais = 100000  # Limite global para evitar loops infinitos"""
        )
        print("   ✅ Adicionado controle de duplicatas no construtor")
    
    # 2. Modifica método gerar_combinacao_academica para verificar duplicatas
    metodo_original = """    def gerar_combinacao_academica(self, qtd_numeros: int = 15, max_tentativas: int = 1000) -> List[int]:
        \"\"\"Gera uma combinação com quantidade específica baseada nos insights dinâmicos
        
        Args:
            qtd_numeros: Quantidade de números por combinação (15-20)
            max_tentativas: Máximo de tentativas para encontrar combinação válida (1-3268760)
        \"\"\"
        if not self.dados_carregados:
            print("⚠️ Dados não carregados. Calculando insights...")
            if not self.calcular_insights_dinamicos():
                raise Exception("Falha ao carregar dados acadêmicos")
        
        if qtd_numeros not in self.configuracoes_aposta:
            raise ValueError(f"Quantidade {qtd_numeros} não suportada. Use: 15-20")
        
        # Validação do parâmetro max_tentativas
        if not 1 <= max_tentativas <= 3268760:
            raise ValueError(f"max_tentativas deve estar entre 1 e 3.268.760. Valor informado: {max_tentativas}")
        
        # 🎯 GERAÇÃO COM FILTRO VALIDADO
        tentativas = 0
        
        while tentativas < max_tentativas:
            tentativas += 1
            combinacao = []
            numeros_disponiveis = list(range(1, 26))"""
    
    metodo_corrigido = """    def gerar_combinacao_academica(self, qtd_numeros: int = 15, max_tentativas: int = 1000) -> List[int]:
        \"\"\"Gera uma combinação ÚNICA com quantidade específica baseada nos insights dinâmicos
        
        Args:
            qtd_numeros: Quantidade de números por combinação (15-20)
            max_tentativas: Máximo de tentativas para encontrar combinação válida (1-3268760)
        \"\"\"
        if not self.dados_carregados:
            print("⚠️ Dados não carregados. Calculando insights...")
            if not self.calcular_insights_dinamicos():
                raise Exception("Falha ao carregar dados acadêmicos")
        
        if qtd_numeros not in self.configuracoes_aposta:
            raise ValueError(f"Quantidade {qtd_numeros} não suportada. Use: 15-20")
        
        # Validação do parâmetro max_tentativas
        if not 1 <= max_tentativas <= 3268760:
            raise ValueError(f"max_tentativas deve estar entre 1 e 3.268.760. Valor informado: {max_tentativas}")
        
        # 🎯 GERAÇÃO COM CONTROLE DE DUPLICATAS
        tentativas = 0
        tentativas_unicas = 0  # Contador específico para tentativas de combinações únicas
        
        while tentativas < max_tentativas and tentativas_unicas < self.max_tentativas_globais:
            tentativas += 1
            combinacao = []
            numeros_disponiveis = list(range(1, 26))"""
    
    if metodo_original in conteudo:
        conteudo = conteudo.replace(metodo_original, metodo_corrigido)
        print("   ✅ Modificado início do método gerar_combinacao_academica")
    
    # 3. Modifica o final do método para verificar unicidade
    final_original = """            # 🎯 VALIDAÇÃO COM FILTRO
            combinacao_final = sorted(combinacao[:qtd_numeros])
            
            if self.validar_combinacao_filtro(combinacao_final):
                return combinacao_final
            
            # Se chegou aqui, a combinação não passou no filtro
            if tentativas % 100 == 0:  # Log a cada 100 tentativas
                acertos = self.calcular_acertos_filtros(combinacao_final)
                print(f"   🔍 Tentativa {tentativas}: Rejeitada (J1:{acertos['jogo_1']}, J2:{acertos['jogo_2']})")
        
        # Se esgotaram as tentativas, retorna a última gerada (mesmo que não passe no filtro)
        print(f"   ⚠️ Máximo de tentativas atingido ({max_tentativas}). Retornando combinação sem filtro.")
        return sorted(combinacao[:qtd_numeros])"""
    
    final_corrigido = """            # 🎯 VALIDAÇÃO COM FILTRO E CONTROLE DE DUPLICATAS
            combinacao_final = sorted(combinacao[:qtd_numeros])
            combinacao_tuple = tuple(combinacao_final)
            
            # Verifica se é combinação única
            if combinacao_tuple in self.combinacoes_unicas:
                tentativas_unicas += 1
                continue  # Pula para próxima tentativa se for duplicata
            
            if self.validar_combinacao_filtro(combinacao_final):
                # ✅ Combinação única E passou no filtro
                self.combinacoes_unicas.add(combinacao_tuple)
                return combinacao_final
            
            # Se chegou aqui, a combinação não passou no filtro
            if tentativas % 100 == 0:  # Log a cada 100 tentativas
                acertos = self.calcular_acertos_filtros(combinacao_final)
                print(f"   🔍 Tentativa {tentativas}: Rejeitada (J1:{acertos['jogo_1']}, J2:{acertos['jogo_2']}) | Únicas encontradas: {len(self.combinacoes_unicas)}")
        
        # Se esgotaram as tentativas, gera uma combinação puramente aleatória única
        print(f"   ⚠️ Máximo de tentativas atingido ({max_tentativas}). Gerando combinação aleatória única...")
        return self._gerar_combinacao_aleatoria_unica(qtd_numeros)"""
    
    if final_original in conteudo:
        conteudo = conteudo.replace(final_original, final_corrigido)
        print("   ✅ Modificado final do método gerar_combinacao_academica")
    
    # 4. Adiciona método auxiliar para gerar combinação aleatória única
    metodo_auxiliar = """
    def _gerar_combinacao_aleatoria_unica(self, qtd_numeros: int) -> List[int]:
        \"\"\"
        Gera uma combinação aleatória garantidamente única
        Usado como fallback quando métodos acadêmicos falham
        \"\"\"
        import random
        
        max_tentativas_aleatorias = 10000
        tentativas = 0
        
        while tentativas < max_tentativas_aleatorias:
            tentativas += 1
            
            # Gera combinação aleatória
            combinacao = sorted(random.sample(range(1, 26), qtd_numeros))
            combinacao_tuple = tuple(combinacao)
            
            # Verifica se é única
            if combinacao_tuple not in self.combinacoes_unicas:
                self.combinacoes_unicas.add(combinacao_tuple)
                print(f"   🎲 Combinação aleatória única gerada na tentativa {tentativas}")
                return combinacao
        
        # Se chegou aqui, há um problema crítico
        print(f"   ❌ ERRO CRÍTICO: Não foi possível gerar combinação única após {max_tentativas_aleatorias} tentativas")
        print(f"   📊 Combinações únicas já geradas: {len(self.combinacoes_unicas)}")
        
        # Última tentativa: força uma combinação sequencial não usada
        for i in range(1, 26 - qtd_numeros + 1):
            combinacao = list(range(i, i + qtd_numeros))
            combinacao_tuple = tuple(combinacao)
            if combinacao_tuple not in self.combinacoes_unicas:
                self.combinacoes_unicas.add(combinacao_tuple)
                print(f"   🔧 Combinação sequencial forçada: {combinacao}")
                return combinacao
        
        # Se nem sequencial funciona, há problema no algoritmo
        raise Exception("ERRO CRÍTICO: Impossível gerar combinação única - possível bug no algoritmo")
    
    def resetar_combinacoes_unicas(self):
        \"\"\"
        Reseta o controle de combinações únicas
        Útil para iniciar nova sequência de geração
        \"\"\"
        self.combinacoes_unicas.clear()
        print(f"🔄 Cache de combinações únicas resetado")
    
    def obter_estatisticas_unicidade(self) -> dict:
        \"\"\"
        Retorna estatísticas sobre as combinações únicas geradas
        \"\"\"
        total_unicas = len(self.combinacoes_unicas)
        
        # Para 20 números, máximo teórico é 53.130
        if self.combinacoes_unicas:
            # Detecta o tamanho das combinações
            primeira_combinacao = next(iter(self.combinacoes_unicas))
            tamanho = len(primeira_combinacao)
            
            if tamanho == 15:
                maximo_teorico = 3268760  # C(25,15)
            elif tamanho == 20:
                maximo_teorico = 53130    # C(25,20)
            else:
                import math
                maximo_teorico = math.comb(25, tamanho)
        else:
            maximo_teorico = 0
            tamanho = 0
        
        return {
            'combinacoes_unicas': total_unicas,
            'tamanho_combinacao': tamanho,
            'maximo_teorico': maximo_teorico,
            'percentual_explorado': (total_unicas / maximo_teorico * 100) if maximo_teorico > 0 else 0
        }"""
    
    # Adiciona antes do método main() ou no final da classe
    if "def main():" in conteudo:
        conteudo = conteudo.replace("def main():", metodo_auxiliar + "\n\ndef main():")
        print("   ✅ Adicionados métodos auxiliares para controle de unicidade")
    
    # 5. Modifica o método gerar_multiplas_combinacoes para resetar antes de cada geração
    if "def gerar_multiplas_combinacoes(self," in conteudo:
        # Encontra o início do método e adiciona reset
        inicio_metodo = "print(f\"\\n🎯 GERADOR ACADÊMICO DINÂMICO - {qtd_numeros} NÚMEROS\")"
        if inicio_metodo in conteudo:
            conteudo = conteudo.replace(
                inicio_metodo,
                """# 🔄 RESET PARA GARANTIR APENAS COMBINAÇÕES ÚNICAS
        self.resetar_combinacoes_unicas()
        
        print(f"\\n🎯 GERADOR ACADÊMICO DINÂMICO - {qtd_numeros} NÚMEROS (SEM DUPLICATAS)")"""
            )
            print("   ✅ Adicionado reset de combinações únicas no início da geração múltipla")
    
    # 6. Adiciona estatísticas de unicidade no final
    if "print(f\"\\n✅ RETORNANDO {len(combinacoes)} COMBINAÇÕES VALIDADAS\")" in conteudo:
        conteudo = conteudo.replace(
            "print(f\"\\n✅ RETORNANDO {len(combinacoes)} COMBINAÇÕES VALIDADAS\")",
            """# 📊 ESTATÍSTICAS DE UNICIDADE
        stats_unicidade = self.obter_estatisticas_unicidade()
        print(f"\\n📊 ESTATÍSTICAS DE UNICIDADE:")
        print(f"   • Combinações únicas geradas: {stats_unicidade['combinacoes_unicas']:,}")
        print(f"   • Tamanho das combinações: {stats_unicidade['tamanho_combinacao']} números")
        print(f"   • Máximo teórico possível: {stats_unicidade['maximo_teorico']:,}")
        print(f"   • Percentual explorado: {stats_unicidade['percentual_explorado']:.6f}%")
        
        if stats_unicidade['combinacoes_unicas'] == len(combinacoes):
            print(f"   ✅ TODAS AS COMBINAÇÕES SÃO ÚNICAS!")
        else:
            print(f"   ⚠️ Possíveis duplicatas detectadas!")
        
        print(f"\\n✅ RETORNANDO {len(combinacoes)} COMBINAÇÕES VALIDADAS (ÚNICAS GARANTIDAS)")"""
        )
        print("   ✅ Adicionadas estatísticas de unicidade")
    
    return conteudo

def testar_correcao():
    """
    Testa a correção gerando algumas combinações
    """
    print("\n🧪 TESTANDO CORREÇÃO...")
    print("=" * 30)
    
    try:
        # Importa o gerador corrigido
        sys.path.append(r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite")
        from gerador_academico_dinamico import GeradorAcademicoDinamico
        
        # Cria instância do gerador
        gerador = GeradorAcademicoDinamico()
        
        print("🔍 Testando geração de 10 combinações de 20 números...")
        
        # Desabilita filtro para teste rápido
        gerador.configurar_filtro_validado(False)
        
        # Testa geração
        combinacoes = gerador.gerar_multiplas_combinacoes(quantidade=10, qtd_numeros=20, max_tentativas=5000)
        
        if len(combinacoes) > 0:
            print(f"✅ Teste bem-sucedido!")
            print(f"   • Combinações geradas: {len(combinacoes)}")
            
            # Verifica unicidade
            combinacoes_set = set()
            duplicatas = 0
            
            for combinacao in combinacoes:
                combinacao_tuple = tuple(sorted(combinacao))
                if combinacao_tuple in combinacoes_set:
                    duplicatas += 1
                else:
                    combinacoes_set.add(combinacao_tuple)
            
            print(f"   • Combinações únicas: {len(combinacoes_set)}")
            print(f"   • Duplicatas encontradas: {duplicatas}")
            
            if duplicatas == 0:
                print(f"   🎉 CORREÇÃO FUNCIONOU - ZERO DUPLICATAS!")
            else:
                print(f"   ❌ Ainda há duplicatas - revisar correção")
            
            # Mostra amostra
            print(f"\n📋 AMOSTRA DAS PRIMEIRAS 3 COMBINAÇÕES:")
            for i, combinacao in enumerate(combinacoes[:3], 1):
                print(f"   {i}: {sorted(combinacao)}")
        else:
            print(f"❌ Teste falhou - nenhuma combinação gerada")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def main():
    """
    Função principal da correção
    """
    print("🔧 CORRETOR DE DUPLICATAS - GERADOR ACADÊMICO")
    print("=" * 55)
    print("🎯 Objetivo: Eliminar duplicatas massivas no gerador")
    print("📊 Garante apenas combinações únicas")
    print()
    
    # Aplica correção
    if aplicar_correcao_duplicatas():
        print("\n" + "="*50)
        
        # Pergunta se quer testar
        testar = input("Testar a correção agora? (s/n): ").lower().strip()
        
        if testar.startswith('s'):
            testar_correcao()
        else:
            print("✅ Correção aplicada! Execute o gerador para testar.")
    else:
        print("❌ Falha na aplicação da correção")

if __name__ == "__main__":
    main()