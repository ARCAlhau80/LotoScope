#!/usr/bin/env python3
"""
🧠 SISTEMA DE APRENDIZADO AUTOMÁTICO - LOTOSCOPE
==============================================
Sistema que aprende com suas próprias predições e melhora continuamente
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import os

class SistemaAprendizadoAutomatico:
    """Sistema que aprende com predições e resultados para melhorar continuamente"""
    
    def __init__(self, db_path: str = "aprendizado_lotoscope.db"):
        self.db_path = db_path
        self.logger = self._setup_logger()
        self.combinacao_fixa = [1, 2, 4, 6, 8, 9, 11, 13, 15, 16, 19, 20, 22, 24, 25]
        
        # Inicializar banco de dados
        self._inicializar_bd()
        
        self.logger.info("Sistema de Aprendizado Automático inicializado")
    
    def _setup_logger(self):
        """Configurar logger"""
        logger = logging.getLogger('AprendizadoAutomatico')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _inicializar_bd(self):
        """Inicializar banco de dados de aprendizado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de predições realizadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predicoes_realizadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                concurso_alvo INTEGER,
                parametros_previstos TEXT,  -- JSON
                combinacoes_geradas INTEGER,
                confianca_predicao REAL,
                resultado_validado INTEGER DEFAULT 0,
                acertos_obtidos INTEGER,
                melhor_combinacao TEXT,
                score_obtido REAL,
                observacoes TEXT
            )
        ''')
        
        # Tabela de evolução dos parâmetros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolucao_parametros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                parametro TEXT NOT NULL,
                valor_previsto REAL,
                valor_real REAL,
                erro_absoluto REAL,
                erro_percentual REAL,
                acerto_dentro_margem INTEGER  -- 1 se acertou dentro da margem de tolerância
            )
        ''')
        
        # Tabela de padrões descobertos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS padroes_descobertos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                tipo_padrao TEXT,  -- 'sequencial', 'faixas', 'comparativo'
                descricao TEXT,
                frequencia_sucesso REAL,
                contexto TEXT,  -- JSON com detalhes
                validacoes INTEGER DEFAULT 0,
                sucessos INTEGER DEFAULT 0
            )
        ''')
        
        # Tabela de conhecimento acumulado
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conhecimento_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                tipo_conhecimento TEXT,
                chave TEXT UNIQUE,
                valor TEXT,  -- JSON
                confianca REAL,
                ultima_atualizacao TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def registrar_predicao(self, predicoes: Dict, combinacoes: List, resultado_sistema: Dict) -> int:
        """Registra uma predição realizada para futura validação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Preparar dados
        timestamp = datetime.now().isoformat()
        parametros_json = json.dumps({
            k: v for k, v in predicoes.items() 
            if k not in ['timestamp', 'concurso_previsto', 'confianca_geral', 'ultima_combinacao']
        })
        
        cursor.execute('''
            INSERT INTO predicoes_realizadas 
            (timestamp, concurso_alvo, parametros_previstos, combinacoes_geradas, 
             confianca_predicao, melhor_combinacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            predicoes.get('concurso_previsto'),
            parametros_json,
            len(combinacoes),
            predicoes.get('confianca_geral', 0),
            str(combinacoes[0]['combinacao']) if combinacoes else None
        ))
        
        predicao_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.logger.info(f"Predição registrada com ID: {predicao_id}")
        return predicao_id
    
    def validar_predicoes_pendentes(self) -> List[Dict]:
        """Verifica resultados de concursos para predições pendentes e aprende com os resultados"""
        from analisador_preditivo_especializado import AnalisadorPreditivoEspecializado
        
        self.logger.info("Validando predições pendentes...")
        
        # Buscar predições não validadas
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, concurso_alvo, parametros_previstos, melhor_combinacao, confianca_predicao
            FROM predicoes_realizadas 
            WHERE resultado_validado = 0 AND concurso_alvo IS NOT NULL
        ''')
        
        predicoes_pendentes = cursor.fetchall()
        conn.close()
        
        if not predicoes_pendentes:
            self.logger.info("Nenhuma predição pendente para validar")
            return []
        
        # Carregar dados reais para comparação
        analisador = AnalisadorPreditivoEspecializado()
        dados_historicos = analisador.carregar_dados_historicos()
        
        resultados_validacao = []
        
        for predicao in predicoes_pendentes:
            predicao_id, concurso_alvo, parametros_json, melhor_combo, confianca = predicao
            
            # Buscar resultado real do concurso
            resultado_real = None
            for dado in dados_historicos:
                if dado.numero_concurso == concurso_alvo:
                    resultado_real = dado
                    break
            
            if resultado_real:
                # Validar predição
                resultado_validacao = self._validar_predicao_individual(
                    predicao_id, parametros_json, melhor_combo, resultado_real
                )
                resultados_validacao.append(resultado_validacao)
                
                # Aprender com o resultado
                self._aprender_com_resultado(parametros_json, resultado_real)
        
        self.logger.info(f"Validadas {len(resultados_validacao)} predições")
        return resultados_validacao
    
    def _validar_predicao_individual(self, predicao_id: int, parametros_json: str, 
                                   melhor_combo: str, resultado_real) -> Dict:
        """Valida uma predição individual e atualiza o banco"""
        parametros_previstos = json.loads(parametros_json)
        
        # Calcular acertos nos parâmetros
        acertos_parametros = 0
        total_parametros = 0
        erros_detalhados = {}
        
        parametros_comparacao = [
            ('maior_que_ultimo', resultado_real.maior_que_ultimo),
            ('menor_que_ultimo', resultado_real.menor_que_ultimo),
            ('igual_ao_ultimo', resultado_real.igual_ao_ultimo),
            ('n1', resultado_real.n1),
            ('n15', resultado_real.n15),
            ('faixa_6a25', resultado_real.faixa_6a25),
            ('faixa_6a20', resultado_real.faixa_6a20),
            ('acertos_combinacao_fixa', resultado_real.acertos_combinacao_fixa)
        ]
        
        for param_nome, valor_real in parametros_comparacao:
            if param_nome in parametros_previstos:
                valor_previsto = parametros_previstos[param_nome]
                erro_abs = abs(valor_previsto - valor_real)
                
                # Consideramos acerto se erro <= 1
                margem_tolerancia = 1
                acertou = erro_abs <= margem_tolerancia
                
                if acertou:
                    acertos_parametros += 1
                
                total_parametros += 1
                erros_detalhados[param_nome] = {
                    'previsto': valor_previsto,
                    'real': valor_real,
                    'erro_abs': erro_abs,
                    'acertou': acertou
                }
                
                # Registrar evolução do parâmetro
                self._registrar_evolucao_parametro(param_nome, valor_previsto, valor_real)
        
        # Calcular score geral
        score_parametros = acertos_parametros / total_parametros if total_parametros > 0 else 0
        
        # Atualizar registro da predição
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE predicoes_realizadas 
            SET resultado_validado = 1, acertos_obtidos = ?, score_obtido = ?,
                observacoes = ?
            WHERE id = ?
        ''', (
            acertos_parametros,
            score_parametros,
            json.dumps(erros_detalhados),
            predicao_id
        ))
        
        conn.commit()
        conn.close()
        
        resultado = {
            'predicao_id': predicao_id,
            'concurso': resultado_real.numero_concurso,
            'acertos_parametros': acertos_parametros,
            'total_parametros': total_parametros,
            'score': score_parametros,
            'erros_detalhados': erros_detalhados
        }
        
        self.logger.info(f"Predição {predicao_id}: {acertos_parametros}/{total_parametros} acertos (Score: {score_parametros:.2f})")
        
        return resultado
    
    def _registrar_evolucao_parametro(self, parametro: str, valor_previsto: float, valor_real: float):
        """Registra evolução de um parâmetro específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        erro_abs = abs(valor_previsto - valor_real)
        erro_perc = (erro_abs / (valor_real + 0.1)) * 100  # Evitar divisão por zero
        acerto_margem = 1 if erro_abs <= 1 else 0
        
        cursor.execute('''
            INSERT INTO evolucao_parametros 
            (timestamp, parametro, valor_previsto, valor_real, erro_absoluto, 
             erro_percentual, acerto_dentro_margem)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            parametro,
            valor_previsto,
            valor_real,
            erro_abs,
            erro_perc,
            acerto_margem
        ))
        
        conn.commit()
        conn.close()
    
    def _aprender_com_resultado(self, parametros_json: str, resultado_real):
        """Aprende padrões com base no resultado real"""
        parametros_previstos = json.loads(parametros_json)
        
        # Descobrir padrões de sucesso/falha
        padroes_descobertos = []
        
        # Padrão 1: Relação entre parâmetros comparativos
        soma_comparativa_real = resultado_real.maior_que_ultimo + resultado_real.menor_que_ultimo + resultado_real.igual_ao_ultimo
        if soma_comparativa_real == 15:  # Validação da regra
            padrao = {
                'tipo': 'comparativo',
                'descricao': f"Maior:{resultado_real.maior_que_ultimo}, Menor:{resultado_real.menor_que_ultimo}, Igual:{resultado_real.igual_ao_ultimo}",
                'contexto': {
                    'n1': resultado_real.n1,
                    'n15': resultado_real.n15,
                    'faixa_6a25': resultado_real.faixa_6a25
                }
            }
            padroes_descobertos.append(padrao)
        
        # Padrão 2: Relação N1/N15 com faixas
        if resultado_real.n1 <= 3 and resultado_real.n15 >= 23:
            padrao = {
                'tipo': 'extremos',
                'descricao': f"N1 baixo ({resultado_real.n1}) e N15 alto ({resultado_real.n15})",
                'contexto': {
                    'faixa_6a25': resultado_real.faixa_6a25,
                    'faixa_6a20': resultado_real.faixa_6a20
                }
            }
            padroes_descobertos.append(padrao)
        
        # Registrar padrões descobertos
        for padrao in padroes_descobertos:
            self._registrar_padrao_descoberto(padrao)
        
        # Atualizar conhecimento base
        self._atualizar_conhecimento_base(resultado_real)
    
    def _registrar_padrao_descoberto(self, padrao: Dict):
        """Registra um novo padrão descoberto"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO padroes_descobertos 
            (timestamp, tipo_padrao, descricao, contexto, validacoes, sucessos)
            VALUES (?, ?, ?, ?, 1, 1)
        ''', (
            datetime.now().isoformat(),
            padrao['tipo'],
            padrao['descricao'],
            json.dumps(padrao['contexto'])
        ))
        
        conn.commit()
        conn.close()
    
    def _atualizar_conhecimento_base(self, resultado_real):
        """Atualiza base de conhecimento com novos dados"""
        conhecimentos = {}
        
        # Frequência de cada valor de parâmetro
        parametros_valores = {
            'maior_que_ultimo': resultado_real.maior_que_ultimo,
            'menor_que_ultimo': resultado_real.menor_que_ultimo,
            'igual_ao_ultimo': resultado_real.igual_ao_ultimo,
            'n1': resultado_real.n1,
            'n15': resultado_real.n15,
            'faixa_6a25': resultado_real.faixa_6a25,
            'faixa_6a20': resultado_real.faixa_6a20
        }
        
        for param, valor in parametros_valores.items():
            chave = f"freq_{param}_{valor}"
            conhecimentos[chave] = conhecimentos.get(chave, 0) + 1
        
        # Salvar no banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for chave, valor in conhecimentos.items():
            cursor.execute('''
                INSERT OR REPLACE INTO conhecimento_base 
                (timestamp, tipo_conhecimento, chave, valor, confianca, ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                'frequencia',
                chave,
                str(valor),
                min(1.0, valor / 10.0),  # Confiança aumenta com frequência
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def obter_predicoes_melhoradas(self, dados_recentes: List) -> Dict:
        """Gera predições melhoradas baseadas no aprendizado acumulado"""
        self.logger.info("Gerando predições baseadas em aprendizado...")
        
        # Obter estatísticas de performance dos parâmetros
        estatisticas_params = self._obter_estatisticas_parametros()
        
        # Obter padrões mais bem-sucedidos
        padroes_sucesso = self._obter_padroes_sucesso()
        
        # Obter conhecimento base
        conhecimento = self._obter_conhecimento_base()
        
        # Gerar predições melhoradas
        predicoes_base = self._gerar_predicoes_estatisticas(dados_recentes)
        predicoes_melhoradas = self._aplicar_aprendizado(predicoes_base, estatisticas_params, padroes_sucesso, conhecimento)
        
        return predicoes_melhoradas
    
    def _obter_estatisticas_parametros(self) -> Dict:
        """Obtém estatísticas de performance dos parâmetros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT parametro, 
                   AVG(erro_absoluto) as erro_medio,
                   AVG(acerto_dentro_margem) as taxa_acerto,
                   COUNT(*) as total_predicoes
            FROM evolucao_parametros 
            GROUP BY parametro
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        
        estatisticas = {}
        for param, erro_medio, taxa_acerto, total in resultados:
            estatisticas[param] = {
                'erro_medio': erro_medio,
                'taxa_acerto': taxa_acerto,
                'total_predicoes': total,
                'confiabilidade': taxa_acerto * min(1.0, total / 10.0)  # Mais dados = mais confiável
            }
        
        return estatisticas
    
    def _obter_padroes_sucesso(self) -> List[Dict]:
        """Obtém padrões com maior taxa de sucesso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tipo_padrao, descricao, contexto, 
                   (sucessos * 1.0 / validacoes) as taxa_sucesso,
                   validacoes
            FROM padroes_descobertos 
            WHERE validacoes >= 2
            ORDER BY taxa_sucesso DESC, validacoes DESC
            LIMIT 10
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        
        padroes = []
        for tipo, desc, contexto, taxa, validacoes in resultados:
            padroes.append({
                'tipo': tipo,
                'descricao': desc,
                'contexto': json.loads(contexto) if contexto else {},
                'taxa_sucesso': taxa,
                'validacoes': validacoes
            })
        
        return padroes
    
    def _obter_conhecimento_base(self) -> Dict:
        """Obtém conhecimento base acumulado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chave, valor, confianca
            FROM conhecimento_base 
            ORDER BY confianca DESC
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        
        conhecimento = {}
        for chave, valor, confianca in resultados:
            conhecimento[chave] = {
                'valor': valor,
                'confianca': confianca
            }
        
        return conhecimento
    
    def _gerar_predicoes_estatisticas(self, dados_recentes: List) -> Dict:
        """Gera predições base usando estatísticas simples"""
        if len(dados_recentes) < 5:
            return self._predicoes_padrao()
        
        ultimos_10 = dados_recentes[-10:]
        
        predicoes = {}
        parametros = ['maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo', 
                     'n1', 'n15', 'faixa_6a25', 'faixa_6a20', 'acertos_combinacao_fixa']
        
        for param in parametros:
            valores = [getattr(d, param) for d in ultimos_10]
            # Usar média ponderada (mais peso para valores recentes)
            pesos = np.linspace(0.5, 1.0, len(valores))
            valor_previsto = np.average(valores, weights=pesos)
            predicoes[param] = max(0, min(25, round(valor_previsto)))
        
        return predicoes
    
    def _aplicar_aprendizado(self, predicoes_base: Dict, estatisticas: Dict, 
                           padroes: List[Dict], conhecimento: Dict) -> Dict:
        """Aplica aprendizado para melhorar predições base"""
        predicoes_melhoradas = predicoes_base.copy()
        
        # Ajustar predições com base na confiabilidade dos parâmetros
        for param, stats in estatisticas.items():
            if param in predicoes_melhoradas and stats['confiabilidade'] < 0.5:
                # Para parâmetros pouco confiáveis, usar valores mais conservadores
                if param in ['maior_que_ultimo', 'menor_que_ultimo', 'igual_ao_ultimo']:
                    # Tender para valores que mantêm a soma = 15
                    if param == 'maior_que_ultimo':
                        predicoes_melhoradas[param] = max(5, min(10, predicoes_melhoradas[param]))
                    elif param == 'menor_que_ultimo':
                        predicoes_melhoradas[param] = max(2, min(8, predicoes_melhoradas[param]))
        
        # Aplicar padrões bem-sucedidos
        for padrao in padroes[:3]:  # Top 3 padrões
            if padrao['taxa_sucesso'] > 0.7:
                self._aplicar_padrao(predicoes_melhoradas, padrao)
        
        # Garantir consistência matemática
        total_comp = predicoes_melhoradas.get('maior_que_ultimo', 0) + \
                    predicoes_melhoradas.get('menor_que_ultimo', 0) + \
                    predicoes_melhoradas.get('igual_ao_ultimo', 0)
        
        if total_comp != 15:
            # Ajustar proporcionalmente
            fator = 15 / total_comp if total_comp > 0 else 1
            predicoes_melhoradas['maior_que_ultimo'] = round(predicoes_melhoradas.get('maior_que_ultimo', 0) * fator)
            predicoes_melhoradas['menor_que_ultimo'] = round(predicoes_melhoradas.get('menor_que_ultimo', 0) * fator)
            predicoes_melhoradas['igual_ao_ultimo'] = 15 - predicoes_melhoradas['maior_que_ultimo'] - predicoes_melhoradas['menor_que_ultimo']
        
        return predicoes_melhoradas
    
    def _aplicar_padrao(self, predicoes: Dict, padrao: Dict):
        """Aplica um padrão específico às predições"""
        contexto = padrao['contexto']
        
        if padrao['tipo'] == 'extremos':
            # Ajustar N1 e N15 para extremos
            predicoes['n1'] = min(3, predicoes.get('n1', 1))
            predicoes['n15'] = max(23, predicoes.get('n15', 25))
        
        elif padrao['tipo'] == 'comparativo':
            # Aplicar padrão comparativo bem-sucedido
            if 'n1' in contexto:
                predicoes['n1'] = contexto['n1']
            if 'faixa_6a25' in contexto:
                predicoes['faixa_6a25'] = contexto['faixa_6a25']
    
    def _predicoes_padrao(self) -> Dict:
        """Predições padrão quando não há dados suficientes"""
        return {
            'maior_que_ultimo': 8,
            'menor_que_ultimo': 4,
            'igual_ao_ultimo': 3,
            'n1': 2,
            'n15': 24,
            'faixa_6a25': 12,
            'faixa_6a20': 9,
            'acertos_combinacao_fixa': 9
        }
    
    def gerar_relatorio_aprendizado(self) -> Dict:
        """Gera relatório completo do aprendizado"""
        conn = sqlite3.connect(self.db_path)
        
        # Estatísticas gerais
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM predicoes_realizadas')
        total_predicoes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predicoes_realizadas WHERE resultado_validado = 1')
        predicoes_validadas = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(score_obtido) FROM predicoes_realizadas WHERE score_obtido IS NOT NULL')
        score_medio = cursor.fetchone()[0] or 0
        
        # Melhores e piores performances por parâmetro
        cursor.execute('''
            SELECT parametro, AVG(acerto_dentro_margem) as taxa_acerto
            FROM evolucao_parametros 
            GROUP BY parametro 
            ORDER BY taxa_acerto DESC
        ''')
        performance_parametros = cursor.fetchall()
        
        # Padrões mais bem-sucedidos
        cursor.execute('''
            SELECT tipo_padrao, descricao, (sucessos * 1.0 / validacoes) as taxa
            FROM padroes_descobertos 
            WHERE validacoes >= 2
            ORDER BY taxa DESC 
            LIMIT 5
        ''')
        melhores_padroes = cursor.fetchall()
        
        conn.close()
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'resumo': {
                'total_predicoes': total_predicoes,
                'predicoes_validadas': predicoes_validadas,
                'score_medio': round(score_medio, 3),
                'taxa_validacao': round(predicoes_validadas / max(1, total_predicoes), 3)
            },
            'performance_parametros': [
                {'parametro': p[0], 'taxa_acerto': round(p[1], 3)} 
                for p in performance_parametros
            ],
            'melhores_padroes': [
                {'tipo': p[0], 'descricao': p[1], 'taxa_sucesso': round(p[2], 3)} 
                for p in melhores_padroes
            ]
        }
        
        return relatorio

def teste_sistema_aprendizado():
    """Teste do sistema de aprendizado"""
    print("🧠 TESTE SISTEMA DE APRENDIZADO AUTOMÁTICO")
    print("=" * 50)
    
    sistema = SistemaAprendizadoAutomatico()
    
    print("1. Validando predições pendentes...")
    validacoes = sistema.validar_predicoes_pendentes()
    
    if validacoes:
        print(f"✅ Validadas {len(validacoes)} predições")
        for val in validacoes:
            print(f"   Concurso {val['concurso']}: {val['acertos_parametros']}/{val['total_parametros']} acertos")
    else:
        print("ℹ️ Nenhuma predição pendente")
    
    print("\n2. Gerando relatório de aprendizado...")
    relatorio = sistema.gerar_relatorio_aprendizado()
    
    print("📊 RESUMO DO APRENDIZADO:")
    print(f"   Total de predições: {relatorio['resumo']['total_predicoes']}")
    print(f"   Predições validadas: {relatorio['resumo']['predicoes_validadas']}")
    print(f"   Score médio: {relatorio['resumo']['score_medio']}")
    
    if relatorio['performance_parametros']:
        print("\n🎯 PERFORMANCE POR PARÂMETRO:")
        for perf in relatorio['performance_parametros'][:5]:
            print(f"   {perf['parametro']}: {perf['taxa_acerto']:.1%}")
    
    if relatorio['melhores_padroes']:
        print("\n🏆 MELHORES PADRÕES:")
        for padrao in relatorio['melhores_padroes']:
            print(f"   {padrao['tipo']}: {padrao['taxa_sucesso']:.1%}")

if __name__ == "__main__":
    teste_sistema_aprendizado()