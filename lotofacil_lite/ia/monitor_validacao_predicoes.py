#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 MONITOR DE VALIDAÇÃO DE PREDIÇÕES
===================================
Sistema que monitora e valida a eficácia das predições e calibrações
comparando com resultados reais dos concursos.

Funcionalidades:
- Registra predições         resultado_exemplo = {
            'concurso': 3505,
            'numeros': [1, 2, 3, 4, 6, 7, 8, 9, 11, 14, 16, 20, 21, 23, 25],
            'menor_que_anterior': 11,  # CORRIGIDO - método posição por posição
            'maior_que_anterior': 0,   # CORRIGIDO - método posição por posição
            'igual': 4,                # CORRIGIDO - método posição por posição
            'soma': 170,
            'repeticoes_posicao': 4
        }lo sistema
- Compara com resultados reais quando disponíveis  
- Calcula taxa de acerto de cada tipo de predição
- Monitora eficácia das calibrações automáticas
- Gera relatórios de desempenho
- Aprende com erros e acertos para melhorar

Autor: AR CALHAU
Data: 06 de Outubro de 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

@dataclass
class RegistroPredicao:
    """Registro de uma predição feita pelo sistema"""
    timestamp: str
    concurso: int
    tipo_predicao: str  # 'estado_comparacao', 'soma', 'inversao', 'combinacao'
    predicao: dict
    confianca: float
    cenario_detectado: str
    parametros_calibracao: dict
    resultado_real: Optional[dict] = None
    acertou: Optional[bool] = None
    pontuacao_acerto: Optional[float] = None
    observacoes: str = ""

