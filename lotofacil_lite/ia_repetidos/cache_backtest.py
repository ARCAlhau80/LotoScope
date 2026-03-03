# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CACHE DE BACKTESTS - LOTOSCOPE                            ║
║                                                                              ║
║  Sistema robusto de cache para evitar reexecução de backtests já realizados  ║
║  Inspirado no conceito de "session tracking" do MCP Context Hub              ║
║                                                                              ║
║  Funcionalidades:                                                            ║
║  • Cache persistente em JSON (sobrevive reinicializações)                    ║
║  • Hash único por configuração de backtest                                   ║
║  • Estatísticas de economia (tempo/processamento evitado)                    ║
║  • TTL configurável (resultados expiram após N dias)                         ║
║  • Busca por configuração similar (tolerância de parâmetros)                 ║
║                                                                              ║
║  Criado: 02/03/2026                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import time


class CacheBacktest:
    """
    Sistema de cache para backtests do LotoScope.
    
    Evita reexecução de backtests que já foram realizados com os mesmos parâmetros.
    """
    
    # Arquivo de cache
    CACHE_FILE = os.path.join(os.path.dirname(__file__), 'cache_backtests.json')
    
    # TTL padrão em dias (resultados mais antigos são considerados "stale")
    DEFAULT_TTL_DAYS = 30
    
    def __init__(self, ttl_days: int = DEFAULT_TTL_DAYS):
        self.ttl_days = ttl_days
        self.cache = self._carregar_cache()
        self.estatisticas = {
            'hits': 0,
            'misses': 0,
            'tempo_economizado_ms': 0,
            'sessao_inicio': datetime.now().isoformat()
        }
    
    def _carregar_cache(self) -> Dict:
        """Carrega cache do disco ou cria novo"""
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validar estrutura
                    if 'versao' in data and 'entradas' in data:
                        return data
            except Exception as e:
                print(f"   ⚠️ Aviso: Cache corrompido, criando novo ({e})")
        
        # Criar estrutura inicial
        return {
            'versao': '1.0',
            'criado_em': datetime.now().isoformat(),
            'ultima_atualizacao': datetime.now().isoformat(),
            'estatisticas_globais': {
                'total_backtests': 0,
                'hits_totais': 0,
                'tempo_total_economizado_ms': 0
            },
            'entradas': {}
        }
    
    def _salvar_cache(self):
        """Persiste cache no disco"""
        self.cache['ultima_atualizacao'] = datetime.now().isoformat()
        try:
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"   ⚠️ Erro ao salvar cache: {e}")
    
    def _gerar_hash(self, config: Dict) -> str:
        """
        Gera hash único para uma configuração de backtest.
        
        Parâmetros que definem unicidade:
        - Tipo de backtest (pool23, gerador_mestre, etc.)
        - Range de concursos
        - Filtros aplicados
        - Número de exclusões
        - Filtro probabilístico
        """
        # Normalizar configuração para hash consistente
        config_normalizada = {
            'tipo': config.get('tipo', 'unknown'),
            'concurso_inicio': config.get('concurso_inicio'),
            'concurso_fim': config.get('concurso_fim'),
            'nivel': config.get('nivel'),
            'qtd_exclusoes': config.get('qtd_exclusoes'),
            'filtro_probabilistico': config.get('filtro_probabilistico', 0),
            'filtros_ativos': sorted(config.get('filtros_ativos', [])),
            'exclusoes_manuais': sorted(config.get('exclusoes_manuais', [])) if config.get('exclusoes_manuais') else None
        }
        
        # Remover None para hash consistente
        config_limpa = {k: v for k, v in config_normalizada.items() if v is not None}
        
        # Gerar hash MD5
        config_str = json.dumps(config_limpa, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:16]
    
    def buscar(self, config: Dict) -> Optional[Dict]:
        """
        Busca resultado de backtest no cache.
        
        Retorna None se não encontrar ou se expirou.
        """
        hash_config = self._gerar_hash(config)
        
        if hash_config in self.cache['entradas']:
            entrada = self.cache['entradas'][hash_config]
            
            # Verificar TTL
            data_criacao = datetime.fromisoformat(entrada['criado_em'])
            if datetime.now() - data_criacao > timedelta(days=self.ttl_days):
                # Entrada expirada
                del self.cache['entradas'][hash_config]
                self._salvar_cache()
                self.estatisticas['misses'] += 1
                return None
            
            # Cache hit!
            self.estatisticas['hits'] += 1
            self.estatisticas['tempo_economizado_ms'] += entrada.get('tempo_execucao_ms', 0)
            self.cache['estatisticas_globais']['hits_totais'] += 1
            self.cache['estatisticas_globais']['tempo_total_economizado_ms'] += entrada.get('tempo_execucao_ms', 0)
            self._salvar_cache()
            
            return entrada['resultado']
        
        self.estatisticas['misses'] += 1
        return None
    
    def salvar(self, config: Dict, resultado: Dict, tempo_execucao_ms: int = 0):
        """
        Salva resultado de backtest no cache.
        """
        hash_config = self._gerar_hash(config)
        
        self.cache['entradas'][hash_config] = {
            'config': config,
            'resultado': resultado,
            'criado_em': datetime.now().isoformat(),
            'tempo_execucao_ms': tempo_execucao_ms,
            'acessos': 0
        }
        
        self.cache['estatisticas_globais']['total_backtests'] += 1
        self._salvar_cache()
    
    def buscar_similares(self, config: Dict, tolerancia: int = 5) -> List[Dict]:
        """
        Busca backtests similares (mesmo tipo, range próximo).
        
        Útil para sugerir resultados quando não há match exato.
        """
        tipo = config.get('tipo')
        concurso_inicio = config.get('concurso_inicio', 0)
        
        similares = []
        for hash_key, entrada in self.cache['entradas'].items():
            cfg = entrada.get('config', {})
            
            if cfg.get('tipo') == tipo:
                inicio_cache = cfg.get('concurso_inicio', 0)
                
                # Verificar se está dentro da tolerância
                if abs(inicio_cache - concurso_inicio) <= tolerancia:
                    similares.append({
                        'hash': hash_key,
                        'config': cfg,
                        'resultado': entrada['resultado'],
                        'distancia': abs(inicio_cache - concurso_inicio)
                    })
        
        # Ordenar por distância
        return sorted(similares, key=lambda x: x['distancia'])
    
    def limpar_expirados(self) -> int:
        """Remove entradas expiradas do cache. Retorna quantidade removida."""
        removidos = 0
        hashes_remover = []
        
        for hash_key, entrada in self.cache['entradas'].items():
            data_criacao = datetime.fromisoformat(entrada['criado_em'])
            if datetime.now() - data_criacao > timedelta(days=self.ttl_days):
                hashes_remover.append(hash_key)
        
        for h in hashes_remover:
            del self.cache['entradas'][h]
            removidos += 1
        
        if removidos > 0:
            self._salvar_cache()
        
        return removidos
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do cache"""
        # Estatísticas da sessão
        sessao = {
            'hits': self.estatisticas['hits'],
            'misses': self.estatisticas['misses'],
            'taxa_acerto': self.estatisticas['hits'] / max(1, self.estatisticas['hits'] + self.estatisticas['misses']) * 100,
            'tempo_economizado_ms': self.estatisticas['tempo_economizado_ms'],
            'tempo_economizado_formatado': self._formatar_tempo(self.estatisticas['tempo_economizado_ms'])
        }
        
        # Estatísticas globais
        globais = self.cache['estatisticas_globais'].copy()
        globais['entradas_ativas'] = len(self.cache['entradas'])
        globais['tempo_total_economizado_formatado'] = self._formatar_tempo(globais['tempo_total_economizado_ms'])
        
        return {
            'sessao': sessao,
            'globais': globais
        }
    
    def _formatar_tempo(self, ms: int) -> str:
        """Formata milissegundos em formato legível"""
        if ms < 1000:
            return f"{ms}ms"
        elif ms < 60000:
            return f"{ms/1000:.1f}s"
        else:
            minutos = ms // 60000
            segundos = (ms % 60000) // 1000
            return f"{minutos}min {segundos}s"
    
    def listar_backtests_salvos(self, tipo: str = None) -> List[Dict]:
        """Lista backtests salvos no cache, opcionalmente filtrado por tipo"""
        resultados = []
        
        for hash_key, entrada in self.cache['entradas'].items():
            cfg = entrada.get('config', {})
            
            if tipo is None or cfg.get('tipo') == tipo:
                resultados.append({
                    'hash': hash_key,
                    'tipo': cfg.get('tipo'),
                    'range': f"{cfg.get('concurso_inicio')}-{cfg.get('concurso_fim')}",
                    'nivel': cfg.get('nivel'),
                    'criado_em': entrada.get('criado_em'),
                    'resumo_roi': entrada.get('resultado', {}).get('roi_medio')
                })
        
        # Ordenar por data de criação (mais recente primeiro)
        return sorted(resultados, key=lambda x: x.get('criado_em', ''), reverse=True)
    
    def exportar_resumo_markdown(self) -> str:
        """Exporta resumo do cache em formato Markdown"""
        stats = self.obter_estatisticas()
        backtests = self.listar_backtests_salvos()
        
        md = []
        md.append("# 📊 Resumo do Cache de Backtests\n")
        md.append(f"**Atualizado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        
        md.append("\n## Estatísticas Globais\n")
        md.append(f"- Total de backtests salvos: **{stats['globais']['total_backtests']}**")
        md.append(f"- Entradas ativas: **{stats['globais']['entradas_ativas']}**")
        md.append(f"- Hits totais: **{stats['globais']['hits_totais']}**")
        md.append(f"- Tempo economizado: **{stats['globais']['tempo_total_economizado_formatado']}**\n")
        
        md.append("\n## Backtests Recentes\n")
        md.append("| Tipo | Range | Nível | ROI Médio | Data |")
        md.append("|------|-------|-------|-----------|------|")
        
        for bt in backtests[:20]:  # Últimos 20
            roi = f"{bt['resumo_roi']:.1f}%" if bt.get('resumo_roi') else "N/A"
            data = bt.get('criado_em', '')[:10] if bt.get('criado_em') else "N/A"
            md.append(f"| {bt.get('tipo', 'N/A')} | {bt.get('range', 'N/A')} | {bt.get('nivel', 'N/A')} | {roi} | {data} |")
        
        return "\n".join(md)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES UTILITÁRIAS PARA USO DIRETO
# ═══════════════════════════════════════════════════════════════════════════════

# Instância global do cache (singleton pattern)
_cache_instance = None


def get_cache() -> CacheBacktest:
    """Retorna instância única do cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheBacktest()
    return _cache_instance


