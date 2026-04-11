# 🔧 REFERÊNCIA TÉCNICA LOTOSCOPE
## Guia de Código, APIs e Integrações

> **Complemento ao CONTEXTO_MASTER_IA.md**
> Este arquivo contém detalhes técnicos para implementação.

```
📅 ÚLTIMA ATUALIZAÇÃO: 26/01/2026
```

---

## 📦 CLASSES E MÓDULOS PRINCIPAIS

### 1. SuperMenuLotofacil (`interfaces/super_menu.py`)

```python
from interfaces.super_menu import SuperMenuLotofacil

menu = SuperMenuLotofacil()

# Métodos principais
menu.executar_menu()                        # Loop principal do menu
menu.executar_estrategia_combo20()          # Submenu opção 22
menu.executar_analise_c1c2_complementar()   # Análise C1/C2 (opção 22.6)
menu.executar_filtro_noneto_personalizado() # Filtro Noneto (opção 22.7)
menu.executar_analise_numero_posicao()      # Heatmap NR × Posição (opção 7.13) ⭐ NOVO!
menu.executar_gerador_academico()           # Gerador dinâmico
menu.executar_super_gerador()               # Super gerador IA

# Métodos internos do Noneto (opção 22.7)
menu._analisar_noneto(resultados, noneto)   # Analisa distribuição
menu._aplicar_filtro_noneto(noneto)         # Aplica filtro e salva
menu._buscar_melhores_nonetos(resultados)   # Busca automática
```

### 2. EstrategiaCombo20 (`analisadores/estrategia_combo20.py`)

```python
from estrategia_combo20 import EstrategiaCombo20

sistema = EstrategiaCombo20()

# Constantes da classe
sistema.COMBO1      # [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
sistema.COMBO2      # [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
sistema.DIV_C1      # [1, 3, 4]
sistema.DIV_C2      # [15, 17, 18]
sistema.NUCLEO      # [6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
sistema.FORA_AMBAS  # [2, 5]

# Métodos principais
sistema.carregar_resultados()               # Carrega do banco
sistema.analisar_tendencia()                # Analisa últimos 100
sistema.exibir_tendencia()                  # Mostra no console
sistema.sugerir_estrategia()                # Retorna 'C1', 'C2' ou 'HIBRIDA'

# Geração de combinações
combinacoes = sistema.gerar_combinacoes(
    quantidade=None,      # None = todas possíveis
    min_c1=0, max_c1=20,  # Range de números da Combo 1
    min_c2=0, max_c2=20,  # Range de números da Combo 2
    usar_fora=False,      # Usar [2, 5]?
    estrategia='SUGERIDA' # 'C1', 'C2', 'HIBRIDA', 'SUGERIDA'
)

# Validação e salvamento
validacao = sistema.validar_combinacoes(combinacoes)
sistema.exibir_combinacoes(combinacoes, validacao)
sistema.salvar_combinacoes(combinacoes)
```

### 3. GeradorAcademicoDinamico (`geradores/gerador_academico_dinamico.py`)

```python
from gerador_academico_dinamico import GeradorAcademicoDinamico

gerador = GeradorAcademicoDinamico()

# Calcular insights (OBRIGATÓRIO antes de gerar)
if gerador.calcular_insights_dinamicos():
    # Gerar combinações
    combinacoes = gerador.gerar_multiplas_combinacoes(
        quantidade=5,
        qtd_numeros=15,      # 15-20 números
        max_tentativas=1000
    )
    
    # Gerar combinação de 20 números
    combo_20 = gerador.gerar_combinacao_20_numeros()
```

---

## 🗃️ QUERIES SQL FREQUENTES

### Últimos N Concursos
```sql
SELECT TOP 20 
    Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 
FROM Resultados_INT 
ORDER BY Concurso DESC
```

### Contagem Total
```sql
SELECT COUNT(*) as Total FROM Resultados_INT
```

### Último Concurso
```sql
SELECT TOP 1 Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
FROM Resultados_INT 
ORDER BY Concurso DESC
```

