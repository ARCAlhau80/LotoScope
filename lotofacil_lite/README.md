# 🎯 LOTOFÁCIL LITE

Sistema enxuto para atualização da base de dados e geração de combinações da Lotofácil baseado na classe de conexão funcional testada.

## 📋 Funcionalidades

### 🌐 Atualização da Base
- ✅ Integração com API da Caixa Federal
- ✅ Retry automático para falhas de rede
- ✅ Atualização individual ou em lote
- ✅ Cálculo automático de campos derivados

### 🎲 Geração de Combinações
- ✅ 5 métodos de geração diferentes
- ✅ Sistema de números obrigatórios/proibidos
- ✅ Expansão de quinas para combinações completas
- ✅ Salvamento automático em arquivos TXT

## ⚙️ Instalação

1. **Pré-requisitos:**
   - Python 3.7+
   - SQL Server (com banco LOTOFACIL)
   - Conexão com internet (para API da Caixa)

2. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar banco de dados:**
   
   **OPÇÃO A - Configurador Automático (Recomendado):**
   ```bash
   python configurador.py
   ```
   
   **OPÇÃO B - Manual:**
   - Edite `database_config.py`
   - Ajuste os parâmetros no `__init__`:
     ```python
     def __init__(self, server="SEU_SERVIDOR\\SQLEXPRESS", 
                  database="LOTOFACIL", 
                  driver="ODBC Driver 17 for SQL Server"):
     ```

4. **Criar estrutura do banco:**
   ```bash
   python setup_banco.py
   ```

5. **Testar sistema:**
   ```bash
   python teste_sistema.py
   ```

## 🚀 Uso

### Executar o sistema:
```bash
python main.py
```

### Menu Principal:
- **Opções 1-5:** Atualização da base de dados
- **Opções 6-13:** Geração de combinações
- **Opções 14-15:** Configurações e manutenção

## 📊 Estrutura do Banco

O sistema espera uma tabela `Resultados` com a estrutura:
```sql
CREATE TABLE Resultados (
    Concurso INT PRIMARY KEY,
    DataSorteio VARCHAR(10),
    N1 INT, N2 INT, N3 INT, N4 INT, N5 INT,
    N6 INT, N7 INT, N8 INT, N9 INT, N10 INT,
    N11 INT, N12 INT, N13 INT, N14 INT, N15 INT,
    Baixos INT, Altos INT, Pares INT, Impares INT,
    Consecutivos INT, SomaTotal INT,
    Acumulado BIT, ValorEstimado DECIMAL(15,2),
    UltimaAtualizacao DATETIME
);
```

Tabela opcional `NumerosCiclos` para análise avançada:
```sql
CREATE TABLE NumerosCiclos (
    Numero INT PRIMARY KEY,
    UltimoSorteio INT,
    CicloAtual INT,
    Urgencia DECIMAL(5,2)
);
```

## 🎯 Métodos de Geração

1. **Aleatórias:** Seleção completamente randômica
2. **Por Frequência:** Baseadas no histórico de sorteios
3. **Por Ciclos:** Usando inteligência de ciclos (se disponível)
4. **Balanceadas:** Equilibrio entre pares/ímpares, baixos/altos
5. **Por Padrões:** Sequências e padrões matemáticos

## 🧠 Sistema de Intuição

Configure números que DEVEM ou NÃO DEVEM aparecer:
- **Obrigatórios:** Sempre incluídos nas combinações
- **Proibidos:** Nunca incluídos nas combinações

## 📁 Arquivos Gerados

As combinações são salvas em arquivos TXT com formato:
```
COMBINAÇÕES LOTOFÁCIL
==================================================
Geradas em: 04/08/2025 15:30:00
Total: 10 combinações

 1: 01 03 05 07 09 11 13 15 17 19 21 23 25 02 04
 2: 02 04 06 08 10 12 14 16 18 20 22 24 01 03 05
...
```

## 🔧 Personalização

### Ajustar Conexão do Banco:
Edite `database_config.py`:
```python
self.connection_string = (
    "DRIVER={SQL Server};"
    "SERVER=seu_servidor;"
    "DATABASE=seu_banco;"
    "Trusted_Connection=yes;"
)
```

### Adicionar Novos Métodos:
Estenda a classe `LotofacilGenerator` com novos métodos de geração.

## 🏆 Vantagens do Sistema Lite

- ✅ **Código limpo e focado** 
- ✅ **Fácil manutenção**
- ✅ **Instalação simples**
- ✅ **Menor consumo de recursos**
- ✅ **Funcionalidades essenciais**

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a conexão com o banco de dados
2. Teste a conectividade com a API da Caixa
3. Consulte os logs de erro no terminal

---
**Autor:** AR CALHAU  
**Data:** Agosto 2025  
**Versão:** Lite 1.0
