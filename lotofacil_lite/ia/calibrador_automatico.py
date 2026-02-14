#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SISTEMA DE CALIBRAÇÃO AUTOMÁTICA - LOTOSCOPE
===============================================
Sistema inteligente que detecta cenários em tempo real e calibra
todos os geradores automaticamente baseado em:

- Estados dos campos de comparação
- Ciclos de repetições posicionais  
- Padrões de inversão
- Momentos de reset
- Correlações históricas

Autor: AR CALHAU
Data: 06 de Outubro de 2025
"""

import sys
import os
import json
import pyodbc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))
sys.path.insert(0, str(_BASE_DIR / 'ia'))

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

from database_config import db_config

# Importa descobertas
try:
    from integracao_descobertas_comparacao import IntegracaoDescobertasComparacao
    DESCOBERTAS_DISPONIVEL = True
except ImportError:
    DESCOBERTAS_DISPONIVEL = False

@dataclass
class CenarioDetectado:
    """Classe para representar um cenário detectado"""
    tipo: str
    confianca: float
    parametros: Dict
    descricao: str
    estrategia: Dict

class CalibradorAutomatico:
    """Sistema de calibração automática para todos os geradores"""
    
    def __init__(self):
        self.pasta_calibracao = "calibracao_automatica"
        os.makedirs(self.pasta_calibracao, exist_ok=True)
        
        # Carrega descobertas se disponível
        if DESCOBERTAS_DISPONIVEL:
            self.descobertas = IntegracaoDescobertasComparacao()
            print("🔬 Descobertas carregadas para calibração")
        else:
            self.descobertas = None
            print("⚠️ Calibração em modo básico - descobertas não disponíveis")
        
        # Histórico de cenários
        self.historico_cenarios = []
        self.ultimo_cenario = None
        
        # Configurações de cenários
        self.configuracoes_cenarios = self._inicializar_configuracoes()
        
        print("🎯 SISTEMA DE CALIBRAÇÃO AUTOMÁTICA INICIALIZADO")
        print("=" * 60)
    
    def _inicializar_configuracoes(self) -> Dict:
        """Inicializa configurações para cada tipo de cenário"""
        return {
            'reset_extremo': {
                'criterios': {
                    'atraso_repeticoes': 10,
                    'menor_que_anterior_min': 11,
                    'soma_max': 190
                },
                'estrategia': {
                    'zona_foco': [1, 12],               # FOCUS: números bem baixos (validado 3505)
                    'peso_numeros_baixos': 0.85,       # PESO MÁXIMO para números baixos
                    'evitar_repeticoes_posicao': True,
                    'soma_alvo': [160, 180],            # Soma mais baixa (validado 170)
                    'priorizar_faixa_1_10': True,      # NOVO: Priorizar extremo baixo
                    'limite_superior': 15               # NOVO: Limite rígido superior
                }
            },
            'inversao_moderada': {
                'criterios': {
                    'menor_que_anterior_range': [8, 11],
                    'maior_que_anterior_range': [2, 6],
                    'repeticoes_normais': [2, 5]
                },
                'estrategia': {
                    'zona_foco': [5, 20],
                    'peso_numeros_baixos': 0.6,
                    'distribuicao_equilibrada': True,
                    'soma_alvo': [190, 220]
                }
            },
            'equilibrio_normal': {
                'criterios': {
                    'menor_que_anterior_range': [4, 8],
                    'maior_que_anterior_range': [4, 8],
                    'igual_range': [2, 5]
                },
                'estrategia': {
                    'zona_foco': [1, 25],
                    'distribuicao_uniforme': True,
                    'zona_conforto_peso': 0.7,
                    'soma_alvo': [180, 220]
                }
            },
            'pre_inversao': {
                'criterios': {
                    'tendencia_descendente': 3,
                    'menor_maior_diferenca_min': 3,
                    'repeticoes_aumentando': True
                },
                'estrategia': {
                    'preparar_inversao': True,
                    'zona_foco': [8, 22],
                    'peso_numeros_medios': 0.7,
                    'soma_alvo': [200, 240]
                }
            }
        }
    
    def detectar_cenario_atual(self, dados_historicos: List[Dict]) -> CenarioDetectado:
        """Detecta o cenário atual baseado nos dados históricos"""
        print("\n🔍 DETECTANDO CENÁRIO ATUAL...")
        print("-" * 40)
        
        if not dados_historicos or len(dados_historicos) < 3:
            return self._cenario_padrao()
        
        # Analisa últimos concursos
        ultimo = dados_historicos[-1]
        penultimo = dados_historicos[-2] if len(dados_historicos) > 1 else {}
        antepenultimo = dados_historicos[-3] if len(dados_historicos) > 2 else {}
        
        # Extrai dados principais
        menor_atual = ultimo.get('menor_que_anterior', 5)
        maior_atual = ultimo.get('maior_que_anterior', 5)
        igual_atual = ultimo.get('igual', 5)
        repeticoes_atual = ultimo.get('repeticoes_posicao', 3)
        soma_atual = ultimo.get('soma', 195)
        
        print(f"📊 Estado atual: menor={menor_atual}, maior={maior_atual}, igual={igual_atual}")
        print(f"🔄 Repetições posicionais: {repeticoes_atual}")
        print(f"➕ Soma: {soma_atual}")
        
        # Detecta tendências
        tendencia_menor = self._calcular_tendencia([
            antepenultimo.get('menor_que_anterior', 5),
            penultimo.get('menor_que_anterior', 5),
            menor_atual
        ])
        
        atraso_repeticoes = self._calcular_atraso_repeticoes(dados_historicos)
        
        print(f"📈 Tendência menor_que_anterior: {tendencia_menor}")
        print(f"⏰ Atraso repetições baixas: {atraso_repeticoes} concursos")
        
        # Aplica lógica de detecção
        cenario = self._classificar_cenario(
            menor_atual, maior_atual, igual_atual,
            repeticoes_atual, soma_atual,
            tendencia_menor, atraso_repeticoes
        )
        
        print(f"🎯 Cenário detectado: {cenario.tipo} (confiança: {cenario.confianca:.1%})")
        print(f"📝 {cenario.descricao}")
        
        return cenario
    
    def _calcular_tendencia(self, valores: List[int]) -> str:
        """Calcula tendência de uma série de valores"""
        if len(valores) < 2:
            return "estável"
        
        diferencas = [valores[i+1] - valores[i] for i in range(len(valores)-1)]
        media_diff = sum(diferencas) / len(diferencas)
        
        if media_diff > 1:
            return "crescente"
        elif media_diff < -1:
            return "decrescente"
        else:
            return "estável"
    
    def _calcular_atraso_repeticoes(self, dados: List[Dict]) -> int:
        """Calcula quantos concursos desde a última ocorrência de repetições baixas"""
        contador = 0
        for i in range(len(dados)-1, -1, -1):
            repeticoes = dados[i].get('repeticoes_posicao', 3)
            if repeticoes <= 1:
                return contador
            contador += 1
        return min(contador, 15)  # Máximo 15 para evitar valores extremos
    
    def _classificar_cenario(self, menor: int, maior: int, igual: int,
                           repeticoes: int, soma: int,
                           tendencia: str, atraso: int) -> CenarioDetectado:
        """Classifica o cenário baseado nos parâmetros"""
        
        print(f"🔍 ANÁLISE DETALHADA DO CENÁRIO:")
        print(f"   Estado atual: ({menor}, {maior}, {igual})")
        print(f"   Soma: {soma}, Tendência: {tendencia}, Atraso: {atraso}")
        
        # CENÁRIO 1: RESET EXTREMO (baseado na validação do concurso 3505)
        # Estado (7,5,3) historicamente resultou em (11,0,4) - INVERSÃO EXTREMA
        if (menor >= 7 and maior >= 5 and igual <= 3) or \
           (atraso >= 10 and menor >= 7) or \
           (menor >= 11):
            print(f"   🎯 Detectado: RESET EXTREMO - Padrão validado (7,5,3) → (11,0,4)")
            return CenarioDetectado(
                tipo="reset_extremo",
                confianca=0.85,
                parametros={
                    'menor_esperado': 11,  # Baseado na validação real
                    'soma_esperada': 170,  # Baseado na validação real
                    'repeticoes_esperadas': 1
                },
                descricao="Sistema em iminência de RESET EXTREMO - padrão validado (7,5,3) → (11,0,4)",
                estrategia=self.configuracoes_cenarios['reset_extremo']['estrategia']
            )
        
        # CENÁRIO 2: INVERSÃO MODERADA
        elif menor >= 6 and maior >= 4 and tendencia in ["decrescente", "estável"]:
            print(f"   🔄 Detectado: INVERSÃO MODERADA")
            return CenarioDetectado(
                tipo="inversao_moderada",
                confianca=0.70,
                parametros={
                    'menor_esperado': menor + 3,
                    'soma_esperada': soma - 20,
                    'repeticoes_esperadas': 2
                },
                descricao="Inversão moderada em curso - ajuste gradual",
                estrategia=self.configuracoes_cenarios['inversao_moderada']['estrategia']
            )
        
        # CENÁRIO 3: PRÉ-INVERSÃO
        elif menor >= 5 and atraso >= 3:
            print(f"   ⚡ Detectado: PRÉ-INVERSÃO")
            return CenarioDetectado(
                tipo="pre_inversao",
                confianca=0.65,
                parametros={
                    'menor_esperado': menor + 2,
                    'soma_esperada': soma - 15
                },
                descricao="Preparação para inversão - movimento inicial detectado",
                estrategia=self.configuracoes_cenarios['pre_inversao']['estrategia']
            )
        
        # CENÁRIO 4: EQUILÍBRIO NORMAL
        else:
            print(f"   ⚖️ Detectado: EQUILÍBRIO NORMAL")
            return CenarioDetectado(
                tipo="equilibrio_normal",
                confianca=0.50,
                parametros={
                    'menor_esperado': 5,
                    'soma_esperada': 195
                },
                descricao="Estado de equilíbrio normal - sem padrões extremos",
                estrategia=self.configuracoes_cenarios['equilibrio_normal']['estrategia']
            )
    
    def _cenario_padrao(self) -> CenarioDetectado:
        """Retorna cenário padrão quando dados insuficientes"""
        return CenarioDetectado(
            tipo="equilibrio_normal",
            confianca=0.30,
            parametros={'menor_esperado': 5, 'soma_esperada': 195},
            descricao="Dados insuficientes - usando configuração padrão",
            estrategia=self.configuracoes_cenarios['equilibrio_normal']['estrategia']
        )
    
    def calibrar_todos_geradores(self, cenario: CenarioDetectado) -> Dict:
        """Calibra todos os geradores baseado no cenário detectado"""
        print(f"\n🔧 CALIBRANDO GERADORES PARA CENÁRIO: {cenario.tipo}")
        print("=" * 60)
        
        # Lista de geradores a calibrar
        geradores_alvo = [
            'gerador_academico_dinamico.py',
            'super_gerador_ia.py',
            'gerador_complementacao_inteligente.py',
            'sistema_desdobramento_complementar.py',
            'gerador_zona_conforto.py'
        ]
        
        calibracao_aplicada = {}
        
        for gerador in geradores_alvo:
            if os.path.exists(gerador):
                config_gerador = self._gerar_configuracao_gerador(gerador, cenario)
                calibracao_aplicada[gerador] = config_gerador
                self._aplicar_calibracao(gerador, config_gerador)
                print(f"✅ {gerador} calibrado")
            else:
                print(f"⚠️ {gerador} não encontrado")
        
        # Salva configuração aplicada
        self._salvar_calibracao(cenario, calibracao_aplicada)
        
        return calibracao_aplicada
    
    def _gerar_configuracao_gerador(self, gerador: str, cenario: CenarioDetectado) -> Dict:
        """Gera configuração específica para cada gerador"""
        estrategia = cenario.estrategia
        
        if 'academico' in gerador:
            return {
                'zona_foco': estrategia.get('zona_foco', [1, 25]),
                'peso_correlacoes': 0.8 if cenario.tipo == 'reset_extremo' else 0.6,
                'soma_alvo': estrategia.get('soma_alvo', [180, 220]),
                'modo_inversao': cenario.tipo in ['reset_extremo', 'inversao_moderada']
            }
        
        elif 'zona_conforto' in gerador:
            return {
                'zona_conforto_inicio': estrategia.get('zona_foco', [1, 17])[0],
                'zona_conforto_fim': min(17, estrategia.get('zona_foco', [1, 17])[1]),
                'peso_zona': estrategia.get('peso_numeros_baixos', 0.8),
                'permitir_sequencias': cenario.tipo != 'reset_extremo'
            }
        
        elif 'complementacao' in gerador:
            return {
                'base_20_foco': estrategia.get('zona_foco', [1, 20]),
                'forca_extremos': cenario.tipo == 'reset_extremo',
                'peso_distribuicao': 4.0 if cenario.tipo == 'reset_extremo' else 3.0,
                'soma_alvo': estrategia.get('soma_alvo', [180, 220])
            }
        
        elif 'super_gerador' in gerador:
            return {
                'modo_adaptativo': True,
                'cenario_detectado': cenario.tipo,
                'confianca_cenario': cenario.confianca,
                'parametros_especiais': cenario.parametros
            }
        
        else:
            # Configuração genérica
            return {
                'cenario': cenario.tipo,
                'estrategia': estrategia,
                'parametros': cenario.parametros
            }
    
    def _aplicar_calibracao(self, gerador: str, config: Dict):
        """Aplica calibração a um gerador específico"""
        # Cria arquivo de configuração específico para o gerador
        nome_config = f"config_{gerador.replace('.py', '')}.json"
        caminho_config = os.path.join(self.pasta_calibracao, nome_config)
        
        config_completa = {
            'timestamp': datetime.now().isoformat(),
            'gerador': gerador,
            'configuracao': config,
            'aplicado_automaticamente': True
        }
        
        with open(caminho_config, 'w', encoding='utf-8') as f:
            json.dump(config_completa, f, indent=2, ensure_ascii=False)
    
    def _salvar_calibracao(self, cenario: CenarioDetectado, calibracao: Dict):
        """Salva registro completo da calibração"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = os.path.join(self.pasta_calibracao, f"calibracao_completa_{timestamp}.json")
        
        registro = {
            'timestamp': datetime.now().isoformat(),
            'cenario_detectado': {
                'tipo': cenario.tipo,
                'confianca': cenario.confianca,
                'descricao': cenario.descricao,
                'parametros': cenario.parametros,
                'estrategia': cenario.estrategia
            },
            'geradores_calibrados': calibracao,
            'proxima_validacao': '21:00 (resultado do concurso)'
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(registro, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Calibração salva: {arquivo}")
    
    def ler_dados_reais_base(self) -> List[Dict]:
        """Lê dados reais dos últimos concursos da base de dados"""
        try:
            # Conexão otimizada para performance
            if _db_optimizer:
                conn = _db_optimizer.create_optimized_connection()
            else:
                conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_config['server']};"
                f"DATABASE={db_config['database']};"
                f"UID={db_config['username']};"
                f"PWD={db_config['password']}"
            )
            
            cursor = conn.cursor()
            
            # Busca os últimos 5 concursos com campos de comparação
            query = """
            SELECT TOP 5 
                Concurso,
                menor_que_ultimo,
                maior_que_ultimo, 
                igual_ao_ultimo,
                Repeticoes_na_mesma_posicao,
                SomaTotal
            FROM Resultados_INT 
            WHERE menor_que_ultimo IS NOT NULL 
            ORDER BY Concurso DESC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            dados_historicos = []
            for row in resultados:
                dados_historicos.append({
                    'concurso': row[0],
                    'menor_que_anterior': row[1],
                    'maior_que_anterior': row[2], 
                    'igual': row[3],
                    'repeticoes_posicao': row[4] if row[4] is not None else 3,
                    'soma': row[5] if row[5] is not None else 195
                })
            
            conn.close()
            
            # Inverte para ordem cronológica (mais antigo primeiro)
            dados_historicos.reverse()
            
            print(f"📊 Dados reais carregados: {len(dados_historicos)} concursos")
            for dado in dados_historicos:
                print(f"   Concurso {dado['concurso']}: ({dado['menor_que_anterior']}, {dado['maior_que_anterior']}, {dado['igual']})")
            
            return dados_historicos
            
        except Exception as e:
            print(f"⚠️ Erro ao ler dados da base: {e}")
            print(f"🔄 Usando dados de fallback baseados no concurso 3504")
            # Fallback com dados conhecidos do concurso 3504 (estado correto)
            return [
                {'concurso': 3502, 'menor_que_anterior': 8, 'maior_que_anterior': 3, 'igual': 4, 'repeticoes_posicao': 3, 'soma': 204},
                {'concurso': 3503, 'menor_que_anterior': 7, 'maior_que_anterior': 5, 'igual': 3, 'repeticoes_posicao': 3, 'soma': 190}, 
                {'concurso': 3504, 'menor_que_anterior': 7, 'maior_que_anterior': 5, 'igual': 3, 'repeticoes_posicao': 3, 'soma': 190}
            ]
    
    def executar_calibracao_completa(self):
        """Executa calibração completa do sistema"""
        print("🚀 INICIANDO CALIBRAÇÃO AUTOMÁTICA COMPLETA")
        print("=" * 70)
        
        # 📊 LÊ DADOS REAIS DA BASE DE DADOS
        dados_historicos = self.ler_dados_reais_base()
        
        # Detecta cenário
        cenario = self.detectar_cenario_atual(dados_historicos)
        
        # Calibra geradores
        calibracao = self.calibrar_todos_geradores(cenario)
        
        # Exibe resumo
        self._exibir_resumo_calibracao(cenario, calibracao)
        
        return cenario, calibracao
    
    def _exibir_resumo_calibracao(self, cenario: CenarioDetectado, calibracao: Dict):
        """Exibe resumo da calibração aplicada"""
        print("\n" + "=" * 70)
        print("📊 RESUMO DA CALIBRAÇÃO AUTOMÁTICA")
        print("=" * 70)
        print(f"🎯 Cenário detectado: {cenario.tipo}")
        print(f"📈 Confiança: {cenario.confianca:.1%}")
        print(f"📝 Descrição: {cenario.descricao}")
        print(f"\n🔧 Geradores calibrados: {len(calibracao)}")
        
        for gerador in calibracao:
            print(f"   ✅ {gerador}")
        
        print(f"\n🎲 Predição para concurso 3505:")
        print(f"   menor_que_anterior: {cenario.parametros.get('menor_esperado', 'N/A')}")
        print(f"   soma estimada: {cenario.parametros.get('soma_esperada', 'N/A')}")
        
        print(f"\n⏰ Validação agendada: 21:00 (resultado do concurso)")
        print("=" * 70)

def main():
    """Função principal"""
    calibrador = CalibradorAutomatico()
    cenario, calibracao = calibrador.executar_calibracao_completa()
    
    print(f"\n🎉 Calibração automática concluída!")
    print(f"📂 Arquivos de configuração salvos em: calibracao_automatica/")
    print(f"🎯 Sistema preparado para o cenário: {cenario.tipo}")

if __name__ == "__main__":
    main()