### Frequência de Números (últimos 100)
```sql
-- Não existe diretamente, calcular via Python:
SELECT TOP 100 N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
FROM Resultados_INT 
ORDER BY Concurso DESC
```

---

## 🐍 SNIPPETS PYTHON ÚTEIS

### Conexão Padrão com Banco
```python
import pyodbc

def conectar_banco():
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

# Uso
with conectar_banco() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
```

### Calcular Frequências
```python
from collections import Counter

def calcular_frequencias(n_concursos=100):
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT TOP {n_concursos} N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT ORDER BY Concurso DESC
        ''')
        frequencias = Counter()
        for row in cursor.fetchall():
            frequencias.update([row[i] for i in range(15)])
    return frequencias

# Uso
freq = calcular_frequencias(100)
print(freq.most_common(10))  # Top 10 mais frequentes
```

### Analisar Tendência C1/C2
```python
DIV_C1 = {1, 3, 4}
DIV_C2 = {15, 17, 18}

def analisar_tendencia(n_concursos=20):
    c1, c2, neutro = 0, 0, 0
    
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT TOP {n_concursos} Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT ORDER BY Concurso DESC
        ''')
        for row in cursor.fetchall():
            resultado = set(row[i] for i in range(1, 16))
            d1 = len(resultado & DIV_C1)
            d2 = len(resultado & DIV_C2)
            
            if d1 > d2: c1 += 1
            elif d2 > d1: c2 += 1
            else: neutro += 1
    
    return {'c1': c1, 'c2': c2, 'neutro': neutro}

# Uso
tend = analisar_tendencia(20)
if tend['c1'] > tend['c2']:
    print("Jogar C1")
else:
    print("Jogar C2")
```

### Analisar Noneto Personalizado (NOVO!)
```python
def analisar_noneto(noneto=[1, 2, 4, 8, 10, 13, 20, 24, 25]):
    """Analisa um noneto nos resultados históricos"""
    from collections import Counter
    noneto_set = set(noneto)
    
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT ORDER BY Concurso
        ''')
        acertos = []
        for row in cursor.fetchall():
            resultado = set(row)
            ac = len(resultado & noneto_set)
            acertos.append(ac)
    
    dist = Counter(acertos)
    faixa_5_7 = sum(dist[a] for a in [5,6,7]) / len(acertos) * 100
    
    return {
        'media': sum(acertos)/len(acertos),
        'faixa_5_7_pct': faixa_5_7,
        'distribuicao': dict(dist)
    }

# Uso
result = analisar_noneto([1, 2, 4, 8, 10, 13, 20, 24, 25])
print(f"Média: {result['media']:.2f}")
print(f"Faixa 5-7: {result['faixa_5_7_pct']:.1f}%")
```

### Análise Número × Posição - Heatmap (NOVO!)
```python
def analisar_numero_posicao(conc_ini=None, conc_fim=None):
    """
    Analisa frequência de cada número (1-25) em cada posição (N1-N15)
    Retorna matriz com percentuais e desvios da média histórica
    
    Cores (desvio da média):
    - Vermelho: 10%+ abaixo (frio)
    - Azul: 6-10% abaixo
    - Branco: ±6% (normal)
    - Laranja: 6-10% acima
    - Roxo: 10%+ acima (quente)
    """
    from collections import defaultdict
    import pyodbc
    
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
    
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        
        # Definir range (default: últimos 30)
        if not conc_fim:
            cursor.execute("SELECT MAX(Concurso) FROM Resultados_INT")
            conc_fim = cursor.fetchone()[0]
        if not conc_ini:
            conc_ini = conc_fim - 29
        
        # Buscar período e histórico
        cursor.execute(f"""
            SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT WHERE Concurso BETWEEN {conc_ini} AND {conc_fim}
        """)
        periodo = cursor.fetchall()
        
        cursor.execute("SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 FROM Resultados_INT")
        historico = cursor.fetchall()
    
    # Calcular frequências
    freq_periodo = defaultdict(lambda: defaultdict(int))
    for row in periodo:
        for pos in range(15):
            freq_periodo[row[pos]][pos] += 1
    
    freq_hist = defaultdict(lambda: defaultdict(int))
    for row in historico:
        for pos in range(15):
            freq_hist[row[pos]][pos] += 1
    
    # Retornar matriz de percentuais e desvios
    resultado = {}
    for num in range(1, 26):
        resultado[num] = {}
        for pos in range(15):
            pct_per = freq_periodo[num][pos] / len(periodo) * 100 if periodo else 0
            pct_hist = freq_hist[num][pos] / len(historico) * 100 if historico else 0
            desvio = ((pct_per - pct_hist) / pct_hist * 100) if pct_hist > 0 else 0
            resultado[num][pos] = {'pct': pct_per, 'desvio': desvio}
    
    return resultado

# Uso no menu: Opção 7.13
```

