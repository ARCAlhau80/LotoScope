#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 ATUALIZADOR DE ACERTOS - COMBINACOES_LOTOFACIL (15 números)
==============================================================
Processa acertos para a tabela de combinações de 15 números.

FUNCIONALIDADES:
- Na PRIMEIRA execução: processa todo o histórico desde o concurso 1
- Nas execuções SEGUINTES: processa apenas a partir do UltimoConcursoAtualizado
- Atualiza contagem de acertos (Acertos_11 a Acertos_15)
- Rastreia último concurso de cada tipo (Ultimo_Acertos_11 a Ultimo_Acertos_15)
- Atualiza campo de controle UltimoConcursoAtualizado

MODOS DE EXECUÇÃO:
  python atualizar_acertos_lotofacil15.py           # Incremental automático
  python atualizar_acertos_lotofacil15.py --full    # Forçar processamento completo
  python atualizar_acertos_lotofacil15.py --desde X # Processar a partir do concurso X

DIFERENÇA DA TABELA DE 20 NÚMEROS:
- Combinações de 15 números (aposta padrão)
- Acerto é comparação direta: combinação == sorteio (15 números = 15 acertos)

Autor: AR CALHAU
Data: 15/02/2026
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Adicionar paths necessários
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


class AtualizadorAcertosLotofacil15:
    """
    Classe responsável pela atualização de acertos para combinações de 15 números.
    """
    
    TABELA = 'COMBINACOES_LOTOFACIL'
    NIVEIS_ACERTOS = [10, 11, 12, 13, 14, 15]
    
    def __init__(self):
        self.db = DatabaseConfig()
        self.estatisticas = {
            'combinacoes_processadas': 0,
            'concursos_processados': 0,
            'tempo_total': 0,
            'atualizacoes': {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
        }
    
    def verificar_estrutura_tabela(self) -> bool:
        """Verifica se todas as colunas necessárias existem."""
        print("\n🔍 Verificando estrutura da tabela COMBINACOES_LOTOFACIL...")
        
        colunas_necessarias = [
            'Acertos_10', 'Acertos_11', 'Acertos_12', 'Acertos_13', 'Acertos_14', 'Acertos_15',
            'Ultimo_Acertos_10', 'Ultimo_Acertos_11', 'Ultimo_Acertos_12', 'Ultimo_Acertos_13',
            'Ultimo_Acertos_14', 'Ultimo_Acertos_15', 'UltimoConcursoAtualizado'
        ]
        
        query = f"""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{self.TABELA}'
        AND COLUMN_NAME IN ({','.join(f"'{c}'" for c in colunas_necessarias)})
        """
        
        resultado = self.db.execute_query_dataframe(query)
        colunas_existentes = set(resultado['COLUMN_NAME'].tolist())
        colunas_faltantes = set(colunas_necessarias) - colunas_existentes
        
        if colunas_faltantes:
            print(f"❌ Colunas faltantes: {', '.join(colunas_faltantes)}")
            print("💡 Execute primeiro: adicionar_colunas_acertos_lotofacil15.sql")
            return False
        
        print("✅ Todas as colunas necessárias existem")
        return True
    
    def obter_menor_concurso_atualizado(self) -> int:
        """Obtém o menor valor de UltimoConcursoAtualizado."""
        query = f"""
        SELECT ISNULL(MIN(UltimoConcursoAtualizado), 0) as min_atualizado
        FROM {self.TABELA}
        """
        resultado = self.db.execute_query_dataframe(query)
        return int(resultado.iloc[0]['min_atualizado'])
    
    def obter_ultimo_concurso_disponivel(self) -> int:
        """Obtém o último concurso disponível na tabela Resultados_INT."""
        query = "SELECT MAX(Concurso) as max_concurso FROM Resultados_INT"
        resultado = self.db.execute_query_dataframe(query)
        return int(resultado.iloc[0]['max_concurso'])
    
    def obter_primeiro_concurso(self) -> int:
        """Obtém o primeiro concurso da tabela Resultados_INT."""
        query = "SELECT MIN(Concurso) as min_concurso FROM Resultados_INT"
        resultado = self.db.execute_query_dataframe(query)
        return int(resultado.iloc[0]['min_concurso'])
    
    def obter_total_combinacoes(self) -> int:
        """Obtém o total de combinações na tabela."""
        query = f"SELECT COUNT(*) as total FROM {self.TABELA}"
        resultado = self.db.execute_query_dataframe(query)
        return int(resultado.iloc[0]['total'])
    
    def obter_concursos_pendentes(self, desde_concurso: int) -> List[Dict]:
        """Obtém lista de concursos pendentes de processamento."""
        query = f"""
        SELECT 
            Concurso,
            N1, N2, N3, N4, N5, N6, N7, N8, N9, N10,
            N11, N12, N13, N14, N15
        FROM Resultados_INT 
        WHERE Concurso > {desde_concurso}
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
    
    def processar_concurso_sql(self, concurso: int, numeros: List[int]) -> Dict[int, int]:
        """
        Processa um concurso usando SQL puro.
        Para combinações de 15 números, comparamos diretamente os 15 números.
        """
        numeros_str = ','.join(map(str, numeros))
        resultados = {}
        
        # SQL para contar acertos de uma combinação de 15 números
        # Conta quantos números da combinação estão no sorteio
        sql_contar_acertos = f"""
        (SELECT COUNT(*)
         FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                      (N11),(N12),(N13),(N14),(N15)) AS comb(numero)
         WHERE numero IN ({numeros_str}))
        """
        
        # Processar cada nível de acerto
        for nivel in self.NIVEIS_ACERTOS:
            sql_update = f"""
            UPDATE {self.TABELA}
            SET 
                Acertos_{nivel} = Acertos_{nivel} + 1,
                Ultimo_Acertos_{nivel} = {concurso}
            WHERE {sql_contar_acertos} = {nivel}
            """
            
            try:
                # Conta quantas linhas serão afetadas
                sql_count = f"""
                SELECT COUNT(*) as qtd
                FROM {self.TABELA}
                WHERE {sql_contar_acertos} = {nivel}
                """
                
                count_result = self.db.execute_query_dataframe(sql_count)
                qtd_afetadas = int(count_result.iloc[0]['qtd'])
                
                if qtd_afetadas > 0:
                    self.db.execute_command(sql_update)
                    resultados[nivel] = qtd_afetadas
                    self.estatisticas['atualizacoes'][nivel] += qtd_afetadas
                else:
                    resultados[nivel] = 0
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar nível {nivel}: {e}")
                resultados[nivel] = 0
        
        return resultados
    
    def atualizar_controle_concurso(self, concurso: int):
        """Atualiza o campo UltimoConcursoAtualizado."""
        sql_update = f"""
        UPDATE {self.TABELA}
        SET UltimoConcursoAtualizado = {concurso}
        WHERE UltimoConcursoAtualizado < {concurso}
        """
        self.db.execute_command(sql_update)
    
    def processar_lote_concursos(self, concursos: List[Dict], mostrar_progresso: bool = True) -> bool:
        """Processa um lote de concursos."""
        total = len(concursos)
        
        if total == 0:
            print("✅ Nenhum concurso pendente para processar")
            return True
        
        print(f"\n🔄 Processando {total} concurso(s)...")
        print("=" * 70)
        
        inicio_lote = datetime.now()
        
        for i, conc_data in enumerate(concursos, 1):
            concurso = conc_data['concurso']
            numeros = conc_data['numeros']
            
            inicio_conc = datetime.now()
            
            if mostrar_progresso:
                print(f"\n📍 Concurso {concurso} ({i}/{total}) | Números: {', '.join(map(str, numeros))}")
            
            # Processar acertos
            resultados = self.processar_concurso_sql(concurso, numeros)
            
            # Atualizar controle
            self.atualizar_controle_concurso(concurso)
            
            tempo_conc = (datetime.now() - inicio_conc).total_seconds()
            self.estatisticas['concursos_processados'] += 1
            
            if mostrar_progresso:
                acertos_str = ' | '.join(f"{k}ac:{v:,}" for k, v in resultados.items() if v > 0)
                if not acertos_str:
                    acertos_str = "Nenhum acerto 11+"
                print(f"   ✅ {acertos_str} | Tempo: {tempo_conc:.1f}s")
        
        tempo_total = (datetime.now() - inicio_lote).total_seconds()
        self.estatisticas['tempo_total'] += tempo_total
        
        print(f"\n⏱️ Lote processado em {tempo_total:.1f}s ({tempo_total/total:.2f}s/concurso)")
        
        return True
    
    def executar_atualizacao_incremental(self) -> bool:
        """Executa atualização incremental automática."""
        print("\n" + "=" * 70)
        print("🔄 ATUALIZAÇÃO INCREMENTAL - COMBINACOES_LOTOFACIL (15 números)")
        print("=" * 70)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if not self.verificar_estrutura_tabela():
            return False
        
        menor_atualizado = self.obter_menor_concurso_atualizado()
        ultimo_disponivel = self.obter_ultimo_concurso_disponivel()
        total_combinacoes = self.obter_total_combinacoes()
        
        print(f"\n📊 Estado atual:")
        print(f"   • Total de combinações: {total_combinacoes:,}")
        print(f"   • Último concurso atualizado: {menor_atualizado}")
        print(f"   • Último concurso disponível: {ultimo_disponivel}")
        
        if menor_atualizado >= ultimo_disponivel:
            print(f"\n✅ Base já está atualizada! Nenhum concurso novo.")
            return True
        
        concursos = self.obter_concursos_pendentes(menor_atualizado)
        
        if not concursos:
            print(f"\n✅ Nenhum concurso novo encontrado")
            return True
        
        print(f"\n🆕 {len(concursos)} concurso(s) novo(s) detectado(s)")
        print(f"   • Do concurso {concursos[0]['concurso']} até {concursos[-1]['concurso']}")
        
        return self.processar_lote_concursos(concursos)
    
    def executar_atualizacao_completa(self, desde_concurso: Optional[int] = None, auto_confirm: bool = False) -> bool:
        """Executa atualização completa."""
        print("\n" + "=" * 70)
        print("🔄 ATUALIZAÇÃO COMPLETA - COMBINACOES_LOTOFACIL (15 números)")
        print("=" * 70)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if not self.verificar_estrutura_tabela():
            return False
        
        total_combinacoes = self.obter_total_combinacoes()
        print(f"\n📊 Total de combinações na tabela: {total_combinacoes:,}")
        
        if desde_concurso is None:
            desde_concurso = self.obter_primeiro_concurso() - 1
            print(f"\n⚠️ MODO COMPLETO: Processando desde o início!")
            
            if auto_confirm or self._confirmar_reset():
                self._resetar_contagens()
            else:
                print("\n❌ Operação cancelada pelo usuário")
                return False
        else:
            print(f"\n📍 Processando a partir do concurso {desde_concurso + 1}")
        
        ultimo_disponivel = self.obter_ultimo_concurso_disponivel()
        
        print(f"\n📊 Informações:")
        print(f"   • Primeiro concurso a processar: {desde_concurso + 1}")
        print(f"   • Último concurso disponível: {ultimo_disponivel}")
        print(f"   • Total de concursos: {ultimo_disponivel - desde_concurso}")
        
        concursos = self.obter_concursos_pendentes(desde_concurso)
        
        if not concursos:
            print(f"\n✅ Nenhum concurso para processar")
            return True
        
        print(f"\n⏳ Processando {len(concursos)} concursos...")
        print("💡 Isso pode demorar. Não interrompa o processo.")
        
        # Processar em lotes
        LOTE = 50
        total_lotes = (len(concursos) + LOTE - 1) // LOTE
        
        for i in range(0, len(concursos), LOTE):
            lote = concursos[i:i + LOTE]
            num_lote = i // LOTE + 1
            print(f"\n📦 Lote {num_lote}/{total_lotes} (concursos {lote[0]['concurso']} - {lote[-1]['concurso']})")
            self.processar_lote_concursos(lote, mostrar_progresso=False)
        
        return True
    
    def _confirmar_reset(self) -> bool:
        """Solicita confirmação para resetar contagens."""
        print("\n⚠️ ATENÇÃO: Isso vai ZERAR todas as contagens de acertos!")
        resposta = input("   Confirma? (S/N): ").strip().upper()
        return resposta == 'S'
    
    def _resetar_contagens(self):
        """Reseta todas as contagens de acertos para zero."""
        print("\n🔄 Resetando contagens...")
        
        sql_reset = f"""
        UPDATE {self.TABELA}
        SET 
            Acertos_10 = 0,
            Acertos_11 = 0,
            Acertos_12 = 0,
            Acertos_13 = 0,
            Acertos_14 = 0,
            Acertos_15 = 0,
            Ultimo_Acertos_10 = NULL,
            Ultimo_Acertos_11 = NULL,
            Ultimo_Acertos_12 = NULL,
            Ultimo_Acertos_13 = NULL,
            Ultimo_Acertos_14 = NULL,
            Ultimo_Acertos_15 = NULL,
            UltimoConcursoAtualizado = 0
        """
        
        self.db.execute_command(sql_reset)
        print("✅ Contagens resetadas")
    
    def gerar_relatorio_final(self):
        """Gera relatório final do processamento."""
        print("\n" + "=" * 70)
        print("📋 RELATÓRIO FINAL - COMBINACOES_LOTOFACIL")
        print("=" * 70)
        
        print(f"\n📊 Estatísticas do processamento:")
        print(f"   • Concursos processados: {self.estatisticas['concursos_processados']}")
        print(f"   • Tempo total: {self.estatisticas['tempo_total']:.1f}s")
        
        print(f"\n🎯 Atualizações por nível de acerto:")
        for nivel in self.NIVEIS_ACERTOS:
            qtd = self.estatisticas['atualizacoes'][nivel]
            print(f"   • {nivel} acertos: {qtd:,} combinações atualizadas")
        
        # Consultar estatísticas finais
        query_stats = f"""
        SELECT 
            SUM(Acertos_10) as total_10,
            SUM(Acertos_11) as total_11,
            SUM(Acertos_12) as total_12,
            SUM(Acertos_13) as total_13,
            SUM(Acertos_14) as total_14,
            SUM(Acertos_15) as total_15,
            MAX(UltimoConcursoAtualizado) as ultimo_atualizado
        FROM {self.TABELA}
        """
        
        stats = self.db.execute_query_dataframe(query_stats).iloc[0]
        
        print(f"\n📈 Estado final da tabela:")
        print(f"   • Total acertos 10: {int(stats['total_10']):,}")
        print(f"   • Total acertos 11: {int(stats['total_11']):,}")
        print(f"   • Total acertos 12: {int(stats['total_12']):,}")
        print(f"   • Total acertos 13: {int(stats['total_13']):,}")
        print(f"   • Total acertos 14: {int(stats['total_14']):,}")
        print(f"   • Total acertos 15: {int(stats['total_15']):,}")
        print(f"   • Último concurso atualizado: {int(stats['ultimo_atualizado'])}")
        
        print("\n" + "=" * 70)
        print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Atualizador de acertos - COMBINACOES_LOTOFACIL (15 números)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python atualizar_acertos_lotofacil15.py           # Incremental automático
  python atualizar_acertos_lotofacil15.py --full    # Reprocessar tudo
  python atualizar_acertos_lotofacil15.py --desde 3600  # A partir do concurso 3600
        """
    )
    
    parser.add_argument('--full', action='store_true', help='Força processamento completo')
    parser.add_argument('--desde', type=int, help='Processa a partir de um concurso específico')
    parser.add_argument('--yes', '-y', action='store_true', help='Confirma automaticamente')
    
    args = parser.parse_args()
    
    atualizador = AtualizadorAcertosLotofacil15()
    
    try:
        if args.full:
            sucesso = atualizador.executar_atualizacao_completa(auto_confirm=args.yes)
        elif args.desde:
            sucesso = atualizador.executar_atualizacao_completa(desde_concurso=args.desde - 1, auto_confirm=args.yes)
        else:
            sucesso = atualizador.executar_atualizacao_incremental()
        
        if sucesso:
            atualizador.gerar_relatorio_final()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processamento interrompido pelo usuário")
        print("💡 Execute novamente para continuar de onde parou")
    except Exception as e:
        print(f"\n❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
