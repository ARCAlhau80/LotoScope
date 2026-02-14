#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANÁLISE DE PROBABILIDADES DO ÚLTIMO CONCURSO
==============================================
Script que pega o último resultado da tabela RESULTADOS_INT
e gera relatório completo de probabilidades de transição
para o próximo concurso baseado na análise posicional

Baseado no analisador_transicao_posicional.py
"""

import pyodbc
import json
from datetime import datetime
from analisador_transicao_posicional import AnalisadorTransicaoPosicional

class AnaliseProbabilidadeAtual:
    """Classe para análise de probabilidades do último concurso"""
    
    def __init__(self):
        """Inicializa o analisador"""
        self.analisador = AnalisadorTransicaoPosicional()
        self.ultimo_concurso = None
        self.ultimo_resultado = None
        self.probabilidades_calculadas = {}
        
        print("[INICIANDO] Analise de Probabilidades do Ultimo Concurso")
        print("=" * 60)
    
    def conectar_e_carregar(self):
        """Conecta banco e carrega análise de transições"""
        try:
            # Conecta ao banco
            if not self.analisador.conectar_banco():
                return False
            
            # Carrega dados históricos e calcula matrizes
            if not self.analisador.analisar_todas_posicoes():
                return False
            
            print("[OK] Matrizes de transição carregadas com sucesso")
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha na conexão/carregamento: {e}")
            return False
    
    def buscar_ultimo_concurso(self):
        """Busca o último concurso na tabela"""
        try:
            query = """
            SELECT TOP 1 CONCURSO, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, Data_Sorteio
            FROM RESULTADOS_INT
            ORDER BY CONCURSO DESC
            """
            
            cursor = self.analisador.conexao.cursor()
            cursor.execute(query)
            resultado = cursor.fetchone()
            
            if resultado:
                self.ultimo_concurso = resultado[0]
                self.ultimo_resultado = {
                    'concurso': resultado[0],
                    'numeros': list(resultado[1:16]),  # N1 a N15
                    'data_sorteio': resultado[16]
                }
                
                print(f"[OK] Ultimo concurso encontrado: {self.ultimo_concurso}")
                print(f"    Data: {self.ultimo_resultado['data_sorteio']}")
                print(f"    Numeros: {self.ultimo_resultado['numeros']}")
                
                return True
            else:
                print("[ERRO] Nenhum concurso encontrado")
                return False
                
        except Exception as e:
            print(f"[ERRO] Falha ao buscar ultimo concurso: {e}")
            return False
    
    def calcular_probabilidades_proximo_concurso(self):
        """Calcula probabilidades para próximo concurso baseado no último resultado"""
        
        if not self.ultimo_resultado:
            print("[ERRO] Ultimo resultado não carregado")
            return False
        
        print(f"\n[CALCULANDO] Probabilidades para o proximo concurso...")
        print("-" * 60)
        
        probabilidades_por_posicao = {}
        
        # Para cada posição (N1 a N15)
        for posicao in range(1, 16):
            numero_atual = self.ultimo_resultado['numeros'][posicao - 1]  # índice 0-based
            
            # Consulta probabilidades de transição
            consulta = self.analisador.consultar_transicao_especifica(posicao, numero_atual)
            
            if consulta and consulta['transicoes_ordenadas']:
                probabilidades_por_posicao[f'N{posicao}'] = {
                    'numero_atual': numero_atual,
                    'total_ocorrencias': consulta['total_ocorrencias'],
                    'top_5_probabilidades': consulta['transicoes_ordenadas'][:5],
                    'todas_probabilidades': consulta['transicoes_ordenadas']
                }
                
                # Exibe resultado para a posição
                top_prob = consulta['transicoes_ordenadas'][0] if consulta['transicoes_ordenadas'] else None
                if top_prob:
                    print(f"  N{posicao:2d} (atual: {numero_atual:2d}) -> Provavel: {top_prob['destino']:2d} ({top_prob['probabilidade']:6.1%})")
            else:
                probabilidades_por_posicao[f'N{posicao}'] = {
                    'numero_atual': numero_atual,
                    'total_ocorrencias': 0,
                    'top_5_probabilidades': [],
                    'todas_probabilidades': []
                }
                print(f"  N{posicao:2d} (atual: {numero_atual:2d}) -> Sem dados historicos")
        
        self.probabilidades_calculadas = probabilidades_por_posicao
        print(f"\n[OK] Probabilidades calculadas para todas as 15 posicoes")
        
        return True
    
    def gerar_relatorio_detalhado(self):
        """Gera relatório detalhado das probabilidades"""
        
        if not self.probabilidades_calculadas:
            print("[ERRO] Probabilidades não calculadas")
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_json = f'probabilidades_proximo_concurso_{timestamp}.json'
        arquivo_texto = f'relatorio_probabilidades_concurso_{timestamp}.txt'
        
        # Prepara dados para JSON
        dados_completos = {
            'metadados': {
                'ultimo_concurso_analisado': self.ultimo_concurso,
                'data_ultimo_sorteio': str(self.ultimo_resultado['data_sorteio']),
                'numeros_ultimo_sorteio': self.ultimo_resultado['numeros'],
                'data_analise': datetime.now().isoformat(),
                'proximo_concurso_estimado': self.ultimo_concurso + 1
            },
            'probabilidades_por_posicao': self.probabilidades_calculadas
        }
        
        # Salva JSON completo
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados_completos, f, indent=2, ensure_ascii=False, default=str)
        
        # Gera relatório em texto
        self._gerar_relatorio_texto(arquivo_texto, dados_completos)
        
        print(f"\n[SALVO] Relatorio JSON: {arquivo_json}")
        print(f"[SALVO] Relatorio texto: {arquivo_texto}")
        
        return arquivo_json, arquivo_texto
    
    def _gerar_relatorio_texto(self, arquivo, dados):
        """Gera relatório executivo em texto"""
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RELATORIO DE PROBABILIDADES PARA PROXIMO CONCURSO\n")
            f.write("=" * 80 + "\n\n")
            
            # Informações gerais
            meta = dados['metadados']
            f.write(f"CONCURSO ANALISADO: {meta['ultimo_concurso_analisado']}\n")
            f.write(f"DATA DO SORTEIO: {meta['data_ultimo_sorteio']}\n")
            f.write(f"NUMEROS SORTEADOS: {meta['numeros_ultimo_sorteio']}\n")
            f.write(f"PROXIMO CONCURSO ESTIMADO: {meta['proximo_concurso_estimado']}\n")
            f.write(f"DATA DA ANALISE: {meta['data_analise'][:19]}\n\n")
            
            # Probabilidades por posição
            f.write("PROBABILIDADES POR POSICAO:\n")
            f.write("=" * 80 + "\n\n")
            
            for posicao_key in sorted(dados['probabilidades_por_posicao'].keys()):
                dados_posicao = dados['probabilidades_por_posicao'][posicao_key]
                numero_atual = dados_posicao['numero_atual']
                total_ocorrencias = dados_posicao['total_ocorrencias']
                top_5 = dados_posicao['top_5_probabilidades']
                
                f.write(f"POSICAO {posicao_key}:\n")
                f.write(f"  Numero atual: {numero_atual}\n")
                f.write(f"  Total de ocorrencias historicas: {total_ocorrencias}\n")
                
                if top_5:
                    f.write(f"  Top 5 probabilidades para proximo concurso:\n")
                    for i, prob in enumerate(top_5, 1):
                        f.write(f"    {i}. Numero {prob['destino']:2d}: "
                               f"{prob['probabilidade']:6.1%} ({prob['ocorrencias']:2d}x historico)\n")
                else:
                    f.write(f"  Sem dados historicos suficientes\n")
                f.write("\n")
            
            # Resumo estatístico
            self._gerar_resumo_estatistico(f, dados)
    
    def _gerar_resumo_estatistico(self, arquivo, dados):
        """Gera resumo estatístico das probabilidades"""
        
        arquivo.write("RESUMO ESTATISTICO:\n")
        arquivo.write("=" * 80 + "\n")
        
        # Coleta todas as probabilidades mais altas
        probabilidades_maximas = []
        numeros_mais_provaveis = []
        repeticoes_esperadas = []
        
        for posicao_key, dados_posicao in dados['probabilidades_por_posicao'].items():
            if dados_posicao['top_5_probabilidades']:
                top_1 = dados_posicao['top_5_probabilidades'][0]
                probabilidades_maximas.append(top_1['probabilidade'])
                numeros_mais_provaveis.append(top_1['destino'])
                
                # Verifica se é repetição (mesmo número)
                if top_1['destino'] == dados_posicao['numero_atual']:
                    repeticoes_esperadas.append(posicao_key)
        
        if probabilidades_maximas:
            prob_media = sum(probabilidades_maximas) / len(probabilidades_maximas)
            arquivo.write(f"Probabilidade media das transicoes mais provaveis: {prob_media:.1%}\n")
            arquivo.write(f"Posicoes com tendencia de repeticao: {len(repeticoes_esperadas)}/15\n")
            arquivo.write(f"Posicoes que devem repetir: {', '.join(repeticoes_esperadas)}\n")
            
            # Números mais prováveis por frequência
            from collections import Counter
            contador_numeros = Counter(numeros_mais_provaveis)
            numeros_frequentes = contador_numeros.most_common(10)
            
            arquivo.write(f"\nNumeros que mais aparecem nas predicoes:\n")
            for numero, freq in numeros_frequentes:
                arquivo.write(f"  Numero {numero:2d}: {freq:2d} posicoes\n")
        
        # Combinação sugerida baseada nas probabilidades máximas
        arquivo.write(f"\nCOMBINACAO SUGERIDA (baseada em probabilidades maximas):\n")
        if numeros_mais_provaveis:
            # Remove duplicatas mantendo ordem
            combinacao_sugerida = []
            for num in numeros_mais_provaveis:
                if num not in combinacao_sugerida:
                    combinacao_sugerida.append(num)
            
            # Ordena para formato padrão
            combinacao_ordenada = sorted(combinacao_sugerida)
            arquivo.write(f"{combinacao_ordenada}\n")
            
            if len(combinacao_ordenada) == 15:
                arquivo.write("COMBINACAO COMPLETA - 15 numeros unicos gerados!\n")
            else:
                arquivo.write(f"ATENCAO: Apenas {len(combinacao_ordenada)} numeros unicos "
                             f"(algumas posicoes repetem numeros)\n")
    
    def gerar_combinacao_otimizada(self):
        """Gera combinação otimizada baseada nas probabilidades"""
        
        if not self.probabilidades_calculadas:
            return None
        
        # Estratégia: pega o número mais provável de cada posição
        # Se houver repetições, usa segunda opção, etc.
        combinacao = []
        numeros_usados = set()
        
        for posicao in range(1, 16):
            posicao_key = f'N{posicao}'
            dados_posicao = self.probabilidades_calculadas[posicao_key]
            
            numero_escolhido = None
            if dados_posicao['todas_probabilidades']:
                # Tenta encontrar número não usado
                for prob_data in dados_posicao['todas_probabilidades']:
                    numero = prob_data['destino']
                    if numero not in numeros_usados:
                        numero_escolhido = numero
                        numeros_usados.add(numero)
                        break
                
                # Se todos estão usados, pega o mais provável mesmo repetindo
                if numero_escolhido is None:
                    numero_escolhido = dados_posicao['todas_probabilidades'][0]['destino']
            
            if numero_escolhido:
                combinacao.append(numero_escolhido)
        
        # Remove duplicatas e ordena
        combinacao_final = sorted(list(set(combinacao)))
        
        print(f"\n[COMBINACAO] Numeros sugeridos baseados em probabilidades:")
        print(f"  {combinacao_final}")
        print(f"  Total de numeros unicos: {len(combinacao_final)}")
        
        return combinacao_final
    
    def executar_analise_completa(self):
        """Executa análise completa do último concurso"""
        
        print("EXECUTANDO ANALISE COMPLETA DO ULTIMO CONCURSO")
        print("=" * 80)
        
        # Passo 1: Conecta e carrega análise
        if not self.conectar_e_carregar():
            return False
        
        # Passo 2: Busca último concurso
        if not self.buscar_ultimo_concurso():
            return False
        
        # Passo 3: Calcula probabilidades
        if not self.calcular_probabilidades_proximo_concurso():
            return False
        
        # Passo 4: Gera relatórios
        arquivo_json, arquivo_texto = self.gerar_relatorio_detalhado()
        
        # Passo 5: Gera combinação otimizada
        combinacao = self.gerar_combinacao_otimizada()
        
        # Estatísticas finais
        print(f"\n[OK] ANALISE COMPLETA CONCLUIDA!")
        print(f"  - Concurso analisado: {self.ultimo_concurso}")
        print(f"  - Probabilidades calculadas: 15 posicoes")
        print(f"  - Relatorios gerados: 2 arquivos")
        if combinacao and len(combinacao) >= 15:
            print(f"  - Combinacao sugerida: COMPLETA ({len(combinacao)} numeros)")
        
        return True

def main():
    """Função principal"""
    
    try:
        # Cria analisador
        analisador = AnaliseProbabilidadeAtual()
        
        # Executa análise
        if analisador.executar_analise_completa():
            print("\n" + "="*60)
            print("ANALISE CONCLUIDA COM SUCESSO!")
            print("Verifique os arquivos gerados para detalhes completos.")
        else:
            print("\n[ERRO] Falha na analise")
    
    except KeyboardInterrupt:
        print("\n[PARADA] Analise interrompida pelo usuario")
    except Exception as e:
        print(f"\n[ERRO CRITICO] {e}")
    finally:
        # Fecha conexão se existir
        try:
            if hasattr(analisador, 'analisador') and analisador.analisador.conexao:
                analisador.analisador.conexao.close()
                print("[OK] Conexao fechada")
        except:
            pass

if __name__ == "__main__":
    main()