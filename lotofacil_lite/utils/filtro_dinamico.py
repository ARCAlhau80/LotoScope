#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 FILTRO DINÂMICO INTELIGENTE - LOTOFÁCIL
Sistema de filtro adaptativo baseado em padrões históricos
Autor: AR CALHAU
Data: 11 de Agosto de 2025
"""

import sys
from pathlib import Path
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

import statistics
from collections import Counter
from datetime import datetime

class FiltroDinamico:
    """Classe para geração de filtros dinâmicos baseados em padrões históricos"""
    
    def __init__(self):
        self.ultimo_concurso = None
        self.historico_recente = []
        self.tendencias = {}
        
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
                        'qtde_primos': row[16],
                        'qtde_fibonacci': row[17],
                        'qtde_impares': row[18],
                        'soma_total': row[19],
                        'quintil1': row[20],
                        'quintil2': row[21],
                        'quintil3': row[22],
                        'quintil4': row[23],
                        'quintil5': row[24],
                        'qtde_gaps': row[25],
                        'seq': row[26],
                        'distancia_extremos': row[27],
                        'pares_sequencia': row[28],
                        'qtde_multiplos3': row[29],
                        'pares_saltados': row[30],
                        'faixa_baixa': row[31],
                        'faixa_media': row[32],
                        'faixa_alta': row[33],
                        'qtde_repetidos': row[34],
                        'repetidos_mesma_posicao': row[35]
                    }
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter último concurso: {e}")
            return None
    
    def obter_historico_recente(self, quantidade: int = 50) -> list:
        """Obtém histórico dos últimos N concursos"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(f"""
                    SELECT TOP {quantidade} Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                           QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal, Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                           QtdeGaps, SEQ, DistanciaExtremos, ParesSequencia, QtdeMultiplos3, ParesSaltados,
                           Faixa_Baixa, Faixa_Media, Faixa_Alta, QtdeRepetidos, RepetidosMesmaPosicao
                    FROM Resultados_INT 
                    ORDER BY Concurso DESC
                """)
                
                historico = []
                for row in cursor.fetchall():
                    historico.append({
                        'concurso': row[0],
                        'numeros': list(row[1:16]),
                        'qtde_primos': row[16],
                        'qtde_fibonacci': row[17],
                        'qtde_impares': row[18],
                        'soma_total': row[19],
                        'quintil1': row[20],
                        'quintil2': row[21],
                        'quintil3': row[22],
                        'quintil4': row[23],
                        'quintil5': row[24],
                        'qtde_gaps': row[25],
                        'seq': row[26],
                        'distancia_extremos': row[27],
                        'pares_sequencia': row[28],
                        'qtde_multiplos3': row[29],
                        'pares_saltados': row[30],
                        'faixa_baixa': row[31],
                        'faixa_media': row[32],
                        'faixa_alta': row[33],
                        'qtde_repetidos': row[34],
                        'repetidos_mesma_posicao': row[35]
                    })
                
                return historico
                
        except Exception as e:
            print(f"❌ Erro ao obter histórico: {e}")
            return []
    
    def calcular_tendencias(self, historico: list) -> dict:
        """Calcula tendências estatísticas do histórico"""
        if not historico:
            return {}
        
        tendencias = {}
        
        # Análise de cada campo estatístico
        campos = ['qtde_primos', 'qtde_fibonacci', 'qtde_impares', 'soma_total',
                 'quintil1', 'quintil2', 'quintil3', 'quintil4', 'quintil5',
                 'qtde_gaps', 'seq', 'distancia_extremos', 'pares_sequencia',
                 'qtde_multiplos3', 'pares_saltados', 'faixa_baixa', 'faixa_media', 'faixa_alta',
                 'qtde_repetidos', 'repetidos_mesma_posicao']
        
        for campo in campos:
            valores = [concurso[campo] for concurso in historico if concurso[campo] is not None]
            if valores:
                tendencias[campo] = {
                    'media': statistics.mean(valores),
                    'mediana': statistics.median(valores),
                    'moda': statistics.mode(valores) if len(set(valores)) < len(valores) else valores[0],
                    'min': min(valores),
                    'max': max(valores),
                    'desvio': statistics.stdev(valores) if len(valores) > 1 else 0,
                    'valores_mais_frequentes': Counter(valores).most_common(3)
                }
        
        return tendencias
    
    def gerar_filtro_adaptativo(self, modo: str = "conservador") -> dict:
        """
        Gera filtro adaptativo baseado nos padrões
        
        Args:
            modo: "conservador", "moderado", "agressivo"
        """
        print("🎯 GERANDO FILTRO DINÂMICO ADAPTATIVO")
        print("=" * 50)
        
        # Obtém dados
        self.ultimo_concurso = self.obter_ultimo_concurso()
        self.historico_recente = self.obter_historico_recente(30)  # Últimos 30 concursos
        self.tendencias = self.calcular_tendencias(self.historico_recente)
        
        if not self.ultimo_concurso or not self.tendencias:
            print("❌ Não foi possível obter dados suficientes")
            return {}
        
        print(f"📊 Último concurso: {self.ultimo_concurso['concurso']}")
        print(f"📈 Analisando últimos {len(self.historico_recente)} concursos")
        
        # Configurações por modo
        config = {
            "conservador": {"tolerancia": 0.5, "amplitude": 1},
            "moderado": {"tolerancia": 0.3, "amplitude": 2}, 
            "agressivo": {"tolerancia": 0.1, "amplitude": 3}
        }
        
        tol = config[modo]["tolerancia"]
        amp = config[modo]["amplitude"]
        
        filtro = {}
        
        # 1. FILTRO DE PRIMOS (baseado na tendência)
        media_primos = self.tendencias['qtde_primos']['media']
        ultimo_primos = self.ultimo_concurso['qtde_primos']
        
        # Se último concurso teve muitos primos, reduz um pouco
        if ultimo_primos > media_primos:
            filtro['QtdePrimos'] = {
                'min': max(0, int(media_primos - amp)),
                'max': int(media_primos + amp)
            }
        else:
            filtro['QtdePrimos'] = {
                'min': int(media_primos - amp),
                'max': int(media_primos + amp + 1)
            }
        
        # 2. FILTRO DE ÍMPARES (complementar aos pares)
        media_impares = self.tendencias['qtde_impares']['media']
        filtro['QtdeImpares'] = {
            'min': max(5, int(media_impares - amp)),
            'max': min(10, int(media_impares + amp))
        }
        
        # 3. FILTRO DE SOMA (baseado no padrão)
        media_soma = self.tendencias['soma_total']['media']
        desvio_soma = self.tendencias['soma_total']['desvio']
        filtro['SomaTotal'] = {
            'min': int(media_soma - desvio_soma * (2 - tol)),
            'max': int(media_soma + desvio_soma * (2 - tol))
        }
        
        # 4. FILTROS DE QUINTIS (distribuição equilibrada)
        for i in range(1, 6):
            campo = f'quintil{i}'
            media_quintil = self.tendencias[campo]['media']
            filtro[f'Quintil{i}'] = {
                'min': max(0, int(media_quintil - amp)),
                'max': min(6, int(media_quintil + amp))
            }
        
        # 5. FILTRO DE FAIXAS (baseado na tendência recente)
        for faixa in ['faixa_baixa', 'faixa_media', 'faixa_alta']:
            campo_db = faixa.replace('_', '_').title().replace('_', '_')
            media_faixa = self.tendencias[faixa]['media']
            filtro[campo_db] = {
                'min': max(0, int(media_faixa - amp)),
                'max': min(8, int(media_faixa + amp))
            }
        
        # 6. FILTRO DE SEQUÊNCIAS (pares em sequência)
        ultimo_pares_seq = self.ultimo_concurso['pares_sequencia']
        media_pares_seq = self.tendencias['pares_sequencia']['media']
        
        # Tendência de inversão - se último teve muitos, próximo pode ter menos
        if ultimo_pares_seq > media_pares_seq:
            filtro['ParesSequencia'] = {
                'min': 0,
                'max': int(media_pares_seq)
            }
        else:
            filtro['ParesSequencia'] = {
                'min': int(media_pares_seq - 1),
                'max': int(media_pares_seq + amp)
            }
        
        # 7. FILTRO DE PARES SALTADOS
        media_pares_saltados = self.tendencias['pares_saltados']['media']
        filtro['ParesSaltados'] = {
            'min': max(0, int(media_pares_saltados - amp)),
            'max': int(media_pares_saltados + amp)
        }
        
        # 8. FILTRO DE REPETIDOS (baseado no último concurso)
        # Calcula quantos números do último concurso devem repetir
        media_repetidos = self.tendencias['qtde_repetidos']['media']
        if modo == "conservador":
            filtro['QtdeRepetidos'] = {
                'min': max(5, int(media_repetidos - 2)),
                'max': min(10, int(media_repetidos + 2))
            }
        elif modo == "moderado":
            filtro['QtdeRepetidos'] = {
                'min': max(4, int(media_repetidos - 3)),
                'max': min(11, int(media_repetidos + 3))
            }
        else:  # agressivo
            filtro['QtdeRepetidos'] = {
                'min': max(3, int(media_repetidos - 4)),
                'max': min(12, int(media_repetidos + 4))
            }
        
        return filtro
    
    def contar_combinacoes_filtradas(self, filtros: dict) -> int:
        """Conta quantas combinações passam pelos filtros"""
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # Constrói a query WHERE dinamicamente
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
                SELECT COUNT_BIG(*) 
                FROM COMBINACOES_LOTOFACIL 
                WHERE {where_clause}
                """
                
                cursor.execute(query, parametros)
                resultado = cursor.fetchone()
                
                return resultado[0] if resultado else 0
                
        except Exception as e:
            print(f"❌ Erro ao contar combinações: {e}")
            return 0
    
    def exibir_filtro_detalhado(self, filtros: dict, modo: str):
        """Exibe o filtro gerado de forma detalhada"""
        total_original = 3268760  # Total de combinações possíveis
        total_filtrado = self.contar_combinacoes_filtradas(filtros)
        reducao_percentual = ((total_original - total_filtrado) / total_original) * 100
        
        print(f"\n🎯 FILTRO DINÂMICO - MODO {modo.upper()}")
        print("=" * 60)
        print(f"📊 Baseado no concurso {self.ultimo_concurso['concurso']}")
        print(f"📈 Últimos {len(self.historico_recente)} concursos analisados")
        
        print(f"\n📋 FILTROS GERADOS:")
        for campo, valores in filtros.items():
            if 'min' in valores and 'max' in valores:
                print(f"   {campo}: {valores['min']} a {valores['max']}")
            elif 'min' in valores:
                print(f"   {campo}: >= {valores['min']}")
            elif 'max' in valores:
                print(f"   {campo}: <= {valores['max']}")
        
        print(f"\n📊 ESTATÍSTICAS DE REDUÇÃO:")
        print(f"   • Combinações originais: {total_original:,}")
        print(f"   • Combinações filtradas: {total_filtrado:,}")
        print(f"   • Redução: {reducao_percentual:.2f}%")
        print(f"   • Fator de redução: {total_original/total_filtrado:.1f}x")
        
        # Análise da redução
        if reducao_percentual > 99:
            print(f"   🎯 REDUÇÃO EXCELENTE! Filtro muito eficiente")
        elif reducao_percentual > 95:
            print(f"   ✅ REDUÇÃO MUITO BOA! Filtro eficiente")
        elif reducao_percentual > 90:
            print(f"   👍 REDUÇÃO BOA! Filtro moderado")
        else:
            print(f"   ⚠️ REDUÇÃO BAIXA! Considere modo mais agressivo")
    
    def gerar_sql_filtro(self, filtros: dict) -> str:
        """Gera SQL para aplicar os filtros"""
        condicoes = []
        
        for campo, valores in filtros.items():
            if 'min' in valores and 'max' in valores:
                condicoes.append(f"{campo} BETWEEN {valores['min']} AND {valores['max']}")
            elif 'min' in valores:
                condicoes.append(f"{campo} >= {valores['min']}")
            elif 'max' in valores:
                condicoes.append(f"{campo} <= {valores['max']}")
        
        where_clause = " AND ".join(condicoes)
        
        sql = f"""
SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
FROM COMBINACOES_LOTOFACIL 
WHERE {where_clause}
ORDER BY ID
"""
        return sql
    
    def gerar_combinacoes_arquivo(self, filtros: dict, modo: str) -> str:
        """
        Gera arquivo TXT com as combinações filtradas
        
        Args:
            filtros: Dicionário com os filtros a aplicar
            modo: Modo do filtro (conservador, moderado, agressivo)
            
        Returns:
            str: Caminho do arquivo gerado
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
                from datetime import datetime
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
    
    def executar_analise_completa(self):
        """Executa análise completa com todos os modos"""
        print("🎯 ANÁLISE COMPLETA DE FILTROS DINÂMICOS")
        print("=" * 60)
        
        modos = ["conservador", "moderado", "agressivo"]
        
        for modo in modos:
            filtros = self.gerar_filtro_adaptativo(modo)
            if filtros:
                self.exibir_filtro_detalhado(filtros, modo)
                print("\n" + "-" * 60)
        
        # Recomendação
        print("\n💡 RECOMENDAÇÕES:")
        print("   • CONSERVADOR: Maior chance de acerto, redução moderada")
        print("   • MODERADO: Equilíbrio entre acerto e redução")
        print("   • AGRESSIVO: Máxima redução, maior risco")

if __name__ == "__main__":
    print("🎯 SISTEMA DE FILTRO DINÂMICO")
    print("=" * 50)
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco. Verifique as configurações.")
        exit(1)
    
    filtro = FiltroDinamico()
    
    ultimo_concurso_dados = filtro.obter_ultimo_concurso()
    if not ultimo_concurso_dados:
        print("❌ Erro ao carregar dados do último concurso")
        exit(1)
    
    # Armazena os dados para uso posterior
    filtro.ultimo_concurso = ultimo_concurso_dados
    
    print(f"\n� Último concurso analisado: {filtro.ultimo_concurso['concurso']}")
    print(f"🎲 Números: {','.join(map(str, sorted(filtro.ultimo_concurso['numeros'])))}")
    
    # Menu de opções
    print("\n🎯 OPÇÕES DISPONÍVEIS:")
    print("1 - Apenas analisar e mostrar estatísticas")
    print("2 - Gerar arquivo TXT com combinações filtradas")
    
    opcao = input("\nEscolha uma opção (1-2): ").strip()
    
    if opcao == "1":
        # Análise apenas
        print(f"\n🧮 ANALISANDO TENDÊNCIAS DOS ÚLTIMOS {filtro.janela_analise} CONCURSOS...")
        
        tendencias = filtro.calcular_tendencias()
        
        print(f"\n📈 RESULTADOS DOS FILTROS:")
        print("=" * 60)
        
        modos = ['conservador', 'moderado', 'agressivo']
        
        for modo in modos:
            print(f"\n🎯 MODO {modo.upper()}:")
            filtros = filtro.gerar_filtro_adaptativo(tendencias, modo)
            
            if filtros:
                print("   📋 Filtros aplicados:")
                for campo, valores in filtros.items():
                    if 'min' in valores and 'max' in valores:
                        print(f"      • {campo}: {valores['min']} a {valores['max']}")
                    elif 'min' in valores:
                        print(f"      • {campo}: >= {valores['min']}")
                    elif 'max' in valores:
                        print(f"      • {campo}: <= {valores['max']}")
                
                combinacoes_restantes = filtro.contar_combinacoes_filtradas(filtros)
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
            exit(1)
        
        print(f"\n🧮 CALCULANDO TENDÊNCIAS E GERANDO FILTROS...")
        
        tendencias = filtro.calcular_tendencias()
        filtros = filtro.gerar_filtro_adaptativo(tendencias, modo_escolhido)
        
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
            combinacoes_restantes = filtro.contar_combinacoes_filtradas(filtros)
            reducao = ((3268760 - combinacoes_restantes) / 3268760) * 100
            
            print(f"\n📊 Combinações que serão geradas: {combinacoes_restantes:,}")
            print(f"📉 Redução: {reducao:.2f}%")
            
            confirma = input(f"\nGerar arquivo com {combinacoes_restantes:,} combinações? (s/n): ").strip().lower()
            
            if confirma == 's':
                arquivo = filtro.gerar_combinacoes_arquivo(filtros, modo_escolhido)
                if arquivo:
                    print(f"\n✅ ARQUIVO GERADO COM SUCESSO!")
                    print(f"📁 Arquivo: {arquivo}")
                    print(f"📊 Total de combinações: {combinacoes_restantes:,}")
                    print(f"📉 Redução alcançada: {reducao:.2f}%")
                else:
                    print("❌ Erro ao gerar arquivo")
            else:
                print("❌ Operação cancelada")
        else:
            print(f"❌ Não foi possível gerar filtros para o modo {modo_escolhido}")
    
    else:
        print("❌ Opção inválida")