class MonitorValidacao:
    """Monitor principal para validação de predições"""
    
    def __init__(self):
        self.pasta_validacao = "validacao_predicoes"
        os.makedirs(self.pasta_validacao, exist_ok=True)
        
        self.arquivo_registros = os.path.join(self.pasta_validacao, "registros_predicoes.json")
        self.arquivo_metricas = os.path.join(self.pasta_validacao, "metricas_desempenho.json")
        
        # Carrega registros existentes
        self.registros = self._carregar_registros()
        
        print("📊 Monitor de Validação de Predições inicializado")
        print(f"📁 Pasta: {self.pasta_validacao}")
        print(f"📝 Registros carregados: {len(self.registros)}")
    
    def _carregar_registros(self) -> List[RegistroPredicao]:
        """Carrega registros existentes do arquivo"""
        if os.path.exists(self.arquivo_registros):
            try:
                with open(self.arquivo_registros, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                return [RegistroPredicao(**registro) for registro in dados]
            except Exception as e:
                print(f"⚠️ Erro ao carregar registros: {e}")
        return []
    
    def _salvar_registros(self):
        """Salva registros no arquivo"""
        try:
            dados = [asdict(registro) for registro in self.registros]
            with open(self.arquivo_registros, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erro ao salvar registros: {e}")
    
    def registrar_predicao_concurso_3505(self):
        """Registra nossa predição específica para o concurso 3505"""
        predicao_3505 = RegistroPredicao(
            timestamp=datetime.now().isoformat(),
            concurso=3505,
            tipo_predicao="reset_extremo_com_combinacoes",
            predicao={
                'menor_que_anterior_esperado': 12,
                'maior_que_anterior_esperado': 2,
                'igual_esperado': 1,
                'soma_esperada': [160, 185],
                'repeticoes_posicao_esperadas': [0, 1],
                'combinacoes_otimizadas': [
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  # Radical
                    [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14, 15, 16, 17],  # Equilibrada  
                    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]   # Conservadora
                ],
                'meta_minima_acertos': 12
            },
            confianca=0.85,
            cenario_detectado="reset_extremo",
            parametros_calibracao={
                'atraso_repeticoes': 10,
                'tendencia_menor': 'decrescente',
                'estado_atual': [7, 5, 3],
                'convergencia_padroes': True
            },
            observacoes="Predição baseada em análise convergente de inversão + atraso de repetições posicionais. Meta: pelo menos 12 pontos em uma das 3 combinações."
        )
        
        self.registros.append(predicao_3505)
        self._salvar_registros()
        
        print("📝 PREDIÇÃO REGISTRADA PARA CONCURSO 3505")
        print("=" * 50)
        print(f"🎯 Tipo: {predicao_3505.tipo_predicao}")
        print(f"📈 Confiança: {predicao_3505.confianca:.1%}")
        print(f"🎪 Cenário: {predicao_3505.cenario_detectado}")
        print(f"🎲 Meta mínima: {predicao_3505.predicao['meta_minima_acertos']} acertos")
        print(f"⏰ Validação: 21:00 hoje")
        print("=" * 50)
    
    def registrar_resultado_concurso(self, concurso: int, resultado: Dict):
        """Registra resultado real de um concurso"""
        # Encontra registros para este concurso
        registros_concurso = [r for r in self.registros if r.concurso == concurso]
        
        if not registros_concurso:
            print(f"⚠️ Nenhuma predição encontrada para concurso {concurso}")
            return
        
        # Atualiza cada registro com o resultado
        for registro in registros_concurso:
            registro.resultado_real = resultado
            registro.acertou = self._avaliar_acerto(registro, resultado)
            registro.pontuacao_acerto = self._calcular_pontuacao(registro, resultado)
        
        self._salvar_registros()
        
        print(f"✅ Resultado registrado para concurso {concurso}")
        print(f"📊 Predições atualizadas: {len(registros_concurso)}")
    
    def _avaliar_acerto(self, registro: RegistroPredicao, resultado: Dict) -> bool:
        """Avalia se uma predição acertou baseado no tipo"""
        if registro.tipo_predicao == "reset_extremo_com_combinacoes":
            # Verifica se pelo menos uma combinação atingiu a meta
            numeros_sorteados = resultado.get('numeros', [])
            combinacoes = registro.predicao.get('combinacoes_otimizadas', [])
            meta_minima = registro.predicao.get('meta_minima_acertos', 12)
            
            for combinacao in combinacoes:
                acertos = len(set(combinacao) & set(numeros_sorteados))
                if acertos >= meta_minima:
                    return True
            return False
        
        elif registro.tipo_predicao == "estado_comparacao":
            # Verifica campos de comparação
            menor_esperado = registro.predicao.get('menor_que_anterior_esperado')
            menor_real = resultado.get('menor_que_anterior')
            
            if menor_esperado and menor_real:
                # Aceita margem de erro de ±1
                return abs(menor_esperado - menor_real) <= 1
        
        elif registro.tipo_predicao == "soma":
            soma_esperada = registro.predicao.get('soma_esperada', [])
            soma_real = resultado.get('soma')
            
            if len(soma_esperada) == 2 and soma_real:
                return soma_esperada[0] <= soma_real <= soma_esperada[1]
        
        return False
    
    def _calcular_pontuacao(self, registro: RegistroPredicao, resultado: Dict) -> float:
        """Calcula pontuação de acerto (0.0 a 1.0)"""
        if registro.tipo_predicao == "reset_extremo_com_combinacoes":
            numeros_sorteados = resultado.get('numeros', [])
            combinacoes = registro.predicao.get('combinacoes_otimizadas', [])
            
            # Calcula acertos de cada combinação
            acertos = []
            for combinacao in combinacoes:
                acerto = len(set(combinacao) & set(numeros_sorteados))
                acertos.append(acerto / 15.0)  # Normaliza para 0-1
            
            # Retorna a melhor pontuação
            return max(acertos) if acertos else 0.0
        
        elif registro.tipo_predicao == "estado_comparacao":
            menor_esperado = registro.predicao.get('menor_que_anterior_esperado')
            menor_real = resultado.get('menor_que_anterior')
            
            if menor_esperado and menor_real:
                erro = abs(menor_esperado - menor_real)
                return max(0.0, 1.0 - (erro / 5.0))  # Pontuação decresce com erro
        
        return 0.0
    
    def gerar_relatorio_desempenho(self) -> Dict:
        """Gera relatório completo de desempenho"""
        if not self.registros:
            return {'erro': 'Nenhum registro disponível'}
        
        # Filtra registros com resultado
        registros_validados = [r for r in self.registros if r.resultado_real is not None]
        
        if not registros_validados:
            return {'erro': 'Nenhum registro validado ainda'}
        
        # Calcula métricas gerais
        total_predicoes = len(registros_validados)
        acertos = sum(1 for r in registros_validados if r.acertou)
        taxa_acerto = acertos / total_predicoes if total_predicoes > 0 else 0
        
        # Pontuação média
        pontuacoes = [r.pontuacao_acerto for r in registros_validados if r.pontuacao_acerto is not None]
        pontuacao_media = statistics.mean(pontuacoes) if pontuacoes else 0
        
        # Por tipo de predição
        por_tipo = {}
        for registro in registros_validados:
            tipo = registro.tipo_predicao
            if tipo not in por_tipo:
                por_tipo[tipo] = {'total': 0, 'acertos': 0, 'pontuacoes': []}
            
            por_tipo[tipo]['total'] += 1
            if registro.acertou:
                por_tipo[tipo]['acertos'] += 1
            if registro.pontuacao_acerto is not None:
                por_tipo[tipo]['pontuacoes'].append(registro.pontuacao_acerto)
        
        # Calcula taxa por tipo
        for tipo in por_tipo:
            dados = por_tipo[tipo]
            dados['taxa_acerto'] = dados['acertos'] / dados['total'] if dados['total'] > 0 else 0
            dados['pontuacao_media'] = statistics.mean(dados['pontuacoes']) if dados['pontuacoes'] else 0
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'metricas_gerais': {
                'total_predicoes': total_predicoes,
                'total_acertos': acertos,
                'taxa_acerto_geral': taxa_acerto,
                'pontuacao_media_geral': pontuacao_media
            },
            'por_tipo_predicao': por_tipo,
            'registros_pendentes': len(self.registros) - len(registros_validados)
        }
        
        # Salva métricas
        with open(self.arquivo_metricas, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        return relatorio
    
    def exibir_relatorio_completo(self):
        """Exibe relatório detalhado no console"""
        relatorio = self.gerar_relatorio_desempenho()
        
        if 'erro' in relatorio:
            print(f"⚠️ {relatorio['erro']}")
            return
        
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO DE DESEMPENHO DAS PREDIÇÕES")
        print("=" * 70)
        
        metricas = relatorio['metricas_gerais']
        print(f"📝 Total de predições validadas: {metricas['total_predicoes']}")
        print(f"✅ Total de acertos: {metricas['total_acertos']}")
        print(f"📈 Taxa de acerto geral: {metricas['taxa_acerto_geral']:.1%}")
        print(f"🎯 Pontuação média: {metricas['pontuacao_media_geral']:.3f}")
        print(f"⏳ Registros pendentes: {relatorio['registros_pendentes']}")
        
        print(f"\n📊 DESEMPENHO POR TIPO DE PREDIÇÃO:")
        print("-" * 50)
        
        for tipo, dados in relatorio['por_tipo_predicao'].items():
            print(f"\n🎯 {tipo}:")
            print(f"   📝 Total: {dados['total']}")
            print(f"   ✅ Acertos: {dados['acertos']}")
            print(f"   📈 Taxa: {dados['taxa_acerto']:.1%}")
            print(f"   🎯 Pontuação: {dados['pontuacao_media']:.3f}")
        
        print("\n" + "=" * 70)
    
    def validar_concurso_3505_exemplo(self):
        """Simula validação do concurso 3505 com resultado exemplo"""
        # Resultado exemplo (será substituído pelo real às 21:00)
        resultado_exemplo = {
            'concurso': 3505,
            'numeros': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            'menor_que_anterior': 11,
            'maior_que_anterior': 3,
            'igual': 1,
            'soma': 165,
            'repeticoes_posicao': 1
        }
        
        print("🔮 SIMULAÇÃO DE VALIDAÇÃO - CONCURSO 3505")
        print("=" * 50)
        print("⚠️ Este é um resultado EXEMPLO para teste")
        print("📊 Resultado real será inserido às 21:00")
        print("=" * 50)
        
        self.registrar_resultado_concurso(3505, resultado_exemplo)
        self.exibir_relatorio_completo()

def main():
    """Função principal"""
    monitor = MonitorValidacao()
    
    # Registra predição para 3505 se ainda não foi registrada
    registros_3505 = [r for r in monitor.registros if r.concurso == 3505]
    if not registros_3505:
        monitor.registrar_predicao_concurso_3505()
    else:
        print("📝 Predição para concurso 3505 já registrada")
    
    # Exibe status atual
    print(f"\n📊 MONITOR DE VALIDAÇÃO - STATUS ATUAL")
    print(f"📝 Total de registros: {len(monitor.registros)}")
    print(f"⏳ Aguardando resultado do concurso 3505 às 21:00")
    
    # Simula validação exemplo
    print(f"\n🧪 Executando simulação de validação...")
    monitor.validar_concurso_3505_exemplo()

if __name__ == "__main__":
    main()