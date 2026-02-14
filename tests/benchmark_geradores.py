#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🏆 BENCHMARK DE GERADORES - LOTOSCOPE
Testa performance e qualidade de todos os geradores disponíveis
"""

import sys
import os
import time
import ast
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import statistics

# Configurar paths
ROOT_DIR = Path(__file__).parent.parent
LOTOFACIL_DIR = ROOT_DIR / 'lotofacil_lite'
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR))
sys.path.insert(0, str(LOTOFACIL_DIR / 'utils'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'geradores'))
sys.path.insert(0, str(LOTOFACIL_DIR / 'ia'))

# Importar database config
try:
    from database_config import db_config
    DB_DISPONIVEL = True
except:
    DB_DISPONIVEL = False

class BenchmarkGeradores:
    """Classe para benchmark de geradores"""
    
    def __init__(self):
        self.resultados = []
        self.ultimo_resultado = None
        self.ultimos_numeros = None
        
        # Carregar último resultado do banco
        if DB_DISPONIVEL:
            self._carregar_ultimo_resultado()
    
    def _carregar_ultimo_resultado(self):
        """Carrega o último resultado da lotofácil"""
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 1 Concurso, N1, N2, N3, N4, N5, N6, N7, N8, 
                       N9, N10, N11, N12, N13, N14, N15
                FROM RESULTADOS_INT
                ORDER BY Concurso DESC
            """)
            row = cursor.fetchone()
            if row:
                self.ultimo_resultado = row[0]
                self.ultimos_numeros = set(row[1:16])
            cursor.close()
            conn.close()
            print(f"📊 Último concurso: {self.ultimo_resultado}")
            print(f"   Números: {sorted(self.ultimos_numeros)}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar resultado: {e}")
    
    def _contar_acertos(self, combinacao: set) -> int:
        """Conta acertos de uma combinação contra o último resultado"""
        if not self.ultimos_numeros:
            return 0
        return len(combinacao.intersection(self.ultimos_numeros))
    
    def _verificar_sintaxe(self, caminho: Path) -> bool:
        """Verifica se arquivo tem sintaxe válida"""
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            if conteudo.startswith('\ufeff'):
                conteudo = conteudo[1:]
            ast.parse(conteudo)
            return True
        except:
            return False
    
    def _encontrar_classe_gerador(self, modulo) -> Any:
        """Encontra a classe geradora no módulo"""
        classes_gerador = []
        for nome in dir(modulo):
            obj = getattr(modulo, nome)
            if isinstance(obj, type) and nome.lower().find('gerador') >= 0:
                classes_gerador.append((nome, obj))
            elif isinstance(obj, type) and any(x in nome.lower() for x in ['super', 'piramide', 'academico', 'combinacao', 'pipeline']):
                classes_gerador.append((nome, obj))
        return classes_gerador
    
    def _executar_gerador(self, classe, nome_classe: str, qtd_combinacoes: int = 5) -> Dict:
        """Executa um gerador e coleta métricas"""
        resultado = {
            'classe': nome_classe,
            'sucesso': False,
            'tempo_ms': 0,
            'combinacoes': [],
            'acertos': [],
            'media_acertos': 0,
            'max_acertos': 0,
            'erro': None
        }
        
        try:
            # Medir tempo de instanciação
            inicio = time.perf_counter()
            instancia = classe()
            tempo_init = (time.perf_counter() - inicio) * 1000
            
            # Procurar método de geração
            metodos_geracao = ['gerar', 'gerar_combinacoes', 'gerar_combinacao', 
                              'executar', 'run', 'processar', 'gerar_super_combinacoes']
            
            metodo_encontrado = None
            for metodo_nome in metodos_geracao:
                if hasattr(instancia, metodo_nome):
                    metodo_encontrado = getattr(instancia, metodo_nome)
                    break
            
            if not metodo_encontrado:
                resultado['erro'] = "Método de geração não encontrado"
                return resultado
            
            # Executar geração
            inicio = time.perf_counter()
            
            # Tentar diferentes assinaturas
            combinacoes = None
            try:
                combinacoes = metodo_encontrado(qtd_combinacoes)
            except TypeError:
                try:
                    combinacoes = metodo_encontrado()
                except:
                    pass
            
            tempo_geracao = (time.perf_counter() - inicio) * 1000
            
            if combinacoes is None:
                resultado['erro'] = "Geração retornou None"
                return resultado
            
            # Processar combinações
            if isinstance(combinacoes, (list, tuple)):
                for comb in combinacoes[:qtd_combinacoes]:
                    if isinstance(comb, (list, tuple, set)):
                        numeros = set(comb) if not isinstance(comb, set) else comb
                        # Filtrar apenas números válidos (1-25)
                        numeros = {n for n in numeros if isinstance(n, int) and 1 <= n <= 25}
                        if len(numeros) >= 15:
                            numeros = set(sorted(numeros)[:15])
                            resultado['combinacoes'].append(sorted(numeros))
                            acertos = self._contar_acertos(numeros)
                            resultado['acertos'].append(acertos)
                    elif isinstance(comb, dict) and 'numeros' in comb:
                        numeros = set(comb['numeros'])
                        resultado['combinacoes'].append(sorted(numeros))
                        acertos = self._contar_acertos(numeros)
                        resultado['acertos'].append(acertos)
            
            if resultado['acertos']:
                resultado['media_acertos'] = statistics.mean(resultado['acertos'])
                resultado['max_acertos'] = max(resultado['acertos'])
            
            resultado['tempo_ms'] = tempo_init + tempo_geracao
            resultado['sucesso'] = len(resultado['combinacoes']) > 0
            
        except Exception as e:
            resultado['erro'] = str(e)[:100]
        
        return resultado
    
    def benchmark_geradores(self):
        """Executa benchmark em todos os geradores"""
        print("\n" + "=" * 70)
        print("🏆 BENCHMARK DE GERADORES - LOTOSCOPE")
        print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        pasta_geradores = LOTOFACIL_DIR / 'geradores'
        
        if not pasta_geradores.exists():
            print("❌ Pasta de geradores não encontrada!")
            return
        
        # Listar geradores válidos
        geradores_validos = []
        for arquivo in pasta_geradores.glob('*.py'):
            if arquivo.name.startswith('__'):
                continue
            if self._verificar_sintaxe(arquivo):
                geradores_validos.append(arquivo)
        
        print(f"\n📋 Encontrados {len(geradores_validos)} geradores válidos")
        print("-" * 70)
        
        resultados_benchmark = []
        
        for i, arquivo in enumerate(geradores_validos, 1):
            nome_modulo = arquivo.stem
            print(f"\n[{i}/{len(geradores_validos)}] 📦 {nome_modulo}")
            
            try:
                # Importar módulo
                spec = importlib.util.spec_from_file_location(nome_modulo, arquivo)
                modulo = importlib.util.module_from_spec(spec)
                sys.modules[nome_modulo] = modulo
                spec.loader.exec_module(modulo)
                
                # Encontrar classes geradoras
                classes = self._encontrar_classe_gerador(modulo)
                
                if not classes:
                    print(f"   ⚠️ Nenhuma classe geradora encontrada")
                    continue
                
                for nome_classe, classe in classes:
                    print(f"   🔧 Testando: {nome_classe}")
                    resultado = self._executar_gerador(classe, nome_classe)
                    resultado['arquivo'] = nome_modulo
                    
                    if resultado['sucesso']:
                        print(f"      ✅ {len(resultado['combinacoes'])} combinações")
                        print(f"      ⏱️ {resultado['tempo_ms']:.1f}ms")
                        if resultado['acertos']:
                            print(f"      🎯 Média acertos: {resultado['media_acertos']:.1f}")
                            print(f"      🏆 Max acertos: {resultado['max_acertos']}")
                    else:
                        print(f"      ❌ {resultado['erro']}")
                    
                    resultados_benchmark.append(resultado)
                    
            except Exception as e:
                print(f"   ❌ Erro ao importar: {str(e)[:50]}")
        
        # Ranking final
        self._gerar_ranking(resultados_benchmark)
        
        return resultados_benchmark
    
    def _gerar_ranking(self, resultados: List[Dict]):
        """Gera ranking dos melhores geradores"""
        print("\n" + "=" * 70)
        print("🏆 RANKING DOS GERADORES")
        print("=" * 70)
        
        # Filtrar apenas os que funcionaram
        funcionando = [r for r in resultados if r['sucesso']]
        
        if not funcionando:
            print("❌ Nenhum gerador funcionou corretamente")
            return
        
        # Ordenar por média de acertos (decrescente) e tempo (crescente)
        funcionando.sort(key=lambda x: (-x['media_acertos'], x['tempo_ms']))
        
        print(f"\n📊 {len(funcionando)} geradores funcionais\n")
        
        print(f"{'Pos':<4} {'Gerador':<45} {'Acertos':<10} {'Tempo':<10}")
        print("-" * 70)
        
        for i, r in enumerate(funcionando[:15], 1):
            nome = f"{r['arquivo']}/{r['classe']}"[:44]
            acertos = f"{r['media_acertos']:.1f}" if r['acertos'] else "N/A"
            tempo = f"{r['tempo_ms']:.0f}ms"
            
            if i <= 3:
                medalha = ['🥇', '🥈', '🥉'][i-1]
                print(f"{medalha:<4} {nome:<45} {acertos:<10} {tempo:<10}")
            else:
                print(f"{i:<4} {nome:<45} {acertos:<10} {tempo:<10}")
        
        # Top 3 detalhado
        if funcionando:
            print("\n" + "=" * 70)
            print("🎯 TOP 3 - DETALHES")
            print("=" * 70)
            
            for i, r in enumerate(funcionando[:3], 1):
                medalha = ['🥇 OURO', '🥈 PRATA', '🥉 BRONZE'][i-1]
                print(f"\n{medalha}: {r['classe']}")
                print(f"   Arquivo: {r['arquivo']}.py")
                print(f"   Tempo: {r['tempo_ms']:.1f}ms")
                print(f"   Média acertos: {r['media_acertos']:.1f}")
                print(f"   Max acertos: {r['max_acertos']}")
                if r['combinacoes']:
                    print(f"   Exemplo: {r['combinacoes'][0]}")
        
        # Estatísticas gerais
        print("\n" + "=" * 70)
        print("📈 ESTATÍSTICAS GERAIS")
        print("=" * 70)
        
        medias = [r['media_acertos'] for r in funcionando if r['acertos']]
        tempos = [r['tempo_ms'] for r in funcionando]
        
        if medias:
            print(f"\n   Média geral de acertos: {statistics.mean(medias):.2f}")
            print(f"   Melhor média: {max(medias):.1f}")
            print(f"   Pior média: {min(medias):.1f}")
        
        if tempos:
            print(f"\n   Tempo médio: {statistics.mean(tempos):.1f}ms")
            print(f"   Mais rápido: {min(tempos):.1f}ms")
            print(f"   Mais lento: {max(tempos):.1f}ms")


