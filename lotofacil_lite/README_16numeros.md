# 🎯 SISTEMA GERADOR LOTOFÁCIL 16 NÚMEROS

Sistema completo para geração e análise de todas as combinações possíveis de 16 números da Lotofácil.

## 📋 VISÃO GERAL

O sistema gera todas as **2.042.975 combinações únicas** de 16 números (de 1 a 25) e armazena em banco SQL Server com análises estatísticas completas.

## 📁 ARQUIVOS PRINCIPAIS

### 🚀 Scripts de Execução
- **`controle_principal_16numeros.py`** - Menu principal com todas as opções
- **`gerar_combinacoes_16numeros.py`** - Gerador completo (2.042.975 combinações)
- **`gerar_combinacoes_16numeros_teste.py`** - Versão de teste (amostra configurável)

### ⚙️ Arquivos de Configuração
- **`database_config.py`** - Configurações do banco de dados

## 🎮 COMO USAR

### Opção 1: Menu Interativo (RECOMENDADO)
```bash
python controle_principal_16numeros.py
```

### Opção 2: Execução Direta

**Teste rápido (amostra):**
```bash
python gerar_combinacoes_16numeros_teste.py
```

**Geração completa:**
```bash
python gerar_combinacoes_16numeros.py
```

## 📊 ESTRUTURA DA TABELA

### Tabela: `COMBINACOES_LOTOFACIL16`

#### Colunas de Números (16 campos)
- `N1` a `N16` (tinyint) - Os 16 números da combinação

#### Propriedades Estatísticas
- `SOMA` (int) - Soma total dos números
- `PARES` (tinyint) - Quantidade de números pares
- `IMPARES` (tinyint) - Quantidade de números ímpares
- `FAIXA_01_05` (tinyint) - Números de 1 a 5
- `FAIXA_06_10` (tinyint) - Números de 6 a 10
- `FAIXA_11_15` (tinyint) - Números de 11 a 15
- `FAIXA_16_20` (tinyint) - Números de 16 a 20
- `FAIXA_21_25` (tinyint) - Números de 21 a 25
- `SEQ_MAX` (tinyint) - Maior sequência consecutiva
- `PRIMOS` (tinyint) - Quantidade de números primos
- `FIBONACCI` (tinyint) - Quantidade de números Fibonacci

#### Campos de Controle
- `ID` (bigint) - Chave primária
- `DATA_CRIACAO` (datetime) - Data de criação
- `QTDE_NUMEROS` (tinyint) - Sempre 16

## 🔧 PRÉ-REQUISITOS

### Software Necessário
- Python 3.7+
- SQL Server (qualquer versão)
- Driver ODBC para SQL Server

### Bibliotecas Python
```bash
pip install pyodbc
```

### Configuração do Banco
1. Configure as credenciais em `database_config.py`
2. Certifique-se que o banco `LOTOFACIL` existe
3. O usuário deve ter permissões de CREATE TABLE

## ⚡ MODOS DE OPERAÇÃO

### 🧪 Modo Teste
- Gera amostra configurável (1.000 a 500.000 combinações)
- Cria tabela `COMBINACOES_LOTOFACIL16_TESTE`
- Ideal para validar estrutura e performance
- **Tempo:** Segundos a poucos minutos

### 🚀 Modo Completo
- Gera TODAS as 2.042.975 combinações
- Cria tabela `COMBINACOES_LOTOFACIL16`
- Processamento em lotes de 10.000
- **Tempo:** 2-4 horas
- **Espaço:** ~500MB

## 📈 PERFORMANCE

### Otimizações Implementadas
- ✅ Processamento em lotes (10.000 por vez)
- ✅ Índices automáticos
- ✅ Transações otimizadas
- ✅ Progress tracking
- ✅ Validação de integridade

### Recursos do Sistema
- **RAM:** Mínimo 2GB, recomendado 4GB+
- **CPU:** Qualquer (multi-core acelera)
- **Disco:** 1GB livre (incluindo logs)
- **Rede:** Conexão estável com SQL Server

## 📋 FUNCIONALIDADES DO MENU

### 1. 🧪 Gerar Amostra de Teste
- Opções: 1K, 10K, 100K ou personalizado
- Valida estrutura da tabela
- Testa consultas e índices

### 2. 🚀 Gerar TODAS as Combinações
- 2.042.975 combinações completas
- Progress em tempo real
- Validação final

### 3. 📊 Verificar Status da Tabela
- Conta registros em cada tabela
- Exibe estatísticas básicas
- Status da conexão

### 4. 🔍 Consultar Combinações
- Visualiza registros existentes
- Suporte para todas as tabelas
- Primeiros 10 registros

### 5. ⚙️ Testar Conexão
- Valida conectividade
- Exibe configurações
- Diagnóstico de problemas

### 6. 🧹 Limpar Tabela de Teste
- Remove tabela de teste
- Libera espaço em disco
- Operação segura

## 🔍 EXEMPLOS DE CONSULTAS

### Combinações com Soma Entre 200-220
```sql
SELECT TOP 10 N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15, N16
FROM COMBINACOES_LOTOFACIL16 
WHERE SOMA BETWEEN 200 AND 220
ORDER BY SOMA
```

### Combinações Balanceadas (8 Pares, 8 Ímpares)
```sql
SELECT COUNT(*) as total
FROM COMBINACOES_LOTOFACIL16 
WHERE PARES = 8 AND IMPARES = 8
```

### Distribuição por Faixas
```sql
SELECT FAIXA_01_05, FAIXA_06_10, FAIXA_11_15, FAIXA_16_20, FAIXA_21_25, COUNT(*) as qtde
FROM COMBINACOES_LOTOFACIL16 
GROUP BY FAIXA_01_05, FAIXA_06_10, FAIXA_11_15, FAIXA_16_20, FAIXA_21_25
ORDER BY qtde DESC
```

## 🚨 SOLUÇÃO DE PROBLEMAS

### Erro de Conexão
```
❌ Erro na conexão com o banco
```
**Solução:** Verifique `database_config.py` e teste conectividade

### Erro de Permissão
```
❌ CREATE permission denied
```
**Solução:** Usuario precisa de permissões DDL no banco

### Erro de Memória
```
❌ Memory error during generation
```
**Solução:** Reduza o tamanho do lote ou use modo teste

### Tabela já Existe
```
❌ Table already exists
```
**Solução:** Use menu para verificar status ou limpar tabelas

## 📞 SUPORTE

### Log de Execução
- Todos os scripts exibem progress detalhado
- Erros são capturados e exibidos
- Timestamp em todas as operações

### Validação Automática
- Contagem de registros
- Verificação de integridade
- Testes de consulta

### Recuperação
- Processo pode ser interrompido com Ctrl+C
- Lotes já processados permanecem salvos
- Reinício seguro a qualquer momento

## 📈 ESTATÍSTICAS ESPERADAS

### Distribuições Típicas (16 números)
- **Soma mínima:** 136 (números 1-16)
- **Soma máxima:** 304 (números 10-25)
- **Soma média:** ~208
- **Pares:** 4-12 (distribuição normal ~8)
- **Sequência máxima:** 1-16 possível

### Volume de Dados
- **Registros:** 2.042.975
- **Campos por registro:** 25
- **Tamanho estimado:** 400-500MB
- **Índices:** +100MB

---

## 🎯 PRONTO PARA USAR!

Execute o menu principal:
```bash
python controle_principal_16numeros.py
```

**Dica:** Comece sempre com o modo teste para validar sua configuração! 🧪

---

**Autor:** AR CALHAU  
**Data:** 24 de Agosto de 2025  
**Versão:** 1.0
