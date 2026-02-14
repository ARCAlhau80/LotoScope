#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 INTEGRADOR MENU LOTOFÁCIL - TABELA 20 NÚMEROS
===============================================
Script para integrar a atualização da tabela COMBINACOES_LOTOFACIL20_COMPLETO
no menu_lotofacil.py existente.

Substitui a função atualizar_campos_repetidos_combinacoes pela versão estendida.

Autor: AR CALHAU
Data: 09/09/2025
"""

import os
import shutil
from datetime import datetime

def fazer_backup():
    """
    Faz backup do arquivo original
    """
    arquivo_original = "lotofacil_lite/menu_lotofacil.py"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo_backup = f"lotofacil_lite/menu_lotofacil_backup_{timestamp}.py"
    
    try:
        shutil.copy2(arquivo_original, arquivo_backup)
        print(f"✅ Backup criado: {arquivo_backup}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def aplicar_integracao():
    """
    Aplica a integração no menu_lotofacil.py
    """
    arquivo = "lotofacil_lite/menu_lotofacil.py"
    
    try:
        # Ler arquivo original
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Localizar a função original
        inicio_funcao = conteudo.find('def atualizar_campos_repetidos_combinacoes(self, ultimo_concurso: int, cursor, conn) -> bool:')
        
        if inicio_funcao == -1:
            print("❌ Função atualizar_campos_repetidos_combinacoes não encontrada")
            return False
        
        # Encontrar o final da função (próximo def ou final do arquivo)
        linha_inicio = conteudo[:inicio_funcao].count('\n') + 1
        
        # Procurar pelo próximo def na mesma indentação
        linhas = conteudo[inicio_funcao:].split('\n')
        fim_funcao_relativo = 0
        
        for i, linha in enumerate(linhas):
            if i > 0 and linha.strip() and not linha.startswith('        ') and not linha.startswith('\t\t'):
                if linha.startswith('    def ') or linha.startswith('def '):
                    fim_funcao_relativo = i
                    break
        
        if fim_funcao_relativo == 0:
            fim_funcao_relativo = len(linhas)
        
        fim_funcao = inicio_funcao + len('\n'.join(linhas[:fim_funcao_relativo]))
        
        print(f"📍 Função encontrada: linha {linha_inicio}")
        print(f"📏 Tamanho: {fim_funcao - inicio_funcao} caracteres")
        
        # Nova função integrada
        nova_funcao = '''    def atualizar_campos_repetidos_combinacoes(self, ultimo_concurso: int, cursor, conn) -> bool:
        """
        VERSÃO ESTENDIDA: Atualiza os campos QtdeRepetidos e RepetidosMesmaPosicao 
        em AMBAS as tabelas: COMBINACOES_LOTOFACIL e COMBINACOES_LOTOFACIL20_COMPLETO
        
        Também atualiza Acertos_15 e Acertos_14 incrementalmente na tabela de 20 números.
        
        Args:
            ultimo_concurso: Número do último concurso atualizado
            cursor: Cursor da conexão
            conn: Conexão com o banco
            
        Returns:
            bool: True se atualizou com sucesso
        """
        try:
            # Busca números do último concurso
            cursor.execute("""
                SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT 
                WHERE Concurso = ?
            """, (ultimo_concurso,))
            
            resultado = cursor.fetchone()
            if not resultado:
                print(f"❌ Concurso {ultimo_concurso} não encontrado")
                return False
            
            numeros_ultimo_concurso = list(resultado)
            print(f"📊 Números do concurso {ultimo_concurso}: {','.join(map(str, sorted(numeros_ultimo_concurso)))}")
            
            # =====================================================================
            # 1️⃣ ATUALIZAR TABELA ORIGINAL (COMBINACOES_LOTOFACIL) - 15 NÚMEROS
            # =====================================================================
            print("🔄 Atualizando tabela COMBINACOES_LOTOFACIL...")
            
            # Para cada combinação, calcula quantos números repetem do último concurso
            cursor.execute("""
                UPDATE COMBINACOES_LOTOFACIL SET
                    QtdeRepetidos = (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),(N11),(N12),(N13),(N14),(N15)) AS combinacao(numero)
                        WHERE numero IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ),
                    RepetidosMesmaPosicao = (
                        CASE WHEN N1 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N2 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N3 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N4 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N5 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N6 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N7 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N8 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N9 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N10 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N11 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N12 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N13 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N14 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N15 = ? THEN 1 ELSE 0 END
                    )
            """, (
                # Parâmetros para QtdeRepetidos (números do último concurso)
                *numeros_ultimo_concurso,
                # Parâmetros para RepetidosMesmaPosicao (números do último concurso, uma vez por posição)
                *numeros_ultimo_concurso
            ))
            
            rows_affected_15 = cursor.rowcount
            conn.commit()
            
            print(f"✅ {rows_affected_15} combinações atualizadas na COMBINACOES_LOTOFACIL")
            
            # =====================================================================
            # 2️⃣ VERIFICAR SE TABELA DE 20 NÚMEROS EXISTE
            # =====================================================================
            cursor.execute("""
                SELECT COUNT_BIG(*) as count FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
            """)
            
            tabela_20_existe = cursor.fetchone()[0] > 0
            
            if not tabela_20_existe:
                print("⚠️ Tabela COMBINACOES_LOTOFACIL20_COMPLETO não encontrada - mantendo comportamento original")
                print(f"📊 Referência: Concurso {ultimo_concurso}")
                return True
            
            # Verificar se as colunas de acertos existem
            cursor.execute("""
                SELECT COUNT_BIG(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
                AND COLUMN_NAME IN ('Acertos_15', 'Acertos_14')
            """)
            
            colunas_acertos_existem = cursor.fetchone()[0] == 2
            
            # =====================================================================
            # 3️⃣ ATUALIZAR TABELA DE 20 NÚMEROS - CAMPOS REPETIDOS
            # =====================================================================
            print("🔄 Atualizando tabela COMBINACOES_LOTOFACIL20_COMPLETO...")
            
            # Atualizar QtdeRepetidos e RepetidosMesmaPosicao na tabela de 20 números
            cursor.execute("""
                UPDATE COMBINACOES_LOTOFACIL20_COMPLETO SET
                    QtdeRepetidos = (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS combinacao(numero)
                        WHERE numero IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ),
                    RepetidosMesmaPosicao = (
                        CASE WHEN N1 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N2 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N3 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N4 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N5 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N6 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N7 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N8 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N9 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N10 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N11 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N12 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N13 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N14 = ? THEN 1 ELSE 0 END +
                        CASE WHEN N15 = ? THEN 1 ELSE 0 END
                    )
            """, (
                # Parâmetros para QtdeRepetidos (números do último concurso)
                *numeros_ultimo_concurso,
                # Parâmetros para RepetidosMesmaPosicao (números do último concurso)
                *numeros_ultimo_concurso
            ))
            
            rows_affected_20 = cursor.rowcount
            conn.commit()
            
            print(f"✅ {rows_affected_20} combinações atualizadas na COMBINACOES_LOTOFACIL20_COMPLETO (repetidos)")
            
            # =====================================================================
            # 4️⃣ ATUALIZAR ACERTOS INCREMENTAIS (SE COLUNAS EXISTEM)
            # =====================================================================
            if colunas_acertos_existem:
                print("🔄 Atualizando acertos incrementais na tabela de 20 números...")
                
                # Atualizar acertos de 15
                cursor.execute(f"""
                    UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                    SET Acertos_15 = Acertos_15 + 1
                    WHERE (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 15
                """, numeros_ultimo_concurso)
                
                acertos_15_atualizados = cursor.rowcount
                
                # Atualizar acertos de 14
                cursor.execute(f"""
                    UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                    SET Acertos_14 = Acertos_14 + 1
                    WHERE (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 14
                """, numeros_ultimo_concurso)
                
                acertos_14_atualizados = cursor.rowcount
                conn.commit()
                
                print(f"✅ Acertos atualizados: {acertos_15_atualizados} com 15 pontos, {acertos_14_atualizados} com 14 pontos")
                
                # Atualizar controle de processamento
                try:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'CONTROLE_PROCESSAMENTO_ACERTOS')
                        BEGIN
                            CREATE TABLE CONTROLE_PROCESSAMENTO_ACERTOS (
                                ID INT IDENTITY(1,1) PRIMARY KEY,
                                UltimoConcursoProcessado INT NOT NULL,
                                DataProcessamento DATETIME DEFAULT GETDATE(),
                                TipoProcessamento VARCHAR(20) NOT NULL
                            )
                        END
                    """)
                    
                    cursor.execute("""
                        INSERT INTO CONTROLE_PROCESSAMENTO_ACERTOS (UltimoConcursoProcessado, TipoProcessamento)
                        VALUES (?, 'INCREMENTAL')
                    """, (ultimo_concurso,))
                    
                    conn.commit()
                    
                except Exception as e:
                    print(f"⚠️ Aviso: Controle de processamento: {e}")
                
                print(f"🎯 Resumo: COMBINACOES_LOTOFACIL: {rows_affected_15:,} | COMBINACOES_LOTOFACIL20_COMPLETO: {rows_affected_20:,} | 15-acertos: +{acertos_15_atualizados} | 14-acertos: +{acertos_14_atualizados}")
            
            else:
                print(f"🎯 Resumo: COMBINACOES_LOTOFACIL: {rows_affected_15:,} | COMBINACOES_LOTOFACIL20_COMPLETO: {rows_affected_20:,}")
            
            print(f"📊 Referência: Concurso {ultimo_concurso}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar campos repetidos completo: {e}")
            return False

'''
        
        # Substituir a função
        novo_conteudo = conteudo[:inicio_funcao] + nova_funcao + conteudo[fim_funcao:]
        
        # Salvar arquivo modificado
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        
        print("✅ Integração aplicada com sucesso!")
        print(f"📊 Função atualizada no {arquivo}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar integração: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🔧 INTEGRADOR MENU LOTOFÁCIL - TABELA 20 NÚMEROS")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    print("⚠️  IMPORTANTE:")
    print("   Esta operação vai modificar o arquivo menu_lotofacil.py")
    print("   Um backup será criado automaticamente")
    print("   A função será estendida para atualizar também a tabela de 20 números")
    print()
    
    resposta = input("🤔 Continuar com a integração? (s/n): ").strip().lower()
    if not resposta.startswith('s'):
        print("❌ Operação cancelada.")
        return
    
    print("\n🔄 INICIANDO INTEGRAÇÃO...")
    
    # 1. Fazer backup
    if fazer_backup():
        print("✅ Backup realizado")
    else:
        print("❌ Falha no backup - cancelando operação")
        return
    
    # 2. Aplicar integração
    if aplicar_integracao():
        print("\n🎊 INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        print("✅ Função atualizar_campos_repetidos_combinacoes modificada")
        print("✅ Agora atualiza ambas as tabelas automaticamente:")
        print("   • COMBINACOES_LOTOFACIL (15 números)")
        print("   • COMBINACOES_LOTOFACIL20_COMPLETO (20 números)")
        print("✅ Atualização incremental de acertos 15 e 14")
        print("✅ Controle automático de processamento")
        print()
        print("🚀 PRÓXIMO PASSO:")
        print("   Execute o menu_lotofacil.py normalmente")
        print("   Ambas as tabelas serão atualizadas automaticamente!")
        print("=" * 50)
    else:
        print("\n❌ FALHA NA INTEGRAÇÃO!")
        print("💡 Verifique os logs de erro e tente novamente")

if __name__ == "__main__":
    main()
