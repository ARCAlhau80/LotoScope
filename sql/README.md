# Scripts SQL — LotoScope

Ordem recomendada de execução em um banco novo:

```powershell
sqlcmd -S localhost -E -i sql\01_core_tables.sql
sqlcmd -S localhost -E -i sql\03_procedures_triggers.sql
# opcional (gerador de 20 dezenas):
sqlcmd -S localhost -E -i sql\02_opcional_combinacoes_20.sql
```

## Arquivos

| Arquivo | Obrigatório | O que faz |
|---|---|---|
| `01_core_tables.sql` | Sim | Cria o banco `LOTOFACIL` e as tabelas essenciais (`Resultados_INT`, `NumerosCiclos`, `COMBINACOES_LOTOFACIL`, `COMBINACOES_LOTOFACIL20_COMPLETO`, resultados das loterias). Idempotente. |
| `02_opcional_combinacoes_20.sql` | Não | Cria `COMBINACOES_LOTOFACIL20` sem apagar dados existentes. |
| `03_procedures_triggers.sql` | Sim | Procedures/triggers de ciclos e acertos (`AtualizaNumerosCiclos`, `sp_AtualizarAcertos_LF15`, `trg_AtualizarAcertos_LF15_AfterInsert`, `sp_AtualizarAcertos`, `trg_AtualizarAcertos_AfterInsert`, `SP_AtualizarCamposComparacao`, `SP_AtualizarCombinacoesComparacao`). Usa `CREATE OR ALTER` (SQL Server 2016+). |

## Cuidados

- `01` **não apaga** tabelas existentes; se a tabela já existe, ele não altera a estrutura.
  Em um banco antigo, confira se `NumerosCiclos` tem as 7 colunas esperadas pelo
  dashboard (`Ciclo, Numero, QtdSorteados, ConcursoInicio, ConcursoFechamento,
  DataInicio, DataFim`).
- `criar_tabela_combinacoes_20.sql` e `gerador_combinacoes_20.py` **recriam**
  `COMBINACOES_LOTOFACIL20` (DROP TABLE). Prefira `02_opcional_combinacoes_20.sql`
  se não quiser perder dados.
- Os scripts `adicionar_colunas_*` e `criar_procedure_*` da raiz do repositório
  são idempotentes e podem ser usados como alternativa/complemento ao `01`/`03`.
- Faça backup antes de rodar qualquer script em banco de produção.

## Teste rápido

```sql
SELECT COUNT(*) AS concursos FROM dbo.Resultados_INT;
SELECT COUNT(*) AS ciclos FROM dbo.NumerosCiclos;
SELECT TOP 1 * FROM dbo.Resultados_INT ORDER BY Concurso DESC;
```

## Popular os dados

Depois de criar as tabelas:

```powershell
.\.venv\Scripts\Activate.ps1
python atualizar_todas.py
```

As tabelas de combinações (3,2M/50M linhas) são opcionais e devem ser importadas
de backup ou geradas pelos scripts específicos.