### Carregar Combinações de Arquivo
```python
def carregar_combinacoes(arquivo: str) -> list:
    """Carrega combinações de arquivo TXT"""
    combinacoes = []
    with open(arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                try:
                    nums = [int(n) for n in linha.split(',')]
                    if len(nums) == 15:
                        combinacoes.append(nums)
                except ValueError:
                    continue
    return combinacoes
```

### Validar Combinações contra Histórico
```python
def validar_historico(combinacoes: list, n_concursos: int = 100):
    """Valida combinações contra últimos N concursos"""
    
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT Concurso, N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
            FROM Resultados_INT 
            ORDER BY Concurso DESC
        ''')
        resultados = [(row.Concurso, set(row[i] for i in range(1,16))) 
                      for row in cursor.fetchall()[:n_concursos]]
    
    PREMIOS = {11: 7, 12: 14, 13: 35, 14: 1000, 15: 1800000}
    CUSTO = 3.00
    
    total_apostado = len(combinacoes) * CUSTO * n_concursos
    total_ganho = 0
    
    for concurso, resultado in resultados:
        for combo in combinacoes:
            acertos = len(set(combo) & resultado)
            if acertos >= 11:
                total_ganho += PREMIOS[acertos]
    
    retorno = (total_ganho / total_apostado - 1) * 100
    
    return {
        'apostado': total_apostado,
        'ganho': total_ganho,
        'retorno_pct': retorno
    }
```

---

## 📁 FORMATO DOS ARQUIVOS

### Arquivos de Combinações (.txt)
```
# COMENTÁRIO - Linhas começando com # são ignoradas
# Data: 22/01/2026 12:00
# Total: 1000 combinações

1,3,4,6,7,8,9,10,11,12,13,14,19,20,21
1,3,4,6,7,8,9,10,11,12,13,14,19,20,22
1,3,4,6,7,8,9,10,11,12,13,14,19,20,23
...
```

### Padrão de Nomenclatura
```
combo20_[TIPO]_[ESTRATEGIA]_[TIMESTAMP].txt

Exemplos:
- combo20_estrategia_20260121_143756.txt
- combo20_FILTRADAS_TOP1000.txt
- combo20_C1_TOP50_20260122_120000.txt
- combo20_C2_tendencia.txt
```

---

## 🌐 API FLASK (web/backend/app.py)

### Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Interface HTML principal |
| GET | `/api/health` | Status da API |
| GET | `/api/last-draw` | Último sorteio |
| POST | `/api/generate-combinations` | Gerar combinações |
| POST | `/api/calculate-probability` | Calcular probabilidades |
| GET | `/api/trend-info` | Informações de tendência |

### Exemplo: Gerar Combinações via API
```python
import requests

response = requests.post('http://localhost:5000/api/generate-combinations', json={
    'quantidade': 5,
    'selecionados': [7, 8, 9, 10, 11],      # Preferidos
    'obrigatorios': [12, 13],               # Sempre incluir
    'excluidos': [1, 2, 3],                 # Nunca incluir
    'perfil_risco': 'moderado'
})

data = response.json()
print(data['combinacoes'])
```

---

## 🔄 FLUXOS DE DADOS

