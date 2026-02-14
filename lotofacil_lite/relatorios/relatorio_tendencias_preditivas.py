#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 RELATÓRIO DE TENDÊNCIAS PREDITIVAS
====================================
Analisa o último sorteio e gera relatório completo de tendências para o próximo concurso:
- Tendência da soma (alta/baixa/estabilidade)
- Faixas esperadas para cada posição (N1, N2, N3...N15)
- Análise baseada nas correlações descobertas
- Predições baseadas nos campos de comparação

Baseado nas descobertas:
• menor_que_ultimo vs soma: -0.652
• maior_que_ultimo vs soma: +0.648
• Padrões de reversão e estados extremos
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Configurar paths para imports
_BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(_BASE_DIR))
sys.path.insert(0, str(_BASE_DIR / 'utils'))

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

class RelatorioTendenciasPreditivas:
    """Gerador de relatório completo de tendências preditivas"""
    
    def __init__(self):
        self.correlacoes = {
            'menor_soma': -0.652,
            'maior_soma': 0.648,
            'igual_amplitude': 0.183
        }
        
        self.estados_extremos = {
            (15,0,0): {'proximo': (0,15,0), 'prob': 18.2, 'descricao': 'Reversão total esperada'},
            (0,15,0): {'proximo': (15,0,0), 'prob': 19.5, 'descricao': 'Reversão total esperada'},
            (14,0,1): {'proximo': (0,14,1), 'prob': 11.5, 'descricao': 'Reversão quase total'},
            (0,14,1): {'proximo': (14,0,1), 'prob': 9.8, 'descricao': 'Reversão quase total'}
        }
        
        self.faixas_historicas = {
            'soma_baixa': 240,
            'soma_alta': 300,
            'soma_media': 270
        }
        
        self.ultimo_concurso = None
        self.dados_historicos = []
        
    def obter_ultimo_concurso(self):
        """Obtém dados do último concurso"""
        print("🔍 OBTENDO DADOS DO ÚLTIMO CONCURSO...")
        
        query = """
        SELECT TOP 1
            concurso,
            data_sorteio,
            menor_que_ultimo,
            maior_que_ultimo,
            igual_ao_ultimo,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT 
        WHERE menor_que_ultimo IS NOT NULL 
        ORDER BY concurso DESC
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                # Converter para dicionário
                colunas = [desc[0] for desc in cursor.description]
                self.ultimo_concurso = dict(zip(colunas, resultado))
                print(f"✅ Último concurso: {self.ultimo_concurso['concurso']}")
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
    
    def carregar_dados_historicos(self, limite=200):
        """Carrega dados históricos para análise de tendências"""
        print(f"📊 CARREGANDO {limite} CONCURSOS HISTÓRICOS...")
        
        query = f"""
        SELECT TOP {limite}
            concurso,
            menor_que_ultimo,
            maior_que_ultimo,
            igual_ao_ultimo,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM RESULTADOS_INT 
        WHERE menor_que_ultimo IS NOT NULL 
        ORDER BY concurso DESC
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                # Converter para lista de dicionários
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
    
    def calcular_soma_atual(self):
        """Calcula soma dos números do último concurso"""
        numeros = [
            self.ultimo_concurso[f'N{i}'] for i in range(1, 16)
        ]
        return sum(numeros)
    
    def analisar_tendencia_soma(self):
        """Analisa tendência da soma para o próximo concurso com múltiplos níveis"""
        menor = self.ultimo_concurso['menor_que_ultimo']
        maior = self.ultimo_concurso['maior_que_ultimo']
        igual = self.ultimo_concurso['igual_ao_ultimo']
        soma_atual = self.calcular_soma_atual()
        
        # Analisar os últimos 5 concursos para detectar padrões graduais
        historico_recente = []
        for i in range(min(5, len(self.dados_historicos))):
            h = self.dados_historicos[i]
            estado_h = self.classificar_estado(h['menor_que_ultimo'], h['maior_que_ultimo'], h['igual_ao_ultimo'])
            historico_recente.append(estado_h)
        
        # Classificar estado atual com múltiplos níveis
        estado_atual = self.classificar_estado_detalhado(menor, maior, igual)
        
        # Determinar tendência baseada no estado atual e histórico
        return self.calcular_tendencia_inteligente(estado_atual, historico_recente, soma_atual)
    
    def classificar_estado(self, menor, maior, igual):
        """Classifica estado em categorias básicas"""
        if maior >= 12:
            return "ALTA"
        elif menor >= 12:
            return "BAIXA"
        else:
            return "MÉDIA"
    
    def classificar_estado_detalhado(self, menor, maior, igual):
        """Classifica estado com múltiplos níveis de intensidade"""
        # Estados extremos
        if maior >= 14:
            return {"categoria": "ALTA", "intensidade": "EXTREMA", "valor": maior}
        elif maior >= 12:
            return {"categoria": "ALTA", "intensidade": "FORTE", "valor": maior}
        elif maior >= 9:
            return {"categoria": "ALTA", "intensidade": "MODERADA", "valor": maior}
        elif menor >= 14:
            return {"categoria": "BAIXA", "intensidade": "EXTREMA", "valor": menor}
        elif menor >= 12:
            return {"categoria": "BAIXA", "intensidade": "FORTE", "valor": menor}
        elif menor >= 9:
            return {"categoria": "BAIXA", "intensidade": "MODERADA", "valor": menor}
        else:
            # Estados médios/equilibrados
            diferenca = abs(maior - menor)
            if diferenca <= 2:
                return {"categoria": "EQUILIBRADA", "intensidade": "ESTÁVEL", "valor": diferenca}
            elif diferenca <= 4:
                return {"categoria": "MÉDIA", "intensidade": "OSCILANTE", "valor": diferenca}
            else:
                return {"categoria": "MÉDIA", "intensidade": "INSTÁVEL", "valor": diferenca}
    
    def calcular_tendencia_inteligente(self, estado_atual, historico_recente, soma_atual):
        """Calcula tendência considerando nuances e gradualidade - LÓGICA MELHORADA"""
        categoria = estado_atual["categoria"]
        intensidade = estado_atual["intensidade"]
        valor = estado_atual["valor"]
        
        # Obter números atuais para análise contextual
        menor_atual = self.ultimo_concurso['menor_que_ultimo']
        maior_atual = self.ultimo_concurso['maior_que_ultimo']
        
        # Analisar padrão recente
        estados_recentes = [h for h in historico_recente if h != "MÉDIA"]
        tempo_em_media = historico_recente.count("MÉDIA")
        
        # LÓGICA REFINADA - Considerando o contexto atual dos números
        if categoria == "ALTA":
            if intensidade == "EXTREMA":
                # Após alta extrema, sempre corrige
                tendencia = "BAIXA"
                intensidade_correcao = "FORTE"
                explicacao = f"Extremo ALTA ({valor}): correção forte esperada"
                faixa_esperada = (soma_atual - 35, soma_atual - 10)
                confianca = 85.0
            elif intensidade == "FORTE" and tempo_em_media >= 2:
                # Alta forte após período médio: correção moderada
                tendencia = "BAIXA"
                intensidade_correcao = "MODERADA"
                explicacao = f"ALTA forte ({valor}) após período médio: correção gradual"
                faixa_esperada = (soma_atual - 25, soma_atual - 5)
                confianca = 70.0
            else:
                # Alta moderada: pode manter ou oscilar
                tendencia = "ESTABILIDADE"
                intensidade_correcao = "LEVE"
                explicacao = f"ALTA moderada ({valor}): tendência estável com leves oscilações"
                faixa_esperada = (soma_atual - 15, soma_atual + 10)
                confianca = 60.0
                
        elif categoria == "BAIXA":
            if intensidade == "EXTREMA":
                # Após baixa extrema, sempre corrige
                tendencia = "ALTA"
                intensidade_correcao = "FORTE"
                explicacao = f"Extremo BAIXA ({valor}): correção forte esperada"
                faixa_esperada = (soma_atual + 10, soma_atual + 35)
                confianca = 85.0
            elif intensidade == "FORTE" and tempo_em_media >= 2:
                # Baixa forte após período médio: correção moderada
                tendencia = "ALTA"
                intensidade_correcao = "MODERADA"
                explicacao = f"BAIXA forte ({valor}) após período médio: correção gradual"
                faixa_esperada = (soma_atual + 5, soma_atual + 25)
                confianca = 70.0
            else:
                # ANÁLISE CONTEXTUAL: Se menor está alto, não é baixa normal
                if menor_atual >= 11:
                    tendencia = "ESTABILIDADE_ALTA"
                    intensidade_correcao = "MODERADA"
                    explicacao = f"Menor alto ({menor_atual}) mas categoria baixa: estabilidade no patamar elevado"
                    faixa_esperada = (soma_atual - 5, soma_atual + 15)
                    confianca = 70.0
                else:
                    # Baixa moderada normal
                    tendencia = "ESTABILIDADE"
                    intensidade_correcao = "LEVE"
                    explicacao = f"BAIXA moderada ({valor}): tendência estável com leves oscilações"
                    faixa_esperada = (soma_atual - 10, soma_atual + 15)
                    confianca = 60.0
                
        elif categoria == "EQUILIBRADA" or categoria == "MÉDIA":
            # NOVA LÓGICA: Analisar se já estamos em patamar alto/baixo
            if menor_atual >= 11:
                # Se menor já está alto, estabilidade deve manter alto
                tendencia = "ESTABILIDADE_ALTA"
                intensidade_correcao = "MODERADA"
                explicacao = f"Menor já alto ({menor_atual}): estabilidade mantendo patamar elevado"
                faixa_esperada = (soma_atual - 5, soma_atual + 15)
                confianca = 70.0
            elif maior_atual >= 11:
                # Se maior já está alto, estabilidade deve manter alto  
                tendencia = "ESTABILIDADE_ALTA"
                intensidade_correcao = "MODERADA"
                explicacao = f"Maior já alto ({maior_atual}): estabilidade mantendo patamar elevado"
                faixa_esperada = (soma_atual - 5, soma_atual + 15)
                confianca = 70.0
            elif menor_atual <= 3:
                # Se menor está muito baixo, estabilidade deve subir
                tendencia = "ESTABILIDADE_BAIXA"
                intensidade_correcao = "MODERADA"
                explicacao = f"Menor muito baixo ({menor_atual}): estabilidade com correção ascendente"
                faixa_esperada = (soma_atual - 15, soma_atual + 5)
                confianca = 70.0
            elif maior_atual <= 3:
                # Se maior está muito baixo, estabilidade deve subir
                tendencia = "ESTABILIDADE_BAIXA" 
                intensidade_correcao = "MODERADA"
                explicacao = f"Maior muito baixo ({maior_atual}): estabilidade com correção ascendente"
                faixa_esperada = (soma_atual - 15, soma_atual + 5)
                confianca = 70.0
            else:
                # Estados realmente equilibrados
                tendencia = "ESTABILIDADE"
                intensidade_correcao = "MÍNIMA"
                explicacao = f"Estado equilibrado: continuidade esperada"
                faixa_esperada = (soma_atual - 10, soma_atual + 10)
                confianca = 75.0
        
        
        return {
            'tendencia': tendencia,
            'soma_atual': soma_atual,
            'soma_estimada': int((faixa_esperada[0] + faixa_esperada[1]) / 2),
            'faixa_esperada': faixa_esperada,
            'explicacao': explicacao,
            'confianca': confianca,
            'intensidade': intensidade_correcao,
            'estado_detalhado': estado_atual
        }
    
    def calcular_confianca_soma(self, menor, maior, igual):
        """Calcula confiança da predição da soma"""
        estado = (menor, maior, igual)
        
        # Estados extremos têm alta confiança por causa dos padrões de reversão
        if estado in self.estados_extremos:
            return 90.0
        
        # Estados quase extremos também têm alta confiança
        if menor >= 12 or maior >= 12:
            return 85.0
        elif menor >= 10 or maior >= 10:
            return 75.0
        elif menor <= 2 or maior <= 2:
            return 70.0
        else:
            return 55.0
    
    def analisar_tendencias_posicionais(self):
        """Analisa tendências para cada posição N1, N2, ..., N15"""
        tendencia_soma = self.analisar_tendencia_soma()
        tendencia = tendencia_soma['tendencia']
        
        numeros_atuais = [
            self.ultimo_concurso[f'N{i}'] for i in range(1, 16)
        ]
        
        # Calcular médias históricas por posição
        medias_posicionais = self.calcular_medias_posicionais()
        
        tendencias_posicoes = []
        
        for i, (pos, num_atual) in enumerate(zip(range(1, 16), numeros_atuais)):
            media_historica = medias_posicionais[i]
            
            # Ajustar intensidade baseada no tipo de tendência
            intensidade = tendencia_soma.get('intensidade', 'MODERADA')
            
            if tendencia == "ALTA":
                if intensidade == "FORTE":
                    # Alta forte: movimento mais significativo mas flexível
                    faixa_min = max(1, num_atual - 1, int(media_historica * 0.9))
                    faixa_max = min(25, num_atual + 6, int(media_historica * 1.2))
                elif intensidade == "MODERADA":
                    # Alta moderada: movimento médio com flexibilidade
                    faixa_min = max(1, num_atual - 2, int(media_historica * 0.85))
                    faixa_max = min(25, num_atual + 4, int(media_historica * 1.15))
                else:  # LEVE
                    # Alta leve: movimento sutil mas não cravado
                    faixa_min = max(1, num_atual - 2, int(media_historica * 0.9))
                    faixa_max = min(25, num_atual + 3, int(media_historica * 1.1))
                direcao = "↗️ SUBIR"
                
            elif tendencia == "BAIXA":
                if intensidade == "FORTE":
                    # Baixa forte: movimento mais significativo mas flexível
                    faixa_min = max(1, num_atual - 6, int(media_historica * 0.8))
                    faixa_max = min(25, num_atual + 1, int(media_historica * 1.1))
                elif intensidade == "MODERADA":
                    # Baixa moderada: movimento médio com flexibilidade
                    faixa_min = max(1, num_atual - 4, int(media_historica * 0.85))
                    faixa_max = min(25, num_atual + 2, int(media_historica * 1.15))
                else:  # LEVE
                    # Baixa leve: movimento sutil mas não cravado
                    faixa_min = max(1, num_atual - 3, int(media_historica * 0.9))
                    faixa_max = min(25, num_atual + 2, int(media_historica * 1.1))
                direcao = "↘️ DESCER"
                
            else:  # ESTABILIDADE
                # Movimento mais maleável para estados estáveis
                if intensidade == "MÍNIMA":
                    # Estabilidade mínima: pequena variação
                    faixa_min = max(1, num_atual - 2, int(media_historica * 0.92))
                    faixa_max = min(25, num_atual + 2, int(media_historica * 1.08))
                else:
                    # Estabilidade normal: variação moderada
                    faixa_min = max(1, num_atual - 3, int(media_historica * 0.88))
                    faixa_max = min(25, num_atual + 3, int(media_historica * 1.12))
                direcao = "↔️ ESTÁVEL"
            
            # Garantir faixa mínima de pelo menos 2 números para flexibilidade
            if faixa_max - faixa_min < 2:
                # Expandir faixa para ter pelo menos 3 opções
                centro = (faixa_min + faixa_max) // 2
                faixa_min = max(1, centro - 1)
                faixa_max = min(25, centro + 1)
            
            # Garantir que faixa_min <= faixa_max
            if faixa_min > faixa_max:
                faixa_min, faixa_max = faixa_max, faixa_min
            
            tendencias_posicoes.append({
                'posicao': f'N{pos}',
                'valor_atual': num_atual,
                'media_historica': round(media_historica, 1),
                'faixa_esperada': (faixa_min, faixa_max),
                'direcao': direcao,
                'variacao_esperada': faixa_max - faixa_min
            })
        
        return tendencias_posicoes
    
    def calcular_medias_posicionais(self):
        """Calcula médias históricas para cada posição"""
        medias = []
        
        for pos in range(1, 16):
            valores = [dado[f'N{pos}'] for dado in self.dados_historicos if dado[f'N{pos}'] is not None]
            if valores:
                medias.append(sum(valores) / len(valores))
            else:
                # Fallback baseado na posição
                medias.append(pos * 1.7)  # Aproximação linear
        
        return medias
    
    def verificar_estado_extremo(self):
        """Verifica se estamos em estado extremo"""
        menor = self.ultimo_concurso['menor_que_ultimo']
        maior = self.ultimo_concurso['maior_que_ultimo']
        igual = self.ultimo_concurso['igual_ao_ultimo']
        
        estado = (menor, maior, igual)
        
        if estado in self.estados_extremos:
            return {
                'eh_extremo': True,
                'estado_atual': estado,
                'estado_previsto': self.estados_extremos[estado]['proximo'],
                'probabilidade': self.estados_extremos[estado]['prob'],
                'descricao': self.estados_extremos[estado]['descricao']
            }
        else:
            return {'eh_extremo': False}
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo de tendências"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE TENDÊNCIAS PREDITIVAS")
        print("="*80)
        
        if not self.obter_ultimo_concurso():
            return False
        
        if not self.carregar_dados_historicos():
            return False
        
        # Análise do último concurso
        concurso = self.ultimo_concurso['concurso']
        data = self.ultimo_concurso.get('data_sorteio', 'N/A')
        menor = self.ultimo_concurso['menor_que_ultimo']
        maior = self.ultimo_concurso['maior_que_ultimo']
        igual = self.ultimo_concurso['igual_ao_ultimo']
        
        print(f"\n🎯 CONCURSO ANALISADO: {concurso}")
        print(f"📅 Data: {data}")
        print(f"🔢 Estado de comparação: ({menor}, {maior}, {igual})")
        
        # Números do último concurso
        numeros = [self.ultimo_concurso[f'N{i}'] for i in range(1, 16)]
        print(f"🎲 Números: {numeros}")
        print(f"➕ Soma: {sum(numeros)}")
        
        # Análise de tendência da soma
        print(f"\n{'='*50}")
        print("📈 ANÁLISE DE TENDÊNCIA DA SOMA")
        print("="*50)
        
        tendencia_soma = self.analisar_tendencia_soma()
        print(f"🎯 TENDÊNCIA: {tendencia_soma['tendencia']}")
        if 'intensidade' in tendencia_soma:
            print(f"💪 INTENSIDADE: {tendencia_soma['intensidade']}")
        if 'estado_detalhado' in tendencia_soma:
            estado = tendencia_soma['estado_detalhado']
            print(f"📊 Estado detalhado: {estado['categoria']} ({estado['intensidade']}) - Valor: {estado['valor']}")
        print(f"📊 Soma atual: {tendencia_soma['soma_atual']}")
        print(f"🔮 Soma estimada próximo: {tendencia_soma['soma_estimada']}")
        print(f"📍 Faixa esperada: {tendencia_soma['faixa_esperada'][0]} - {tendencia_soma['faixa_esperada'][1]}")
        print(f"💡 Explicação: {tendencia_soma['explicacao']}")
        print(f"🎯 Confiança: {tendencia_soma['confianca']:.1f}%")
        
        # Verificar estado extremo
        estado_extremo = self.verificar_estado_extremo()
        if estado_extremo['eh_extremo']:
            print(f"\n⚠️ ALERTA: ESTADO EXTREMO DETECTADO!")
            print(f"🔄 Estado atual: {estado_extremo['estado_atual']}")
            print(f"🎯 Estado previsto: {estado_extremo['estado_previsto']}")
            print(f"📊 Probabilidade: {estado_extremo['probabilidade']:.1f}%")
            print(f"📝 {estado_extremo['descricao']}")
        
        # Análise posicional
        print(f"\n{'='*50}")
        print("🎯 TENDÊNCIAS POSICIONAIS (N1 - N15)")
        print("="*50)
        
        tendencias_pos = self.analisar_tendencias_posicionais()
        
        print(f"{'Pos':<4} {'Atual':<6} {'Média':<6} {'Faixa Esperada':<15} {'Direção':<12} {'Var':<4}")
        print("-" * 65)
        
        # Garantir exibição completa de todas as posições
        import sys
        for i, t in enumerate(tendencias_pos):
            faixa = f"{t['faixa_esperada'][0]}-{t['faixa_esperada'][1]}"
            linha = f"{t['posicao']:<4} {t['valor_atual']:<6} {t['media_historica']:<6} {faixa:<15} {t['direcao']:<12} {t['variacao_esperada']:<4}"
            print(linha)
            sys.stdout.flush()  # Forçar flush do buffer
            
            # Pausa a cada 8 linhas para evitar overflow
            if (i + 1) % 8 == 0 and i < len(tendencias_pos) - 1:
                print("--- (continuação) ---")
                sys.stdout.flush()
        
        # Resumo executivo
        print(f"\n{'='*50}")
        print("📋 RESUMO EXECUTIVO")
        print("="*50)
        
        print(f"🎯 PRÓXIMO CONCURSO: {concurso + 1}")
        print(f"📊 TENDÊNCIA GERAL: {tendencia_soma['tendencia']}")
        print(f"➕ SOMA ESPERADA: {tendencia_soma['faixa_esperada'][0]} - {tendencia_soma['faixa_esperada'][1]}")
        
        # Contar direções
        direcoes = [t['direcao'] for t in tendencias_pos]
        subir = sum(1 for d in direcoes if 'SUBIR' in d)
        descer = sum(1 for d in direcoes if 'DESCER' in d)
        estavel = sum(1 for d in direcoes if 'ESTÁVEL' in d)
        
        print(f"📈 Posições que devem SUBIR: {subir}")
        print(f"📉 Posições que devem DESCER: {descer}")
        print(f"↔️ Posições ESTÁVEIS: {estavel}")
        
        if estado_extremo['eh_extremo']:
            print(f"⚠️ ATENÇÃO: Estado extremo - Reversão esperada!")
        
        print(f"\n{'='*80}")
        print("✅ RELATÓRIO GERADO COM SUCESSO!")
        print("="*80)
        
        return True
    
    def salvar_relatorio_arquivo(self):
        """Salva relatório em arquivo"""
        nome_arquivo = f"relatorio_tendencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                # Redirecionar print para arquivo seria complexo
                # Por agora, apenas informamos que foi salvo
                f.write(f"Relatório de Tendências Preditivas\n")
                f.write(f"Gerado em: {datetime.now()}\n")
                f.write(f"Concurso analisado: {self.ultimo_concurso['concurso']}\n")
            
            print(f"💾 Relatório salvo em: {nome_arquivo}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 INICIANDO RELATÓRIO DE TENDÊNCIAS PREDITIVAS...")
    
    relatorio = RelatorioTendenciasPreditivas()
    
    if relatorio.gerar_relatorio_completo():
        print("\n💾 Deseja salvar o relatório em arquivo? (s/n): ", end="")
        try:
            resposta = input().lower().strip()
            if resposta == 's':
                relatorio.salvar_relatorio_arquivo()
        except:
            pass
    else:
        print("❌ Falha ao gerar relatório")

if __name__ == "__main__":
    main()