def main():
    benchmark = BenchmarkGeradores()
    resultados = benchmark.benchmark_geradores()
    
    # Propostas de melhoria
    print("\n" + "=" * 70)
    print("💡 PROPOSTAS DE MELHORIA")
    print("=" * 70)
    
    print("""
    1. 🔄 PADRONIZAÇÃO DE INTERFACE
       - Criar interface base para todos os geradores
       - Método padrão: gerar(quantidade) -> List[Set[int]]
       - Facilita testes e comparações
    
    2. 📊 VALIDAÇÃO HISTÓRICA
       - Testar geradores contra N últimos concursos
       - Calcular taxa de acerto média real
       - Identificar padrões de sucesso
    
    3. 🧪 TESTES AUTOMATIZADOS
       - CI/CD para validar geradores
       - Regressão de performance
       - Alertas de degradação
    
    4. 🔧 CACHE INTELIGENTE
       - Cache de análises posicionais
       - Pré-computar estatísticas frequentes
       - Reduzir tempo de inicialização
    
    5. 🤖 ENSEMBLE DE GERADORES
       - Combinar top 3 geradores
       - Votação ponderada por performance
       - Meta-gerador otimizado
    
    6. 📈 MÉTRICAS AVANÇADAS
       - Tracking de performance ao longo do tempo
       - Dashboard de evolução
       - Relatórios automáticos
    """)
    
    return 0 if resultados else 1


if __name__ == "__main__":
    sys.exit(main())
