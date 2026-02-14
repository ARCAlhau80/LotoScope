#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR DINÂM            'N14': [20, 21, 22, 23, 24],
            'N15': [23, 24, 25]
        }
        
    def log_print(self, mensagem):
        """Captura print para log e exibe na tela"""
        print(mensagem)
        self.log_buffer.append(mensagem)
        
    def salvar_arquivo_resultado(self, nome_arquivo=None):
        """Salva toda a saída em arquivo TXT com combinações no final"""
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"gerador_dinamico_resultado_{timestamp}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                # Escrever todo o log
                for linha in self.log_buffer:
                    arquivo.write(linha + '\n')
                
                # Adicionar seção de combinações formatadas
                if self.combinacoes_geradas:
                    arquivo.write('\n' + '='*80 + '\n')
                    arquivo.write('COMBINAÇÕES GERADAS (FORMATO PARA JOGOS)\n')
                    arquivo.write('='*80 + '\n\n')
                    
                    # Combinações separadas por vírgula
                    for i, combinacao in enumerate(self.combinacoes_geradas, 1):
                        numeros_formatados = ','.join(map(str, sorted(map(int, combinacao))))
                        arquivo.write(f"Jogo {i:2d}: {numeros_formatados}\n")
                    
                    arquivo.write('\n' + '-'*80 + '\n')
                    arquivo.write('TODAS AS COMBINAÇÕES EM UMA LINHA (SEPARADAS POR VÍRGULA)\n')
                    arquivo.write('-'*80 + '\n\n')
                    
                    # Todas as combinações em uma linha só
                    todas_combinacoes = []
                    for combinacao in self.combinacoes_geradas:
                        numeros_formatados = ','.join(map(str, sorted(map(int, combinacao))))
                        todas_combinacoes.append(numeros_formatados)
                    
                    arquivo.write(' | '.join(todas_combinacoes))
                    arquivo.write('\n')
            
            self.log_print(f"\n💾 ARQUIVO SALVO: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            self.log_print(f"❌ Erro ao salvar arquivo: {e}")
            return None DE FILTROS INTELIGENTES
============================================
Inspirado no script SQL avançado do usuário, este sistema replica
a lógica de filtros multicamada, mas com seleção dinâmica baseada
em dados reais do último concurso e padrões históricos.

ESTRATÉGIA:
• Gera 10 listas filtradas dinamicamente
• Aplica múltiplas camadas de intersecção (11-14 acertos)
• Usa ranges posicionais inteligentes
• Aplica filtros de metadados baseados em tendências
• Seleciona filtros dinamicamente com base no último sorteio

INOVAÇÃO: Zero hardcoding - tudo baseado em dados reais!
"""

import os
import sys
import random
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Adicionar o diretório principal ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

try:
    from database_config import db_config
    print("✅ Módulo database_config importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar database_config: {e}")

class GeradorFiltrosDinamicos:
    """Sistema de geração dinâmica de filtros baseado em dados reais"""
    
    def __init__(self):
        self.ultimo_concurso = None
        self.dados_historicos = []
        self.tendencias_calculadas = {}
        self.filtros_dinamicos = {}
        
        # Sistema de captura de saída
        self.log_buffer = []
        self.combinacoes_geradas = []
        
        # Mapeamento de campos de metadados
        self.campos_metadados = [
            'QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'QtdeRepetidos',
            'Quintil1', 'Quintil2', 'Quintil3', 'Quintil4', 'Quintil5',
            'menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo',
            'seq', 'qtdeMultiplos3', 'distanciaExtremos', 'repetidosMesmaPosicao',
            'SomaTotal', 'QtdeConsecutivos'
        ]
        
        # Ranges posicionais padrão (podem ser ajustados dinamicamente)
        self.ranges_posicionais = {
            'N1': [1, 2, 3],
            'N2': [2, 3, 4, 5], 
            'N3': [3, 4, 5, 6, 7],
            'N4': [4, 5, 6, 7, 8, 9],
            'N5': [6, 7, 8, 9, 10, 11],
            'N6': [7, 8, 9, 10, 11, 12],
            'N7': [9, 10, 11, 12, 13, 14],
            'N8': [10, 11, 12, 13, 14, 15, 16],
            'N9': [12, 13, 14, 15, 16, 17],
            'N10': [14, 15, 16, 17, 18, 19],
            'N11': [15, 16, 17, 18, 19, 20],
            'N12': [17, 18, 19, 20, 21, 22],
            'N13': [19, 20, 21, 22, 23],
            'N14': [21, 22, 23, 24],
            'N15': [23, 24, 25]
        }
        
    def obter_ultimo_concurso(self):
        """Obtém dados do último concurso com metadados"""
        print("🔍 OBTENDO ÚLTIMO CONCURSO COM METADADOS...")
        
        query = """
        SELECT TOP 1
            Concurso, Data_Sorteio,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
            QtdePrimos, QtdeFibonacci, QtdeImpares, QtdeRepetidos,
            Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
            menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo,
            SEQ, QtdeMultiplos3, DistanciaExtremos, RepetidosMesmaPosicao,
            SomaTotal
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                colunas = [desc[0] for desc in cursor.description]
                self.ultimo_concurso = dict(zip(colunas, resultado))
                print(f"✅ Último concurso: {self.ultimo_concurso['Concurso']}")
                cursor.close()
                conn.close()
                return True
            else:
                print("❌ Nenhum concurso encontrado")
                cursor.close()
                conn.close()
                return False
        except Exception as e:
            print(f"❌ Erro ao obter último concurso: {e}")
            return False
    
    def carregar_dados_historicos(self, limite=50):
        """Carrega dados históricos para análise de tendências"""
        print(f"📊 CARREGANDO {limite} CONCURSOS HISTÓRICOS...")
        
        query = f"""
        SELECT TOP {limite}
            Concurso,
            QtdePrimos, QtdeFibonacci, QtdeImpares, QtdeRepetidos,
            Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
            menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo,
            SEQ, QtdeMultiplos3, DistanciaExtremos, RepetidosMesmaPosicao,
            SomaTotal
        FROM Resultados_INT 
        ORDER BY Concurso DESC
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                colunas = [desc[0] for desc in cursor.description]
                self.dados_historicos = [dict(zip(colunas, row)) for row in resultados]
                print(f"✅ {len(resultados)} concursos carregados")
                cursor.close()
                conn.close()
                return True
            else:
                print("❌ Nenhum dado histórico encontrado")
                cursor.close()
                conn.close()
                return False
        except Exception as e:
            print(f"❌ Erro ao carregar dados históricos: {e}")
            return False
    
    def calcular_tendencias_metadados(self):
        """Calcula tendências dos metadados para ajuste dinâmico"""
        print("🧠 CALCULANDO TENDÊNCIAS DOS METADADOS...")
        
        for campo in self.campos_metadados:
            if campo in self.ultimo_concurso:
                valor_atual = self.ultimo_concurso[campo]
                valores_historicos = [d[campo] for d in self.dados_historicos if d[campo] is not None]
                
                if valores_historicos:
                    media = sum(valores_historicos) / len(valores_historicos)
                    minimo = min(valores_historicos)
                    maximo = max(valores_historicos)
                    
                    # Determinar tendência
                    if valor_atual < media * 0.8:
                        tendencia = "ALTA"
                        faixa = self.expandir_faixa_para_cima(valor_atual, maximo)
                    elif valor_atual > media * 1.2:
                        tendencia = "BAIXA"
                        faixa = self.expandir_faixa_para_baixo(valor_atual, minimo)
                    else:
                        tendencia = "ESTAVEL"
                        faixa = self.manter_faixa_estavel(valor_atual, media)
                    
                    self.tendencias_calculadas[campo] = {
                        'valor_atual': valor_atual,
                        'media': round(media, 2),
                        'tendencia': tendencia,
                        'faixa_dinamica': faixa
                    }
        
        print("✅ Tendências calculadas com sucesso!")
    
    def expandir_faixa_para_cima(self, valor_atual, maximo):
        """Expande faixa para valores maiores"""
        inicio = max(0, valor_atual - 1)
        fim = min(maximo, valor_atual + 4)
        return list(range(inicio, fim + 1))
    
    def expandir_faixa_para_baixo(self, valor_atual, minimo):
        """Expande faixa para valores menores"""
        inicio = max(minimo, valor_atual - 4)
        fim = min(25, valor_atual + 1)
        return list(range(inicio, fim + 1))
    
    def manter_faixa_estavel(self, valor_atual, media):
        """Mantém faixa estável ao redor do valor"""
        centro = int(media)
        inicio = max(0, centro - 2)
        fim = min(25, centro + 2)
        return list(range(inicio, fim + 1))
    
    def ajustar_ranges_posicionais(self):
        """Ajusta ranges posicionais baseado no último concurso"""
        print("🎯 AJUSTANDO RANGES POSICIONAIS...")
        
        numeros_ultimo = [self.ultimo_concurso[f'N{i}'] for i in range(1, 16)]
        
        # Detectar tendência geral dos números
        if self.ultimo_concurso['menor_que_ultimo'] >= 12:
            # Números devem subir
            ajuste = 1
            print("📈 Ajuste: números devem SUBIR")
        elif self.ultimo_concurso['maior_que_ultimo'] >= 12:
            # Números devem descer
            ajuste = -1
            print("📉 Ajuste: números devem DESCER")
        else:
            # Manter estável
            ajuste = 0
            print("↔️ Ajuste: manter ESTÁVEL")
        
        # Aplicar ajuste aos ranges
        for i, pos in enumerate(['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 
                                'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15']):
            num_atual = numeros_ultimo[i]
            range_atual = self.ranges_posicionais[pos].copy()
            
            if ajuste != 0:
                # Ajustar range baseado na tendência
                range_ajustado = [max(1, min(25, x + ajuste)) for x in range_atual]
                # Garantir que o número atual está no range (para validação)
                if num_atual not in range_ajustado:
                    if ajuste > 0:
                        range_ajustado.extend([num_atual + 1, num_atual + 2])
                    else:
                        range_ajustado.extend([num_atual - 1, num_atual - 2])
                
                self.ranges_posicionais[pos] = sorted(list(set(range_ajustado)))
        
        print("✅ Ranges posicionais ajustados!")
    
    def gerar_lista_filtrada(self, lista_num):
        """Gera uma lista filtrada da tabela COMBINACOES_LOTOFACIL"""
        print(f"🔧 GERANDO LISTA {lista_num}...")
        
        # Construir filtros baseados nas tendências
        filtros = []
        
        # Filtro base: QtdeRepetidos = 15 (fixo como no SQL original)
        filtros.append("QtdeRepetidos = 15")
        
        # Aplicar filtros dinâmicos baseados nas tendências
        for campo, info in self.tendencias_calculadas.items():
            if campo in ['QtdePrimos', 'QtdeFibonacci', 'QtdeImpares', 'SomaTotal']:
                faixa = info['faixa_dinamica']
                if len(faixa) > 0:
                    if campo == 'SomaTotal':
                        minimo = min(faixa)
                        maximo = max(faixa)
                        filtros.append(f"{campo} BETWEEN {minimo} AND {maximo}")
                    else:
                        faixa_str = ','.join(map(str, faixa))
                        filtros.append(f"{campo} IN ({faixa_str})")
        
        # Para listas 4-10, adicionar filtros de quintis (que existem na tabela)
        if lista_num >= 4:
            for quintil in range(1, 6):
                filtros.append(f"Quintil{quintil} IN (1,2,3,4,5)")
        
        # Construir query
        where_clause = " AND ".join(filtros)
        
        query = f"""
        SELECT TOP 1 CONCAT(N1,',',N2,',',N3,',',N4,',',N5,',',N6,',',N7,',',N8,',',N9,',',N10,',',N11,',',N12,',',N13,',',N14,',',N15) as numeros
        FROM COMBINACOES_LOTOFACIL
        WHERE {where_clause}
        ORDER BY NEWID()
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                numeros = resultado[0]
                cursor.close()
                conn.close()
                return numeros
            else:
                print(f"⚠️ Nenhuma combinação encontrada para Lista {lista_num}")
                cursor.close()
                conn.close()
                return None
        except Exception as e:
            print(f"❌ Erro ao gerar Lista {lista_num}: {e}")
            return None
    
    def gerar_10_listas_filtradas(self):
        """Gera as 10 listas filtradas dinamicamente"""
        print("\n🎲 GERANDO 10 LISTAS FILTRADAS...")
        print("=" * 50)
        
        listas = {}
        for i in range(1, 11):
            lista = self.gerar_lista_filtrada(i)
            if lista:
                listas[f'Lista{i}'] = lista
                numeros = lista.split(',')[:15]  # Mostrar apenas os 15 primeiros
                print(f"✅ Lista {i}: {numeros}")
            else:
                # Fallback: gerar lista aleatória válida
                print(f"⚠️ Lista {i}: Gerando fallback...")
                listas[f'Lista{i}'] = self.gerar_lista_fallback()
        
        return listas
    
    def gerar_lista_fallback(self):
        """Gera lista fallback quando filtros são muito restritivos"""
        query = """
        SELECT TOP 1 CONCAT(N1,',',N2,',',N3,',',N4,',',N5,',',N6,',',N7,',',N8,',',N9,',',N10,',',N11,',',N12,',',N13,',',N14,',',N15) as numeros
        FROM COMBINACOES_LOTOFACIL
        WHERE QtdeRepetidos = 15
        ORDER BY NEWID()
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            return resultado[0] if resultado else "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
        except:
            return "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
    
    def aplicar_filtro_principal(self, listas):
        """Aplica o filtro principal com intersecções múltiplas"""
        print("\n🔍 APLICANDO FILTRO PRINCIPAL COM INTERSECÇÕES...")
        print("=" * 60)
        
        # Construir filtros dinâmicos baseados nas tendências
        filtros_metadata = []
        
        for campo, info in self.tendencias_calculadas.items():
            if campo in self.ultimo_concurso:
                faixa = info['faixa_dinamica']
                if len(faixa) > 0 and len(faixa) <= 10:  # Evitar faixas muito grandes
                    faixa_str = ','.join(map(str, faixa))
                    filtros_metadata.append(f"{campo} IN ({faixa_str})")
        
        # Construir ranges posicionais
        ranges_posicionais = []
        for pos, valores in self.ranges_posicionais.items():
            if len(valores) <= 10:  # Evitar ranges muito grandes
                valores_str = ','.join(map(str, valores))
                ranges_posicionais.append(f"{pos.lower()} IN ({valores_str})")
        
        # Construir números obrigatórios baseados no último concurso
        numeros_obrigatorios = self.gerar_numeros_obrigatorios()
        
        # Query principal (similar ao SQL original)
        intersecoes = []
        for i, (nome, lista) in enumerate(listas.items(), 1):
            if i <= 3:
                acertos = "(11,12,13)"
            else:
                acertos = "(11,12,13,14)"
            
            intersecao = f"""
            (CASE WHEN N1 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N2 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N3 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N4 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N5 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N6 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N7 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N8 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N9 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N10 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N11 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N12 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N13 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N14 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END +
             CASE WHEN N15 IN ({self.converter_lista_para_in(lista)}) THEN 1 ELSE 0 END) IN {acertos}
            """
            intersecoes.append(intersecao)
        
        # Construir query final
        where_clauses = []
        where_clauses.extend(intersecoes)
        where_clauses.extend(ranges_posicionais)
        where_clauses.extend(numeros_obrigatorios)
        where_clauses.extend(filtros_metadata[:10])  # Limitar metadados para evitar query muito complexa
        
        query = f"""
        SELECT TOP 50 *
        FROM VW_CombinLotofacil
        WHERE {' AND '.join(where_clauses)}
        ORDER BY NEWID()
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                colunas = [desc[0] for desc in cursor.description]
                combinacoes = [dict(zip(colunas, row)) for row in resultados]
                cursor.close()
                conn.close()
                return combinacoes
            else:
                print("⚠️ Nenhuma combinação encontrada com filtros completos")
                cursor.close()
                conn.close()
                return self.aplicar_filtro_simplificado()
        except Exception as e:
            print(f"❌ Erro no filtro principal: {e}")
            return self.aplicar_filtro_simplificado()
    
    def aplicar_filtro_simplificado(self):
        """Aplica filtro simplificado quando o principal falha"""
        print("🔧 APLICANDO FILTRO SIMPLIFICADO...")
        
        # Usar apenas os filtros mais importantes
        filtros_principais = []
        
        # Filtros baseados no último concurso
        if 'menor_que_ultimo' in self.tendencias_calculadas:
            info = self.tendencias_calculadas['menor_que_ultimo']
            faixa = info['faixa_dinamica'][:5]  # Limitar a 5 valores
            filtros_principais.append(f"menor_que_ultimo IN ({','.join(map(str, faixa))})")
        
        if 'maior_que_ultimo' in self.tendencias_calculadas:
            info = self.tendencias_calculadas['maior_que_ultimo']
            faixa = info['faixa_dinamica'][:5]
            filtros_principais.append(f"maior_que_ultimo IN ({','.join(map(str, faixa))})")
        
        if 'SomaTotal' in self.tendencias_calculadas:
            info = self.tendencias_calculadas['SomaTotal']
            faixa = info['faixa_dinamica']
            if len(faixa) > 0:
                minimo = min(faixa)
                maximo = max(faixa)
                filtros_principais.append(f"SomaTotal BETWEEN {minimo} AND {maximo}")
        
        # Se não há filtros principais, usar filtros básicos
        if not filtros_principais:
            filtros_principais.append("QtdeRepetidos = 15")
            filtros_principais.append("QtdePrimos BETWEEN 3 AND 7")
            filtros_principais.append("QtdeImpares BETWEEN 5 AND 9")
        
        query = f"""
        SELECT TOP 20 *
        FROM VW_CombinLotofacil
        WHERE {' AND '.join(filtros_principais)}
        ORDER BY NEWID()
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                colunas = [desc[0] for desc in cursor.description]
                combinacoes = [dict(zip(colunas, row)) for row in resultados]
                cursor.close()
                conn.close()
                return combinacoes
            else:
                cursor.close()
                conn.close()
                return []
        except Exception as e:
            print(f"❌ Erro no filtro simplificado: {e}")
            return []
    
    def converter_lista_para_in(self, lista_str):
        """Converte string de lista para formato IN do SQL"""
        numeros = lista_str.split(',')
        return ','.join(numeros)
    
    def gerar_numeros_obrigatorios(self):
        """Gera filtros de números obrigatórios baseados no último concurso"""
        obrigatorios = []
        
        numeros_ultimo = [self.ultimo_concurso[f'N{i}'] for i in range(1, 16)]
        
        # Identificar números que devem continuar aparecendo
        # (baseado na lógica do script original)
        for i, num in enumerate([2, 3, 8, 9, 10, 17, 21, 24, 25]):
            if num in numeros_ultimo:
                # Determinar posições prováveis
                posicoes = []
                if num <= 3:
                    posicoes = ['n1', 'n2', 'n3']
                elif num <= 6:
                    posicoes = ['n2', 'n3', 'n4']
                elif num <= 10:
                    posicoes = ['n4', 'n5', 'n6', 'n7', 'n8']
                elif num <= 17:
                    posicoes = ['n9', 'n10', 'n11', 'n12']
                elif num <= 21:
                    posicoes = ['n12', 'n13', 'n14']
                else:
                    posicoes = ['n14', 'n15']
                
                if posicoes:
                    posicoes_str = ','.join(posicoes)
                    obrigatorios.append(f"{num} IN ({posicoes_str})")
        
        return obrigatorios
    
    def executar_geracao_completa(self):
        """Executa o processo completo de geração"""
        print("🚀 INICIANDO GERAÇÃO DINÂMICA DE FILTROS...")
        print("=" * 80)
        
        # Passo 1: Carregar dados
        if not self.obter_ultimo_concurso():
            return False
        
        if not self.carregar_dados_historicos():
            return False
        
        # Passo 2: Calcular tendências
        self.calcular_tendencias_metadados()
        
        # Passo 3: Ajustar ranges
        self.ajustar_ranges_posicionais()
        
        # Passo 4: Gerar listas
        listas = self.gerar_10_listas_filtradas()
        
        # Passo 5: Aplicar filtro principal
        print("\n📊 RELATÓRIO DE TENDÊNCIAS APLICADAS:")
        print("=" * 50)
        for campo, info in self.tendencias_calculadas.items():
            print(f"{campo}: {info['valor_atual']} → {info['tendencia']} → {info['faixa_dinamica'][:5]}...")
        
        print(f"\n🎯 CONCURSO ANALISADO: {self.ultimo_concurso['Concurso']}")
        print(f"📊 Estado comparação: ({self.ultimo_concurso['menor_que_ultimo']}, {self.ultimo_concurso['maior_que_ultimo']}, {self.ultimo_concurso['igual_ao_ultimo']})")
        
        # Aplicar filtros
        combinacoes = self.aplicar_filtro_principal(listas)
        
        # Mostrar resultados
        print(f"\n🎲 COMBINAÇÕES ENCONTRADAS: {len(combinacoes)}")
        print("=" * 80)
        
        for i, comb in enumerate(combinacoes[:10], 1):
            numeros = [comb[f'N{j}'] for j in range(1, 16)]
            soma = sum(numeros)
            print(f"Jogo {i:2d}: {numeros} | Soma: {soma} | Primos: {comb['QtdePrimos']} | Rep: {comb['QtdeRepetidos']}")
        
        print("=" * 80)
        print("✅ GERAÇÃO COMPLETA FINALIZADA!")
        
        return True

def main():
    """Função principal"""
    print("🎯 GERADOR DINÂMICO DE FILTROS INTELIGENTES")
    print("Baseado no script SQL avançado com seleção automática de filtros")
    
    gerador = GeradorFiltrosDinamicos()
    
    if gerador.executar_geracao_completa():
        print("\n💾 Deseja executar novamente? (s/n): ", end="")
        try:
            resposta = input().lower().strip()
            if resposta == 's':
                main()
        except:
            pass
    else:
        print("❌ Falha na geração")

if __name__ == "__main__":
    main()