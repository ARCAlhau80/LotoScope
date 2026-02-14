#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════════════════════╗
║          ANALISADOR DE JANELAS TÉRMICAS - LOTOFÁCIL                            ║
║   Análise de padrões de temperatura dos números em janelas de 5 concursos      ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  Grupos Térmicos:                                                              ║
║    • Grupo 1 (MUITO QUENTES): 80-100% (4-5 aparições em 5 concursos)           ║
║    • Grupo 2 (QUENTES):       60-80%  (3 aparições em 5 concursos)             ║
║    • Grupo 3 (MORNOS):        20-60%  (1-2 aparições em 5 concursos)           ║
║    • Grupo 4 (FRIOS):         0-20%   (0 aparições em 5 concursos)             ║
╚════════════════════════════════════════════════════════════════════════════════╝

Data: Janeiro 2026
Autor: LotoScope AI Analysis
"""

import pyodbc
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import statistics
from datetime import datetime


class AnalisadorJanelasTermicas:
    """Analisa padrões térmicos de números em janelas de 5 concursos"""
    
    # Configurações dos grupos térmicos (baseado em frequência dentro da janela)
    GRUPOS = {
        1: {'nome': 'MUITO_QUENTES', 'min': 4, 'max': 5, 'cor': '🔴', 'desc': '80-100%'},
        2: {'nome': 'QUENTES',       'min': 3, 'max': 3, 'cor': '🟠', 'desc': '60-80%'},
        3: {'nome': 'MORNOS',        'min': 1, 'max': 2, 'cor': '🟡', 'desc': '20-60%'},
        4: {'nome': 'FRIOS',         'min': 0, 'max': 0, 'cor': '🔵', 'desc': '0-20%'}
    }
    
    def __init__(self, tamanho_janela: int = 5):
        """Inicializa o analisador
        
        Args:
            tamanho_janela: Quantidade de concursos por janela (padrão: 5)
        """
        self.tamanho_janela = tamanho_janela
        self.conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
        self.resultados: List[Tuple[int, Set[int]]] = []
        self.janelas: List[Dict] = []
        
    def conectar_banco(self):
        """Conecta ao banco de dados SQL Server"""
        return pyodbc.connect(self.conn_str)
    
    def carregar_resultados(self, limite: Optional[int] = None) -> int:
        """Carrega todos os resultados do banco de dados
        
        Args:
            limite: Número máximo de concursos a carregar (None = todos)
            
        Returns:
            Quantidade de resultados carregados
        """
        print("\n⏳ Carregando resultados do banco de dados...")
        
        query = """
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT 
            ORDER BY Concurso ASC
        """
        
        if limite:
            query = f"""
                SELECT TOP {limite} Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
                FROM Resultados_INT 
                ORDER BY Concurso DESC
            """
        
        with self.conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
            self.resultados = []
            for row in cursor.fetchall():
                concurso = row[0]
                numeros = set(row[1:16])
                self.resultados.append((concurso, numeros))
        
        # Se pegou os últimos N, inverter para ordem cronológica
        if limite:
            self.resultados.reverse()
            
        print(f"✅ {len(self.resultados)} concursos carregados (de {self.resultados[0][0]} a {self.resultados[-1][0]})")
        return len(self.resultados)
    
    def classificar_numero(self, aparicoes: int) -> int:
        """Classifica um número em um grupo térmico
        
        Args:
            aparicoes: Quantidade de vezes que apareceu na janela
            
        Returns:
            Número do grupo (1-4)
        """
        for grupo_id, config in self.GRUPOS.items():
            if config['min'] <= aparicoes <= config['max']:
                return grupo_id
        return 4  # Padrão: frio
    
    def analisar_janela(self, inicio: int, fim: int) -> Dict:
        """Analisa uma janela específica de concursos
        
        Args:
            inicio: Índice inicial (inclusivo)
            fim: Índice final (exclusivo)
            
        Returns:
            Dicionário com análise da janela
        """
        # Contar frequências na janela
        frequencias = Counter()
        concursos_janela = []
        
        for idx in range(inicio, fim):
            if idx < len(self.resultados):
                concurso, numeros = self.resultados[idx]
                frequencias.update(numeros)
                concursos_janela.append(concurso)
        
        # Classificar cada número em grupos
        grupos = {1: set(), 2: set(), 3: set(), 4: set()}
        
        for numero in range(1, 26):
            aparicoes = frequencias.get(numero, 0)
            grupo = self.classificar_numero(aparicoes)
            grupos[grupo].add(numero)
        
        return {
            'inicio_idx': inicio,
            'fim_idx': fim,
            'concursos': concursos_janela,
            'primeiro_concurso': concursos_janela[0] if concursos_janela else None,
            'ultimo_concurso': concursos_janela[-1] if concursos_janela else None,
            'frequencias': dict(frequencias),
            'grupos': grupos
        }
    
    def processar_todas_janelas(self, sobrepor: bool = False) -> int:
        """Processa todas as janelas possíveis
        
        Args:
            sobrepor: Se True, janelas se sobrepõem (deslizante)
                      Se False, janelas são consecutivas
        
        Returns:
            Quantidade de janelas processadas
        """
        if not self.resultados:
            raise ValueError("Carregue os resultados primeiro!")
        
        self.janelas = []
        passo = 1 if sobrepor else self.tamanho_janela
        
        print(f"\n⏳ Processando janelas de {self.tamanho_janela} concursos...")
        print(f"   Modo: {'Deslizante (sobreposição)' if sobrepor else 'Consecutivo (sem sobreposição)'}")
        
        for i in range(0, len(self.resultados) - self.tamanho_janela + 1, passo):
            janela = self.analisar_janela(i, i + self.tamanho_janela)
            self.janelas.append(janela)
        
        print(f"✅ {len(self.janelas)} janelas processadas")
        return len(self.janelas)
    
    def analisar_estabilidade_grupos(self) -> Dict:
        """Analisa a estabilidade dos grupos ao longo das janelas
        
        Returns:
            Estatísticas de permanência e mudança dos grupos
        """
        if len(self.janelas) < 2:
            return {}
        
        print("\n" + "="*80)
        print(" 📊 ANÁLISE DE ESTABILIDADE DOS GRUPOS TÉRMICOS")
        print("="*80)
        
        estatisticas = {
            grupo_id: {
                'permanencia': [],      # % dos números que permanecem no grupo
                'entrada': [],          # números que entraram no grupo
                'saida': [],            # números que saíram do grupo
                'duracao_media': [],    # duração média de um número no grupo
                'ciclos': []            # ciclos completos detectados
            }
            for grupo_id in self.GRUPOS.keys()
        }
        
        # Rastrear duração de cada número em cada grupo
        duracao_atual = {num: {g: 0 for g in self.GRUPOS.keys()} for num in range(1, 26)}
        
        for idx in range(len(self.janelas) - 1):
            janela_atual = self.janelas[idx]
            janela_seguinte = self.janelas[idx + 1]
            
            for grupo_id in self.GRUPOS.keys():
                atual = janela_atual['grupos'][grupo_id]
                seguinte = janela_seguinte['grupos'][grupo_id]
                
                # Permanência
                if len(atual) > 0:
                    perm = len(atual & seguinte) / len(atual) * 100
                else:
                    perm = 0
                estatisticas[grupo_id]['permanencia'].append(perm)
                
                # Entradas e saídas
                entraram = seguinte - atual
                sairam = atual - seguinte
                estatisticas[grupo_id]['entrada'].append(len(entraram))
                estatisticas[grupo_id]['saida'].append(len(sairam))
                
                # Atualizar durações
                for num in atual:
                    duracao_atual[num][grupo_id] += 1
                    
                # Registrar durações quando saem
                for num in sairam:
                    if duracao_atual[num][grupo_id] > 0:
                        estatisticas[grupo_id]['duracao_media'].append(duracao_atual[num][grupo_id])
                        duracao_atual[num][grupo_id] = 0
        
        return estatisticas
    
    def detectar_ciclos(self) -> Dict:
        """Detecta padrões cíclicos na movimentação dos grupos
        
        Returns:
            Dicionário com análise de ciclos
        """
        print("\n" + "="*80)
        print(" 🔄 DETECÇÃO DE CICLOS E PADRÕES")
        print("="*80)
        
        # Rastrear histórico de grupo de cada número
        historico_grupos = {num: [] for num in range(1, 26)}
        
        for janela in self.janelas:
            for grupo_id in self.GRUPOS.keys():
                for num in janela['grupos'][grupo_id]:
                    historico_grupos[num].append(grupo_id)
        
        # Analisar ciclos para cada número
        ciclos_detectados = {}
        
        for num in range(1, 26):
            historico = historico_grupos[num]
            if len(historico) < 10:
                continue
                
            # Detectar padrões de repetição
            ciclos_num = self._detectar_padrao_repetitivo(historico)
            if ciclos_num:
                ciclos_detectados[num] = ciclos_num
        
        return {
            'historico_grupos': historico_grupos,
            'ciclos_detectados': ciclos_detectados
        }
    
    def _detectar_padrao_repetitivo(self, sequencia: List[int]) -> Optional[Dict]:
        """Detecta padrões repetitivos em uma sequência
        
        Args:
            sequencia: Lista de grupos ao longo do tempo
            
        Returns:
            Informações sobre o padrão detectado ou None
        """
        if len(sequencia) < 6:
            return None
            
        # Tentar detectar ciclos de diferentes tamanhos
        for tamanho_ciclo in range(3, min(20, len(sequencia) // 2)):
            padrao = sequencia[:tamanho_ciclo]
            repeticoes = 0
            match_total = 0
            
            for i in range(tamanho_ciclo, len(sequencia) - tamanho_ciclo + 1, tamanho_ciclo):
                segmento = sequencia[i:i+tamanho_ciclo]
                if len(segmento) == tamanho_ciclo:
                    match = sum(1 for a, b in zip(padrao, segmento) if a == b)
                    if match >= tamanho_ciclo * 0.7:  # 70% de similaridade
                        repeticoes += 1
                        match_total += match
            
            if repeticoes >= 2:
                return {
                    'tamanho_ciclo': tamanho_ciclo,
                    'repeticoes': repeticoes,
                    'similaridade': match_total / (repeticoes * tamanho_ciclo) * 100 if repeticoes > 0 else 0,
                    'padrao_base': padrao
                }
        
        return None
    
    def analisar_transicoes(self) -> Dict:
        """Analisa transições entre grupos (de quente para frio e vice-versa)
        
        Returns:
            Matriz de transição e estatísticas
        """
        print("\n" + "="*80)
        print(" 🔀 ANÁLISE DE TRANSIÇÕES ENTRE GRUPOS")
        print("="*80)
        
        # Matriz de transição: de grupo X para grupo Y
        transicoes = defaultdict(lambda: defaultdict(int))
        
        # Rastrear grupo de cada número por janela
        grupo_por_numero = {}
        
        for janela_idx, janela in enumerate(self.janelas):
            for grupo_id, numeros in janela['grupos'].items():
                for num in numeros:
                    if num in grupo_por_numero:
                        grupo_anterior = grupo_por_numero[num]
                        transicoes[grupo_anterior][grupo_id] += 1
                    grupo_por_numero[num] = grupo_id
        
        # Converter para probabilidades
        probabilidades = {}
        for grupo_origem, destinos in transicoes.items():
            total = sum(destinos.values())
            probabilidades[grupo_origem] = {
                destino: contagem / total * 100
                for destino, contagem in destinos.items()
            }
        
        return {
            'contagens': dict(transicoes),
            'probabilidades': probabilidades
        }
    
    def analisar_inversoes(self) -> Dict:
        """Detecta momentos de inversão (números quentes viram frios e vice-versa)
        
        Returns:
            Análise de inversões
        """
        print("\n" + "="*80)
        print(" ⚡ ANÁLISE DE INVERSÕES TÉRMICAS")
        print("="*80)
        
        inversoes = {
            'quente_para_frio': [],  # Grupo 1 → Grupo 4
            'frio_para_quente': [],  # Grupo 4 → Grupo 1
            'inversoes_por_janela': [],
            'janelas_maior_inversao': []
        }
        
        for idx in range(len(self.janelas) - 1):
            janela_atual = self.janelas[idx]
            janela_seguinte = self.janelas[idx + 1]
            
            muito_quentes_atual = janela_atual['grupos'][1]
            muito_quentes_seguinte = janela_seguinte['grupos'][1]
            frios_atual = janela_atual['grupos'][4]
            frios_seguinte = janela_seguinte['grupos'][4]
            
            # Números que eram muito quentes e viraram frios
            q_para_f = muito_quentes_atual & frios_seguinte
            # Números que eram frios e viraram muito quentes
            f_para_q = frios_atual & muito_quentes_seguinte
            
            if q_para_f:
                inversoes['quente_para_frio'].append({
                    'janela': idx,
                    'concurso_referencia': janela_atual['ultimo_concurso'],
                    'numeros': sorted(q_para_f)
                })
            
            if f_para_q:
                inversoes['frio_para_quente'].append({
                    'janela': idx,
                    'concurso_referencia': janela_atual['ultimo_concurso'],
                    'numeros': sorted(f_para_q)
                })
            
            total_inversoes = len(q_para_f) + len(f_para_q)
            inversoes['inversoes_por_janela'].append(total_inversoes)
        
        # Identificar janelas com maior inversão
        if inversoes['inversoes_por_janela']:
            max_inv = max(inversoes['inversoes_por_janela'])
            for i, inv in enumerate(inversoes['inversoes_por_janela']):
                if inv == max_inv and max_inv > 0:
                    inversoes['janelas_maior_inversao'].append(i)
        
        return inversoes
    
    def analisar_continuidade_quentes(self) -> Dict:
        """Analisa quantos números do grupo mais quente continuam quentes na janela seguinte
        
        Returns:
            Estatísticas de continuidade
        """
        print("\n" + "="*80)
        print(" 🔥 ANÁLISE DE CONTINUIDADE DOS NÚMEROS QUENTES")
        print("="*80)
        
        continuidade = {
            'pct_permanencia': [],
            'numeros_que_permanecem': [],
            'numeros_que_esfriam': [],
            'media_permanencia': 0,
            'mediana_permanencia': 0,
            'desvio_padrao': 0
        }
        
        for idx in range(len(self.janelas) - 1):
            janela_atual = self.janelas[idx]
            janela_seguinte = self.janelas[idx + 1]
            
            quentes_atual = janela_atual['grupos'][1] | janela_atual['grupos'][2]  # Grupos 1 e 2
            quentes_seguinte = janela_seguinte['grupos'][1] | janela_seguinte['grupos'][2]
            
            if quentes_atual:
                permaneceram = quentes_atual & quentes_seguinte
                esfriaram = quentes_atual - quentes_seguinte
                
                pct = len(permaneceram) / len(quentes_atual) * 100
                continuidade['pct_permanencia'].append(pct)
                continuidade['numeros_que_permanecem'].append(sorted(permaneceram))
                continuidade['numeros_que_esfriam'].append(sorted(esfriaram))
        
        if continuidade['pct_permanencia']:
            continuidade['media_permanencia'] = statistics.mean(continuidade['pct_permanencia'])
            continuidade['mediana_permanencia'] = statistics.median(continuidade['pct_permanencia'])
            if len(continuidade['pct_permanencia']) > 1:
                continuidade['desvio_padrao'] = statistics.stdev(continuidade['pct_permanencia'])
        
        return continuidade
    
    def gerar_relatorio_completo(self, ultimas_n_janelas: int = 10) -> str:
        """Gera um relatório completo da análise
        
        Args:
            ultimas_n_janelas: Quantidade de janelas recentes para exibir em detalhe
            
        Returns:
            String com o relatório formatado
        """
        relatorio = []
        relatorio.append("\n" + "═"*100)
        relatorio.append(" 📊 RELATÓRIO COMPLETO - ANÁLISE DE JANELAS TÉRMICAS")
        relatorio.append(" Data: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
        relatorio.append(" Tamanho da janela: " + str(self.tamanho_janela) + " concursos")
        relatorio.append(" Total de janelas analisadas: " + str(len(self.janelas)))
        relatorio.append("═"*100 + "\n")
        
        # 1. Estatísticas de Estabilidade
        estab = self.analisar_estabilidade_grupos()
        
        relatorio.append("\n┌" + "─"*98 + "┐")
        relatorio.append("│ 1️⃣  ESTABILIDADE DOS GRUPOS                                                                      │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        for grupo_id, config in self.GRUPOS.items():
            perm = estab[grupo_id]['permanencia']
            dur = estab[grupo_id]['duracao_media']
            
            media_perm = statistics.mean(perm) if perm else 0
            media_dur = statistics.mean(dur) if dur else 0
            
            relatorio.append(f"   {config['cor']} Grupo {grupo_id} ({config['nome']} - {config['desc']}):")
            relatorio.append(f"      • Taxa média de permanência: {media_perm:.1f}%")
            relatorio.append(f"      • Duração média no grupo: {media_dur:.1f} janelas")
            relatorio.append(f"      • Média de entradas por janela: {statistics.mean(estab[grupo_id]['entrada']):.1f}")
            relatorio.append(f"      • Média de saídas por janela: {statistics.mean(estab[grupo_id]['saida']):.1f}")
            relatorio.append("")
        
        # 2. Matriz de Transição
        trans = self.analisar_transicoes()
        
        relatorio.append("\n┌" + "─"*98 + "┐")
        relatorio.append("│ 2️⃣  MATRIZ DE TRANSIÇÃO (Probabilidade de ir de um grupo para outro)                            │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        header = "   DE\\PARA  │"
        for g in self.GRUPOS.keys():
            header += f" Grupo {g} │"
        relatorio.append(header)
        relatorio.append("   " + "─"*11 + "┼" + ("─"*9 + "┼") * 4)
        
        for g_origem in self.GRUPOS.keys():
            linha = f"   Grupo {g_origem}  │"
            for g_destino in self.GRUPOS.keys():
                prob = trans['probabilidades'].get(g_origem, {}).get(g_destino, 0)
                linha += f"  {prob:5.1f}% │"
            relatorio.append(linha)
        
        # 3. Análise de Inversões
        inv = self.analisar_inversoes()
        
        relatorio.append("\n\n┌" + "─"*98 + "┐")
        relatorio.append("│ 3️⃣  ANÁLISE DE INVERSÕES TÉRMICAS                                                                │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        total_q_f = len(inv['quente_para_frio'])
        total_f_q = len(inv['frio_para_quente'])
        
        relatorio.append(f"   🔴→🔵 Inversões Quente→Frio: {total_q_f} ocorrências")
        relatorio.append(f"   🔵→🔴 Inversões Frio→Quente: {total_f_q} ocorrências")
        
        if inv['inversoes_por_janela']:
            media_inv = statistics.mean(inv['inversoes_por_janela'])
            relatorio.append(f"   📊 Média de inversões por janela: {media_inv:.2f}")
        
        # Últimas inversões
        relatorio.append("\n   Últimas 5 inversões Quente→Frio:")
        for item in inv['quente_para_frio'][-5:]:
            relatorio.append(f"      • Concurso ~{item['concurso_referencia']}: números {item['numeros']}")
        
        relatorio.append("\n   Últimas 5 inversões Frio→Quente:")
        for item in inv['frio_para_quente'][-5:]:
            relatorio.append(f"      • Concurso ~{item['concurso_referencia']}: números {item['numeros']}")
        
        # 4. Continuidade dos Quentes
        cont = self.analisar_continuidade_quentes()
        
        relatorio.append("\n\n┌" + "─"*98 + "┐")
        relatorio.append("│ 4️⃣  CONTINUIDADE DOS NÚMEROS QUENTES                                                             │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        relatorio.append(f"   📊 Taxa média de permanência: {cont['media_permanencia']:.1f}%")
        relatorio.append(f"   📊 Mediana de permanência: {cont['mediana_permanencia']:.1f}%")
        relatorio.append(f"   📊 Desvio padrão: {cont['desvio_padrao']:.1f}%")
        
        # 5. Detecção de Ciclos
        ciclos = self.detectar_ciclos()
        
        relatorio.append("\n\n┌" + "─"*98 + "┐")
        relatorio.append("│ 5️⃣  DETECÇÃO DE PADRÕES CÍCLICOS                                                                 │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        if ciclos['ciclos_detectados']:
            relatorio.append(f"   ✅ {len(ciclos['ciclos_detectados'])} números com padrões cíclicos detectados:")
            for num, info in sorted(ciclos['ciclos_detectados'].items()):
                relatorio.append(f"      • Número {num:02d}: ciclo de ~{info['tamanho_ciclo']} janelas, "
                               f"{info['repeticoes']} repetições, {info['similaridade']:.0f}% similaridade")
        else:
            relatorio.append("   ⚠️ Nenhum padrão cíclico forte detectado")
            relatorio.append("   ℹ️ Isso indica comportamento mais aleatório/caótico")
        
        # 6. Últimas N Janelas (detalhado)
        relatorio.append("\n\n┌" + "─"*98 + "┐")
        relatorio.append(f"│ 6️⃣  ÚLTIMAS {ultimas_n_janelas} JANELAS (DETALHADO)                                                                │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        for janela in self.janelas[-ultimas_n_janelas:]:
            relatorio.append(f"\n   📅 Janela: Concursos {janela['primeiro_concurso']} a {janela['ultimo_concurso']}")
            for grupo_id, config in self.GRUPOS.items():
                nums = sorted(janela['grupos'][grupo_id])
                nums_str = ', '.join(f'{n:02d}' for n in nums) if nums else '(nenhum)'
                relatorio.append(f"      {config['cor']} G{grupo_id} ({config['desc']}): [{nums_str}]")
        
        # 7. Previsibilidade e Conclusões
        relatorio.append("\n\n┌" + "─"*98 + "┐")
        relatorio.append("│ 7️⃣  ANÁLISE DE PREVISIBILIDADE E CONCLUSÕES                                                      │")
        relatorio.append("└" + "─"*98 + "┘\n")
        
        # Calcular índice de previsibilidade
        if cont['desvio_padrao'] > 0:
            indice_prev = 100 - (cont['desvio_padrao'] * 2)
            indice_prev = max(0, min(100, indice_prev))
        else:
            indice_prev = 50
        
        ciclos_detectados = len(ciclos['ciclos_detectados'])
        
        relatorio.append(f"   📈 Índice de Previsibilidade: {indice_prev:.1f}%")
        relatorio.append(f"   🔄 Números com padrões cíclicos: {ciclos_detectados}/25")
        relatorio.append(f"   🔥 Permanência média dos quentes: {cont['media_permanencia']:.1f}%")
        
        # Conclusões
        relatorio.append("\n   📋 CONCLUSÕES:")
        
        if cont['media_permanencia'] > 60:
            relatorio.append("   ✅ Alta persistência: números quentes tendem a continuar quentes")
        elif cont['media_permanencia'] > 40:
            relatorio.append("   ⚠️ Persistência moderada: alguma continuidade, mas com variação")
        else:
            relatorio.append("   ❌ Baixa persistência: alta rotatividade nos grupos")
        
        if ciclos_detectados > 10:
            relatorio.append("   ✅ Sistema apresenta comportamento cíclico detectável")
        elif ciclos_detectados > 5:
            relatorio.append("   ⚠️ Alguns padrões cíclicos, mas não dominantes")
        else:
            relatorio.append("   ❌ Comportamento predominantemente aleatório")
        
        # Probabilidades úteis
        prob_g1_g1 = trans['probabilidades'].get(1, {}).get(1, 0)
        prob_g4_g1 = trans['probabilidades'].get(4, {}).get(1, 0)
        
        relatorio.append(f"\n   💡 INSIGHTS PARA APOSTAS:")
        relatorio.append(f"      • Prob. número muito quente continuar muito quente: {prob_g1_g1:.1f}%")
        relatorio.append(f"      • Prob. número frio virar muito quente: {prob_g4_g1:.1f}%")
        
        relatorio.append("\n" + "═"*100)
        relatorio.append(" FIM DO RELATÓRIO")
        relatorio.append("═"*100 + "\n")
        
        return '\n'.join(relatorio)
    
    def obter_previsao_proxima_janela(self) -> Dict:
        """Gera previsão para a próxima janela baseada nos padrões detectados
        
        Returns:
            Dicionário com previsões
        """
        if len(self.janelas) < 3:
            return {'erro': 'Dados insuficientes para previsão'}
        
        ultima_janela = self.janelas[-1]
        trans = self.analisar_transicoes()
        
        previsao = {
            'provaveis_quentes': set(),
            'provaveis_frios': set(),
            'em_transicao': set(),
            'confianca': {}
        }
        
        # Para cada número, calcular probabilidade de estado
        for num in range(1, 26):
            # Encontrar grupo atual
            grupo_atual = None
            for g_id, nums in ultima_janela['grupos'].items():
                if num in nums:
                    grupo_atual = g_id
                    break
            
            if grupo_atual is None:
                continue
            
            # Usar matriz de transição para prever
            probs = trans['probabilidades'].get(grupo_atual, {})
            
            prob_quente = probs.get(1, 0) + probs.get(2, 0)
            prob_frio = probs.get(4, 0)
            
            if prob_quente > 60:
                previsao['provaveis_quentes'].add(num)
                previsao['confianca'][num] = prob_quente
            elif prob_frio > 60:
                previsao['provaveis_frios'].add(num)
                previsao['confianca'][num] = prob_frio
            else:
                previsao['em_transicao'].add(num)
        
        return previsao


def executar_analise_interativa():
    """Função principal para análise interativa"""
    
    print("\n" + "╔"+"═"*78+"╗")
    print("║" + " "*20 + "ANALISADOR DE JANELAS TÉRMICAS" + " "*28 + "║")
    print("║" + " "*20 + "Lotofácil - Análise de Padrões" + " "*27 + "║")
    print("╚"+"═"*78+"╝")
    
    analisador = AnalisadorJanelasTermicas(tamanho_janela=5)
    
    # Carregar dados
    analisador.carregar_resultados()
    
    # Menu interativo
    while True:
        print("\n" + "─"*60)
        print(" OPÇÕES DE ANÁLISE")
        print("─"*60)
        print(" 1. Processar janelas CONSECUTIVAS (sem sobreposição)")
        print(" 2. Processar janelas DESLIZANTES (com sobreposição)")
        print(" 3. Gerar relatório completo")
        print(" 4. Ver últimas N janelas")
        print(" 5. Previsão para próxima janela")
        print(" 6. Alterar tamanho da janela (atual: %d)" % analisador.tamanho_janela)
        print(" 7. Exportar relatório para arquivo")
        print(" 0. Sair")
        print("─"*60)
        
        opcao = input("\n Escolha uma opção: ").strip()
        
        if opcao == '0':
            print("\n👋 Até logo!")
            break
            
        elif opcao == '1':
            analisador.processar_todas_janelas(sobrepor=False)
            print("\n✅ Janelas consecutivas processadas!")
            
        elif opcao == '2':
            analisador.processar_todas_janelas(sobrepor=True)
            print("\n✅ Janelas deslizantes processadas!")
            
        elif opcao == '3':
            if not analisador.janelas:
                print("\n⚠️ Processe as janelas primeiro (opções 1 ou 2)!")
                continue
            relatorio = analisador.gerar_relatorio_completo()
            print(relatorio)
            
        elif opcao == '4':
            if not analisador.janelas:
                print("\n⚠️ Processe as janelas primeiro (opções 1 ou 2)!")
                continue
            try:
                n = int(input("   Quantas janelas exibir? "))
                for janela in analisador.janelas[-n:]:
                    print(f"\n   📅 Concursos {janela['primeiro_concurso']}-{janela['ultimo_concurso']}:")
                    for g_id, config in analisador.GRUPOS.items():
                        nums = sorted(janela['grupos'][g_id])
                        print(f"      {config['cor']} G{g_id}: {nums}")
            except ValueError:
                print("   ❌ Número inválido!")
                
        elif opcao == '5':
            if not analisador.janelas:
                print("\n⚠️ Processe as janelas primeiro (opções 1 ou 2)!")
                continue
            previsao = analisador.obter_previsao_proxima_janela()
            print("\n   🔮 PREVISÃO PARA PRÓXIMA JANELA:")
            print(f"      🔴 Provavelmente QUENTES: {sorted(previsao['provaveis_quentes'])}")
            print(f"      🔵 Provavelmente FRIOS: {sorted(previsao['provaveis_frios'])}")
            print(f"      🟡 Em TRANSIÇÃO: {sorted(previsao['em_transicao'])}")
            
        elif opcao == '6':
            try:
                novo_tam = int(input("   Novo tamanho da janela: "))
                if 2 <= novo_tam <= 20:
                    analisador.tamanho_janela = novo_tam
                    print(f"   ✅ Tamanho alterado para {novo_tam}")
                else:
                    print("   ❌ Use um valor entre 2 e 20!")
            except ValueError:
                print("   ❌ Número inválido!")
                
        elif opcao == '7':
            if not analisador.janelas:
                print("\n⚠️ Processe as janelas primeiro (opções 1 ou 2)!")
                continue
            relatorio = analisador.gerar_relatorio_completo()
            arquivo = f"relatorio_janelas_termicas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            print(f"\n   ✅ Relatório exportado para: {arquivo}")


def executar_analise_automatica():
    """Executa análise completa automaticamente"""
    
    print("\n" + "╔"+"═"*78+"╗")
    print("║" + " "*20 + "ANALISADOR DE JANELAS TÉRMICAS" + " "*28 + "║")
    print("║" + " "*15 + "Lotofácil - Análise Automática Completa" + " "*23 + "║")
    print("╚"+"═"*78+"╝")
    
    analisador = AnalisadorJanelasTermicas(tamanho_janela=5)
    
    # Carregar dados
    analisador.carregar_resultados()
    
    # Processar janelas deslizantes para maior detalhamento
    analisador.processar_todas_janelas(sobrepor=True)
    
    # Gerar relatório completo
    relatorio = analisador.gerar_relatorio_completo(ultimas_n_janelas=15)
    print(relatorio)
    
    # Previsão
    previsao = analisador.obter_previsao_proxima_janela()
    print('\n🔮 PREVISÃO PARA PRÓXIMA JANELA:')
    print(f'   🔴 Provavelmente QUENTES: {sorted(previsao.get("provaveis_quentes", set()))}')
    print(f'   🔵 Provavelmente FRIOS: {sorted(previsao.get("provaveis_frios", set()))}')
    print(f'   🟡 Em TRANSIÇÃO: {sorted(previsao.get("em_transicao", set()))}')
    
    return analisador


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        executar_analise_automatica()
    else:
        executar_analise_interativa()
