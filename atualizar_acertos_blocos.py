#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ATUALIZADOR OTIMIZADO - COMBINACOES_LOTOFACIL (15 números)
=============================================================
Versão otimizada que processa em blocos menores para evitar
estouro de log do banco de dados.

OTIMIZAÇÕES:
- Processa em lotes de 10 concursos
- Faz checkpoint a cada lote
- Usa SIMPLE recovery para evitar crescimento do log

Autor: AR CALHAU
Data: 15/02/2026
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Optional, Dict, List

# Adicionar paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'lotofacil_lite'))
sys.path.insert(0, os.path.join(script_dir, 'lotofacil_lite', 'utils'))

try:
    from database_config import DatabaseConfig
    print("✅ DatabaseConfig importado")
except ImportError:
    try:
        from lotofacil_lite.utils.database_config import DatabaseConfig
        print("✅ DatabaseConfig importado (via lotofacil_lite.utils)")
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        sys.exit(1)


class AtualizadorOtimizado:
    """Versão otimizada que processa em blocos menores."""
    
    def __init__(self, tabela: str, num_colunas: int = 15):
        """
        Args:
            tabela: Nome da tabela (COMBINACOES_LOTOFACIL ou COMBINACOES_LOTOFACIL20_COMPLETO)
            num_colunas: Número de colunas N (15 ou 20)
        """
        self.db = DatabaseConfig()
        self.tabela = tabela
        self.num_colunas = num_colunas
        self.niveis = [11, 12, 13, 14, 15]
        self.estatisticas = {n: 0 for n in self.niveis}
        self.concursos_processados = 0
    
    def checkpoint(self):
        """Força checkpoint no banco para liberar log."""
        try:
            self.db.execute_command("CHECKPOINT")
        except:
            pass
    
    def obter_concursos(self, desde: int, limite: int = 10) -> List[Dict]:
        """Obtém um bloco de concursos."""
        query = f"""
        SELECT TOP {limite}
            Concurso, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
        FROM Resultados_INT 
        WHERE Concurso > {desde}
        ORDER BY Concurso ASC
        """
        resultado = self.db.execute_query_dataframe(query)
        
        concursos = []
        for _, row in resultado.iterrows():
            concursos.append({
                'concurso': int(row['Concurso']),
                'numeros': [int(row[f'N{i}']) for i in range(1, 16)]
            })
        return concursos
    
    def processar_concurso(self, concurso: int, numeros: List[int]) -> Dict[int, int]:
        """Processa um único concurso."""
        numeros_str = ','.join(map(str, numeros))
        resultados = {}
        
        # Montar SQL de contagem baseado no número de colunas
        if self.num_colunas == 15:
            sql_valores = "(N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)"
        else:  # 20 colunas
            sql_valores = "(N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)"
        
        sql_contar = f"""
        (SELECT COUNT(*) FROM (VALUES {sql_valores}) AS comb(numero)
         WHERE numero IN ({numeros_str}))
        """
        
        for nivel in self.niveis:
            sql_update = f"""
            UPDATE {self.tabela}
            SET Acertos_{nivel} = Acertos_{nivel} + 1,
                Ultimo_Acertos_{nivel} = {concurso}
            WHERE {sql_contar} = {nivel}
            """
            
            try:
                self.db.execute_command(sql_update)
                # Não vamos contar linhas afetadas para economizar tempo
                resultados[nivel] = 0
            except Exception as e:
                print(f"   ⚠️ Erro nível {nivel}: {e}")
                resultados[nivel] = 0
        
        return resultados
    
    def atualizar_controle(self, concurso: int):
        """Atualiza campo de controle."""
        sql = f"""
        UPDATE {self.tabela}
        SET UltimoConcursoAtualizado = {concurso}
        WHERE UltimoConcursoAtualizado < {concurso}
        """
        self.db.execute_command(sql)
    
    def obter_ultimo_atualizado(self) -> int:
        """Obtém menor valor de UltimoConcursoAtualizado."""
        query = f"SELECT ISNULL(MIN(UltimoConcursoAtualizado), 0) as min_atualizado FROM {self.tabela}"
        resultado = self.db.execute_query_dataframe(query)
        return int(resultado.iloc[0]['min_atualizado'])
    
    def obter_ultimo_concurso(self) -> int:
        """Obtém último concurso disponível."""
        query = "SELECT MAX(Concurso) as max_concurso FROM Resultados_INT"
        resultado = self.db.execute_query_dataframe(query)
        return int(resultado.iloc[0]['max_concurso'])
    
    def resetar_contagens(self):
        """Reseta todas as contagens."""
        print("🔄 Resetando contagens...")
        sql = f"""
        UPDATE {self.tabela} SET 
            Acertos_11 = 0, Acertos_12 = 0, Acertos_13 = 0, Acertos_14 = 0, Acertos_15 = 0,
            Ultimo_Acertos_11 = NULL, Ultimo_Acertos_12 = NULL, Ultimo_Acertos_13 = NULL,
            Ultimo_Acertos_14 = NULL, Ultimo_Acertos_15 = NULL,
            UltimoConcursoAtualizado = 0
        """
        self.db.execute_command(sql)
        self.checkpoint()
        print("✅ Contagens resetadas")
    
    def executar(self, desde: int = 0, tamanho_bloco: int = 10, reset: bool = False):
        """
        Executa processamento em blocos.
        
        Args:
            desde: Processar a partir deste concurso (0 = automático)
            tamanho_bloco: Concursos por bloco
            reset: Se True, zera contagens antes
        """
        print(f"\n{'='*70}")
        print(f"🔄 PROCESSAMENTO EM BLOCOS - {self.tabela}")
        print(f"{'='*70}")
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Colunas: N1-N{self.num_colunas}")
        print(f"📦 Tamanho do bloco: {tamanho_bloco} concursos")
        
        if reset:
            self.resetar_contagens()
            desde = 0
        
        if desde == 0:
            desde = self.obter_ultimo_atualizado()
        
        ultimo_concurso = self.obter_ultimo_concurso()
        total_pendentes = ultimo_concurso - desde
        
        print(f"\n📊 Status:")
        print(f"   • Último atualizado: {desde}")
        print(f"   • Último disponível: {ultimo_concurso}")
        print(f"   • Concursos pendentes: {total_pendentes}")
        
        if total_pendentes <= 0:
            print("\n✅ Base já está atualizada!")
            return
        
        print(f"\n⏳ Processando...")
        inicio = datetime.now()
        
        concurso_atual = desde
        blocos_processados = 0
        
        while concurso_atual < ultimo_concurso:
            # Obter bloco de concursos
            concursos = self.obter_concursos(concurso_atual, tamanho_bloco)
            
            if not concursos:
                break
            
            # Processar cada concurso do bloco
            for conc in concursos:
                self.processar_concurso(conc['concurso'], conc['numeros'])
                self.concursos_processados += 1
            
            # Atualizar controle com o último do bloco
            ultimo_do_bloco = concursos[-1]['concurso']
            self.atualizar_controle(ultimo_do_bloco)
            
            # Checkpoint a cada bloco
            self.checkpoint()
            
            concurso_atual = ultimo_do_bloco
            blocos_processados += 1
            
            # Mostrar progresso a cada 10 blocos
            if blocos_processados % 10 == 0:
                progresso = (concurso_atual - desde) / total_pendentes * 100
                tempo_decorrido = (datetime.now() - inicio).total_seconds()
                print(f"   📍 Bloco {blocos_processados} | Concurso {concurso_atual} | {progresso:.1f}% | {tempo_decorrido:.0f}s")
        
        tempo_total = (datetime.now() - inicio).total_seconds()
        
        print(f"\n{'='*70}")
        print(f"📋 RELATÓRIO FINAL")
        print(f"{'='*70}")
        print(f"✅ Concursos processados: {self.concursos_processados}")
        print(f"📦 Blocos processados: {blocos_processados}")
        print(f"⏱️ Tempo total: {tempo_total:.1f}s ({tempo_total/60:.1f} min)")
        print(f"📈 Velocidade: {self.concursos_processados/tempo_total:.1f} concursos/segundo")
        
        # Estatísticas finais
        query_stats = f"""
        SELECT 
            SUM(Acertos_15) as t15, SUM(Acertos_14) as t14, SUM(Acertos_13) as t13,
            SUM(Acertos_12) as t12, SUM(Acertos_11) as t11,
            MAX(UltimoConcursoAtualizado) as ultimo
        FROM {self.tabela}
        """
        stats = self.db.execute_query_dataframe(query_stats).iloc[0]
        
        print(f"\n📈 Estado final:")
        print(f"   • Acertos 15: {int(stats['t15']):,}")
        print(f"   • Acertos 14: {int(stats['t14']):,}")
        print(f"   • Acertos 13: {int(stats['t13']):,}")
        print(f"   • Acertos 12: {int(stats['t12']):,}")
        print(f"   • Acertos 11: {int(stats['t11']):,}")
        print(f"   • Último concurso: {int(stats['ultimo'])}")
        print(f"\n{'='*70}")
        print(f"✅ PROCESSAMENTO CONCLUÍDO!")
        print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description='Atualizador otimizado em blocos')
    parser.add_argument('--tabela', choices=['15', '20'], default='15',
                        help='Tabela: 15=COMBINACOES_LOTOFACIL, 20=COMBINACOES_LOTOFACIL20_COMPLETO')
    parser.add_argument('--bloco', type=int, default=10, help='Tamanho do bloco (padrão: 10)')
    parser.add_argument('--desde', type=int, default=0, help='Processar desde concurso')
    parser.add_argument('--reset', action='store_true', help='Resetar contagens antes')
    
    args = parser.parse_args()
    
    if args.tabela == '15':
        tabela = 'COMBINACOES_LOTOFACIL'
        num_colunas = 15
    else:
        tabela = 'COMBINACOES_LOTOFACIL20_COMPLETO'
        num_colunas = 20
    
    atualizador = AtualizadorOtimizado(tabela, num_colunas)
    
    try:
        atualizador.executar(desde=args.desde, tamanho_bloco=args.bloco, reset=args.reset)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido! Execute novamente para continuar.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
