#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 EXTENSÃO MENU LOTOFÁCIL - INTEGRAÇÃO TABELA 20 NÚMEROS
========================================================
Função modificada que atualiza tanto COMBINACOES_LOTOFACIL quanto
COMBINACOES_LOTOFACIL20_COMPLETO com repetidos e acertos incrementais.

Para ser integrada no menu_lotofacil.py original.

Autor: AR CALHAU
Data: 09/09/2025
"""

def atualizar_campos_repetidos_combinacoes_completo(self, ultimo_concurso: int, cursor, conn) -> bool:
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
        
        # Busca números do concurso anterior (se existir)
        if ultimo_concurso > 1:
            cursor.execute("""
                SELECT N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15
                FROM Resultados_INT 
                WHERE Concurso = ?
            """, (ultimo_concurso - 1,))
            
            resultado_anterior = cursor.fetchone()
            if resultado_anterior:
                numeros_concurso_anterior = list(resultado_anterior)
                
                # Calcula repetidos do último concurso em relação ao anterior
                qtde_repetidos = len(set(numeros_ultimo_concurso) & set(numeros_concurso_anterior))
                
                # Calcula repetidos na mesma posição
                repetidos_mesma_posicao = 0
                for i in range(15):
                    if numeros_ultimo_concurso[i] == numeros_concurso_anterior[i]:
                        repetidos_mesma_posicao += 1
                
                print(f"📈 Calculado: {qtde_repetidos} repetidos, {repetidos_mesma_posicao} na mesma posição")
            else:
                # Se não encontrou concurso anterior, usa valores zerados
                qtde_repetidos = 0
                repetidos_mesma_posicao = 0
        else:
            # Primeiro concurso, não tem repetidos
            qtde_repetidos = 0
            repetidos_mesma_posicao = 0
        
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
            print("⚠️ Tabela COMBINACOES_LOTOFACIL20_COMPLETO não encontrada - pulando atualização")
            return True
        
        # Verificar se as colunas de acertos existem (inclui 11, 12, 13, 14 e 15)
        cursor.execute("""
            SELECT COUNT_BIG(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'COMBINACOES_LOTOFACIL20_COMPLETO'
            AND COLUMN_NAME IN ('Acertos_15', 'Acertos_14', 'Acertos_13', 'Acertos_12', 'Acertos_11')
        """)
        
        qtd_colunas_acertos = cursor.fetchone()[0]
        colunas_acertos_existem = qtd_colunas_acertos >= 2  # Mínimo 14 e 15
        colunas_acertos_completas = qtd_colunas_acertos == 5  # Todas: 11, 12, 13, 14, 15
        
        # =====================================================================
        # 3️⃣ ATUALIZAR TABELA DE 20 NÚMEROS - CAMPOS REPETIDOS E DATA
        # =====================================================================
        print("🔄 Atualizando tabela COMBINACOES_LOTOFACIL20_COMPLETO...")
        
        # Atualizar QtdeRepetidos, RepetidosMesmaPosicao, DataGeracao e Processado
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
                ),
                DataGeracao = CONVERT(VARCHAR(19), GETDATE(), 120),
                Processado = 'S'
        """, (
            # Parâmetros para QtdeRepetidos (números do último concurso)
            *numeros_ultimo_concurso,
            # Parâmetros para RepetidosMesmaPosicao (números do último concurso)
            # Para posições 1-15, usamos os números; para 16-20 usamos 0 (nunca vai coincidir)
            *numeros_ultimo_concurso
        ))
        
        rows_affected_20 = cursor.rowcount
        conn.commit()
        
        print(f"✅ {rows_affected_20} combinações atualizadas na COMBINACOES_LOTOFACIL20_COMPLETO (repetidos + DataGeracao)")
        
        # =====================================================================
        # 4️⃣ ATUALIZAR ACERTOS INCREMENTAIS (SE COLUNAS EXISTEM)
        # =====================================================================
        if colunas_acertos_existem:
            print("🔄 Atualizando acertos incrementais na tabela de 20 números...")
            
            # Contar quantas combinações vão ter acertos 15 e 14
            cursor.execute(f"""
                SELECT 
                    SUM(CASE WHEN (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 15 THEN 1 ELSE 0 END) as acertos_15,
                    SUM(CASE WHEN (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 14 THEN 1 ELSE 0 END) as acertos_14
                FROM COMBINACOES_LOTOFACIL20_COMPLETO
            """, (*numeros_ultimo_concurso, *numeros_ultimo_concurso))
            
            contadores = cursor.fetchone()
            acertos_15_esperados = contadores[0] if contadores[0] else 0
            acertos_14_esperados = contadores[1] if contadores[1] else 0
            
            print(f"📊 Esperado: {acertos_15_esperados} combinações com 15 acertos, {acertos_14_esperados} com 14 acertos")
            
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
            
            # =====================================================================
            # 🆕 ATUALIZAR ACERTOS 13, 12 E 11 (SE AS COLUNAS EXISTEM)
            # =====================================================================
            acertos_13_atualizados = 0
            acertos_12_atualizados = 0
            acertos_11_atualizados = 0
            
            if colunas_acertos_completas:
                # Acertos 13
                cursor.execute(f"""
                    UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                    SET Acertos_13 = Acertos_13 + 1
                    WHERE (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 13
                """, numeros_ultimo_concurso)
                
                acertos_13_atualizados = cursor.rowcount
                
                # Acertos 12
                cursor.execute(f"""
                    UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                    SET Acertos_12 = Acertos_12 + 1
                    WHERE (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 12
                """, numeros_ultimo_concurso)
                
                acertos_12_atualizados = cursor.rowcount
                
                # Acertos 11
                cursor.execute(f"""
                    UPDATE COMBINACOES_LOTOFACIL20_COMPLETO 
                    SET Acertos_11 = Acertos_11 + 1
                    WHERE (
                        SELECT COUNT_BIG(*)
                        FROM (VALUES (N1),(N2),(N3),(N4),(N5),(N6),(N7),(N8),(N9),(N10),
                                     (N11),(N12),(N13),(N14),(N15),(N16),(N17),(N18),(N19),(N20)) AS comb(numero)
                        WHERE numero IN ({','.join(['?'] * 15)})
                    ) = 11
                """, numeros_ultimo_concurso)
                
                acertos_11_atualizados = cursor.rowcount
                conn.commit()
                
                print(f"✅ Acertos adicionais: +{acertos_13_atualizados} (13), +{acertos_12_atualizados} (12), +{acertos_11_atualizados} (11)")
            
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
                
                print(f"✅ Controle de processamento atualizado para concurso {ultimo_concurso}")
                
            except Exception as e:
                print(f"⚠️ Aviso: Não foi possível atualizar controle de processamento: {e}")
        
        else:
            print("⚠️ Colunas Acertos_15 e Acertos_14 não encontradas - pulando atualização de acertos")
        
        # =====================================================================
        # 5️⃣ RESUMO FINAL
        # =====================================================================
        print(f"\n📊 RESUMO DA ATUALIZAÇÃO - CONCURSO {ultimo_concurso}:")
        print("=" * 60)
        print(f"✅ COMBINACOES_LOTOFACIL: {rows_affected_15:,} combinações")
        print(f"✅ COMBINACOES_LOTOFACIL20_COMPLETO: {rows_affected_20:,} combinações")
        
        if colunas_acertos_existem:
            print(f"🎯 Acertos 15: +{acertos_15_atualizados} combinações")
            print(f"🎯 Acertos 14: +{acertos_14_atualizados} combinações")
            if colunas_acertos_completas:
                print(f"🎯 Acertos 13: +{acertos_13_atualizados} combinações")
                print(f"🎯 Acertos 12: +{acertos_12_atualizados} combinações")
                print(f"🎯 Acertos 11: +{acertos_11_atualizados} combinações")
        
        print(f"📈 Referência: Números {','.join(map(str, sorted(numeros_ultimo_concurso)))}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar campos repetidos completo: {e}")
        import traceback
        traceback.print_exc()
        return False