### Fluxo: Geração de Combinações
```
1. Usuário escolhe opção no menu
2. Sistema carrega dados do SQL Server
3. Calcula frequências/tendências
4. Aplica filtros (núcleo, divergentes, etc.)
5. Gera combinações ordenadas por score
6. Valida contra histórico (opcional)
7. Salva em arquivo .txt
```

### Fluxo: Análise C1/C2
```
1. Carregar últimos 20 resultados
2. Para cada resultado:
   - Contar divergentes C1 (interseção com {1,3,4})
   - Contar divergentes C2 (interseção com {15,17,18})
   - Classificar: C1 favorável, C2 favorável, ou Neutro
3. Somar totais
4. Recomendar baseado na maioria
5. Carregar arquivo correspondente (C1 ou C2)
6. Exibir/salvar TOP combinações
```

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### Constantes do Sistema
```python
# Lotofácil
NUMEROS_DISPONIVEIS = list(range(1, 26))  # 1 a 25
NUMEROS_POR_APOSTA = 15
NUMEROS_SORTEADOS = 15

# Prêmios (valores médios)
PREMIOS = {
    11: 7,
    12: 14,
    13: 35,
    14: 1000,
    15: 1800000
}

# Custo base
CUSTO_APOSTA = 3.00

# Combo 20
COMBO1 = [1,3,4,6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
COMBO2 = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
DIV_C1 = [1, 3, 4]
DIV_C2 = [15, 17, 18]
NUCLEO = [6,7,8,9,10,11,12,13,14,16,19,20,21,22,23,24,25]
FORA_AMBAS = [2, 5]
```

### Filtros Padrão
```python
# Filtro de núcleo
MIN_NUCLEO = 13  # Mínimo de números do núcleo na combinação

# Filtro de frequência
TOP_FREQ_PCT = 0.20  # Top 20% por frequência

# Limite de combinações
TOP_COMBINACOES = 1000
```

### Pós-carga da Resultados_INT
```powershell
cd "C:\Users\AR CALHAU\source\repos\LotoScope"
python pos_carga_resultados_int.py
```

Use após `TRUNCATE` ou reimport da `Resultados_INT` para recomputar:
- `menor_que_ultimo`
- `maior_que_ultimo`
- `igual_ao_ultimo`

Rotina base reutilizável em código:
```python
from validar_campos_posicionais import recalcular_campos_posicionais

resumo = recalcular_campos_posicionais(verbose=True)
```

---

## 🐛 DEBUG E LOGS

### Ativar Modo Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verificar Estrutura do Banco
```python
with conectar_banco() as conn:
    cursor = conn.cursor()
    
    # Ver tabelas
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES")
    print([row[0] for row in cursor.fetchall()])
    
    # Ver colunas da tabela principal
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Resultados_INT'
    """)
    for col in cursor.fetchall():
        print(f"{col[0]}: {col[1]}")
```

---

## 📊 MÉTRICAS E KPIs

### Cálculo de Retorno
```python
def calcular_retorno(apostado, ganho):
    if apostado == 0:
        return 0
    return ((ganho / apostado) - 1) * 100

# Exemplo
apostado = 300000  # R$ 300k
ganho = 1960210    # R$ 1.96M
retorno = calcular_retorno(apostado, ganho)
print(f"Retorno: {retorno:+.2f}%")  # +553.40%
```

### Distribuição de Acertos
```python
from collections import Counter

def distribuicao_acertos(combinacoes, resultado):
    """Conta quantas combinações acertaram cada faixa"""
    resultado_set = set(resultado)
    acertos = [len(set(c) & resultado_set) for c in combinacoes]
    return Counter(acertos)

# Uso
dist = distribuicao_acertos(minhas_combinacoes, [1,3,7,8,9,10,11,12,13,14,19,20,21,22,25])
print(dist)  # Counter({11: 450, 12: 280, 10: 200, 13: 50, 14: 15, 9: 5})
```

---

> 💡 Este documento é complementar ao `CONTEXTO_MASTER_IA.md`.
> Para visão geral do projeto, consulte o documento principal.
