#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR AVANÇADO DE COMBINAÇÕES LOTOFÁCIL
Sistema avançado com filtros posicionais e palpites pessoais
Autor: AR CALHAU
Data: 13 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

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

from datetime import datetime
import sys

class GeradorAvancado:
    """Classe para geração avançada de combinações filtradas"""
    
    def __init__(self):
        """Inicializa o gerador avançado"""
        self.ultimo_concurso = None
        self.janela_analise = 30  # Últimos 30 concursos para análise
        self.numeros_incluir = []  # Números que DEVEM estar na combinação
        self.numeros_excluir = []  # Números que NÃO devem estar na combinação
        self.filtros_posicionais = {}  # Filtros para cada posição N1-N15
    
    def obter_ultimo_concurso(self) -> dict:
        """Obtém dados do último concurso"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                           QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal, Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                           QtdeGaps, SEQ, DistanciaExtremos, ParesSequencia, QtdeMultiplos3, ParesSaltados,
                           Faixa_Baixa, Faixa_Media, Faixa_Alta, QtdeRepetidos, RepetidosMesmaPosicao
                    FROM Resultados_INT 
                    ORDER BY Concurso DESC
                """)
                
                row = cursor.fetchone()
                if row:
                    return {
                        'concurso': row[0],
                        'numeros': list(row[1:16]),
                        'QtdePrimos': row[16],
                        'QtdeFibonacci': row[17],
                        'QtdeImpares': row[18],
                        'SomaTotal': row[19],
                        'Quintil1': row[20],
                        'Quintil2': row[21],
                        'Quintil3': row[22],
                        'Quintil4': row[23],
                        'Quintil5': row[24],
                        'QtdeGaps': row[25],
                        'SEQ': row[26],
                        'DistanciaExtremos': row[27],
                        'ParesSequencia': row[28],
                        'QtdeMultiplos3': row[29],
                        'ParesSaltados': row[30],
                        'Faixa_Baixa': row[31],
                        'Faixa_Media': row[32],
                        'Faixa_Alta': row[33],
                        'QtdeRepetidos': row[34],
                        'RepetidosMesmaPosicao': row[35]
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter último concurso: {e}")
            return None

    def calcular_tendencias_posicionais(self) -> dict:
        """Calcula tendências para cada posição N1 até N15"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # Busca os últimos 30 concursos para análise posicional
                cursor.execute(f"""
                    SELECT TOP {self.janela_analise} 
                           N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                    FROM Resultados_INT 
                    ORDER BY Concurso DESC
                """)
                
                dados = cursor.fetchall()
                
                if not dados:
                    return {}
                
                # Calcula estatísticas para cada posição
                tendencias_posicionais = {}
                
                for pos in range(15):  # N1 até N15
                    posicao = f"N{pos + 1}"
                    valores = [row[pos] for row in dados if row[pos] is not None]
                    
                    if valores:
                        media = sum(valores) / len(valores)
                        valores_unicos = list(set(valores))
                        valores_unicos.sort()
                        
                        # Calcula frequência de cada número na posição
                        frequencias = {}
                        for valor in valores:
                            frequencias[valor] = frequencias.get(valor, 0) + 1
                        
                        # Ordena por frequência
                        mais_frequentes = sorted(frequencias.items(), key=lambda x: x[1], reverse=True)
                        
                        tendencias_posicionais[posicao] = {
                            'media': round(media, 1),
                            'min': min(valores),
                            'max': max(valores),
                            'valores_unicos': valores_unicos,
                            'mais_frequentes': mais_frequentes[:5],  # Top 5
                            'range_comum': (min(valores), max(valores))
                        }
                
                return tendencias_posicionais
                
        except Exception as e:
            print(f"❌ Erro ao calcular tendências posicionais: {e}")
            return {}

    def calcular_tendencias_estatisticas(self) -> dict:
        """Calcula tendências dos campos estatísticos"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT TOP {self.janela_analise} 
                           QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal, 
                           Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                           QtdeGaps, SEQ, DistanciaExtremos, ParesSequencia, 
                           QtdeMultiplos3, ParesSaltados, Faixa_Baixa, Faixa_Media, Faixa_Alta,
                           QtdeRepetidos, RepetidosMesmaPosicao
                    FROM Resultados_INT 
                    ORDER BY Concurso DESC
                """)
                
                dados = cursor.fetchall()
                
                if not dados:
                    return {}
                
                tendencias = {}
                campos = [
                    'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal',
                    'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
                    'QtdeGaps', 'SEQ', 'DistanciaExtremos', 'ParesSequencia',
                    'QtdeMultiplos3', 'ParesSaltados', 'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta',
                    'QtdeRepetidos', 'RepetidosMesmaPosicao'
                ]
                
                for i, campo in enumerate(campos):
                    valores = [row[i] for row in dados if row[i] is not None]
                    if valores:
                        media = sum(valores) / len(valores)
                        variancia = sum((x - media) ** 2 for x in valores) / len(valores)
                        desvio = variancia ** 0.5
                        
                        tendencias[campo] = {
                            'media': media,
                            'desvio': desvio,
                            'min': min(valores),
                            'max': max(valores)
                        }
                
                return tendencias
                
        except Exception as e:
            print(f"❌ Erro ao calcular tendências estatísticas: {e}")
            return {}

    def configurar_palpites(self):
        """Interface para configurar números incluir/excluir"""
        print("\n🎯 CONFIGURAÇÃO DE PALPITES PESSOAIS")
        print("=" * 50)
        
        # Números para incluir obrigatoriamente
        print("\n📈 NÚMEROS QUE DEVEM ESTAR NA COMBINAÇÃO:")
        print("   (Digite os números separados por vírgula, ou ENTER para pular)")
        incluir_input = input("   Números para incluir: ").strip()
        
        if incluir_input:
            try:
                self.numeros_incluir = [int(x.strip()) for x in incluir_input.split(',')]
                self.numeros_incluir = [n for n in self.numeros_incluir if 1 <= n <= 25]
                print(f"   ✅ Números para incluir: {sorted(self.numeros_incluir)}")
            except ValueError:
                print("   ⚠️ Formato inválido, ignorando números para incluir")
                self.numeros_incluir = []
        
        # Números para excluir
        print("\n📉 NÚMEROS QUE NÃO DEVEM ESTAR NA COMBINAÇÃO:")
        print("   (Digite os números separados por vírgula, ou ENTER para pular)")
        excluir_input = input("   Números para excluir: ").strip()
        
        if excluir_input:
            try:
                self.numeros_excluir = [int(x.strip()) for x in excluir_input.split(',')]
                self.numeros_excluir = [n for n in self.numeros_excluir if 1 <= n <= 25]
                print(f"   ✅ Números para excluir: {sorted(self.numeros_excluir)}")
            except ValueError:
                print("   ⚠️ Formato inválido, ignorando números para excluir")
                self.numeros_excluir = []

    def configurar_filtros_posicionais(self, tendencias_posicionais: dict):
        """Interface para configurar filtros posicionais"""
        print("\n🎯 CONFIGURAÇÃO DE FILTROS POSICIONAIS")
        print("=" * 50)
        print("   Configure ranges específicos para cada posição (N1 até N15)")
        print("   Deixe em branco para usar tendências automáticas")
        
        usar_posicionais = input("\nDeseja configurar filtros posicionais? (s/n): ").strip().lower()
        
        if usar_posicionais != 's':
            return
        
        for pos in range(1, 16):
            posicao = f"N{pos}"
            
            if posicao in tendencias_posicionais:
                stats = tendencias_posicionais[posicao]
                print(f"\n📊 {posicao}:")
                print(f"   • Range histórico: {stats['min']} - {stats['max']}")
                print(f"   • Média: {stats['media']}")
                print(f"   • Mais frequentes: {[str(x[0]) for x in stats['mais_frequentes'][:3]]}")
                
                filtro_input = input(f"   Range para {posicao} (min-max ou ENTER): ").strip()
                
                if filtro_input and '-' in filtro_input:
                    try:
                        min_val, max_val = map(int, filtro_input.split('-'))
                        if 1 <= min_val <= max_val <= 25:
                            self.filtros_posicionais[posicao] = {'min': min_val, 'max': max_val}
                            print(f"   ✅ {posicao}: {min_val} - {max_val}")
                    except ValueError:
                        print(f"   ⚠️ Formato inválido para {posicao}")

    def gerar_filtros_inteligentes(self, tendencias: dict, modo: str) -> dict:
        """Gera filtros estatísticos baseados nas tendências"""
        if not tendencias:
            return {}
        
        filtros = {}
        
        # Configurações por modo
        configs = {
            'conservador': {'margem': 1.0, 'cobertura': 0.8},
            'moderado': {'margem': 1.5, 'cobertura': 0.9},
            'agressivo': {'margem': 2.0, 'cobertura': 0.95}
        }
        
        config = configs.get(modo, configs['moderado'])
        
        # Campos para filtrar - CONFIGURAÇÃO OTIMIZADA PARA PERFORMANCE
        campos_filtro = [
            'QtdePrimos', 'QtdeImpares', 'SomaTotal', 'QtdeGaps',
            'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta', 'ParesSequencia'
        ]
        
        for campo in campos_filtro:
            if campo in tendencias:
                stats = tendencias[campo]
                media = stats['media']
                desvio = stats['desvio']
                
                min_val = max(0, int(media - desvio * config['margem']))
                max_val = int(media + desvio * config['margem'])
                
                # Ajustes específicos por campo
                if campo == 'SomaTotal':
                    min_val = max(125, min_val)
                    max_val = min(300, max_val)
                elif campo in ['Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta']:
                    min_val = max(0, min_val)
                    max_val = min(15, max_val)
                elif campo == 'QtdePrimos':
                    min_val = max(0, min_val)
                    max_val = min(9, max_val)
                elif campo == 'QtdeImpares':
                    min_val = max(0, min_val)
                    max_val = min(15, max_val)
                elif campo == 'ParesSequencia':
                    min_val = max(0, min_val)
                    max_val = min(6, max_val)
                
                if min_val <= max_val:
                    filtros[campo] = {'min': min_val, 'max': max_val}
        
        return filtros

    def construir_query_completa(self, filtros_estatisticos: dict) -> tuple:
        """Constrói query SQL com todos os filtros aplicados"""
        condicoes = []
        parametros = []
        
        # 1. Filtros estatísticos
        for campo, valores in filtros_estatisticos.items():
            if 'min' in valores and 'max' in valores:
                condicoes.append(f"{campo} BETWEEN ? AND ?")
                parametros.extend([valores['min'], valores['max']])
        
        # 2. Filtros posicionais
        for posicao, valores in self.filtros_posicionais.items():
            if 'min' in valores and 'max' in valores:
                condicoes.append(f"{posicao} BETWEEN ? AND ?")
                parametros.extend([valores['min'], valores['max']])
        
        # 3. Números para incluir obrigatoriamente
        if self.numeros_incluir:
            # Cada número deve estar presente em alguma posição da combinação
            for numero in self.numeros_incluir:
                condicao_numero = " OR ".join([f"N{i} = ?" for i in range(1, 16)])
                condicoes.append(f"({condicao_numero})")
                parametros.extend([numero] * 15)
        
        # 4. Números para excluir
        if self.numeros_excluir:
            # Nenhum destes números pode estar em nenhuma posição
            for numero in self.numeros_excluir:
                condicao_exclusao = " AND ".join([f"N{i} <> ?" for i in range(1, 16)])
                condicoes.append(f"({condicao_exclusao})")
                parametros.extend([numero] * 15)
        
        # Query final - removendo ORDER BY problemático
        where_clause = " AND ".join(condicoes) if condicoes else "1=1"
        
        query = f"""
        SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM COMBINACOES_LOTOFACIL 
        WHERE {where_clause}
        """
        
        return query, parametros

    def _substituir_parametros_na_query(self, query: str, parametros: list) -> str:
        """
        Substitui os placeholders (?) pelos valores reais na query SQL
        
        Args:
            query: Query SQL com placeholders
            parametros: Lista de parâmetros
            
        Returns:
            str: Query SQL com valores reais
        """
        if not parametros:
            return query
        
        query_final = query
        for parametro in parametros:
            # Substitui o primeiro ? encontrado pelo valor do parâmetro
            if isinstance(parametro, str):
                valor = f"'{parametro}'"
            elif isinstance(parametro, (int, float)):
                valor = str(parametro)
            elif parametro is None:
                valor = "NULL"
            else:
                valor = str(parametro)
            
            query_final = query_final.replace('?', valor, 1)
        
        return query_final

    def contar_combinacoes_filtradas(self, filtros_estatisticos: dict) -> int:
        """Conta combinações que atendem a todos os filtros"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                query, parametros = self.construir_query_completa(filtros_estatisticos)
                count_query = query.replace(
                    "SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15",
                    "SELECT COUNT_BIG(*)"
                )
                
                # Exibe a query de contagem com valores reais
                count_query_com_valores = self._substituir_parametros_na_query(count_query, parametros)
                
                print(f"\n📊 QUERY DE CONTAGEM:")
                print("-" * 60)
                print(count_query_com_valores)
                print("-" * 60)
                
                cursor.execute(count_query, parametros)
                resultado = cursor.fetchone()
                
                return resultado[0] if resultado else 0
                
        except Exception as e:
            print(f"❌ Erro ao contar combinações: {e}")
            return 0

    def gerar_arquivo_combinacoes_avancado(self, filtros_estatisticos: dict, modo: str) -> str:
        """Gera arquivo com combinações usando todos os filtros"""
        try:
            print(f"\n📁 GERANDO ARQUIVO AVANÇADO COM FILTROS...")
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                query, parametros = self.construir_query_completa(filtros_estatisticos)
                
                # ===== EXIBE A QUERY SQL COMPLETA COM VALORES REAIS =====
                query_com_valores = self._substituir_parametros_na_query(query, parametros)
                
                print(f"\n📊 QUERY SQL UTILIZADA:")
                print("=" * 80)
                print(query_com_valores)
                print("=" * 80)
                
                print(f"🔍 Executando consulta com filtros avançados...")
                cursor.execute(query, parametros)
                
                # Nome do arquivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"combinacoes_avancadas_{modo}_{timestamp}.txt"
                
                print(f"💾 Gravando combinações no arquivo: {nome_arquivo}")
                
                contador = 0
                with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                    # Cabeçalho detalhado
                    arquivo.write(f"# COMBINAÇÕES FILTRADAS AVANÇADAS - MODO {modo.upper()}\n")
                    arquivo.write(f"# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    arquivo.write(f"# Baseado no concurso: {self.ultimo_concurso['concurso']}\n")
                    arquivo.write(f"#\n")
                    
                    # Filtros estatísticos
                    arquivo.write(f"# FILTROS ESTATÍSTICOS:\n")
                    for campo, valores in filtros_estatisticos.items():
                        if 'min' in valores and 'max' in valores:
                            arquivo.write(f"#   {campo}: {valores['min']} a {valores['max']}\n")
                    
                    # Filtros posicionais
                    if self.filtros_posicionais:
                        arquivo.write(f"#\n# FILTROS POSICIONAIS:\n")
                        for posicao, valores in self.filtros_posicionais.items():
                            arquivo.write(f"#   {posicao}: {valores['min']} a {valores['max']}\n")
                    
                    # Palpites pessoais
                    if self.numeros_incluir:
                        arquivo.write(f"#\n# NÚMEROS OBRIGATÓRIOS: {sorted(self.numeros_incluir)}\n")
                    
                    if self.numeros_excluir:
                        arquivo.write(f"# NÚMEROS EXCLUÍDOS: {sorted(self.numeros_excluir)}\n")
                    
                    arquivo.write(f"#\n")
                    arquivo.write(f"# QUERY SQL UTILIZADA:\n")
                    
                    # Escreve a query SQL com valores reais como comentário
                    query_com_valores = self._substituir_parametros_na_query(query, parametros)
                    for linha_query in query_com_valores.split('\n'):
                        arquivo.write(f"# {linha_query.strip()}\n")
                    
                    arquivo.write(f"#\n")
                    arquivo.write(f"# Formato: N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15\n")
                    arquivo.write(f"#" + "="*60 + "\n")
                    
                    # Escreve as combinações
                    while True:
                        linhas = cursor.fetchmany(1000)
                        if not linhas:
                            break
                        
                        for linha in linhas:
                            numeros = ','.join(map(str, linha))
                            arquivo.write(f"{numeros}\n")
                            contador += 1
                        
                        if contador % 10000 == 0:
                            print(f"   💾 {contador:,} combinações gravadas...")
                
                print(f"✅ Arquivo avançado gerado com sucesso!")
                print(f"📁 Arquivo: {nome_arquivo}")
                print(f"📊 Total de combinações: {contador:,}")
                
                return nome_arquivo
                
        except Exception as e:
            print(f"❌ Erro ao gerar arquivo avançado: {e}")
            return ""

    def exibir_resumo_filtros(self, filtros_estatisticos: dict, modo: str):
        """Exibe resumo de todos os filtros configurados"""
        print(f"\n🎯 RESUMO DOS FILTROS - MODO {modo.upper()}")
        print("=" * 60)
        
        # Filtros estatísticos
        print("📊 FILTROS ESTATÍSTICOS:")
        for campo, valores in filtros_estatisticos.items():
            if 'min' in valores and 'max' in valores:
                print(f"   • {campo}: {valores['min']} a {valores['max']}")
        
        # Filtros posicionais
        if self.filtros_posicionais:
            print("\n📍 FILTROS POSICIONAIS:")
            for posicao, valores in self.filtros_posicionais.items():
                print(f"   • {posicao}: {valores['min']} a {valores['max']}")
        
        # Palpites pessoais
        if self.numeros_incluir:
            print(f"\n✅ NÚMEROS OBRIGATÓRIOS: {sorted(self.numeros_incluir)}")
        
        if self.numeros_excluir:
            print(f"\n❌ NÚMEROS EXCLUÍDOS: {sorted(self.numeros_excluir)}")
        
        # Conta e exibe resultado
        combinacoes_restantes = self.contar_combinacoes_filtradas(filtros_estatisticos)
        reducao = ((3268760 - combinacoes_restantes) / 3268760) * 100
        
        print(f"\n📈 RESULTADO:")
        print(f"   📊 Combinações restantes: {combinacoes_restantes:,}")
        print(f"   📉 Redução: {reducao:.2f}%")
        
        if combinacoes_restantes > 0:
            fator_reducao = 3268760 / combinacoes_restantes
            print(f"   ⚡ Fator de redução: {fator_reducao:.1f}x")

def main():
    """Função principal do gerador avançado"""
    print("🎯 GERADOR AVANÇADO DE COMBINAÇÕES LOTOFÁCIL")
    print("=" * 60)
    print("   🔹 Filtros estatísticos adaptativos")
    print("   🔹 Filtros posicionais (N1 até N15)")
    print("   🔹 Palpites pessoais (incluir/excluir números)")
    print("=" * 60)
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco. Verifique as configurações.")
        return
    
    gerador = GeradorAvancado()
    
    # Carrega último concurso
    print("\n📊 Carregando dados do último concurso...")
    gerador.ultimo_concurso = gerador.obter_ultimo_concurso()
    
    if not gerador.ultimo_concurso:
        print("❌ Erro ao carregar dados do último concurso")
        return
    
    print(f"✅ Último concurso: {gerador.ultimo_concurso['concurso']}")
    print(f"🎲 Números: {','.join(map(str, sorted(gerador.ultimo_concurso['numeros'])))}")
    
    try:
        # Configurações avançadas
        gerador.configurar_palpites()
        
        print(f"\n🧮 CALCULANDO TENDÊNCIAS...")
        tendencias_estatisticas = gerador.calcular_tendencias_estatisticas()
        tendencias_posicionais = gerador.calcular_tendencias_posicionais()
        
        # Configurar filtros posicionais
        gerador.configurar_filtros_posicionais(tendencias_posicionais)
        
        # Escolher modo
        print("\n🎯 SELECIONE O MODO DO FILTRO:")
        print("1 - Conservador (máxima redução)")
        print("2 - Moderado (balanceado)")
        print("3 - Agressivo (menor redução, mais abrangente)")
        
        modo_opcao = input("\nEscolha o modo (1-3): ").strip()
        modo_map = {'1': 'conservador', '2': 'moderado', '3': 'agressivo'}
        modo_escolhido = modo_map.get(modo_opcao)
        
        if not modo_escolhido:
            print("❌ Opção inválida")
            return
        
        # Gera filtros estatísticos
        filtros_estatisticos = gerador.gerar_filtros_inteligentes(tendencias_estatisticas, modo_escolhido)
        
        if not filtros_estatisticos:
            print("❌ Não foi possível gerar filtros estatísticos")
            return
        
        # Exibe resumo
        gerador.exibir_resumo_filtros(filtros_estatisticos, modo_escolhido)
        
        # Opções finais
        print("\n🎯 OPÇÕES:")
        print("1 - Apenas visualizar resultados")
        print("2 - Gerar arquivo TXT com as combinações")
        
        opcao_final = input("\nEscolha uma opção (1-2): ").strip()
        
        if opcao_final == "2":
            combinacoes_restantes = gerador.contar_combinacoes_filtradas(filtros_estatisticos)
            
            if combinacoes_restantes == 0:
                print("❌ Nenhuma combinação atende aos filtros configurados")
                print("💡 Tente relaxar alguns filtros ou reduzir os números obrigatórios")
                return
            
            confirma = input(f"\nGerar arquivo com {combinacoes_restantes:,} combinações? (s/n): ").strip().lower()
            
            if confirma == 's':
                arquivo = gerador.gerar_arquivo_combinacoes_avancado(filtros_estatisticos, modo_escolhido)
                if arquivo:
                    print(f"\n✅ ARQUIVO AVANÇADO GERADO COM SUCESSO!")
                    print(f"📁 Arquivo: {arquivo}")
                    print(f"📊 Total de combinações: {combinacoes_restantes:,}")
                    
                    reducao = ((3268760 - combinacoes_restantes) / 3268760) * 100
                    print(f"📉 Redução alcançada: {reducao:.2f}%")
                    
                    print(f"\n💡 CARACTERÍSTICAS DO ARQUIVO:")
                    print(f"   • Filtros estatísticos baseados nos últimos {gerador.janela_analise} concursos")
                    if gerador.filtros_posicionais:
                        print(f"   • Filtros posicionais personalizados")
                    if gerador.numeros_incluir:
                        print(f"   • Números obrigatórios incluídos")
                    if gerador.numeros_excluir:
                        print(f"   • Números indesejados excluídos")
                    print(f"   • Formato CSV pronto para sistemas de apostas")
                else:
                    print("❌ Erro ao gerar arquivo")
            else:
                print("❌ Operação cancelada")
        
        print(f"\n✅ Análise avançada concluída!")
    
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
