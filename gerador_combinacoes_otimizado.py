#!/usr/bin/env python3
"""
🎲 GERADOR DE COMBINAÇÕES BASEADO EM PARÂMETROS PRECISOS
================================================================
Usa os 8 parâmetros previstos para gerar combinações específicas
Objetivo: De 3.268.760 combinações → Algumas centenas
"""

import itertools
import numpy as np
from typing import List, Dict, Tuple
import logging
from datetime import datetime

class GeradorCombinacoesOtimizado:
    """Gerador de combinações baseado em parâmetros precisos"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.combinacao_fixa = [1, 2, 4, 6, 8, 9, 11, 13, 15, 16, 19, 20, 22, 24, 25]
        
    def _setup_logger(self):
        """Configurar logger"""
        logger = logging.getLogger('GeradorOtimizado')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def gerar_combinacoes_por_parametros(self, parametros_previstos: Dict) -> List[List[int]]:
        """
        Gera combinações baseadas nos parâmetros previstos
        
        Args:
            parametros_previstos: Dict com os 8 parâmetros previstos
            
        Returns:
            Lista de combinações candidatas
        """
        self.logger.info("Gerando combinações baseadas em parâmetros precisos...")
        
        # Extrair parâmetros
        maior_que_ultimo = parametros_previstos.get('maior_que_ultimo', 0)
        menor_que_ultimo = parametros_previstos.get('menor_que_ultimo', 0)
        igual_ao_ultimo = parametros_previstos.get('igual_ao_ultimo', 0)
        n1_previsto = parametros_previstos.get('n1', 1)
        n15_previsto = parametros_previstos.get('n15', 25)
        faixa_6a25_previsto = parametros_previstos.get('faixa_6a25', 12)
        faixa_6a20_previsto = parametros_previstos.get('faixa_6a20', 9)
        acertos_combinacao_previsto = parametros_previstos.get('acertos_combinacao_fixa', 9)
        
        # Última combinação (simulada - na prática, seria do banco de dados)
        ultima_combinacao = parametros_previstos.get('ultima_combinacao', [1, 5, 8, 11, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
        
        self.logger.info(f"Parâmetros alvo:")
        self.logger.info(f"   N1={n1_previsto}, N15={n15_previsto}")
        self.logger.info(f"   Maior={maior_que_ultimo}, Menor={menor_que_ultimo}, Igual={igual_ao_ultimo}")
        self.logger.info(f"   Faixa 6-25={faixa_6a25_previsto}, Faixa 6-20={faixa_6a20_previsto}")
        self.logger.info(f"   Acertos combinação fixa={acertos_combinacao_previsto}")
        
        combinacoes_candidatas = []
        
        # Estratégia 1: Gerar por faixas controladas
        combinacoes_candidatas.extend(
            self._gerar_por_faixas_controladas(
                n1_previsto, n15_previsto, faixa_6a25_previsto, 
                faixa_6a20_previsto, acertos_combinacao_previsto
            )
        )
        
        # Estratégia 2: Gerar por comparação com último concurso
        combinacoes_candidatas.extend(
            self._gerar_por_comparacao_ultimo(
                ultima_combinacao, maior_que_ultimo, 
                menor_que_ultimo, igual_ao_ultimo,
                n1_previsto, n15_previsto
            )
        )
        
        # Estratégia 3: Gerar por padrões híbridos
        combinacoes_candidatas.extend(
            self._gerar_por_padroes_hibridos(parametros_previstos)
        )
        
        # Filtrar e validar todas as combinações
        combinacoes_validas = self._filtrar_e_validar(combinacoes_candidatas, parametros_previstos)
        
        # Remover duplicatas
        combinacoes_unicas = []
        for combo in combinacoes_validas:
            combo_sorted = tuple(sorted(combo))
            if combo_sorted not in [tuple(sorted(c)) for c in combinacoes_unicas]:
                combinacoes_unicas.append(combo)
        
        self.logger.info(f"Geradas {len(combinacoes_unicas)} combinações únicas válidas")
        
        return combinacoes_unicas
    
    def _gerar_por_faixas_controladas(self, n1, n15, faixa_6a25, faixa_6a20, acertos_fixa) -> List[List[int]]:
        """Gera combinações controlando faixas numéricas"""
        combinacoes = []
        
        # Definir faixas baseadas nos parâmetros
        faixa_baixa = list(range(1, 6))    # 1-5
        faixa_media_baixa = list(range(6, 11))   # 6-10
        faixa_media = list(range(11, 16))  # 11-15
        faixa_media_alta = list(range(16, 21))  # 16-20
        faixa_alta = list(range(21, 26))   # 21-25
        
        # Números da combinação fixa que devemos acertar
        numeros_fixa_alvo = self.combinacao_fixa[:acertos_fixa] if acertos_fixa <= 15 else self.combinacao_fixa
        
        # Gerar múltiplas tentativas
        for tentativa in range(100):  # 100 tentativas
            combo = []
            
            # Garantir N1 e N15
            combo.append(n1)
            if n15 != n1:
                combo.append(n15)
            
            # Adicionar números da combinação fixa
            for num in numeros_fixa_alvo:
                if num not in combo and len(combo) < 15:
                    combo.append(num)
            
            # Completar com números das faixas apropriadas
            faixa_6a20_atual = len([n for n in combo if 6 <= n <= 20])
            faixa_6a25_atual = len([n for n in combo if 6 <= n <= 25])
            
            # Adicionar números para atingir as faixas previstas
            while len(combo) < 15:
                # Escolher faixa baseada nas necessidades
                if faixa_6a20_atual < faixa_6a20:
                    # Precisa de mais números 6-20
                    candidatos = [n for n in range(6, 21) if n not in combo]
                elif faixa_6a25_atual < faixa_6a25:
                    # Precisa de mais números 6-25
                    candidatos = [n for n in range(6, 26) if n not in combo]
                else:
                    # Pode pegar qualquer número
                    candidatos = [n for n in range(1, 26) if n not in combo]
                
                if candidatos:
                    num_escolhido = np.random.choice(candidatos)
                    combo.append(num_escolhido)
                    
                    if 6 <= num_escolhido <= 20:
                        faixa_6a20_atual += 1
                    if 6 <= num_escolhido <= 25:
                        faixa_6a25_atual += 1
                else:
                    break
            
            if len(combo) == 15:
                combinacoes.append(sorted(combo))
        
        return combinacoes
    
    def _gerar_por_comparacao_ultimo(self, ultima_combo, maior_que, menor_que, igual_que, n1, n15) -> List[List[int]]:
        """Gera combinações baseadas na comparação com último concurso"""
        combinacoes = []
        
        # Separar números da última combinação por categorias
        ultimo_set = set(ultima_combo)
        
        for tentativa in range(50):  # 50 tentativas
            combo = []
            
            # Garantir N1 e N15
            combo.append(n1)
            if n15 != n1:
                combo.append(n15)
            
            # Números iguais ao último (repetidos)
            if igual_que > 0:
                numeros_iguais = np.random.choice(
                    [n for n in ultima_combo if n not in combo], 
                    size=min(igual_que, len(ultima_combo) - len(combo)),
                    replace=False
                )
                combo.extend(numeros_iguais)
            
            # Números maiores que o maior do último
            if maior_que > 0:
                max_ultimo = max(ultima_combo)
                numeros_maiores = [n for n in range(max_ultimo + 1, 26) if n not in combo]
                if numeros_maiores:
                    escolhidos = np.random.choice(
                        numeros_maiores,
                        size=min(maior_que, len(numeros_maiores)),
                        replace=False
                    )
                    combo.extend(escolhidos)
            
            # Números menores que o menor do último
            if menor_que > 0:
                min_ultimo = min(ultima_combo)
                numeros_menores = [n for n in range(1, min_ultimo) if n not in combo]
                if numeros_menores:
                    escolhidos = np.random.choice(
                        numeros_menores,
                        size=min(menor_que, len(numeros_menores)),
                        replace=False
                    )
                    combo.extend(escolhidos)
            
            # Completar até 15 números
            while len(combo) < 15:
                candidatos = [n for n in range(1, 26) if n not in combo]
                if candidatos:
                    combo.append(np.random.choice(candidatos))
                else:
                    break
            
            if len(combo) == 15:
                combinacoes.append(sorted(combo))
        
        return combinacoes
    
    def _gerar_por_padroes_hibridos(self, parametros) -> List[List[int]]:
        """Gera combinações usando padrões híbridos e inteligência artificial"""
        combinacoes = []
        
        # Padrões baseados em análise histórica
        padroes = [
            # Padrão equilibrado
            {'baixos': 3, 'medios': 6, 'altos': 6},
            # Padrão tendência alta
            {'baixos': 2, 'medios': 5, 'altos': 8},
            # Padrão tendência baixa
            {'baixos': 4, 'medios': 7, 'altos': 4},
            # Padrão concentrado no meio
            {'baixos': 3, 'medios': 9, 'altos': 3}
        ]
        
        for padrao in padroes:
            for tentativa in range(25):  # 25 tentativas por padrão
                combo = []
                
                # Números baixos (1-8)
                baixos_disponiveis = [n for n in range(1, 9) if n not in combo]
                if padrao['baixos'] > 0 and baixos_disponiveis:
                    escolhidos = np.random.choice(
                        baixos_disponiveis,
                        size=min(padrao['baixos'], len(baixos_disponiveis)),
                        replace=False
                    )
                    combo.extend(escolhidos)
                
                # Números médios (9-17)
                medios_disponiveis = [n for n in range(9, 18) if n not in combo]
                if padrao['medios'] > 0 and medios_disponiveis:
                    escolhidos = np.random.choice(
                        medios_disponiveis,
                        size=min(padrao['medios'], len(medios_disponiveis)),
                        replace=False
                    )
                    combo.extend(escolhidos)
                
                # Números altos (18-25)
                altos_disponiveis = [n for n in range(18, 26) if n not in combo]
                if padrao['altos'] > 0 and altos_disponiveis:
                    escolhidos = np.random.choice(
                        altos_disponiveis,
                        size=min(padrao['altos'], len(altos_disponiveis)),
                        replace=False
                    )
                    combo.extend(escolhidos)
                
                # Completar se necessário
                while len(combo) < 15:
                    candidatos = [n for n in range(1, 26) if n not in combo]
                    if candidatos:
                        combo.append(np.random.choice(candidatos))
                    else:
                        break
                
                if len(combo) == 15:
                    combinacoes.append(sorted(combo))
        
        return combinacoes
    
    def _filtrar_e_validar(self, combinacoes_candidatas, parametros_previstos) -> List[List[int]]:
        """Filtra e valida combinações baseadas nos parâmetros previstos"""
        combinacoes_validas = []
        
        tolerancia = 1  # Tolerância de ±1 para validação
        
        for combo in combinacoes_candidatas:
            if len(combo) != 15 or len(set(combo)) != 15:
                continue
            
            # Validar parâmetros
            n1_combo = min(combo)
            n15_combo = max(combo)
            faixa_6a25_combo = len([n for n in combo if 6 <= n <= 25])
            faixa_6a20_combo = len([n for n in combo if 6 <= n <= 20])
            acertos_combo = len(set(combo) & set(self.combinacao_fixa))
            
            # Verificar se está dentro da tolerância
            validacoes = [
                abs(n1_combo - parametros_previstos.get('n1', 1)) <= tolerancia,
                abs(n15_combo - parametros_previstos.get('n15', 25)) <= tolerancia,
                abs(faixa_6a25_combo - parametros_previstos.get('faixa_6a25', 12)) <= tolerancia,
                abs(faixa_6a20_combo - parametros_previstos.get('faixa_6a20', 9)) <= tolerancia,
                abs(acertos_combo - parametros_previstos.get('acertos_combinacao_fixa', 9)) <= tolerancia * 2
            ]
            
            # Se pelo menos 80% das validações passaram
            if sum(validacoes) >= len(validacoes) * 0.8:
                combinacoes_validas.append(combo)
        
        return combinacoes_validas
    
    def avaliar_combinacoes(self, combinacoes: List[List[int]], parametros_previstos: Dict) -> List[Dict]:
        """Avalia e classifica as combinações geradas"""
        self.logger.info("Avaliando e classificando combinações...")
        
        avaliacoes = []
        
        for i, combo in enumerate(combinacoes):
            # Calcular parâmetros da combinação
            n1_combo = min(combo)
            n15_combo = max(combo)
            faixa_6a25_combo = len([n for n in combo if 6 <= n <= 25])
            faixa_6a20_combo = len([n for n in combo if 6 <= n <= 20])
            acertos_combo = len(set(combo) & set(self.combinacao_fixa))
            
            # Calcular score de proximidade
            score = 0
            score += max(0, 10 - abs(n1_combo - parametros_previstos.get('n1', 1)))
            score += max(0, 10 - abs(n15_combo - parametros_previstos.get('n15', 25)))
            score += max(0, 10 - abs(faixa_6a25_combo - parametros_previstos.get('faixa_6a25', 12)))
            score += max(0, 10 - abs(faixa_6a20_combo - parametros_previstos.get('faixa_6a20', 9)))
            score += max(0, 10 - abs(acertos_combo - parametros_previstos.get('acertos_combinacao_fixa', 9)))
            
            avaliacao = {
                'combinacao': combo,
                'score': score,
                'n1': n1_combo,
                'n15': n15_combo,
                'faixa_6a25': faixa_6a25_combo,
                'faixa_6a20': faixa_6a20_combo,
                'acertos_combinacao_fixa': acertos_combo,
                'ranking': i + 1
            }
            
            avaliacoes.append(avaliacao)
        
        # Ordenar por score (melhor primeiro)
        avaliacoes.sort(key=lambda x: x['score'], reverse=True)
        
        # Atualizar ranking
        for i, avaliacao in enumerate(avaliacoes):
            avaliacao['ranking'] = i + 1
        
        return avaliacoes

def teste_gerador():
    """Teste do gerador de combinações"""
    print("🎲 TESTE DO GERADOR DE COMBINAÇÕES OTIMIZADO")
    print("=" * 55)
    
    # Parâmetros de exemplo (baseados na predição real)
    parametros_teste = {
        'maior_que_ultimo': 10,
        'menor_que_ultimo': 3,
        'igual_ao_ultimo': 2,
        'n1': 2,
        'n15': 24,
        'faixa_6a25': 12,
        'faixa_6a20': 9,
        'acertos_combinacao_fixa': 9,
        'ultima_combinacao': [1, 5, 8, 11, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    }
    
    gerador = GeradorCombinacoesOtimizado()
    
    # Gerar combinações
    combinacoes = gerador.gerar_combinacoes_por_parametros(parametros_teste)
    
    # Avaliar combinações
    avaliacoes = gerador.avaliar_combinacoes(combinacoes, parametros_teste)
    
    # Mostrar top 10
    print(f"\n🏆 TOP 10 MELHORES COMBINAÇÕES:")
    print("-" * 55)
    
    for i, avaliacao in enumerate(avaliacoes[:10]):
        combo = avaliacao['combinacao']
        score = avaliacao['score']
        print(f"{i+1:2d}. {combo} (Score: {score:.1f})")
    
    print(f"\n📊 Resumo:")
    print(f"   Total de combinações geradas: {len(combinacoes)}")
    print(f"   Redução: de 3.268.760 para {len(combinacoes)} ({len(combinacoes)/3268760*100:.4f}%)")
    print(f"   Fator de redução: {3268760//len(combinacoes) if len(combinacoes) > 0 else 'N/A'}x")

if __name__ == "__main__":
    teste_gerador()