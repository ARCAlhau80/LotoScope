"""
📦 CARGA DE COMBINAÇÕES PARA BANCO DE DADOS
============================================

Sistema para:
1. Ler arquivo TXT de combinações
2. Calcular todos os campos estatísticos
3. Comparar com último resultado (campos dinâmicos)
4. Inserir na tabela Combinacoes_finais

Autor: LotoScope Team
Versão: 1.0
"""

import os
import sys
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# Configurar path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, 'utils'))

try:
    import pyodbc
    from database_config import DatabaseConfig
    db_config = DatabaseConfig(server="localhost", database="Lotofacil")
except ImportError as e:
    print(f"⚠️ Erro ao importar módulos: {e}")
    db_config = None


class CargaCombinacoesBanco:
    """
    Carrega combinações de arquivo TXT para tabela Combinacoes_finais no SQL Server.
    """
    
    # Constantes para cálculos
    PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    FIBONACCI = {1, 2, 3, 5, 8, 13, 21}
    MULTIPLOS_3 = {3, 6, 9, 12, 15, 18, 21, 24}
    
    # Faixas
    QUINTIL_1 = set(range(1, 6))    # 1-5
    QUINTIL_2 = set(range(6, 11))   # 6-10
    QUINTIL_3 = set(range(11, 16))  # 11-15
    QUINTIL_4 = set(range(16, 21))  # 16-20
    QUINTIL_5 = set(range(21, 26))  # 21-25
    
    FAIXA_BAIXA = set(range(1, 9))    # 1-8
    FAIXA_MEDIA = set(range(9, 18))   # 9-17
    FAIXA_ALTA = set(range(18, 26))   # 18-25
    
    def __init__(self):
        self.conn = None
        self.ultimo_resultado = None
        self.ultimo_concurso = None
        
    def conectar(self) -> bool:
        """Estabelece conexão com o banco de dados."""
        try:
            # Usar db_config se disponível, senão usar valores padrão
            if db_config:
                server = db_config.server
                database = db_config.database
            else:
                server = "localhost"
                database = "Lotofacil"
            
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
            )
            self.conn = pyodbc.connect(conn_str)
            print(f"✅ Conectado ao banco {database} em {server}")
            return True
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def criar_tabela_se_nao_existir(self) -> bool:
        """Cria a tabela Combinacoes_finais se não existir."""
        if not self.conn:
            return False
            
        sql_create = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Combinacoes_finais')
        BEGIN
            CREATE TABLE Combinacoes_finais (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                DataCarga DATETIME DEFAULT GETDATE(),
                ArquivoOrigem VARCHAR(255),
                
                -- Números da combinação
                N1 INT, N2 INT, N3 INT, N4 INT, N5 INT,
                N6 INT, N7 INT, N8 INT, N9 INT, N10 INT,
                N11 INT, N12 INT, N13 INT, N14 INT, N15 INT,
                
                -- Chave única para evitar duplicatas
                Combinacao VARCHAR(50) UNIQUE,
                
                -- Campos calculados fixos
                QtdePrimos INT,
                QtdeFibonacci INT,
                QtdeImpares INT,
                SomaTotal INT,
                Quintil1 INT,
                Quintil2 INT,
                Quintil3 INT,
                Quintil4 INT,
                Quintil5 INT,
                QtdeGaps INT,
                SEQ INT,
                DistanciaExtremos INT,
                ParesSequencia INT,
                QtdeMultiplos3 INT,
                ParesSaltados INT,
                Faixa_Baixa INT,
                Faixa_Media INT,
                Faixa_Alta INT,
                
                -- Campos comparativos com último resultado
                ConcursoReferencia INT,
                QtdeRepetidos INT,
                RepetidosMesmaPosicao INT,
                MenorQueUltimo INT,
                MaiorQueUltimo INT,
                IgualAoUltimo INT
            )
            
            PRINT 'Tabela Combinacoes_finais criada com sucesso!'
        END
        ELSE
        BEGIN
            PRINT 'Tabela Combinacoes_finais ja existe.'
        END
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_create)
            self.conn.commit()
            print("✅ Tabela Combinacoes_finais verificada/criada")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    def carregar_ultimo_resultado(self) -> bool:
        """Carrega o último resultado da tabela Resultados_INT."""
        if not self.conn:
            return False
            
        sql = """
        SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT
        ORDER BY Concurso DESC
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            
            if row:
                self.ultimo_concurso = row[0]
                self.ultimo_resultado = [row[i] for i in range(1, 16)]
                print(f"✅ Último resultado carregado: Concurso {self.ultimo_concurso}")
                print(f"   Números: {'-'.join(f'{n:02d}' for n in self.ultimo_resultado)}")
                return True
            else:
                print("⚠️ Nenhum resultado encontrado na tabela Resultados_INT")
                return False
        except Exception as e:
            print(f"❌ Erro ao carregar último resultado: {e}")
            return False
    
    def ler_arquivo_combinacoes(self, caminho: str) -> List[List[int]]:
        """Lê combinações de um arquivo TXT."""
        combinacoes = []
        
        if not os.path.exists(caminho):
            print(f"❌ Arquivo não encontrado: {caminho}")
            return combinacoes
        
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith('#'):
                        continue
                    
                    # Tentar diferentes separadores
                    numeros = []
                    if ',' in linha:
                        partes = linha.split(',')
                    elif '-' in linha:
                        partes = linha.split('-')
                    elif ';' in linha:
                        partes = linha.split(';')
                    else:
                        partes = linha.split()
                    
                    for p in partes:
                        try:
                            n = int(p.strip())
                            if 1 <= n <= 25:
                                numeros.append(n)
                        except ValueError:
                            continue
                    
                    if len(numeros) == 15:
                        numeros_ordenados = sorted(numeros)
                        combinacoes.append(numeros_ordenados)
            
            print(f"✅ Arquivo lido: {len(combinacoes):,} combinações encontradas")
            return combinacoes
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return []
    
    def calcular_campos(self, numeros: List[int]) -> Dict:
        """Calcula todos os campos estatísticos de uma combinação."""
        nums_set = set(numeros)
        
        # Campos fixos
        qtde_primos = len(nums_set & self.PRIMOS)
        qtde_fibonacci = len(nums_set & self.FIBONACCI)
        qtde_impares = sum(1 for n in numeros if n % 2 == 1)
        soma_total = sum(numeros)
        
        # Quintis
        quintil1 = len(nums_set & self.QUINTIL_1)
        quintil2 = len(nums_set & self.QUINTIL_2)
        quintil3 = len(nums_set & self.QUINTIL_3)
        quintil4 = len(nums_set & self.QUINTIL_4)
        quintil5 = len(nums_set & self.QUINTIL_5)
        
        # Faixas
        faixa_baixa = len(nums_set & self.FAIXA_BAIXA)
        faixa_media = len(nums_set & self.FAIXA_MEDIA)
        faixa_alta = len(nums_set & self.FAIXA_ALTA)
        
        # QtdeGaps - buracos entre números
        qtde_gaps = 0
        for i in range(1, len(numeros)):
            gap = numeros[i] - numeros[i-1] - 1
            if gap > 0:
                qtde_gaps += gap
        
        # SEQ - maior sequência consecutiva
        seq_max = 1
        seq_atual = 1
        for i in range(1, len(numeros)):
            if numeros[i] == numeros[i-1] + 1:
                seq_atual += 1
                seq_max = max(seq_max, seq_atual)
            else:
                seq_atual = 1
        
        # Distância extremos
        distancia_extremos = numeros[-1] - numeros[0]
        
        # Pares em sequência (números consecutivos)
        pares_sequencia = sum(1 for i in range(1, len(numeros)) if numeros[i] == numeros[i-1] + 1)
        
        # Múltiplos de 3
        qtde_multiplos3 = len(nums_set & self.MULTIPLOS_3)
        
        # Pares saltados (diferença de 2, ex: 3-5, 7-9)
        pares_saltados = sum(1 for i in range(1, len(numeros)) if numeros[i] == numeros[i-1] + 2)
        
        # Campos comparativos com último resultado
        qtde_repetidos = 0
        repetidos_mesma_posicao = 0
        menor_que_ultimo = 0
        maior_que_ultimo = 0
        igual_ao_ultimo = 0
        
        if self.ultimo_resultado:
            ultimo_set = set(self.ultimo_resultado)
            qtde_repetidos = len(nums_set & ultimo_set)
            
            for i in range(15):
                if numeros[i] == self.ultimo_resultado[i]:
                    repetidos_mesma_posicao += 1
                    igual_ao_ultimo += 1
                elif numeros[i] < self.ultimo_resultado[i]:
                    menor_que_ultimo += 1
                else:
                    maior_que_ultimo += 1
        
        return {
            'QtdePrimos': qtde_primos,
            'QtdeFibonacci': qtde_fibonacci,
            'QtdeImpares': qtde_impares,
            'SomaTotal': soma_total,
            'Quintil1': quintil1,
            'Quintil2': quintil2,
            'Quintil3': quintil3,
            'Quintil4': quintil4,
            'Quintil5': quintil5,
            'QtdeGaps': qtde_gaps,
            'SEQ': seq_max,
            'DistanciaExtremos': distancia_extremos,
            'ParesSequencia': pares_sequencia,
            'QtdeMultiplos3': qtde_multiplos3,
            'ParesSaltados': pares_saltados,
            'Faixa_Baixa': faixa_baixa,
            'Faixa_Media': faixa_media,
            'Faixa_Alta': faixa_alta,
            'QtdeRepetidos': qtde_repetidos,
            'RepetidosMesmaPosicao': repetidos_mesma_posicao,
            'MenorQueUltimo': menor_que_ultimo,
            'MaiorQueUltimo': maior_que_ultimo,
            'IgualAoUltimo': igual_ao_ultimo
        }
    
    def inserir_combinacoes(self, combinacoes: List[List[int]], arquivo_origem: str) -> Tuple[int, int]:
        """
        Insere combinações na tabela Combinacoes_finais.
        Retorna: (inseridos, ignorados_duplicados)
        """
        if not self.conn:
            return 0, 0
        
        sql_insert = """
        INSERT INTO Combinacoes_finais (
            ArquivoOrigem,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15,
            Combinacao,
            QtdePrimos, QtdeFibonacci, QtdeImpares, SomaTotal,
            Quintil1, Quintil2, Quintil3, Quintil4, Quintil5,
            QtdeGaps, SEQ, DistanciaExtremos, ParesSequencia,
            QtdeMultiplos3, ParesSaltados,
            Faixa_Baixa, Faixa_Media, Faixa_Alta,
            ConcursoReferencia, QtdeRepetidos, RepetidosMesmaPosicao,
            MenorQueUltimo, MaiorQueUltimo, IgualAoUltimo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.cursor()
        inseridos = 0
        ignorados = 0
        
        total = len(combinacoes)
        print(f"\n📥 Inserindo {total:,} combinações no banco...")
        print("=" * 60)
        
        # Variáveis para controle de tempo
        import time
        tempo_inicio = time.time()
        ultimo_update = tempo_inicio
        
        for i, numeros in enumerate(combinacoes):
            # Atualizar barra de progresso a cada 1% ou a cada 0.5 segundos
            tempo_atual = time.time()
            pct = ((i + 1) / total) * 100
            
            if (tempo_atual - ultimo_update >= 0.5) or (i + 1) == total or pct % 5 < (100 / total):
                ultimo_update = tempo_atual
                tempo_decorrido = tempo_atual - tempo_inicio
                
                # Calcular velocidade e tempo restante
                if i > 0:
                    vel = (i + 1) / tempo_decorrido  # registros por segundo
                    restante = (total - i - 1) / vel if vel > 0 else 0
                else:
                    vel = 0
                    restante = 0
                
                # Barra visual
                barra_tamanho = 30
                preenchido = int(barra_tamanho * pct / 100)
                barra = '█' * preenchido + '░' * (barra_tamanho - preenchido)
                
                # Formatar tempo restante
                if restante >= 60:
                    tempo_rest_str = f"{int(restante // 60)}m {int(restante % 60)}s"
                else:
                    tempo_rest_str = f"{int(restante)}s"
                
                # Status em uma linha (com \r para sobrescrever)
                status = f"\r   [{barra}] {pct:5.1f}% | {i+1:,}/{total:,} | {vel:.0f}/s | Restante: {tempo_rest_str}  "
                print(status, end='', flush=True)
            
            # Calcular campos
            campos = self.calcular_campos(numeros)
            
            # Chave única da combinação
            combinacao_str = '-'.join(f'{n:02d}' for n in numeros)
            
            try:
                cursor.execute(sql_insert, (
                    os.path.basename(arquivo_origem),
                    numeros[0], numeros[1], numeros[2], numeros[3], numeros[4],
                    numeros[5], numeros[6], numeros[7], numeros[8], numeros[9],
                    numeros[10], numeros[11], numeros[12], numeros[13], numeros[14],
                    combinacao_str,
                    campos['QtdePrimos'], campos['QtdeFibonacci'], campos['QtdeImpares'], campos['SomaTotal'],
                    campos['Quintil1'], campos['Quintil2'], campos['Quintil3'], campos['Quintil4'], campos['Quintil5'],
                    campos['QtdeGaps'], campos['SEQ'], campos['DistanciaExtremos'], campos['ParesSequencia'],
                    campos['QtdeMultiplos3'], campos['ParesSaltados'],
                    campos['Faixa_Baixa'], campos['Faixa_Media'], campos['Faixa_Alta'],
                    self.ultimo_concurso,
                    campos['QtdeRepetidos'], campos['RepetidosMesmaPosicao'],
                    campos['MenorQueUltimo'], campos['MaiorQueUltimo'], campos['IgualAoUltimo']
                ))
                inseridos += 1
            except pyodbc.IntegrityError:
                # Combinação já existe (duplicata)
                ignorados += 1
            except Exception as e:
                print(f"\n   ⚠️ Erro na combinação {combinacao_str}: {e}")
                ignorados += 1
        
        # Nova linha após a barra de progresso
        print()
        
        # Tempo total
        tempo_total = time.time() - tempo_inicio
        if tempo_total >= 60:
            tempo_str = f"{int(tempo_total // 60)}m {int(tempo_total % 60)}s"
        else:
            tempo_str = f"{tempo_total:.1f}s"
        
        print(f"\n   ✅ Processamento concluído em {tempo_str}")
        print(f"   📊 Velocidade média: {total / tempo_total:.0f} registros/segundo")
        
        self.conn.commit()
        return inseridos, ignorados
    
    def mostrar_estatisticas_tabela(self):
        """Mostra estatísticas da tabela Combinacoes_finais."""
        if not self.conn:
            return
        
        sql_stats = """
        SELECT 
            COUNT(*) as Total,
            MIN(DataCarga) as PrimeiraCarga,
            MAX(DataCarga) as UltimaCarga,
            COUNT(DISTINCT ArquivoOrigem) as QtdeArquivos,
            AVG(CAST(QtdeRepetidos as FLOAT)) as MediaRepetidos,
            AVG(CAST(SomaTotal as FLOAT)) as MediaSoma
        FROM Combinacoes_finais
        """
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_stats)
            row = cursor.fetchone()
            
            if row and row[0] > 0:
                print("\n📊 ESTATÍSTICAS DA TABELA Combinacoes_finais:")
                print("=" * 50)
                print(f"   📦 Total de combinações: {row[0]:,}")
                print(f"   📅 Primeira carga: {row[1]}")
                print(f"   📅 Última carga: {row[2]}")
                print(f"   📁 Arquivos carregados: {row[3]}")
                print(f"   🔄 Média de repetidos: {row[4]:.2f}")
                print(f"   ➕ Média da soma: {row[5]:.1f}")
            else:
                print("\n📊 Tabela Combinacoes_finais está vazia")
                
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
    
    def contar_registros_tabela(self) -> int:
        """Conta quantos registros existem na tabela."""
        if not self.conn:
            return 0
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Combinacoes_finais")
            row = cursor.fetchone()
            return row[0] if row else 0
        except:
            return 0
    
    def truncar_tabela(self) -> bool:
        """Limpa todos os registros da tabela Combinacoes_finais."""
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("TRUNCATE TABLE Combinacoes_finais")
            self.conn.commit()
            print("✅ Tabela Combinacoes_finais truncada com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao truncar tabela: {e}")
            return False
    
    def executar_carga(self, caminho_arquivo: str, truncar: bool = False) -> bool:
        """Executa o processo completo de carga."""
        print("\n" + "=" * 60)
        print("📦 CARGA DE COMBINAÇÕES PARA BANCO DE DADOS")
        print("=" * 60)
        
        # 1. Conectar
        if not self.conectar():
            return False
        
        # 2. Criar tabela se necessário
        if not self.criar_tabela_se_nao_existir():
            return False
        
        # 3. Verificar se tabela tem dados e perguntar sobre truncar
        registros_existentes = self.contar_registros_tabela()
        if registros_existentes > 0:
            print(f"\n⚠️ A tabela Combinacoes_finais já possui {registros_existentes:,} registros!")
            print()
            print("   Opções:")
            print("   1. TRUNCAR - Limpar tabela e carregar novos dados")
            print("   2. ADICIONAR - Manter dados existentes e adicionar novos")
            print("   3. CANCELAR - Abortar operação")
            print()
            opcao = input("   Escolha (1/2/3): ").strip()
            
            if opcao == "1":
                print("\n🗑️ Truncando tabela...")
                if not self.truncar_tabela():
                    return False
            elif opcao == "2":
                print("\n➕ Modo ADICIONAR - Novos registros serão inseridos")
                print("   (Duplicatas serão ignoradas automaticamente)")
            else:
                print("\n❌ Operação cancelada pelo usuário.")
                return False
        
        # 4. Carregar último resultado
        if not self.carregar_ultimo_resultado():
            print("⚠️ Continuando sem comparação com último resultado...")
        
        # 5. Ler arquivo
        combinacoes = self.ler_arquivo_combinacoes(caminho_arquivo)
        if not combinacoes:
            return False
        
        # 6. Inserir no banco
        inseridos, ignorados = self.inserir_combinacoes(combinacoes, caminho_arquivo)
        
        # 7. Mostrar resultado
        print("\n" + "=" * 60)
        print("✅ CARGA CONCLUÍDA!")
        print("=" * 60)
        print(f"   📥 Inseridos: {inseridos:,} combinações")
        print(f"   ⏭️ Ignorados (duplicados): {ignorados:,}")
        print(f"   📁 Arquivo: {os.path.basename(caminho_arquivo)}")
        
        # 8. Estatísticas
        self.mostrar_estatisticas_tabela()
        
        # 9. Fechar conexão
        if self.conn:
            self.conn.close()
        
        return True


