#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 MENU LOTOFÁCIL - ATUALIZAÇÃO DA BASE
Sistema de atualização automática da base de dados
Autor: AR CALHAU
Data: 04 de Agosto de 2025
"""

import sys
import os
from pathlib import Path

# Adicionar diretório base ao path para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

import requests
import json
import time
import math
from datetime import datetime
from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None


class MenuLotofacil:
    """Classe para atualização automática da base de dados Lotofácil"""
    
    def __init__(self):
        self.api_url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
        self.max_retries = 3
        self.retry_delay = 2
        # Números primos até 25
        self.primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        # Sequência de Fibonacci até 25
        self.fibonacci = {1, 2, 3, 5, 8, 13, 21}
        # Cache para concurso anterior (para cálculo de repetidos)
        self.concurso_anterior = None

    def calcular_campos_estatisticos(self, concurso: int, numeros: list, data_sorteio: str) -> dict:
        """
        Calcula todos os campos estatísticos para um concurso
        
        Args:
            concurso: Número do concurso
            numeros: Lista com os 15 números sorteados
            data_sorteio: Data do sorteio
            
        Returns:
            dict: Dicionário com todos os campos calculados
        """
        campos = {}
        
        # ===== CAMPOS BÁSICOS =====
        campos['Concurso'] = concurso
        campos['Data_Sorteio'] = data_sorteio
        for i, num in enumerate(numeros, 1):
            campos[f'N{i}'] = num
        
        # ===== CÁLCULOS ESTATÍSTICOS =====
        
        # 1. QtdePrimos: Quantidade de números primos
        campos['QtdePrimos'] = sum(1 for n in numeros if n in self.primos)
        
        # 2. QtdeFibonacci: Quantidade de números da sequência de Fibonacci
        campos['QtdeFibonacci'] = sum(1 for n in numeros if n in self.fibonacci)
        
        # 3. QtdeImpares: Quantidade de números ímpares
        campos['QtdeImpares'] = sum(1 for n in numeros if n % 2 == 1)
        
        # 4. SomaTotal: Soma de todos os números
        campos['SomaTotal'] = sum(numeros)
        
        # 5. Quintis (distribuição por faixas)
        campos['Quintil1'] = sum(1 for n in numeros if 1 <= n <= 5)    # 1-5
        campos['Quintil2'] = sum(1 for n in numeros if 6 <= n <= 10)   # 6-10
        campos['Quintil3'] = sum(1 for n in numeros if 11 <= n <= 15)  # 11-15
        campos['Quintil4'] = sum(1 for n in numeros if 16 <= n <= 20)  # 16-20
        campos['Quintil5'] = sum(1 for n in numeros if 21 <= n <= 25)  # 21-25
        
        # 6. QtdeGaps: Quantidade de "buracos" na sequência
        numeros_ordenados = sorted(numeros)
        gaps = 0
        for i in range(len(numeros_ordenados) - 1):
            if numeros_ordenados[i+1] - numeros_ordenados[i] > 1:
                gaps += 1
        campos['QtdeGaps'] = gaps
        
        # 7. SEQ: Análise de sequências consecutivas
        consecutivos = 0
        for i in range(len(numeros_ordenados) - 1):
            if numeros_ordenados[i+1] - numeros_ordenados[i] == 1:
                consecutivos += 1
        campos['SEQ'] = float(consecutivos)
        
        # 8. DistanciaExtremos: Distância entre maior e menor número
        campos['DistanciaExtremos'] = max(numeros) - min(numeros)
        
        # 9. ParesSequencia: Números pares em sequência
        pares_sequencia = 0
        pares = [n for n in numeros_ordenados if n % 2 == 0]
        for i in range(len(pares) - 1):
            if pares[i+1] - pares[i] == 2:  # Pares consecutivos
                pares_sequencia += 1
        campos['ParesSequencia'] = pares_sequencia
        
        # 10. QtdeMultiplos3: Quantidade de múltiplos de 3
        campos['QtdeMultiplos3'] = sum(1 for n in numeros if n % 3 == 0)
        
        # 11. ParesSaltados: Análise de pares saltados
        pares_saltados = 0
        pares = [n for n in numeros_ordenados if n % 2 == 0]
        for i in range(len(pares) - 1):
            if pares[i+1] - pares[i] == 4:  # Pares com um par no meio
                pares_saltados += 1
        campos['ParesSaltados'] = pares_saltados
        
        # 12. Faixas de distribuição
        campos['Faixa_Baixa'] = sum(1 for n in numeros if 1 <= n <= 8)   # 1-8
        campos['Faixa_Media'] = sum(1 for n in numeros if 9 <= n <= 17)  # 9-17
        campos['Faixa_Alta'] = sum(1 for n in numeros if 18 <= n <= 25)  # 18-25
        
        # 13. QtdeRepetidos e RepetidosMesmaPosicao (requer concurso anterior)
        if concurso == 1:
            # Primeiro concurso não tem repetidos
            campos['QtdeRepetidos'] = 0
            campos['RepetidosMesmaPosicao'] = 0
        else:
            # Busca concurso anterior
            concurso_ant = self.obter_concurso_anterior(concurso)
            if concurso_ant:
                # Calcula repetidos
                repetidos = len(set(numeros) & set(concurso_ant['numeros']))
                campos['QtdeRepetidos'] = repetidos
                
                # Calcula repetidos na mesma posição
                mesma_posicao = 0
                for i in range(15):
                    if numeros[i] == concurso_ant['numeros'][i]:
                        mesma_posicao += 1
                campos['RepetidosMesmaPosicao'] = mesma_posicao
            else:
                campos['QtdeRepetidos'] = 0
                campos['RepetidosMesmaPosicao'] = 0
        
        # 14. Acumulou (placeholder - seria obtido da API se disponível)
        campos['Acumulou'] = False  # Assumindo que não acumulou por padrão
        
        return campos

    def obter_concurso_anterior(self, concurso: int) -> dict:
        """
        Obtém dados do concurso anterior para cálculo de repetidos
        
        Args:
            concurso: Número do concurso atual
            
        Returns:
            dict: Dados do concurso anterior ou None
        """
        try:
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT
                WHERE Concurso = ?
                """
                
                cursor.execute(query, (concurso - 1,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'numeros': list(row)
                    }
                
                return None
                
        except Exception as e:
            print(f"⚠️ Erro ao buscar concurso anterior {concurso-1}: {e}")
            return None
        self.max_retries = 3
        self.retry_delay = 5
        
    def _api_request_with_retry(self, concurso: int) -> dict:
        """
        Faz requisição à API com retry automático
        
        Args:
            concurso (int): Número do concurso
            
        Returns:
            dict: Dados do concurso ou None se erro
        """
        url = f"{self.api_url}{concurso}"
        
        for attempt in range(self.max_retries):
            try:
                print(f"🌐 Buscando concurso {concurso} (tentativa {attempt + 1})")
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Concurso {concurso} obtido com sucesso")
                    return data
                    
                elif response.status_code in [502, 503, 504]:
                    print(f"⚠️ Erro temporário na API: {response.status_code}")
                    if attempt < self.max_retries - 1:
                        print(f"🔄 Tentando novamente em {self.retry_delay} segundos...")
                        time.sleep(self.retry_delay)
                    continue
                    
                else:
                    print(f"❌ Erro na API: {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão: {e}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Tentando novamente em {self.retry_delay} segundos...")
                    time.sleep(self.retry_delay)
                    
        print(f"❌ Falha ao obter concurso {concurso} após {self.max_retries} tentativas")
        return None
    
    def _calcular_campos_apoio(self, numeros: list) -> dict:
        """
        Calcula campos de apoio derivados
        
        Args:
            numeros (list): Lista dos 15 números sorteados
            
        Returns:
            dict: Campos calculados
        """
        # Análise básica dos números
        numeros_ordenados = sorted(numeros)
        
        # Contagem por faixas
        baixos = len([n for n in numeros if n <= 12])  # 1-12
        altos = len([n for n in numeros if n >= 13])    # 13-25
        
        # Análise de paridade
        pares = len([n for n in numeros if n % 2 == 0])
        impares = len([n for n in numeros if n % 2 == 1])
        
        # Sequências consecutivas
        consecutivos = 0
        for i in range(len(numeros_ordenados) - 1):
            if numeros_ordenados[i + 1] - numeros_ordenados[i] == 1:
                consecutivos += 1
        
        # Soma total
        soma_total = sum(numeros)
        
        return {
            'baixos': baixos,
            'altos': altos,
            'pares': pares,
            'impares': impares,
            'consecutivos': consecutivos,
            'soma_total': soma_total,
            'maior_numero': max(numeros),
            'menor_numero': min(numeros),
            'amplitude': max(numeros) - min(numeros)
        }
    
    def atualizar_concurso_individual(self, concurso: int) -> bool:
        """
        Atualiza um concurso específico com TODOS os campos calculados
        
        Args:
            concurso (int): Número do concurso
            
        Returns:
            bool: True se atualizado com sucesso
        """
        print(f"\n📊 Atualizando concurso {concurso}...")
        
        # Busca dados na API
        data = self._api_request_with_retry(concurso)
        if not data:
            return False
        
        try:
            # Extrai números sorteados
            numeros = [int(n) for n in data.get('listaDezenas', [])]
            if len(numeros) != 15:
                print(f"❌ Dados inválidos: {len(numeros)} números encontrados")
                return False
            
            # Dados básicos
            data_sorteio = data.get('dataApuracao', '')
            
            # Calcula TODOS os campos estatísticos
            campos = self.calcular_campos_estatisticos(concurso, numeros, data_sorteio)
            
            # SQL de UPDATE completo
            sql_update = """
            UPDATE Resultados_INT SET 
                Data_Sorteio = ?, N1 = ?, N2 = ?, N3 = ?, N4 = ?, N5 = ?,
                N6 = ?, N7 = ?, N8 = ?, N9 = ?, N10 = ?, N11 = ?, N12 = ?, N13 = ?, N14 = ?, N15 = ?,
                QtdePrimos = ?, QtdeFibonacci = ?, QtdeImpares = ?, SomaTotal = ?,
                Quintil1 = ?, Quintil2 = ?, Quintil3 = ?, Quintil4 = ?, Quintil5 = ?,
                QtdeGaps = ?, QtdeRepetidos = ?, SEQ = ?, DistanciaExtremos = ?, ParesSequencia = ?,
                QtdeMultiplos3 = ?, ParesSaltados = ?, Faixa_Baixa = ?, Faixa_Media = ?, Faixa_Alta = ?,
                RepetidosMesmaPosicao = ?, Acumulou = ?
            WHERE Concurso = ?
            """
            
            params_update = (
                campos['Data_Sorteio'], campos['N1'], campos['N2'], campos['N3'], campos['N4'], campos['N5'],
                campos['N6'], campos['N7'], campos['N8'], campos['N9'], campos['N10'], campos['N11'], 
                campos['N12'], campos['N13'], campos['N14'], campos['N15'],
                campos['QtdePrimos'], campos['QtdeFibonacci'], campos['QtdeImpares'], campos['SomaTotal'],
                campos['Quintil1'], campos['Quintil2'], campos['Quintil3'], campos['Quintil4'], campos['Quintil5'],
                campos['QtdeGaps'], campos['QtdeRepetidos'], campos['SEQ'], campos['DistanciaExtremos'], 
                campos['ParesSequencia'], campos['QtdeMultiplos3'], campos['ParesSaltados'],
                campos['Faixa_Baixa'], campos['Faixa_Media'], campos['Faixa_Alta'],
                campos['RepetidosMesmaPosicao'], campos['Acumulou'], campos['Concurso']
            )
            
            # SQL de INSERT completo
            sql_insert = """
            INSERT INTO Resultados_INT (
                Concurso, Data_Sorteio, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
                QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
                Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
                QtdeGaps, QtdeRepetidos, SEQ, DistanciaExtremos, ParesSequencia,
                QtdeMultiplos3, ParesSaltados, Faixa_Baixa, Faixa_Media, Faixa_Alta,
                RepetidosMesmaPosicao, Acumulou
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """
            
            params_insert = (
                campos['Concurso'], campos['Data_Sorteio'], campos['N1'], campos['N2'], campos['N3'], 
                campos['N4'], campos['N5'], campos['N6'], campos['N7'], campos['N8'], campos['N9'], 
                campos['N10'], campos['N11'], campos['N12'], campos['N13'], campos['N14'], campos['N15'],
                campos['QtdePrimos'], campos['QtdeFibonacci'], campos['QtdeImpares'], campos['SomaTotal'],
                campos['Quintil1'], campos['Quintil2'], campos['Quintil3'], campos['Quintil4'], campos['Quintil5'],
                campos['QtdeGaps'], campos['QtdeRepetidos'], campos['SEQ'], campos['DistanciaExtremos'], 
                campos['ParesSequencia'], campos['QtdeMultiplos3'], campos['ParesSaltados'],
                campos['Faixa_Baixa'], campos['Faixa_Media'], campos['Faixa_Alta'],
                campos['RepetidosMesmaPosicao'], campos['Acumulou']
            )
            
            # Executa UPDATE primeiro, se não afetar faz INSERT
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                rows_affected = cursor.execute(sql_update, params_update).rowcount
                
                if rows_affected == 0:
                    cursor.execute(sql_insert, params_insert)
                
                conn.commit()
                
            print(f"✅ Concurso {concurso} atualizado com TODOS os campos calculados")
            return True
                    
        except Exception as e:
            print(f"❌ Erro ao processar concurso {concurso}: {e}")
            return False

    def _garantir_colunas_acertos(self, cursor, conn) -> bool:
        """
        Garante que as colunas de acertos existam na tabela COMBINACOES_LOTOFACIL20_COMPLETO.
        Cria as colunas se não existirem.
        
        Args:
            cursor: Cursor da conexão
            conn: Conexão com o banco
            
        Returns:
            bool: True se verificou/criou com sucesso
        """
        try:
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
            """)
            
            if cursor.fetchone()[0] == 0:
                return True  # Tabela não existe, não precisa criar colunas
            
            # Colunas necessárias
            colunas_necessarias = [
                ('Acertos_15', 'INT DEFAULT 0 NOT NULL'),
                ('Acertos_14', 'INT DEFAULT 0 NOT NULL'),
                ('Acertos_13', 'INT DEFAULT 0 NOT NULL'),
                ('Acertos_12', 'INT DEFAULT 0 NOT NULL'),
                ('Acertos_11', 'INT DEFAULT 0 NOT NULL'),
            ]
            
            for coluna_nome, coluna_tipo in colunas_necessarias:
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
                    AND COLUMN_NAME = ?
                """, (coluna_nome,))
                
                if cursor.fetchone()[0] == 0:
                    # Coluna não existe, criar
                    cursor.execute(f"""
                        ALTER TABLE COMBINACOES_LOTOFACIL20_COMPLETO 
                        ADD {coluna_nome} {coluna_tipo}
                    """)
                    conn.commit()
                    print(f"   ✅ Coluna {coluna_nome} criada!")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao garantir colunas de acertos: {e}")
            return False

    def executar_procedures_pos_atualizacao(self, ultimo_concurso: int) -> bool:
        """
        Executa procedures necessárias após atualização de concursos
        
        Args:
            ultimo_concurso: Número do último concurso atualizado
            
        Returns:
            bool: True se executou com sucesso
        """
        try:
            print(f"\n🔄 EXECUTANDO PROCEDURES PÓS-ATUALIZAÇÃO...")
            print(f"📊 Último concurso: {ultimo_concurso}")
            
            with db_config.get_connection() as conn:
                cursor = conn.cursor()
                
                # 0. GARANTIR COLUNAS DE ACERTOS NA TABELA DE 20 NÚMEROS
                print("🔄 Verificando/Criando colunas de acertos na COMBINACOES_LOTOFACIL20_COMPLETO...")
                try:
                    self._garantir_colunas_acertos(cursor, conn)
                    print("✅ Colunas de acertos verificadas/criadas")
                except Exception as e:
                    print(f"⚠️ Aviso ao verificar colunas de acertos: {e}")
                
                # 1. PROC_ATUALIZAR_COMBIN_10
                print("🔄 Executando PROC_ATUALIZAR_COMBIN_10...")
                try:
                    cursor.execute("EXEC PROC_ATUALIZAR_COMBIN_10")
                    conn.commit()
                    print("✅ PROC_ATUALIZAR_COMBIN_10 executada com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro na PROC_ATUALIZAR_COMBIN_10: {e}")
                
                # 2. AtualizaNumerosCiclos
                print("🔄 Executando AtualizaNumerosCiclos...")
                try:
                    cursor.execute("EXEC AtualizaNumerosCiclos")
                    conn.commit()
                    print("✅ AtualizaNumerosCiclos executada com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro na AtualizaNumerosCiclos: {e}")
                
                # 3. PROC_ATUALIZAR_QUINA
                print("🔄 Executando PROC_ATUALIZAR_QUINA...")
                try:
                    cursor.execute("EXEC PROC_ATUALIZAR_QUINA")
                    conn.commit()
                    print("✅ PROC_ATUALIZAR_QUINA executada com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro na PROC_ATUALIZAR_QUINA: {e}")
                
                # 4. Atualizar campos QtdeRepetidos e RepetidosMesmaPosicao na COMBINACOES_LOTOFACIL
                print(f"🔄 Atualizando campos de repetidos na COMBINACOES_LOTOFACIL...")
                try:
                    self.atualizar_campos_repetidos_combinacoes(ultimo_concurso, cursor, conn)
                    print("✅ Campos de repetidos atualizados na COMBINACOES_LOTOFACIL")
                except Exception as e:
                    print(f"⚠️ Erro ao atualizar campos repetidos: {e}")
                
                # 5. Executar procedures de comparação com último concurso
                print(f"🔄 Executando SP_AtualizarCamposComparacao...")
                try:
                    cursor.execute("EXEC SP_AtualizarCamposComparacao @ConcursoNovo = ?", (ultimo_concurso,))
                    conn.commit()
                    print("✅ Campos de comparação atualizados na RESULTADOS_INT")
                except Exception as e:
                    print(f"⚠️ Erro ao executar SP_AtualizarCamposComparacao: {e}")
                
                print(f"🔄 Executando SP_AtualizarCombinacoesComparacao...")
                try:
                    cursor.execute("EXEC SP_AtualizarCombinacoesComparacao @ConcursoReferencia = ?", (ultimo_concurso,))
                    conn.commit()
                    print("✅ Comparações atualizadas na COMBINACOES_LOTOFACIL")
                except Exception as e:
                    print(f"⚠️ Erro ao executar SP_AtualizarCombinacoesComparacao: {e}")
                
            print("✅ Todas as procedures pós-atualização executadas")
            return True
            
        except Exception as e:
            print(f"❌ Erro durante execução das procedures: {e}")
            return False

    def atualizar_campos_repetidos_combinacoes(self, ultimo_concurso: int, cursor, conn) -> bool:
        """
        Atualiza os campos QtdeRepetidos e RepetidosMesmaPosicao na tabela COMBINACOES_LOTOFACIL
        
        Args:
            ultimo_concurso: Número do último concurso atualizado
            cursor: Cursor da conexão
            conn: Conexão com o banco
            
        Returns:
            bool: True se atualizou com sucesso
        """
        try:
            # Busca números do último concurso
            cursor.execute("""
                SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT 
                WHERE Concurso = ?
            """, (ultimo_concurso,))
            
            resultado = cursor.fetchone()
            if not resultado:
                print(f"❌ Concurso {ultimo_concurso} não encontrado")
                return False
            
            numeros_ultimo_concurso = list(resultado)
            print(f"📊 Números do concurso {ultimo_concurso}: {','.join(map(str, sorted(numeros_ultimo_concurso)))}")
            
            # Busca números do concurso anterior (se existir)
            if ultimo_concurso > 1:
                cursor.execute("""
                    SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                    FROM Resultados_INT 
                    WHERE Concurso = ?
                """, (ultimo_concurso - 1,))
                
                resultado_anterior = cursor.fetchone()
                if resultado_anterior:
                    numeros_concurso_anterior = list(resultado_anterior)
                    
                    # Calcula repetidos do último concurso em relação ao anterior
                    qtde_repetidos = len(set(numeros_ultimo_concurso) & set(numeros_concurso_anterior))
                    
                    # Calcula repetidos na mesma posição
                    repetidos_mesma_posicao = 0
                    for i in range(15):
                        if numeros_ultimo_concurso[i] == numeros_concurso_anterior[i]:
                            repetidos_mesma_posicao += 1
                    
                    print(f"📈 Calculado: {qtde_repetidos} repetidos, {repetidos_mesma_posicao} na mesma posição")
                else:
                    # Se não encontrou concurso anterior, usa valores zerados
                    qtde_repetidos = 0
                    repetidos_mesma_posicao = 0
            else:
                # Primeiro concurso, não tem repetidos
                qtde_repetidos = 0
                repetidos_mesma_posicao = 0
            
            # Atualiza todas as combinações na tabela COMBINACOES_LOTOFACIL
            print("🔄 Atualizando tabela COMBINACOES_LOTOFACIL...")
            
            # Para cada combinação, calcula quantos números repetem do último concurso
            cursor.execute("""
                UPDATE COMBINACOES_LOTOFACIL SET
                    QtdeRepetidos = (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS combinacao(numero)
                        WHERE numero IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ),
                    RepetidosMesmaPosicao = (
                        CASE WHEN N1 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N2 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N3 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N4 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N5 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N6 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N7 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N8 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N9 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N10 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N11 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N12 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N13 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N14 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N15 = ? THEN 1 ELSE 0 END
                    )
            """, (
                # Parâmetros para QtdeRepetidos (números do último concurso)
                *numeros_ultimo_concurso,
                # Parâmetros para RepetidosMesmaPosicao (números do último concurso, uma vez por posição)
                *numeros_ultimo_concurso
            ))
            
            rows_affected = cursor.rowcount
            conn.commit()
            
            print(f"✅ {rows_affected} combinações atualizadas na COMBINACOES_LOTOFACIL")
            print(f"📊 Referência: Concurso {ultimo_concurso}")
            
            # =====================================================================
            # 🆕 INTEGRAÇÃO: ATUALIZAR TABELA DE 20 NÚMEROS
            # =====================================================================
            try:
                # Verificar se tabela COMBINACOES_LOTOFACIL20_COMPLETO existe
                cursor.execute("""
                    SELECT COUNT_BIG(*) as count FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
                """)
                
                tabela_20_existe = cursor.fetchone()[0] > 0
                
                if tabela_20_existe:
                    print("🔄 Atualizando tabela COMBINACOES_LOTOFACIL20_COMPLETO...")
                    
                    # Verificar se colunas de acertos existem (inclui 11, 12, 13, 14 e 15)
                    cursor.execute("""
                        SELECT COUNT_BIG(*) as count
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
                        AND COLUMN_NAME IN ('Acertos_15', 'Acertos_14', 'Acertos_13', 'Acertos_12', 'Acertos_11')
                    """)
                    
                    qtd_colunas_acertos = cursor.fetchone()[0]
                    colunas_acertos_existem = qtd_colunas_acertos >= 2  # Mínimo 14 e 15
                    colunas_acertos_completas = qtd_colunas_acertos == 5  # Todas: 11, 12, 13, 14, 15
                    
                    # Atualizar campos repetidos e DataGeracao
                    cursor.execute("""
                        UPDATE COMBINACOES_LOTOFACIL20_COMPLETO SET
                            QtdeRepetidos = (
                                SELECT COUNT_BIG(*)
                                FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                             (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS combinacao(numero)
                                WHERE numero IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ),
                            RepetidosMesmaPosicao = (
                                CASE WHEN N1 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N2 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N3 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N4 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N5 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N6 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N7 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N8 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N9 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N10 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N11 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N12 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N13 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N14 = ? THEN 1 ELSE 0 END +
                                CASE WHEN N15 = ? THEN 1 ELSE 0 END
                            ),
                            DataGeracao = CONVERT(VARCHAR(19), GETDATE(), 120),
                            Processado = 'S'
                    """, (
                        *numeros_ultimo_concurso,  # QtdeRepetidos
                        *numeros_ultimo_concurso   # RepetidosMesmaPosicao
                    ))
                    
                    rows_affected_20 = cursor.rowcount
                    conn.commit()
                    
                    print(f"✅ {rows_affected_20} combinações atualizadas na COMBINACOES_LOTOFACIL20_COMPLETO (repetidos + DataGeracao)")
                    
                    # Atualizar acertos incrementais se as colunas existem
                    if colunas_acertos_existem:
                        # Acertos 15
                        cursor.execute(f"""
                            UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                            SET Acertos_15 = Acertos_15 + 1
                            WHERE (
                                SELECT COUNT_BIG(*)
                                FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                             (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                                WHERE numero IN ({','.join(['?'] * 15)})
                            ) = 15
                        """, numeros_ultimo_concurso)
                        
                        acertos_15_atualizados = cursor.rowcount
                        
                        # Acertos 14
                        cursor.execute(f"""
                            UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                            SET Acertos_14 = Acertos_14 + 1
                            WHERE (
                                SELECT COUNT_BIG(*)
                                FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                             (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                                WHERE numero IN ({','.join(['?'] * 15)})
                            ) = 14
                        """, numeros_ultimo_concurso)
                        
                        acertos_14_atualizados = cursor.rowcount
                        conn.commit()
                        
                        print(f"✅ Acertos incrementais: +{acertos_15_atualizados} (15 acertos), +{acertos_14_atualizados} (14 acertos)")
                        
                        # =====================================================================
                        # 🆕 ATUALIZAR ACERTOS 13, 12 E 11 (SE AS COLUNAS EXISTEM)
                        # =====================================================================
                        acertos_13_atualizados = 0
                        acertos_12_atualizados = 0
                        acertos_11_atualizados = 0
                        
                        if colunas_acertos_completas:
                            # Acertos 13
                            cursor.execute(f"""
                                UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                                SET Acertos_13 = Acertos_13 + 1
                                WHERE (
                                    SELECT COUNT_BIG(*)
                                    FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                                 (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                                    WHERE numero IN ({','.join(['?'] * 15)})
                                ) = 13
                            """, numeros_ultimo_concurso)
                            
                            acertos_13_atualizados = cursor.rowcount
                            
                            # Acertos 12
                            cursor.execute(f"""
                                UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                                SET Acertos_12 = Acertos_12 + 1
                                WHERE (
                                    SELECT COUNT_BIG(*)
                                    FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                                 (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                                    WHERE numero IN ({','.join(['?'] * 15)})
                                ) = 12
                            """, numeros_ultimo_concurso)
                            
                            acertos_12_atualizados = cursor.rowcount
                            
                            # Acertos 11
                            cursor.execute(f"""
                                UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                                SET Acertos_11 = Acertos_11 + 1
                                WHERE (
                                    SELECT COUNT_BIG(*)
                                    FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                                 (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                                    WHERE numero IN ({','.join(['?'] * 15)})
                                ) = 11
                            """, numeros_ultimo_concurso)
                            
                            acertos_11_atualizados = cursor.rowcount
                            conn.commit()
                            
                            print(f"✅ Acertos adicionais: +{acertos_13_atualizados} (13), +{acertos_12_atualizados} (12), +{acertos_11_atualizados} (11)")
                        
                        # Atualizar controle de processamento
                        cursor.execute("""
                            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'CONTROLE_PROCESSAMENTO_ACERTOS')
                            BEGIN
                                CREATE TABLE CONTROLE_PROCESSAMENTO_ACERTOS (
                                    ID INT IDENTITY(1,1) PRIMARY KEY,
                                    UltimoConcursoProcessado INT NOT NULL,
                                    DataProcessamento DATETIME DEFAULT GETDATE(),
                                    TipoProcessamento VARCHAR(20) NOT NULL
                                )
                            END
                        """)
                        
                        cursor.execute("""
                            INSERT INTO CONTROLE_PROCESSAMENTO_ACERTOS (UltimoConcursoProcessado, TipoProcessamento)
                            VALUES (?, 'INCREMENTAL')
                        """, (ultimo_concurso,))
                        
                        conn.commit()
                else:
                    print("⚠️ Tabela COMBINACOES_LOTOFACIL20_COMPLETO não encontrada - mantendo comportamento original")
                    
            except Exception as e:
                print(f"⚠️ Aviso na integração tabela 20 números: {e}")
                # Não falha a função principal
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar campos repetidos: {e}")
            return False
    
    def atualizar_range_concursos(self, inicio: int, fim: int) -> dict:
        """
        Atualiza um range de concursos
        
        Args:
            inicio (int): Concurso inicial
            fim (int): Concurso final
            
        Returns:
            dict: Estatísticas da atualização
        """
        print(f"\n🔄 Atualizando concursos {inicio} a {fim}...")
        
        sucessos = 0
        falhas = 0
        tempo_inicio = time.time()
        ultimo_concurso_sucesso = 0
        
        for concurso in range(inicio, fim + 1):
            if self.atualizar_concurso_individual(concurso):
                sucessos += 1
                ultimo_concurso_sucesso = concurso
            else:
                falhas += 1
            
            # Pausa entre requisições para não sobrecarregar a API
            time.sleep(1)
        
        tempo_total = time.time() - tempo_inicio
        
        stats = {
            'total_processados': fim - inicio + 1,
            'sucessos': sucessos,
            'falhas': falhas,
            'tempo_total': tempo_total,
            'tempo_medio': tempo_total / (fim - inicio + 1),
            'ultimo_concurso_atualizado': ultimo_concurso_sucesso
        }
        
        print(f"\n📊 RELATÓRIO DA ATUALIZAÇÃO:")
        print(f"   • Total processados: {stats['total_processados']}")
        print(f"   • Sucessos: {stats['sucessos']}")
        print(f"   • Falhas: {stats['falhas']}")
        print(f"   • Tempo total: {stats['tempo_total']:.2f}s")
        print(f"   • Tempo médio: {stats['tempo_medio']:.2f}s")
        
        # Executa procedures pós-atualização se houve sucessos
        if sucessos > 0 and ultimo_concurso_sucesso > 0:
            print(f"\n🔄 EXECUTANDO PROCEDURES PÓS-ATUALIZAÇÃO...")
            if self.executar_procedures_pos_atualizacao(ultimo_concurso_sucesso):
                stats['procedures_executadas'] = True
                print("✅ Procedures pós-atualização executadas com sucesso")
            else:
                stats['procedures_executadas'] = False
                print("⚠️ Erro na execução das procedures pós-atualização")
        else:
            stats['procedures_executadas'] = False
            print("⚠️ Nenhum concurso atualizado, procedures não executadas")
        print(f"   • Tempo médio por concurso: {stats['tempo_medio']:.2f}s")
        
        return stats
    
    def obter_ultimo_concurso_api(self) -> int:
        """
        Obtém o número do último concurso disponível na API
        
        Returns:
            int: Número do último concurso ou 0 se erro
        """
        try:
            # A API sem parâmetro retorna o último concurso
            response = requests.get(self.api_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                ultimo = data.get('numero', 0)
                print(f"🎯 Último concurso na API: {ultimo}")
                return ultimo
            else:
                print(f"❌ Erro ao obter último concurso: {response.status_code}")
                return 0
        except Exception as e:
            print(f"❌ Erro ao consultar último concurso: {e}")
            return 0
    
    def atualizar_completo(self) -> dict:
        """
        Atualização completa desde o último concurso na base até o mais recente
        
        Returns:
            dict: Estatísticas da atualização
        """
        print("\n🚀 INICIANDO ATUALIZAÇÃO COMPLETA...")
        
        # Busca último concurso na API
        ultimo_api = self.obter_ultimo_concurso_api()
        if ultimo_api == 0:
            return {'erro': 'Não foi possível obter último concurso da API'}
        
        # Busca último concurso na base
        query = "SELECT MAX(Concurso) FROM Resultados_INT"
        resultado = db_config.execute_query(query)
        
        if resultado and resultado[0][0]:
            ultimo_base = resultado[0][0]
            print(f"📊 Último concurso na base: {ultimo_base}")
        else:
            ultimo_base = 0
            print("📊 Base vazia, iniciando do concurso 1")
        
        # Define range para atualização
        inicio = ultimo_base + 1 if ultimo_base > 0 else 1
        
        if inicio > ultimo_api:
            print("✅ Base já está atualizada!")
            return {'status': 'atualizada', 'ultimo_concurso': ultimo_base}
        
        # Executa atualização
        return self.atualizar_range_concursos(inicio, ultimo_api)

if __name__ == "__main__":
    print("🌐 SISTEMA LOTOFÁCIL - MENU PRINCIPAL")
    print("=" * 50)
    
    menu = MenuLotofacil()
    
    # Teste de conexão
    if not db_config.test_connection():
        print("❌ Erro na conexão com o banco. Verifique as configurações.")
        exit(1)
    
    # Menu principal
    while True:
        print("\n🎯 OPÇÕES DISPONÍVEIS:")
        print("1 - Atualizar base de dados (último concurso da API)")
        print("2 - Atualizar concurso específico")
        print("3 - Atualização completa (desde o último na base)")
        print("4 - Gerar combinações filtradas (arquivo TXT)")
        print("5 - Gerador AVANÇADO (posicionais + palpites)")
        print("6 - 🧠 INTELIGÊNCIA PREDITIVA (análise multi-dimensional)")
        print("7 - 🔮 PREVISÃO ADAPTATIVA (machine learning temporal)")
        print("8 - 🎯 OTIMIZAÇÃO PROBABILÍSTICA (padrões estatísticos)")
        print("9 - 🚀 SISTEMA INTEGRADO AVANÇADO (todos os sistemas)")
        print("10 - 🖥️ SELETOR DE COMBINAÇÕES GUI (aplicativo desktop)")
        print("11 - 🎯 GERADOR SEQUENCIAL PROBABILÍSTICO (P(Ni | N1...Ni-1))")
        print("12 - 🔄 GERADOR INTELIGENTE CICLOS (60% pendentes + 60% quentes)")
        print("13 - 📊 ANÁLISE ACADÊMICA CICLOS (correlações e padrões preditivos)")
        print("14 - 🧠 GERADOR APRENDIZADO ACADÊMICO (baseado em insights científicos)")
        print("15 - 🎯 GERADOR MULTI-NÚMEROS (15-20 números com metodologia acadêmica)")
        print("16 - Testar último concurso da API")
        print("0 - Sair")
        
        opcao = input("\nEscolha uma opção (0-16): ").strip()
        
        if opcao == "0":
            print("👋 Até logo!")
            break
        
        elif opcao == "1":
            ultimo = menu.obter_ultimo_concurso_api()
            if ultimo > 0:
                menu.atualizar_concurso_individual(ultimo)
            
        elif opcao == "2":
            try:
                concurso = int(input("Digite o número do concurso: "))
                menu.atualizar_concurso_individual(concurso)
            except ValueError:
                print("❌ Número inválido")
        
        elif opcao == "3":
            menu.atualizar_completo()
        
        elif opcao == "4":
            # Executa o gerador de combinações
            try:
                print("\n🎯 INICIANDO GERADOR DE COMBINAÇÕES...")
                import subprocess
                import sys
                
                # Executa o gerador de combinações como subprocess
                resultado = subprocess.run([
                    sys.executable, "gerador_combinacoes.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar gerador de combinações: {e}")
        
        elif opcao == "5":
            # Executa o gerador avançado
            try:
                print("\n🎯 INICIANDO GERADOR AVANÇADO...")
                import subprocess
                import sys
                
                # Executa o gerador avançado como subprocess
                resultado = subprocess.run([
                    sys.executable, "gerador_avancado.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar gerador avançado: {e}")
        
        elif opcao == "6":
            # Executa sistema de inteligência preditiva
            try:
                print("\n🧠 INICIANDO SISTEMA DE INTELIGÊNCIA PREDITIVA...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "sistema_inteligencia_preditiva.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar inteligência preditiva: {e}")
        
        elif opcao == "7":
            # Executa sistema de previsão adaptativa
            try:
                print("\n🔮 INICIANDO SISTEMA DE PREVISÃO ADAPTATIVA...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "sistema_previsao_adaptativa.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar previsão adaptativa: {e}")
        
        elif opcao == "8":
            # Executa sistema de otimização probabilística
            try:
                print("\n🎯 INICIANDO SISTEMA DE OTIMIZAÇÃO PROBABILÍSTICA...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "sistema_otimizacao_probabilistica.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar otimização probabilística: {e}")
        
        elif opcao == "9":
            # Executa sistema integrado avançado
            try:
                print("\n🚀 INICIANDO SISTEMA INTEGRADO AVANÇADO...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "sistema_integrado_avancado.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar sistema integrado: {e}")
        
        elif opcao == "10":
            # Executa seletor de combinações GUI
            try:
                print("\n🖥️ INICIANDO SELETOR DE COMBINAÇÕES GUI...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "seletor_combinacoes_gui.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar seletor GUI: {e}")
        
        elif opcao == "11":
            # Executa gerador sequencial probabilístico
            try:
                print("\n🎯 INICIANDO GERADOR SEQUENCIAL PROBABILÍSTICO...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "gerador_sequencial_probabilistico.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar gerador sequencial probabilístico: {e}")
        
        elif opcao == "12":
            # Executa gerador inteligente de ciclos ajustado
            try:
                print("\n🔄 INICIANDO GERADOR INTELIGENTE CICLOS...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "gerador_inteligente_ciclos_ajustado.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar gerador inteligente ciclos: {e}")
        
        elif opcao == "13":
            # Executa análise acadêmica de ciclos
            try:
                print("\n📊 INICIANDO ANÁLISE ACADÊMICA DE CICLOS...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "analise_ciclos_academica.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar análise acadêmica: {e}")
        
        elif opcao == "14":
            # Executa gerador baseado em aprendizado acadêmico
            try:
                print("\n🧠 INICIANDO GERADOR BASEADO EM APRENDIZADO ACADÊMICO...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "gerador_aprendizado_academico.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar gerador acadêmico: {e}")
        
        elif opcao == "15":
            # Executa gerador acadêmico multi-números (15-20 números)
            try:
                print("\n🎯 INICIANDO GERADOR ACADÊMICO MULTI-NÚMEROS...")
                import subprocess
                import sys
                
                resultado = subprocess.run([
                    sys.executable, "gerador_aprendizado_multi_numeros.py"
                ], capture_output=False, text=True)
                
            except Exception as e:
                print(f"❌ Erro ao executar gerador multi-números: {e}")
        
        elif opcao == "16":
            ultimo = menu.obter_ultimo_concurso_api()
            print(f"🎯 Último concurso na API: {ultimo}")
        
        elif opcao == "0":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida")
