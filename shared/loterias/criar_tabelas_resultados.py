"""
Cria as tabelas de resultados para Mega-Sena, Quina e Dupla Sena
no banco LOTOFACIL (mesmo banco da Lotofácil).

Uso:
    python -m shared.loterias.criar_tabelas_resultados

Requer o módulo database_config da lotofacil_lite.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lotofacil_lite.utils.database_config import db_config

TABELAS = {
    "Resultados_MegaSenaFechado": {
        "numeros": 6,
        "descricao": "Mega-Sena (6 números, 1-60)",
    },
    "Resultados_Quina": {
        "numeros": 5,
        "descricao": "Quina (5 números, 1-80)",
    },
    "Resultados_DuplaSena": {
        "numeros": 6,
        "descricao": "Dupla Sena (6 números, 1-50)",
    },
    "Resultados_DiaDeSorte": {
        "numeros": 7,
        "descricao": "Dia de Sorte (7 números, 1-31)",
    },
    "Resultados_Timemania": {
        "numeros": 7,
        "descricao": "Timemania (7 números, 1-80)",
    },
    "Resultados_SuperSete": {
        "numeros": 7,
        "descricao": "Super Sete (7 colunas, 0-9)",
    },
    "Resultados_MaisMilionaria": {
        "numeros": 6,
        "descricao": "Mais Milionária (6 números + 2 trevos)",
        "extras": ["T1 INT", "T2 INT"],
    },
}


def gerar_ddl(nome_tabela: str, qtd_numeros: int, extras: list = None) -> str:
    n_cols = ",\n            ".join(f"N{i} INT" for i in range(1, qtd_numeros + 1))
    s_cols = ",\n            ".join(f"S{i} INT DEFAULT NULL" for i in range(1, qtd_numeros + 1))
    extra_cols = ",\n            ".join(extras) if extras else ""

    cols = f"{n_cols},\n            {s_cols}"
    if extra_cols:
        cols += f",\n            {extra_cols}"

    return f"""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{nome_tabela}' AND xtype='U')
    BEGIN
        CREATE TABLE {nome_tabela} (
            Concurso INT PRIMARY KEY,
            Data_Sorteio VARCHAR(10),
            {cols},
            DataGeracao DATETIME DEFAULT GETDATE()
        );
        PRINT 'Tabela {nome_tabela} criada';
    END
    ELSE
    BEGIN
        PRINT 'Tabela {nome_tabela} ja existe';
    END
    """


def criar_tabela(nome: str, qtd: int, extras: list = None) -> bool:
    extras_str = f" + extras: {extras}" if extras else ""
    print(f"📋 Criando {nome} ({qtd} números{extras_str})...")
    sql = gerar_ddl(nome, qtd, extras)
    return db_config.execute_command(sql)


def main():
    print("=" * 60)
    print("CRIAÇÃO DE TABELAS DE RESULTADOS")
    print("=" * 60)

    if not db_config.test_connection():
        print("❌ Conexão falhou. Abortando.")
        return

    ok = 0
    for nome, info in TABELAS.items():
        extras = info.get("extras")
        if criar_tabela(nome, info["numeros"], extras):
            ok += 1
        else:
            print(f"   ⚠️ Falha ao criar {nome}")

    print(f"\n📊 {ok}/{len(TABELAS)} tabelas criadas/verificadas")
    if ok == len(TABELAS):
        print("🎯 Pronto! Use os atualizadores para popular:")
        for nome in TABELAS:
            print(f"   • from shared.loterias import Atualizador{nome.replace('Resultados_','').replace('MegaSenaFechado','MegaSena')}")
    else:
        print("⚠️ Verifique os erros acima.")


if __name__ == "__main__":
    main()
