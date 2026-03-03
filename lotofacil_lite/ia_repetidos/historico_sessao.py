# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 HISTÓRICO DE SESSÃO - LOTOSCOPE                              ║
║                                                                              ║
║  Sistema de rastreamento de decisões e contexto por sessão.                  ║
║  Inspirado no "session delta tracking" do MCP Context Hub.                   ║
║                                                                              ║
║  Funcionalidades:                                                            ║
║  • Rastreia decisões tomadas (exclusões, filtros, níveis)                    ║
║  • Evita repetir alertas já mostrados                                        ║
║  • Mantém contexto de backtests executados                                   ║
║  • Persiste entre sessões (histórico completo)                               ║
║  • Permite "voltar no tempo" para ver decisões anteriores                    ║
║  • Gera relatórios de padrões de uso                                         ║
║                                                                              ║
║  Criado: 02/03/2026                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import uuid


class HistoricoSessao:
    """
    Rastreia decisões, alertas e contexto de uma sessão de trabalho no LotoScope.
    """
    
    # Arquivos de persistência
    BASE_DIR = os.path.dirname(__file__)
    SESSAO_ATUAL_FILE = os.path.join(BASE_DIR, 'sessao_atual.json')
    HISTORICO_FILE = os.path.join(BASE_DIR, 'historico_sessoes.json')
    
    # Tempo máximo de inatividade antes de considerar nova sessão (minutos)
    TIMEOUT_SESSAO_MINUTOS = 120
    
    def __init__(self):
        self.sessao_id = None
        self.inicio = None
        self.ultima_atividade = None
        
        # Dados da sessão atual
        self.decisoes: List[Dict] = []
        self.alertas_mostrados: Set[str] = set()
        self.backtests_executados: List[Dict] = []
        self.contexto: Dict = {}
        self.metricas: Dict = {
            'opcoes_acessadas': [],
            'tempo_total_minutos': 0,
            'combinacoes_geradas': 0,
            'arquivos_exportados': []
        }
        
        # Carregar ou criar sessão
        self._inicializar_sessao()
    
    def _inicializar_sessao(self):
        """Carrega sessão existente ou cria nova"""
        if os.path.exists(self.SESSAO_ATUAL_FILE):
            try:
                with open(self.SESSAO_ATUAL_FILE, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Verificar se sessão ainda é válida (não expirou)
                ultima = datetime.fromisoformat(dados.get('ultima_atividade', '2000-01-01'))
                if datetime.now() - ultima < timedelta(minutes=self.TIMEOUT_SESSAO_MINUTOS):
                    # Continuar sessão existente
                    self._carregar_sessao(dados)
                    return
                else:
                    # Sessão expirada - arquivar e criar nova
                    self._arquivar_sessao(dados)
            except Exception as e:
                print(f"   ⚠️ Erro ao carregar sessão: {e}")
        
        # Criar nova sessão
        self._criar_nova_sessao()
    
    def _criar_nova_sessao(self):
        """Cria uma nova sessão"""
        self.sessao_id = str(uuid.uuid4())[:8]
        self.inicio = datetime.now()
        self.ultima_atividade = datetime.now()
        self.decisoes = []
        self.alertas_mostrados = set()
        self.backtests_executados = []
        self.contexto = {}
        self.metricas = {
            'opcoes_acessadas': [],
            'tempo_total_minutos': 0,
            'combinacoes_geradas': 0,
            'arquivos_exportados': []
        }
        self._salvar_sessao()
    
    def _carregar_sessao(self, dados: Dict):
        """Carrega dados de sessão existente"""
        self.sessao_id = dados.get('sessao_id')
        self.inicio = datetime.fromisoformat(dados.get('inicio'))
        self.ultima_atividade = datetime.now()
        self.decisoes = dados.get('decisoes', [])
        self.alertas_mostrados = set(dados.get('alertas_mostrados', []))
        self.backtests_executados = dados.get('backtests_executados', [])
        self.contexto = dados.get('contexto', {})
        self.metricas = dados.get('metricas', {
            'opcoes_acessadas': [],
            'tempo_total_minutos': 0,
            'combinacoes_geradas': 0,
            'arquivos_exportados': []
        })
    
    def _salvar_sessao(self):
        """Persiste sessão atual no disco"""
        dados = {
            'sessao_id': self.sessao_id,
            'inicio': self.inicio.isoformat(),
            'ultima_atividade': datetime.now().isoformat(),
            'decisoes': self.decisoes,
            'alertas_mostrados': list(self.alertas_mostrados),
            'backtests_executados': self.backtests_executados,
            'contexto': self.contexto,
            'metricas': self.metricas
        }
        
        try:
            with open(self.SESSAO_ATUAL_FILE, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"   ⚠️ Erro ao salvar sessão: {e}")
    
    def _arquivar_sessao(self, dados: Dict):
        """Arquiva sessão expirada no histórico"""
        historico = self._carregar_historico()
        
        # Calcular duração
        inicio = datetime.fromisoformat(dados.get('inicio', datetime.now().isoformat()))
        fim = datetime.fromisoformat(dados.get('ultima_atividade', datetime.now().isoformat()))
        duracao_min = (fim - inicio).seconds // 60
        
        # Resumir sessão
        resumo = {
            'sessao_id': dados.get('sessao_id'),
            'data': inicio.strftime('%Y-%m-%d'),
            'inicio': inicio.strftime('%H:%M'),
            'duracao_minutos': duracao_min,
            'total_decisoes': len(dados.get('decisoes', [])),
            'total_backtests': len(dados.get('backtests_executados', [])),
            'combinacoes_geradas': dados.get('metricas', {}).get('combinacoes_geradas', 0),
            'resumo_decisoes': self._resumir_decisoes(dados.get('decisoes', []))
        }
        
        historico['sessoes'].append(resumo)
        historico['total_sessoes'] += 1
        historico['ultima_atualizacao'] = datetime.now().isoformat()
        
        self._salvar_historico(historico)
    
    def _carregar_historico(self) -> Dict:
        """Carrega histórico de sessões"""
        if os.path.exists(self.HISTORICO_FILE):
            try:
                with open(self.HISTORICO_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'versao': '1.0',
            'criado_em': datetime.now().isoformat(),
            'ultima_atualizacao': datetime.now().isoformat(),
            'total_sessoes': 0,
            'sessoes': []
        }
    
    def _salvar_historico(self, historico: Dict):
        """Salva histórico de sessões"""
        try:
            with open(self.HISTORICO_FILE, 'w', encoding='utf-8') as f:
                json.dump(historico, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"   ⚠️ Erro ao salvar histórico: {e}")
    
    def _resumir_decisoes(self, decisoes: List[Dict]) -> Dict:
        """Gera resumo das decisões de uma sessão"""
        resumo = {
            'exclusoes': [],
            'niveis_usados': set(),
            'filtros_usados': set()
        }
        
        for d in decisoes:
            if d.get('tipo') == 'exclusao':
                resumo['exclusoes'].extend(d.get('numeros', []))
            elif d.get('tipo') == 'nivel':
                resumo['niveis_usados'].add(d.get('valor'))
            elif d.get('tipo') == 'filtro':
                resumo['filtros_usados'].add(d.get('nome'))
        
        # Converter sets para listas para JSON
        resumo['niveis_usados'] = list(resumo['niveis_usados'])
        resumo['filtros_usados'] = list(resumo['filtros_usados'])
        resumo['exclusoes'] = list(set(resumo['exclusoes']))  # Remover duplicatas
        
        return resumo
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MÉTODOS PÚBLICOS PARA REGISTRAR EVENTOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def registrar_decisao(self, tipo: str, descricao: str, dados: Dict = None):
        """
        Registra uma decisão tomada pelo usuário.
        
        Tipos comuns:
        - 'exclusao': Números excluídos
        - 'nivel': Nível de filtro escolhido
        - 'filtro': Filtro ativado/desativado
        - 'estrategia': Estratégia selecionada
        - 'geracao': Combinações geradas
        - 'exportacao': Arquivo exportado
        """
        decisao = {
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            'descricao': descricao,
            'dados': dados or {}
        }
        
        self.decisoes.append(decisao)
        self.ultima_atividade = datetime.now()
        self._salvar_sessao()
    
    def registrar_exclusao(self, numeros: List[int], motivo: str = None):
        """Atalho para registrar exclusão de números"""
        self.registrar_decisao(
            tipo='exclusao',
            descricao=f"Excluídos: {numeros}" + (f" ({motivo})" if motivo else ""),
            dados={'numeros': numeros, 'motivo': motivo}
        )
    
    def registrar_nivel(self, nivel: int, qtd_combinacoes: int = None):
        """Atalho para registrar escolha de nível"""
        self.registrar_decisao(
            tipo='nivel',
            descricao=f"Nível {nivel} selecionado" + (f" ({qtd_combinacoes:,} combos)" if qtd_combinacoes else ""),
            dados={'valor': nivel, 'combinacoes': qtd_combinacoes}
        )
    
    def registrar_geracao(self, quantidade: int, arquivo: str = None, nivel: int = None):
        """Registra geração de combinações"""
        self.metricas['combinacoes_geradas'] += quantidade
        if arquivo:
            self.metricas['arquivos_exportados'].append(arquivo)
        
        self.registrar_decisao(
            tipo='geracao',
            descricao=f"Geradas {quantidade:,} combinações" + (f" (Nível {nivel})" if nivel else ""),
            dados={'quantidade': quantidade, 'arquivo': arquivo, 'nivel': nivel}
        )
    
    def registrar_backtest(self, config: Dict, resultado: Dict):
        """Registra execução de backtest"""
        backtest = {
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'resultado_resumo': {
                'roi_medio': resultado.get('roi_medio'),
                'jackpots': resultado.get('jackpots'),
                'lucro_total': resultado.get('lucro_total')
            }
        }
        
        self.backtests_executados.append(backtest)
        self._salvar_sessao()
    
    def registrar_opcao_acessada(self, opcao: str):
        """Registra qual opção do menu foi acessada"""
        if opcao not in self.metricas['opcoes_acessadas']:
            self.metricas['opcoes_acessadas'].append(opcao)
        self.ultima_atividade = datetime.now()
        self._salvar_sessao()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONTROLE DE ALERTAS (evita repetir)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def alerta_ja_mostrado(self, alerta_id: str) -> bool:
        """Verifica se um alerta já foi mostrado nesta sessão"""
        return alerta_id in self.alertas_mostrados
    
    def registrar_alerta(self, alerta_id: str):
        """Marca alerta como já mostrado"""
        self.alertas_mostrados.add(alerta_id)
        self._salvar_sessao()
    
    def mostrar_alerta_uma_vez(self, alerta_id: str, mensagem: str) -> bool:
        """
        Mostra alerta apenas se ainda não foi mostrado nesta sessão.
        Retorna True se mostrou, False se já tinha sido mostrado.
        """
        if self.alerta_ja_mostrado(alerta_id):
            return False
        
        print(mensagem)
        self.registrar_alerta(alerta_id)
        return True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXTO (dados que persistem na sessão)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def definir_contexto(self, chave: str, valor: Any):
        """Define valor no contexto da sessão"""
        self.contexto[chave] = valor
        self._salvar_sessao()
    
    def obter_contexto(self, chave: str, padrao: Any = None) -> Any:
        """Obtém valor do contexto da sessão"""
        return self.contexto.get(chave, padrao)
    
    def contexto_existe(self, chave: str) -> bool:
        """Verifica se chave existe no contexto"""
        return chave in self.contexto
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONSULTAS E RELATÓRIOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def obter_ultimas_decisoes(self, n: int = 10) -> List[Dict]:
        """Retorna as últimas N decisões"""
        return self.decisoes[-n:]
    
    def obter_exclusoes_sessao(self) -> List[int]:
        """Retorna todos os números excluídos nesta sessão"""
        exclusoes = []
        for d in self.decisoes:
            if d.get('tipo') == 'exclusao':
                exclusoes.extend(d.get('dados', {}).get('numeros', []))
        return list(set(exclusoes))
    
    def obter_resumo_sessao(self) -> Dict:
        """Retorna resumo da sessão atual"""
        duracao = (datetime.now() - self.inicio).seconds // 60
        
        return {
            'sessao_id': self.sessao_id,
            'inicio': self.inicio.strftime('%d/%m/%Y %H:%M'),
            'duracao_minutos': duracao,
            'total_decisoes': len(self.decisoes),
            'total_backtests': len(self.backtests_executados),
            'combinacoes_geradas': self.metricas['combinacoes_geradas'],
            'arquivos_exportados': len(self.metricas['arquivos_exportados']),
            'opcoes_acessadas': len(self.metricas['opcoes_acessadas']),
            'exclusoes_acumuladas': self.obter_exclusoes_sessao()
        }
    
    def exibir_resumo_sessao(self):
        """Exibe resumo da sessão no console"""
        resumo = self.obter_resumo_sessao()
        
        print("\n" + "═"*60)
        print("📋 RESUMO DA SESSÃO ATUAL")
        print("═"*60)
        print(f"   🆔 ID: {resumo['sessao_id']}")
        print(f"   🕐 Início: {resumo['inicio']}")
        print(f"   ⏱️  Duração: {resumo['duracao_minutos']} minutos")
        print("─"*60)
        print(f"   📝 Decisões registradas: {resumo['total_decisoes']}")
        print(f"   🔬 Backtests executados: {resumo['total_backtests']}")
        print(f"   🎲 Combinações geradas: {resumo['combinacoes_geradas']:,}")
        print(f"   📁 Arquivos exportados: {resumo['arquivos_exportados']}")
        print(f"   📌 Opções acessadas: {resumo['opcoes_acessadas']}")
        
        if resumo['exclusoes_acumuladas']:
            print(f"   ❌ Exclusões acumuladas: {sorted(resumo['exclusoes_acumuladas'])}")
        
        print("═"*60)
    
    def exibir_timeline_decisoes(self, n: int = 10):
        """Exibe timeline das últimas decisões"""
        decisoes = self.obter_ultimas_decisoes(n)
        
        print("\n" + "═"*60)
        print("📜 TIMELINE DE DECISÕES")
        print("═"*60)
        
        if not decisoes:
            print("   Nenhuma decisão registrada ainda.")
        else:
            for i, d in enumerate(reversed(decisoes), 1):
                ts = datetime.fromisoformat(d['timestamp']).strftime('%H:%M:%S')
                tipo = d.get('tipo', 'desconhecido')
                desc = d.get('descricao', '')
                
                # Ícone por tipo
                icones = {
                    'exclusao': '❌',
                    'nivel': '📊',
                    'filtro': '🔧',
                    'geracao': '🎲',
                    'estrategia': '🎯',
                    'exportacao': '📁'
                }
                icone = icones.get(tipo, '📝')
                
                print(f"   {i}. [{ts}] {icone} {desc}")
        
        print("═"*60)
    
    def obter_padroes_uso(self) -> Dict:
        """Analisa padrões de uso baseado no histórico"""
        historico = self._carregar_historico()
        
        if not historico['sessoes']:
            return {'mensagem': 'Histórico insuficiente para análise'}
        
        # Análise básica
        total_sessoes = len(historico['sessoes'])
        total_decisoes = sum(s.get('total_decisoes', 0) for s in historico['sessoes'])
        total_combinacoes = sum(s.get('combinacoes_geradas', 0) for s in historico['sessoes'])
        
        # Exclusões mais frequentes
        todas_exclusoes = []
        for s in historico['sessoes']:
            todas_exclusoes.extend(s.get('resumo_decisoes', {}).get('exclusoes', []))
        
        from collections import Counter
        exclusoes_freq = Counter(todas_exclusoes).most_common(10)
        
        # Níveis mais usados
        todos_niveis = []
        for s in historico['sessoes']:
            todos_niveis.extend(s.get('resumo_decisoes', {}).get('niveis_usados', []))
        
        niveis_freq = Counter(todos_niveis).most_common(5)
        
        return {
            'total_sessoes': total_sessoes,
            'media_decisoes_por_sessao': total_decisoes / max(1, total_sessoes),
            'total_combinacoes_historico': total_combinacoes,
            'numeros_mais_excluidos': exclusoes_freq,
            'niveis_preferidos': niveis_freq
        }
    
    def exibir_padroes_uso(self):
        """Exibe padrões de uso no console"""
        padroes = self.obter_padroes_uso()
        
        print("\n" + "═"*60)
        print("📊 PADRÕES DE USO (HISTÓRICO)")
        print("═"*60)
        
        if 'mensagem' in padroes:
            print(f"   {padroes['mensagem']}")
        else:
            print(f"   📌 Total de sessões: {padroes['total_sessoes']}")
            print(f"   📝 Média de decisões/sessão: {padroes['media_decisoes_por_sessao']:.1f}")
            print(f"   🎲 Total combinações geradas: {padroes['total_combinacoes_historico']:,}")
            
            if padroes['numeros_mais_excluidos']:
                print("\n   ❌ Números mais excluídos:")
                for num, freq in padroes['numeros_mais_excluidos'][:5]:
                    print(f"      • Número {num}: {freq}x")
            
            if padroes['niveis_preferidos']:
                print("\n   📊 Níveis preferidos:")
                for nivel, freq in padroes['niveis_preferidos']:
                    print(f"      • Nível {nivel}: {freq}x")
        
        print("═"*60)
    
    def finalizar_sessao(self):
        """Arquiva sessão atual e cria nova"""
        # Calcular tempo total
        duracao = (datetime.now() - self.inicio).seconds // 60
        self.metricas['tempo_total_minutos'] = duracao
        self._salvar_sessao()
        
        # Arquivar
        with open(self.SESSAO_ATUAL_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        self._arquivar_sessao(dados)
        
        # Criar nova
        self._criar_nova_sessao()
        print("   ✅ Sessão finalizada e arquivada!")


# ═══════════════════════════════════════════════════════════════════════════════
# INSTÂNCIA GLOBAL (singleton)
# ═══════════════════════════════════════════════════════════════════════════════

_sessao_instance = None


def get_sessao() -> HistoricoSessao:
    """Retorna instância única do histórico de sessão"""
    global _sessao_instance
    if _sessao_instance is None:
        _sessao_instance = HistoricoSessao()
    return _sessao_instance


# Atalhos para funções comuns
def registrar_decisao(tipo: str, descricao: str, dados: Dict = None):
    """Wrapper para registrar decisão"""
    get_sessao().registrar_decisao(tipo, descricao, dados)


def registrar_exclusao(numeros: List[int], motivo: str = None):
    """Wrapper para registrar exclusão"""
    get_sessao().registrar_exclusao(numeros, motivo)


def alerta_uma_vez(alerta_id: str, mensagem: str) -> bool:
    """Wrapper para mostrar alerta uma vez"""
    return get_sessao().mostrar_alerta_uma_vez(alerta_id, mensagem)


def obter_contexto(chave: str, padrao: Any = None) -> Any:
    """Wrapper para obter contexto"""
    return get_sessao().obter_contexto(chave, padrao)


def definir_contexto(chave: str, valor: Any):
    """Wrapper para definir contexto"""
    get_sessao().definir_contexto(chave, valor)


if __name__ == "__main__":
    # Teste do histórico de sessão
    print("\n🧪 TESTE DO HISTÓRICO DE SESSÃO\n")
    
    sessao = HistoricoSessao()
    
    # Registrar algumas decisões
    sessao.registrar_exclusao([2, 5], "Fora de ambas as combos")
    sessao.registrar_nivel(3, 100000)
    sessao.registrar_geracao(1000, "pool23_nivel3_20260302.txt", 3)
    
    # Testar alerta
    mostrou = sessao.mostrar_alerta_uma_vez(
        "teste_alerta_1", 
        "   ⚠️ Este é um alerta de teste!"
    )
    print(f"   Alerta mostrado: {mostrou}")
    
    mostrou = sessao.mostrar_alerta_uma_vez(
        "teste_alerta_1", 
        "   ⚠️ Este alerta NÃO deveria aparecer!"
    )
    print(f"   Alerta repetido: {mostrou}")
    
    # Exibir resumos
    sessao.exibir_resumo_sessao()
    sessao.exibir_timeline_decisoes()
    sessao.exibir_padroes_uso()