def executar_menu_carga():
    """Menu interativo para carga de combinações."""
    print("\n" + "=" * 60)
    print("📦 CARGA DE COMBINAÇÕES PARA BANCO DE DADOS")
    print("=" * 60)
    print()
    print("📋 Este sistema irá:")
    print("   1. Ler arquivo TXT de combinações")
    print("   2. Calcular campos estatísticos (primos, fibonacci, soma, etc.)")
    print("   3. Comparar com último resultado (repetidos, posicionais)")
    print("   4. Inserir na tabela Combinacoes_finais")
    print()
    
    # Solicitar caminho do arquivo
    print("📂 Informe o caminho do arquivo de combinações:")
    print("   (Ex: combinacoes_hibrido_20260110_134724_TODAS_27920.txt)")
    print()
    
    caminho = input("   Caminho: ").strip()
    
    if not caminho:
        print("❌ Caminho não informado. Operação cancelada.")
        return
    
    # Se não for caminho absoluto, assume pasta atual
    if not os.path.isabs(caminho):
        # Tentar na pasta geradores primeiro
        pasta_geradores = os.path.dirname(os.path.abspath(__file__))
        caminho_geradores = os.path.join(pasta_geradores, caminho)
        
        if os.path.exists(caminho_geradores):
            caminho = caminho_geradores
        else:
            # Tentar na pasta lotofacil_lite
            pasta_lite = os.path.dirname(pasta_geradores)
            caminho_lite = os.path.join(pasta_lite, caminho)
            
            if os.path.exists(caminho_lite):
                caminho = caminho_lite
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return
    
    print(f"\n✅ Arquivo encontrado: {caminho}")
    
    # Confirmar
    confirma = input("\n⚠️ Deseja iniciar a carga? (s/n): ").strip().lower()
    if confirma != 's':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Executar carga
    carga = CargaCombinacoesBanco()
    carga.executar_carga(caminho)
    
    input("\n⏸️ Pressione ENTER para continuar...")


if __name__ == "__main__":
    executar_menu_carga()
