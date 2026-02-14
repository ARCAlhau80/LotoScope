#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR DE COMBINAÇÕES FILTRADAS
Sistema para gerar arquivos TXT com combinações da Lotofácil filtradas dinamicamente
Autor: AR CALHAU
Data: 12 de Agosto de 2025
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

class GeradorCombinacoes:
    """Classe para geração de combinações filtradas"""
    
    def __init__(self):
        """Inicializa o gerador"""
        self.ultimo_concurso = None
        self.janela_analise = 30  # Últimos 30 concursos para análise
    
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
    
    def calcular_tendencias(self) -> dict:
        """Calcula tendências dos últimos concursos"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # Busca os últimos 30 concursos
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
                
                # Calcula médias e desvios
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
            print(f"❌ Erro ao calcular tendências: {e}")
            return {}
    
    def gerar_filtros_inteligentes(self, tendencias: dict, modo: str) -> dict:
        """
        Gera filtros baseados nas tendências históricas
        
        Args:
            tendencias: Dados estatísticos dos últimos concursos
            modo: Tipo de filtro (conservador, moderado, agressivo)
        """
        if not tendencias:
            return {}
        
        filtros = {}
        
        # Configurações por modo
        configs = {
            'conservador': {'margem': 1.0, 'cobertura': 0.8},  # Mais restritivo
            'moderado': {'margem': 1.5, 'cobertura': 0.9},     # Equilibrado
            'agressivo': {'margem': 2.0, 'cobertura': 0.95}    # Mais abrangente
        }
        
        config = configs.get(modo, configs['moderado'])
        
        # Campos importantes para filtrar
        campos_filtro = [
            'QtdePrimos', 'QtdeImpares', 'SomaTotal', 'QtdeGaps',
            'Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta', 'ParesSequencia'
        ]
        
        for campo in campos_filtro:
            if campo in tendencias:
                stats = tendencias[campo]
                media = stats['media']
                desvio = stats['desvio']
                
                # Calcula range baseado no desvio padrão
                min_val = max(0, int(media - desvio * config['margem']))
                max_val = int(media + desvio * config['margem'])
                
                # Ajustes específicos por campo
                if campo == 'SomaTotal':
                    min_val = max(125, min_val)  # Soma mínima razoável
                    max_val = min(300, max_val)  # Soma máxima razoável
                elif campo in ['Faixa_Baixa', 'Faixa_Media', 'Faixa_Alta']:
                    min_val = max(0, min_val)
                    max_val = min(15, max_val)   # Máximo 15 números
                elif campo == 'QtdePrimos':
                    min_val = max(0, min_val)
                    max_val = min(9, max_val)    # Máximo 9 primos
                elif campo == 'QtdeImpares':
                    min_val = max(0, min_val)
                    max_val = min(15, max_val)   # Máximo 15 ímpares
                
                if min_val <= max_val:
                    filtros[campo] = {'min': min_val, 'max': max_val}
        
        return filtros
    
    def contar_combinacoes_filtradas(self, filtros: dict) -> int:
        """Conta quantas combinações atendem aos filtros"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # Constrói a query com filtros
                condicoes = []
                parametros = []
                
                for campo, valores in filtros.items():
                    if 'min' in valores and 'max' in valores:
                        condicoes.append(f"{campo} BETWEEN ? AND ?")
                        parametros.extend([valores['min'], valores['max']])
                    elif 'min' in valores:
                        condicoes.append(f"{campo} >= ?")
                        parametros.append(valores['min'])
                    elif 'max' in valores:
                        condicoes.append(f"{campo} <= ?")
                        parametros.append(valores['max'])
                
                where_clause = " AND ".join(condicoes)
                
                query = f"SELECT COUNT_BIG(*) FROM COMBINACOES_LOTOFACIL WHERE {where_clause}"
                
                cursor.execute(query, parametros)
                resultado = cursor.fetchone()
                
                return resultado[0] if resultado else 0
                
        except Exception as e:
            print(f"❌ Erro ao contar combinações: {e}")
            return 0
    
    def gerar_arquivo_combinacoes(self, filtros: dict, modo: str) -> str:
        """
        Gera arquivo TXT com as combinações filtradas
        """
        try:
            print(f"\n📁 GERANDO ARQUIVO COM COMBINAÇÕES FILTRADAS...")
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # Constrói a query com filtros
                condicoes = []
                parametros = []
                
                for campo, valores in filtros.items():
                    if 'min' in valores and 'max' in valores:
                        condicoes.append(f"{campo} BETWEEN ? AND ?")
                        parametros.extend([valores['min'], valores['max']])
                    elif 'min' in valores:
                        condicoes.append(f"{campo} >= ?")
                        parametros.append(valores['min'])
                    elif 'max' in valores:
                        condicoes.append(f"{campo} <= ?")
                        parametros.append(valores['max'])
                
                where_clause = " AND ".join(condicoes)
                
                query = f"""
                SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM COMBINACOES_LOTOFACIL 
                WHERE {where_clause}
                ORDER BY ID
                """
                
                print(f"🔍 Executando consulta filtrada...")
                cursor.execute(query, parametros)
                
                # Nome do arquivo com timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"combinacoes_filtradas_{modo}_{timestamp}.txt"
                
                # Gera o arquivo
                print(f"💾 Gravando combinações no arquivo: {nome_arquivo}")
                
                contador = 0
                with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                    # Cabeçalho do arquivo
                    arquivo.write(f"# COMBINAÇÕES FILTRADAS - MODO {modo.upper()}\n")
                    arquivo.write(f"# Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    arquivo.write(f"# Baseado no concurso: {self.ultimo_concurso['concurso']}\n")
                    arquivo.write(f"# Filtros aplicados:\n")
                    
                    for campo, valores in filtros.items():
                        if 'min' in valores and 'max' in valores:
                            arquivo.write(f"#   {campo}: {valores['min']} a {valores['max']}\n")
                        elif 'min' in valores:
                            arquivo.write(f"#   {campo}: >= {valores['min']}\n")
                        elif 'max' in valores:
                            arquivo.write(f"#   {campo}: <= {valores['max']}\n")
                    
                    arquivo.write("#\n")
                    arquivo.write("# Formato: N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15\n")
                    arquivo.write("#" + "="*60 + "\n")
                    
                    # Escreve as combinações
                    while True:
                        linhas = cursor.fetchmany(1000)  # Processa em lotes de 1000
                        if not linhas:
                            break
                        
                        for linha in linhas:
                            numeros = ','.join(map(str, linha))
                            arquivo.write(f"{numeros}\n")
                            contador += 1
                        
                        # Mostra progresso
                        if contador % 10000 == 0:
                            print(f"   💾 {contador:,} combinações gravadas...")
                
                print(f"✅ Arquivo gerado com sucesso!")
                print(f"📁 Arquivo: {nome_arquivo}")
                print(f"📊 Total de combinações: {contador:,}")
                
                return nome_arquivo
                
        except Exception as e:
            print(f"❌ Erro ao gerar arquivo: {e}")
            return ""

def main():
    """Função principal"""
    print("🎯 GERADOR DE COMBINAÇÕES LOTOFÁCIL")
    print("=" * 50)
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco. Verifique as configurações.")
        return
    
    gerador = GeradorCombinacoes()
    
    # Carrega último concurso
    print("📊 Carregando dados do último concurso...")
    gerador.ultimo_concurso = gerador.obter_ultimo_concurso()
    
    if not gerador.ultimo_concurso:
        print("❌ Erro ao carregar dados do último concurso")
        return
    
    print(f"✅ Último concurso: {gerador.ultimo_concurso['concurso']}")
    print(f"🎲 Números: {','.join(map(str, sorted(gerador.ultimo_concurso['numeros'])))}")
    
    # Menu de opções
    print("\n🎯 OPÇÕES DISPONÍVEIS:")
    print("1 - Apenas analisar estatísticas dos filtros")
    print("2 - Gerar arquivo TXT com combinações filtradas")
    
    try:
        opcao = input("\nEscolha uma opção (1-2): ").strip()
        
        if opcao == "1":
            # Análise apenas
            print(f"\n🧮 ANALISANDO TENDÊNCIAS DOS ÚLTIMOS {gerador.janela_analise} CONCURSOS...")
            
            tendencias = gerador.calcular_tendencias()
            
            if not tendencias:
                print("❌ Não foi possível calcular tendências")
                return
            
            print(f"\n📈 RESULTADOS DOS FILTROS:")
            print("=" * 60)
            
            modos = ['conservador', 'moderado', 'agressivo']
            
            for modo in modos:
                print(f"\n🎯 MODO {modo.upper()}:")
                filtros = gerador.gerar_filtros_inteligentes(tendencias, modo)
                
                if filtros:
                    print("   📋 Filtros aplicados:")
                    for campo, valores in filtros.items():
                        if 'min' in valores and 'max' in valores:
                            print(f"      • {campo}: {valores['min']} a {valores['max']}")
                        elif 'min' in valores:
                            print(f"      • {campo}: >= {valores['min']}")
                        elif 'max' in valores:
                            print(f"      • {campo}: <= {valores['max']}")
                    
                    combinacoes_restantes = gerador.contar_combinacoes_filtradas(filtros)
                    reducao = ((3268760 - combinacoes_restantes) / 3268760) * 100
                    fator_reducao = 3268760 / combinacoes_restantes if combinacoes_restantes > 0 else 0
                    
                    print(f"   📊 Combinações restantes: {combinacoes_restantes:,}")
                    print(f"   📉 Redução: {reducao:.2f}%")
                    print(f"   ⚡ Fator de redução: {fator_reducao:.1f}x")
                else:
                    print("   ⚠️ Não foi possível gerar filtros para este modo")
        
        elif opcao == "2":
            # Gerar arquivo
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
            
            print(f"\n🧮 CALCULANDO TENDÊNCIAS E GERANDO FILTROS...")
            
            tendencias = gerador.calcular_tendencias()
            
            if not tendencias:
                print("❌ Não foi possível calcular tendências")
                return
            
            filtros = gerador.gerar_filtros_inteligentes(tendencias, modo_escolhido)
            
            if filtros:
                print(f"\n🎯 FILTROS DO MODO {modo_escolhido.upper()}:")
                for campo, valores in filtros.items():
                    if 'min' in valores and 'max' in valores:
                        print(f"   • {campo}: {valores['min']} a {valores['max']}")
                    elif 'min' in valores:
                        print(f"   • {campo}: >= {valores['min']}")
                    elif 'max' in valores:
                        print(f"   • {campo}: <= {valores['max']}")
                
                # Conta combinações antes de gerar
                combinacoes_restantes = gerador.contar_combinacoes_filtradas(filtros)
                reducao = ((3268760 - combinacoes_restantes) / 3268760) * 100
                
                print(f"\n📊 Combinações que serão geradas: {combinacoes_restantes:,}")
                print(f"📉 Redução: {reducao:.2f}%")
                
                confirma = input(f"\nGerar arquivo com {combinacoes_restantes:,} combinações? (s/n): ").strip().lower()
                
                if confirma == 's':
                    arquivo = gerador.gerar_arquivo_combinacoes(filtros, modo_escolhido)
                    if arquivo:
                        print(f"\n✅ ARQUIVO GERADO COM SUCESSO!")
                        print(f"📁 Arquivo: {arquivo}")
                        print(f"📊 Total de combinações: {combinacoes_restantes:,}")
                        print(f"📉 Redução alcançada: {reducao:.2f}%")
                        
                        # Instruções de uso
                        print(f"\n💡 INSTRUÇÕES:")
                        print(f"   • O arquivo contém uma combinação por linha")
                        print(f"   • Formato: N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15")
                        print(f"   • Pode ser importado em planilhas ou sistemas de apostas")
                    else:
                        print("❌ Erro ao gerar arquivo")
                else:
                    print("❌ Operação cancelada")
            else:
                print(f"❌ Não foi possível gerar filtros para o modo {modo_escolhido}")
        
        else:
            print("❌ Opção inválida")
    
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
