#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 GERADOR DINÂMICO DE FILTROS INTELIGENTES V2
=============================================
Inspirado no script SQL avançado do usuário, este sistema replica
a lógica de filtros multicamada, mas com seleção dinâmica baseada
em dados reais do último concurso e padrões históricos.

NOVA FUNCIONALIDADE: Salva toda a saída em arquivo TXT com
combinações formatadas no final.
"""

import os
import sys
import random
from typing import Dict, List, Tuple, Any
from datetime import datetime
from pathlib import Path
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

try:
    import database_config as db_config
    print("✅ Módulo database_config importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar database_config: {e}")
    sys.exit(1)

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
            'N3': [3, 4, 5, 6],
            'N4': [4, 5, 6, 7, 8],
            'N5': [5, 6, 7, 8, 9],
            'N6': [6, 7, 8, 9, 10, 11],
            'N7': [7, 8, 9, 10, 11, 12],
            'N8': [8, 9, 10, 11, 12, 13, 14],
            'N9': [9, 10, 11, 12, 13, 14, 15],
            'N10': [10, 11, 12, 13, 14, 15, 16],
            'N11': [11, 12, 13, 14, 15, 16, 17, 18],
            'N12': [12, 13, 14, 15, 16, 17, 18, 19],
            'N13': [13, 14, 15, 16, 17, 18, 19, 20, 21],
            'N14': [20, 21, 22, 23, 24],
            'N15': [23, 24, 25]
        }
        
    def get_db_connection(self):
        """Método auxiliar para obter conexão com o banco"""
        db = db_config.DatabaseConfig()
        return db.get_connection()
        
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
                    arquivo.write('COMBINAÇÕES PARA APOSTAS (UMA POR LINHA)\n')
                    arquivo.write('-'*80 + '\n\n')
                    
                    # Cada combinação em uma linha, números separados por vírgula
                    for combinacao in self.combinacoes_geradas:
                        numeros_formatados = ','.join(map(str, sorted(map(int, combinacao))))
                        arquivo.write(f"{numeros_formatados}\n")
            
            self.log_print(f"\n💾 ARQUIVO SALVO: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            self.log_print(f"❌ Erro ao salvar arquivo: {e}")
            return None
        
    def obter_ultimo_concurso(self):
        """Obtém dados do último concurso com metadados"""
        self.log_print("🔍 OBTENDO ÚLTIMO CONCURSO COM METADADOS...")
        
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
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                colunas = [desc[0] for desc in cursor.description]
                self.ultimo_concurso = dict(zip(colunas, resultado))
                self.log_print(f"✅ Último concurso: {self.ultimo_concurso['Concurso']}")
                cursor.close()
                conn.close()
                return True
            else:
                self.log_print("❌ Nenhum concurso encontrado")
                cursor.close()
                conn.close()
                return False
                
        except Exception as e:
            self.log_print(f"❌ Erro ao obter último concurso: {e}")
            return False
            
    def carregar_historico_concursos(self, limite=50):
        """Carrega histórico de concursos para análise de tendências"""
        self.log_print(f"📊 CARREGANDO {limite} CONCURSOS HISTÓRICOS...")
        
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
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                colunas = [desc[0] for desc in cursor.description]
                self.dados_historicos = [dict(zip(colunas, row)) for row in resultados]
                self.log_print(f"✅ {len(self.dados_historicos)} concursos carregados")
                cursor.close()
                conn.close()
                return True
            else:
                self.log_print("❌ Nenhum dado histórico encontrado")
                cursor.close()
                conn.close()
                return False
                
        except Exception as e:
            self.log_print(f"❌ Erro ao carregar histórico: {e}")
            return False
            
    def calcular_tendencias_metadados(self):
        """Calcula tendências dinâmicas baseadas no histórico"""
        self.log_print("🧠 CALCULANDO TENDÊNCIAS DOS METADADOS...")
        
        if not self.dados_historicos:
            self.log_print("❌ Sem dados históricos para análise")
            return False
            
        # Para cada campo de metadado, calcular faixa dinâmica
        for campo in self.campos_metadados:
            if campo in self.ultimo_concurso:
                valor_atual = self.ultimo_concurso[campo]
                
                # Coletar valores históricos
                valores_historicos = []
                for concurso in self.dados_historicos:
                    if campo in concurso and concurso[campo] is not None:
                        valores_historicos.append(concurso[campo])
                
                if valores_historicos:
                    # Estatísticas básicas
                    media = sum(valores_historicos) / len(valores_historicos)
                    valores_ordenados = sorted(valores_historicos)
                    mediana = valores_ordenados[len(valores_ordenados)//2]
                    
                    # Calcular tendência
                    if valor_atual > media + (media * 0.2):
                        tendencia = "BAIXA"
                        # Criar faixa focada em valores menores
                        faixa_base = [v for v in valores_historicos if v <= media]
                    elif valor_atual < media - (media * 0.2):
                        tendencia = "ALTA"
                        # Criar faixa focada em valores maiores
                        faixa_base = [v for v in valores_historicos if v >= media]
                    else:
                        tendencia = "ESTAVEL"
                        # Faixa equilibrada em torno da média
                        faixa_base = valores_historicos
                    
                    # Criar faixa dinâmica (valores únicos e limitados)
                    faixa_dinamica = sorted(list(set(faixa_base)))[-10:]  # Últimos 10 valores únicos
                    
                    self.tendencias_calculadas[campo] = {
                        'valor_atual': valor_atual,
                        'media': media,
                        'mediana': mediana,
                        'tendencia': tendencia,
                        'faixa_dinamica': faixa_dinamica
                    }
        
        self.log_print("✅ Tendências calculadas com sucesso!")
        return True
        
    def ajustar_ranges_posicionais(self):
        """Ajusta ranges posicionais com base na análise do último concurso"""
        self.log_print("🎯 AJUSTANDO RANGES POSICIONAIS...")
        
        # Extrair números do último sorteio
        numeros_ultimo = [self.ultimo_concurso[f'N{i}'] for i in range(1, 16)]
        
        # Detectar tendência geral dos números
        if self.ultimo_concurso['menor_que_ultimo'] >= 12:
            # Números devem subir
            ajuste = 1
            self.log_print("📈 Ajuste: números devem SUBIR")
        elif self.ultimo_concurso['maior_que_ultimo'] >= 12:
            # Números devem descer
            ajuste = -1
            self.log_print("📉 Ajuste: números devem DESCER")
        else:
            # Manter estável
            ajuste = 0
            self.log_print("📊 Ajuste: números devem MANTER")
        
        # Aplicar ajuste nos ranges (exemplo simplificado)
        if ajuste != 0:
            for pos in self.ranges_posicionais:
                range_atual = self.ranges_posicionais[pos]
                range_ajustado = [max(1, min(25, x + ajuste)) for x in range_atual]
                self.ranges_posicionais[pos] = sorted(list(set(range_ajustado)))
        
        self.log_print("✅ Ranges posicionais ajustados!")
        return True
        
    def gerar_lista_filtrada(self, lista_num):
        """Gera uma lista filtrada da tabela COMBINACOES_LOTOFACIL"""
        filtros = []
        
        # Filtro base: EXCLUIR QtdeRepetidos = 15 (para não repetir o resultado anterior)
        filtros.append("QtdeRepetidos != 15")
        
        # Excluir explicitamente o resultado do concurso anterior (3505)
        resultado_anterior = "3,4,5,6,8,11,12,13,16,17,18,22,23,24,25"
        filtros.append(f"CONCAT(N1,',',N2,',',N3,',',N4,',',N5,',',N6,',',N7,',',N8,',',N9,',',N10,',',N11,',',N12,',',N13,',',N14,',',N15) != '{resultado_anterior}'")
        
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
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                numeros = resultado[0].split(',')
                cursor.close()
                conn.close()
                return numeros
            else:
                cursor.close()
                conn.close()
                return self.gerar_fallback()
                
        except Exception as e:
            self.log_print(f"❌ Erro ao gerar Lista {lista_num}: {e}")
            return self.gerar_fallback()
            
    def gerar_fallback(self):
        """Gera lista fallback quando filtros são muito restritivos"""
        query = """
        SELECT TOP 1 CONCAT(N1,',',N2,',',N3,',',N4,',',N5,',',N6,',',N7,',',N8,',',N9,',',N10,',',N11,',',N12,',',N13,',',N14,',',N15) as numeros
        FROM COMBINACOES_LOTOFACIL
        WHERE QtdeRepetidos != 15 
        AND CONCAT(N1,',',N2,',',N3,',',N4,',',N5,',',N6,',',N7,',',N8,',',N9,',',N10,',',N11,',',N12,',',N13,',',N14,',',N15) != '3,4,5,6,8,11,12,13,16,17,18,22,23,24,25'
        ORDER BY NEWID()
        """
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                numeros = resultado[0].split(',')
                cursor.close()
                conn.close()
                return numeros
            else:
                cursor.close()
                conn.close()
                # Fallback final: gerar aleatoriamente
                return [str(i) for i in sorted(random.sample(range(1, 26), 15))]
                
        except Exception as e:
            self.log_print(f"❌ Erro no fallback: {e}")
            return [str(i) for i in sorted(random.sample(range(1, 26), 15))]
            
    def gerar_listas_dinamicas(self, num_listas=10):
        """Gera múltiplas listas com filtros dinâmicos"""
        self.log_print(f"🎲 GERANDO {num_listas} LISTAS FILTRADAS...")
        self.log_print("=" * 50)
        
        listas_geradas = []
        
        for i in range(1, num_listas + 1):
            self.log_print(f"🔧 GERANDO LISTA {i}...")
            
            lista = self.gerar_lista_filtrada(i)
            if lista:
                listas_geradas.append(lista)
                self.log_print(f"✅ Lista {i}: {lista}")
                # Adicionar às combinações para salvamento
                self.combinacoes_geradas.append(lista)
            else:
                self.log_print(f"⚠️ Lista {i}: Gerando fallback...")
                lista_fallback = self.gerar_fallback()
                listas_geradas.append(lista_fallback)
                self.log_print(f"✅ Lista {i} (fallback): {lista_fallback}")
                self.combinacoes_geradas.append(lista_fallback)
        
        return listas_geradas
        
    def aplicar_filtro_principal(self, listas):
        """Aplica filtro principal baseado nas intersecções das listas"""
        self.log_print("🔍 APLICANDO FILTRO PRINCIPAL COM INTERSECÇÕES...")
        self.log_print("=" * 60)
        
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
            filtros_principais.append("QtdeRepetidos != 15")
            
            # Excluir resultado do concurso anterior
            resultado_anterior = "3,4,5,6,8,11,12,13,16,17,18,22,23,24,25"
            filtros_principais.append(f"CONCAT(N1,',',N2,',',N3,',',N4,',',N5,',',N6,',',N7,',',N8,',',N9,',',N10,',',N11,',',N12,',',N13,',',N14,',',N15) != '{resultado_anterior}'")
            filtros_principais.append("QtdePrimos BETWEEN 3 AND 7")
            filtros_principais.append("QtdeImpares BETWEEN 5 AND 9")
        
        query = f"""
        SELECT TOP 20 *
        FROM VW_CombinLotofacil
        WHERE {' AND '.join(filtros_principais)}
        ORDER BY NEWID()
        """
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                colunas = [desc[0] for desc in cursor.description]
                combinacoes = []
                
                for row in resultados:
                    dados = dict(zip(colunas, row))
                    numeros = [dados[f'N{i}'] for i in range(1, 16)]
                    combinacoes.append({
                        'numeros': numeros,
                        'soma': dados.get('SomaTotal', 0),
                        'primos': dados.get('QtdePrimos', 0),
                        'repetidos': dados.get('QtdeRepetidos', 0)
                    })
                
                cursor.close()
                conn.close()
                return combinacoes
            else:
                self.log_print("⚠️ Nenhuma combinação encontrada com filtros completos")
                cursor.close()
                conn.close()
                return self.aplicar_filtro_simplificado()
                
        except Exception as e:
            self.log_print(f"❌ Erro no filtro principal: {e}")
            return self.aplicar_filtro_simplificado()
            
    def aplicar_filtro_simplificado(self):
        """Aplica filtro simplificado quando o principal falha"""
        self.log_print("🔧 APLICANDO FILTRO SIMPLIFICADO...")
        
        return []
        
    def exibir_relatorio_tendencias(self):
        """Exibe relatório detalhado das tendências calculadas"""
        self.log_print("\n📊 RELATÓRIO DE TENDÊNCIAS APLICADAS:")
        self.log_print("=" * 50)
        
        for campo, info in self.tendencias_calculadas.items():
            valor = info['valor_atual']
            tendencia = info['tendencia']
            faixa = info['faixa_dinamica'][:5]  # Primeiros 5 valores
            faixa_str = str(faixa) + "..." if len(info['faixa_dinamica']) > 5 else str(faixa)
            self.log_print(f"{campo}: {valor} → {tendencia} → {faixa_str}")
    
    def executar_geracao_completa(self):
        """Executa todo o processo de geração dinâmica"""
        self.log_print("🎯 GERADOR DINÂMICO DE FILTROS INTELIGENTES")
        self.log_print("Baseado no script SQL avançado com seleção automática de filtros")
        self.log_print("🚀 INICIANDO GERAÇÃO DINÂMICA DE FILTROS...")
        self.log_print("=" * 80)
        
        # Passo 1: Obter último concurso
        if not self.obter_ultimo_concurso():
            self.log_print("❌ Falha na obtenção do último concurso")
            return False
            
        # Passo 2: Carregar histórico
        if not self.carregar_historico_concursos():
            self.log_print("❌ Falha no carregamento do histórico")
            return False
            
        # Passo 3: Calcular tendências
        if not self.calcular_tendencias_metadados():
            self.log_print("❌ Falha no cálculo de tendências")
            return False
            
        # Passo 4: Ajustar ranges
        if not self.ajustar_ranges_posicionais():
            self.log_print("❌ Falha no ajuste de ranges")
            return False
            
        # Passo 5: Gerar listas dinâmicas
        listas = self.gerar_listas_dinamicas()
        
        # Passo 6: Aplicar filtro principal
        combinacoes = self.aplicar_filtro_principal(listas)
        
        # Passo 7: Exibir relatório de tendências
        self.exibir_relatorio_tendencias()
        
        # Passo 8: Mostrar análise do concurso
        self.log_print(f"\n🎯 CONCURSO ANALISADO: {self.ultimo_concurso['Concurso']}")
        self.log_print(f"📊 Estado comparação: ({self.ultimo_concurso['menor_que_ultimo']}, {self.ultimo_concurso['maior_que_ultimo']}, {self.ultimo_concurso['igual_ao_ultimo']})")
        
        # Passo 9: Exibir combinações se encontradas
        if combinacoes:
            self.log_print(f"\n🎲 COMBINAÇÕES ENCONTRADAS: {len(combinacoes)}")
            self.log_print("=" * 80)
            for i, combo in enumerate(combinacoes, 1):
                numeros_str = "[" + ", ".join(map(str, combo['numeros'])) + "]"
                self.log_print(f"Jogo {i:2d}: {numeros_str} | Soma: {combo['soma']} | Primos: {combo['primos']} | Rep: {combo['repetidos']}")
            self.log_print("=" * 80)
            
            # Adicionar combinações finais para salvamento
            for combo in combinacoes:
                self.combinacoes_geradas.append([str(n) for n in combo['numeros']])
        
        self.log_print("✅ GERAÇÃO COMPLETA FINALIZADA!")
        
        # Salvar arquivo automaticamente
        nome_arquivo = self.salvar_arquivo_resultado()
        
        return True

def main():
    """Função principal"""
    gerador = GeradorFiltrosDinamicos()
    
    while True:
        # Limpar buffers para nova execução
        gerador.log_buffer = []
        gerador.combinacoes_geradas = []
        
        if gerador.executar_geracao_completa():
            resposta = input("\n💾 Deseja executar novamente? (s/n): ").lower().strip()
            if resposta != 's':
                break
        else:
            print("❌ Falha na geração")
            break
    
    print("👋 Encerrando gerador dinâmico...")

if __name__ == "__main__":
    main()