def buscar_cache_backtest(config: Dict) -> Optional[Dict]:
    """Wrapper para buscar no cache"""
    return get_cache().buscar(config)


def salvar_cache_backtest(config: Dict, resultado: Dict, tempo_ms: int = 0):
    """Wrapper para salvar no cache"""
    get_cache().salvar(config, resultado, tempo_ms)


def exibir_estatisticas_cache():
    """Exibe estatísticas do cache no console"""
    cache = get_cache()
    stats = cache.obter_estatisticas()
    
    print("\n" + "═"*60)
    print("📊 ESTATÍSTICAS DO CACHE DE BACKTESTS")
    print("═"*60)
    
    print("\n🔄 SESSÃO ATUAL:")
    print(f"   • Cache hits: {stats['sessao']['hits']}")
    print(f"   • Cache misses: {stats['sessao']['misses']}")
    print(f"   • Taxa de acerto: {stats['sessao']['taxa_acerto']:.1f}%")
    print(f"   • Tempo economizado: {stats['sessao']['tempo_economizado_formatado']}")
    
    print("\n📈 HISTÓRICO GLOBAL:")
    print(f"   • Total de backtests salvos: {stats['globais']['total_backtests']}")
    print(f"   • Entradas ativas: {stats['globais']['entradas_ativas']}")
    print(f"   • Hits totais (todas sessões): {stats['globais']['hits_totais']}")
    print(f"   • Tempo total economizado: {stats['globais']['tempo_total_economizado_formatado']}")
    
    print("═"*60)


if __name__ == "__main__":
    # Teste do cache
    print("\n🧪 TESTE DO CACHE DE BACKTESTS\n")
    
    cache = CacheBacktest()
    
    # Configuração de teste
    config_teste = {
        'tipo': 'pool23_historico',
        'concurso_inicio': 3600,
        'concurso_fim': 3610,
        'nivel': 3,
        'qtd_exclusoes': 2,
        'filtro_probabilistico': 1
    }
    
    # Testar busca (deve retornar None)
    resultado = cache.buscar(config_teste)
    print(f"Busca inicial: {'HIT' if resultado else 'MISS'}")
    
    # Salvar resultado de teste
    resultado_teste = {
        'roi_medio': 14.5,
        'jackpots': 1,
        'total_concursos': 10
    }
    cache.salvar(config_teste, resultado_teste, tempo_execucao_ms=5000)
    print("Resultado salvo no cache")
    
    # Testar busca novamente (deve retornar)
    resultado = cache.buscar(config_teste)
    print(f"Busca após salvar: {'HIT' if resultado else 'MISS'}")
    
    # Exibir estatísticas
    exibir_estatisticas_cache()
