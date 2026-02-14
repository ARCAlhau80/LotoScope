# 🎯 AGENTE ESPECIALIZADO LOTOSCOPE - SISTEMA COMPLETO
## Contexto Completo Atualizado para AI Assistant

### 📋 IDENTIDADE DO AGENTE
```
NOME: LotoScope Assistant
ESPECIALIDADE: Sistema Científico Completo para Análise e Geração da Lotofácil
FOCO: Projeto LotoScope (análise + geração + servidor web + IA)
AMBIENTE: Windows PowerShell, VS Code, SQL Server, Flask
DATA ATUALIZAÇÃO: 30/10/2025
```

### 🎲 PROJETO LOTOSCOPE - VISÃO GERAL ATUALIZADA
Sistema científico completo e integrado para análise estatística, geração inteligente de combinações e interface web interativa para Lotofácil. Combina metodologias acadêmicas rigorosas, inteligência artificial avançada e interface web moderna.

#### **Descobertas da Análise Completa:**
- Sistema muito mais extenso e complexo que inicialmente documentado
- **558+ arquivos** no diretório `lotofacil_lite` (incluindo backups)
- **Super Menu integrado** com 16 sistemas diferentes
- **Servidor web Flask** completo com frontend moderno
- **Múltiplos sistemas de IA** com diferentes abordagens
- **Sistema de validação universal** para orquestração automática
- **🆕 SISTEMA DE AUTO-TREINO CONTÍNUO** - IA autônoma 24/7 com evolução automática
- **🆕 ANÁLISE DE TRANSIÇÃO POSICIONAL** - 53.070 transições calculadas, matrizes 25x25 por posição
- **🆕 ANÁLISE DO ÚLTIMO CONCURSO** - Predição automática baseada em transições históricas

### 🗄️ BASE DE DADOS
```
Servidor: DESKTOP-K6JPBDS
Database: LOTOFACIL
Tabela Principal: RESULTADOS_INT
Registros: 3.539 sorteios históricos (Concurso 1 a 3540)
Tabela Combinações: COMBINACOES_LOTOFACIL (3,2 milhões de registros)
Campos: CONCURSO, N1-N15, Data_Sorteio + 21 campos estatísticos
Status: Conectado e validado

Estrutura RESULTADOS_INT:
- CONCURSO (INT) - Número do concurso
- N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, N11, N12, N13, N14, N15 (INT) - Números sorteados por posição
- Data_Sorteio (VARCHAR) - Data do sorteio
- Campos estatísticos: maior_que_ultimo, menor_que_ultimo, igual_ao_ultimo, etc.
```

### 🏗️ ARQUITETURA COMPLETA DO SISTEMA

#### **1. SUPER MENU PRINCIPAL** (`super_menu.py`)
Centro de controle unificado com **16 sistemas integrados**:

**🆕 SISTEMA DE AUTO-TREINO CONTÍNUO** (Nova Funcionalidade):
0. 🤖 **Sistema Auto-Treino Contínuo** - IA autônoma 24/7 com evolução automática

**Sistemas de Geração:**
1. 🧠 IA de Números Repetidos (rede neural 24.384 neurônios)
2. 🎯 Gerador Acadêmico Dinâmico (insights tempo real)
3. 🔒 Gerador TOP Fixo (combinações determinísticas)
4. 🎯 Gerador Zona de Conforto (80% zona 1-17)
5. 🔥 Super Gerador com IA (sistema integrado completo)
6. 🔺 Pirâmide Invertida Dinâmica (análise faixas IA)

**Sistemas de Análise:**
7. 🧠 Sistema Complementação Inteligente (matemática C(5,3))
8. 🎯 Sistema Ultra-Precisão V4 (15-20 números configurável)
9. 🧠 Sistema Neural V7 - Altos/Baixos (distribuição neural)
10. 🔍 Analisador Metadados Preditivos (reversão estatística)
11. 🔬 Análise Híbrida: Neural + Metadados (validação 16/20 acertos)
12. 🔄 Híbrido V2.0: Correção Reversão Neural (75% melhoria)
13. 🧠 Híbrido V3.0: Lógica Adaptativa (RECOMENDADO)
14. 🚀 Sistema Escalonado V4.0: Filtro+Neural+Ranking
15. 🎯 Sistema Híbrido: Conservador + Oportunidades
16. 📊 Análises e Estatísticas da Base

**Sistemas de Manutenção:**
- 🛠️ Configurações - Atualização e Pipeline
- 🎯 Sistema Redutor Híbrido
- 🚀 Treinamento Automatizado Parametrizado (1-N horas)
- 🎯 Sistema de Validação Universal (executa todos os geradores)

#### **2. SERVIDOR WEB FLASK** (`web/backend/app.py`)
**Interface web moderna e interativa:**

**Endpoints Principais:**
- `/` - Interface principal HTML5
- `/api/health` - Status da API
- `/api/calculate-probability` - Cálculo de probabilidades
- `/api/generate-combinations` - Geração com 4 estados de números:
  - 🟢 **Selecionados**: Preferidos (alta chance de inclusão)
  - 🔒 **Obrigatórios**: Sempre incluídos
  - 🚫 **Excluídos**: Nunca incluídos
  - ⚪ **Neutros**: Sem preferência
- `/api/trend-info` - Informações de tendências preditivas
- `/api/analise-sequencial` - Análise sequencial de padrões
- `/api/last-draw` - Números do último sorteio
- `/api/export-combinations` - Exportação em TXT

**Frontend Moderno:**
- Interface responsiva HTML5/CSS3/JavaScript
- Seleção visual de números (25 números da Lotofácil)
- Sistema de 4 estados por número
- Configuração avançada (perfil de risco, filtros dinâmicos)
- Cálculo de probabilidades em tempo real
- Exportação automática de resultados

#### **3. SISTEMAS DE ANÁLISE ACADÊMICA**

**A. Analisador Acadêmico Limpo** (`analisador_academico_limpo.py`)
- **6 Metodologias Científicas Rigorosas:**
  1. Análise Chi-Quadrado (desvios estatísticos)
  2. Análise FFT - Sazonalidade (transformada Fourier)
  3. Análise de Clustering (K-Means + validação silhouette)
  4. Detecção de Anomalias (Isolation Forest)
  5. Análise de Entropia (teoria da informação)
  6. Análise de Tendências (regressão temporal)

**C. Análise de Metadados Preditivos** (`analisador_metadados_preditivos.py`)
- Análise de 21 campos estatísticos
- Identificação de padrões de reversão (75-80% tendência)
- Geração de cláusulas WHERE preditivas
- Correlações descobertas: QtdeGaps ↔ SEQ (-97%)

**D. Sistema de Análise de Transição Posicional** (`analisador_transicao_posicional.py`) **🆕**
- **Análise completa de probabilidades condicionais** para N1-N15
- **Matrizes de transição 25x25** para cada posição
- **53.070 transições calculadas** baseadas em 3.539 concursos históricos
- **Descoberta de padrões**: Tendência de repetição vs. mudanças graduais
- **Relatórios detalhados**: JSON técnico + resumo executivo em texto
- **Consultas específicas**: Probabilidades condicionais por posição e número
- **Exemplo**: Posição N1 número 1 → 59.4% repetição, 25.8% mudança para 2

**C. Sistema Neural V7** (`sistema_neural_network_v7.py`)
- Rede neural TensorFlow para análise Altos/Baixos (14-25)
- Incorpora padrões de reversão descobertos
- Meta: 76%+ (11/15 acertos)
- Ensemble + Tendências Preditivas

#### **4. SISTEMAS DE IA AVANÇADA**

**A. IA de Números Repetidos** (`ia_numeros_repetidos.py`)
- Rede neural massiva: **24.384 neurônios**
- Aprendizado de padrões de repetição entre concursos
- Sistema de treinamento automatizado 4h → 79.9% precisão
- Múltiplos algoritmos: Ensemble, Neural, Genético, Temporal

**B. Sistema Híbrido V3.0** (`analisador_hibrido_v3.py`)
- **Lógica Adaptativa Inteligente** (RECOMENDADO):
  - SEGUIR neural quando próxima da média
  - REVERTER neural quando extrema  
  - MANTER metadados quando neural incerta
- Melhor equilíbrio neural + metadados

**C. Sistema Escalonado V4.0** (`interface_sistema_v4.py`)
- **REVOLUÇÃO**: De 3,2 milhões → TOP combinações ordenadas
- **Fase 1**: Filtro Redutor Automático (1-10 níveis)
- **Fase 2**: Análise Neural Inteligente
- **Fase 3**: Ranking mais → menos provável

#### **5. SISTEMA DE AUTO-TREINO CONTÍNUO** 🆕 (Nova Funcionalidade)

**A. Sistema Principal Auto-Treino** (`sistema_auto_treino.py`)
- **Auto-treino contínuo 24/7** com seleção aleatória de concursos
- **6 Estratégias evolutivas** que se adaptam automaticamente:
  1. Frequência adaptativa
  2. Análise de lacunas (gaps)  
  3. Balanceamento pares/ímpares
  4. Distribuição por faixas
  5. Sequências inteligentes
  6. Estratégia evolutiva (combina todas)
- **Auto-implementação de melhorias** - gera código automaticamente
- **Persistência de conhecimento** - salva e carrega aprendizado
- **Taxa de sucesso**: 44.4% (acertos ≥13 números)
- **Configuração**: 3.268.760 tentativas por concurso (customizável)

**B. Agente Autônomo Completo** (`agente_completo.py`)
- **Evolução automática** de estratégias baseada em resultados
- **Sistema de memória persistente** para padrões descobertos
- **Auto-correção** quando performance degrada
- **Aprendizado por reforço** com feedback inteligente

**C. Interface de Controle** (`executar_auto_treino.py`)
- **Menu principal** para gerenciar sistema autônomo
- **Configuração avançada** de parâmetros operacionais
- **Monitoramento em tempo real** de performance
- **Status detalhado** do sistema e conhecimento acumulado

**D. Demonstração Funcional** (`demo_auto_treino.py`)
- **Simulação completa** do sistema de auto-treino
- **Base de dados sintética** para testes
- **Métricas de evolução** em tempo real
- **Validação** das capacidades do agente

#### **6. GERADORES INTELIGENTES**

**A. Gerador Acadêmico Dinâmico** (`gerador_academico_dinamico.py`)
- Insights calculados em tempo real da base
- Estratégias de sobreposição:
  - **Alta** (15-16 nums): 12-15 números comuns
  - **Média** (17-18 nums): 9-12 números comuns  
  - **Baixa** (19-20 nums): 8-11 números comuns (CIENTIFICAMENTE COMPROVADA)
- ZERO duplicatas garantido

**B. Gerador Inteligente** (`gerador_inteligente.py`)
- **4 Estratégias baseadas em análise acadêmica:**
  1. **Equilibrada**: Combina todas as metodologias
  2. **Por Tendências**: Foca em números crescimento
  3. **Por Faixas**: Distribui por faixas numéricas
  4. **Anomalia Positiva**: Explora padrões únicos

**C. Sistema de Complementação Inteligente** (`sistema_desdobramento_complementar.py`)
- **Estratégia Revolucionária**: 20 números → 12 acertos + 5 restantes → 3 acertos
- **Matemática**: C(5,3) = 10 combinações garantidas
- Controle total de quantidade e configurações avançadas

#### **7. VISUALIZAÇÃO E RELATÓRIOS**

**A. Visualizador Simples** (`visualizador_simples.py`)
- Gráficos de frequências, correlações, clustering
- Dashboard HTML completo
- Relatórios executivos em texto

**B. Sistema de Relatórios**
- Relatórios JSON estruturados
- Análises de performance automáticas
- Validação retroativa de acertos
- Feedback inteligente para melhoria

### 🔧 STACK TECNOLÓGICO COMPLETO

**Backend & Análise:**
```python
# Análise Científica
import numpy as np          # Computação numérica
import pandas as pd         # Manipulação de dados
import scipy.stats as stats # Estatística avançada
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import tensorflow as tf     # Redes neurais

# Servidor Web
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Banco de Dados
import pyodbc  # Conexão SQL Server

# Visualização
import matplotlib.pyplot as plt
import seaborn as sns
```

**Frontend Web:**
```html
<!-- Interface Moderna -->
HTML5 + CSS3 + JavaScript
Font Awesome (ícones)
Layout responsivo
Tema gradiente profissional
```

### 🎮 WORKFLOWS E COMANDOS PRINCIPAIS

#### **Análise Acadêmica Completa:**
```bash
# Sistema completo integrado
python sistema_completo_final.py

# 🆕 AUTO-TREINO CONTÍNUO (Nova Funcionalidade)
python executar_auto_treino.py

# Sistema de produção direto 24/7
python sistema_auto_treino.py

# Demonstração do agente autônomo
python demo_auto_treino.py

# Análise acadêmica isolada
python analisador_academico_limpo.py

# 🆕 ANÁLISE DE TRANSIÇÃO POSICIONAL (Nova Funcionalidade)
python analisador_transicao_posicional.py

# Servidor web
cd web/backend
python app.py
# Acesse: http://localhost:5000
```

#### **Super Menu (Centro de Controle):**
```bash
python super_menu.py

# Opções principais:
# 1. IA Números Repetidos
# 2. Gerador Acadêmico Dinâmico  
# 3. Super Gerador com IA
# 7.6. Híbrido V3.0 (RECOMENDADO)
# 7.7. Sistema Escalonado V4.0
# 11. Sistema Validação Universal
```

#### **Geração Inteligente:**
```bash
# Gerador com 4 estratégias
python gerador_inteligente.py

# Sistema de complementação
python sistema_desdobramento_complementar.py

# Servidor web interativo
python web/backend/app.py
```

### 📊 OUTPUTS E FORMATOS

#### **Análise JSON Estruturada:**
```json
{
  "analise_chi_quadrado": {
    "numeros_significativos": [1, 7, 13, 19, 25],
    "p_values": {...},
    "interpretacao": "Números com desvio estatístico"
  },
  "tendencias_temporais": {
    "crescimento": [2, 8, 14],
    "declinio": [5, 11, 23]
  },
  "clustering": {
    "clusters": [...],
    "silhouette_score": 0.85
  }
}
```

#### **Combinações TXT (Formato Padrão):**
```
# LotoScope - Combinações Geradas
# Estratégia: Híbrida V3.0 - Lógica Adaptativa
# Total: 10 combinações

02,07,12,18,23,25,28,31,35,38,42,45,48,52,55
01,06,11,17,22,24,27,30,34,37,41,44,47,51,54
...

🗝️ CHAVE DE OURO (formato compacto):
02,07,12,18,23,25,28,31,35,38,42,45,48,52,55
01,06,11,17,22,24,27,30,34,37,41,44,47,51,54
```

#### **Interface Web (Exportação):**
```
# Formato separado por ponto e vírgula
02;07;12;18;23;25;28;31;35;38;42;45;48;52;55
01;06;11;17;22;24;27;30;34;37;41;44;47;51;54
```

### 🚀 DESCOBERTAS IMPORTANTES DA ANÁLISE

#### **Estrutura Arquitetural:**
1. **Super Menu** = Centro de controle com 16 sistemas integrados
2. **Servidor Web** = Interface moderna completa com 4 estados de números
3. **558+ arquivos** = Sistema muito mais extenso que documentado
4. **Múltiplos backups** = Histórico completo de evolução
5. **Sistema de validação universal** = Orquestração automática de todos os geradores

#### **Sistemas de IA Avançados:**
1. **Neural V7** = Análise distribuição Altos/Baixos com reversão
2. **Híbrido V3.0** = Lógica adaptativa inteligente (RECOMENDADO)
3. **Escalonado V4.0** = Revolução: 3,2 milhões → TOP combinações
4. **IA 24.384 neurônios** = Rede massiva com 79.9% precisão
5. **Treinamento parametrizado** = 1-N horas configurável

#### **Interface Web Completa:**
1. **4 Estados de números** = Selecionados, Obrigatórios, Excluídos, Neutros
2. **Análise sequencial** = Padrões históricos em tempo real
3. **Filtros dinâmicos** = Baseados em tendências preditivas
4. **Exportação automática** = Múltiplos formatos
5. **Cálculo probabilidades** = Tempo real com validação

### 🔧 ARQUIVOS ESSENCIAIS (PRINCIPAIS)

#### **Sistema Principal:**
- `super_menu.py` - Centro de controle (17 sistemas incluindo auto-treino)
- `sistema_completo_final.py` - Menu integrado análise + geração
- `database_config.py` - Configuração banco de dados
- **🆕 `sistema_auto_treino.py`** - Sistema de auto-treino contínuo 24/7
- **🆕 `executar_auto_treino.py`** - Interface de controle do auto-treino

#### **Análise Acadêmica:**
- `analisador_academico_limpo.py` - 6 metodologias científicas
- `analisador_hibrido_v3.py` - Lógica adaptativa (RECOMENDADO)
- `sistema_neural_network_v7.py` - Rede neural Altos/Baixos
- `analisador_metadados_preditivos.py` - Análise 21 campos
- **🆕 `analisador_transicao_posicional.py`** - Análise de probabilidades de transição N1-N15

#### **Geração Inteligente:**
- `gerador_inteligente.py` - 4 estratégias baseadas em análise
- `gerador_academico_dinamico.py` - Insights tempo real
- `sistema_desdobramento_complementar.py` - Complementação C(5,3)
- `interface_sistema_v4.py` - Sistema escalonado revolucionário

#### **IA Avançada:**
- `ia_numeros_repetidos.py` - Rede neural 24.384 neurônios
- `sistema_escalonado_v4.py` - Filtro+Neural+Ranking
- `treinamento_automatizado_parametrizado.py` - Treino N horas
- **🆕 `agente_completo.py`** - Agente autônomo evolutivo com 24.000+ neurônios
- **🆕 `agente_neuronios_autonomo.py`** - Versão avançada com auto-implementação
- **🆕 `demo_auto_treino.py`** - Demonstração funcional do sistema autônomo

#### **Servidor Web:**
- `web/backend/app.py` - Servidor Flask principal
- `web/frontend/templates/index.html` - Interface moderna
- `web/database/lotofacil_service.py` - Serviço de dados

#### **Visualização:**
- `visualizador_simples.py` - Gráficos e relatórios
- `demo_sistema_completo.py` - Demonstração automatizada

### 🧹 ARQUIVOS DESNECESSÁRIOS (PODEM SER REMOVIDOS)

#### **Backups Excessivos (280+ arquivos):**
- `*.backup` - Backups simples
- `*.backup_comprehensive` - Backups abrangentes  
- Sugestão: Manter apenas versões mais recentes

#### **Arquivos de Teste/Debug (50+ arquivos):**
- `teste_*.py` - Arquivos de teste específicos
- `debug_*.py` - Scripts de debug pontuais
- `demo_*.py` - Demonstrações específicas (manter principais)

#### **Arquivos Temporários/Obsoletos:**
- `fix_*.py` - Scripts de correção já aplicados
- `temp_*.py` - Arquivos temporários
- `*_temp.json` - Configurações temporárias

#### **Duplicatas/Versões Antigas:**
- Múltiplas versões do mesmo arquivo
- `*_backup.py` sem numeração
- Arquivos com nomes similares (consolidar)

### 🎯 METAS E OBJETIVOS

#### **Funcionalidades Validadas:**
- ✅ **15 acertos comprovados** em 50 combinações (Concurso 3474)
- ✅ **Servidor web** completamente funcional
- ✅ **17 sistemas integrados** no Super Menu (incluindo auto-treino)
- ✅ **Análise acadêmica** com 6 metodologias
- ✅ **IA 79.9% precisão** com treinamento automatizado
- ✅ **🆕 Auto-treino contínuo** com 44.4% taxa de sucesso (≥13 acertos)
- ✅ **🆕 Evolução automática** de estratégias sem intervenção humana
- ✅ **🆕 Análise de transição posicional** com 53.070 transições calculadas

#### **🎯 Sistema de Análise de Transição Posicional:**
- **Arquivo Principal:** `analisador_transicao_posicional.py`
- **Funcionalidade:** Calcula probabilidades de transição número-por-número em cada posição N1-N15
- **Dados Analisados:** 53.070 transições entre 3.539 concursos históricos
- **Matrizes Geradas:** 15 matrizes 25x25 (uma para cada posição)
- **Relatórios:** JSON estruturado + TXT formatado para análise manual
- **Algoritmo:** Quando número X aparece em posição Ni, qual probabilidade de cada número 1-25 aparecer em Ni no próximo concurso

#### **🔮 Sistema de Análise do Último Concurso:**
- **Arquivo Principal:** `analise_ultimo_concurso.py`
- **Funcionalidade:** Predição automática baseada no resultado mais recente
- **Processo:** Analisa N1-N15 do último concurso → Calcula probabilidades → Gera combinações otimizadas
- **Baseado em:** Matrizes de transição de `analisador_transicao_posicional.py`
- **Output:** Combinações com números de maior probabilidade por posição
- **Integração:** Acessível via Super Menu → Opção 5 → Subopções 7 e 8

#### **Próximos Desenvolvimentos:**
- 🚀 Implementar análise preditiva em tempo real
- 📈 Expandir sistema de validação universal  
- 🧠 Otimizar treinamento de IA parametrizado
- 🌐 Melhorar interface web com mais filtros
- 📈 Adicionar análise de performance histórica
- 🆕 **Integrar auto-treino com Super Menu**
- 🆕 **Dashboard de monitoramento 24/7 do agente**
- 🆕 **Auto-implementação de novas estratégias descobertas**
- 🆕 **Integração da análise de transição posicional com sistemas de geração**
- 🆕 **Scripts automáticos de análise do último concurso baseado em transições**

### 💡 DICAS PARA O AGENTE

#### **Sempre Fazer:**
- Usar `super_menu.py` como centro de controle principal
- Verificar conectividade do banco antes de análises
- Usar caracteres ASCII (evitar Unicode no Windows)
- Priorizar sistema Híbrido V3.0 (RECOMENDADO)
- Validar outputs JSON antes de usar

#### **Sistemas Recomendados:**
1. **🆕 Sistema Auto-Treino Contínuo** - IA autônoma 24/7 com evolução automática  
2. **Híbrido V3.0** - Melhor equilíbrio neural + metadados
3. **Sistema Escalonado V4.0** - Revolução em filtros
4. **Servidor Web** - Interface moderna completa
5. **IA 24.384 neurônios** - Máxima precisão
6. **Gerador Acadêmico Dinâmico** - Combinações cientificamente validadas

#### **Debugging Prioritário:**
- Problemas Unicode → Verificar caracteres especiais em todos os arquivos
- Erro SQL → Testar string conexão com `database_config.py`
- Performance lenta → Usar análise acadêmica em lotes
- JSON inválido → Validar com `corrigir_json.py`
- Interface web → Verificar status em `/api/health`

### 📚 SISTEMA DE APRENDIZADO CONTÍNUO

#### **Validação Automática:**
- Sistema de feedback inteligente para todos os geradores
- Análise retroativa de acertos
- Ranking automático de performance
- Evolução documentada em JSON

#### **Orquestração Completa:**
- Sistema de validação universal executa todos os 16 geradores
- Comparação automática de resultados
- Feedback distribuído para melhoria
- Dashboard de evolução em tempo real

---

## 🚀 INSTRUÇÕES DE USO PARA AI ASSISTANT

**Quando o usuário mencionar LotoScope:**
1. Usar este documento como contexto completo atualizado
2. **🆕 PRIORIZAR Sistema Auto-Treino** para IA autônoma e evolução contínua
3. Usar Super Menu como centro de controle (17 sistemas)
4. Recomendar sistemas validados (Auto-Treino, Híbrido V3.0, Escalonado V4.0)
5. Usar servidor web para interface moderna
6. Aplicar workflows e comandos documentados

**Para análise e geração:**
- **🆕 Auto-treino contínuo**: `python executar_auto_treino.py`
- **🆕 Sistema de produção 24/7**: `python sistema_auto_treino.py`
- Sistema completo: `python sistema_completo_final.py`
- Centro de controle: `python super_menu.py`
- Interface web: `python web/backend/app.py`
- Sistema recomendado: Opção 0 (Auto-Treino) ou 7.6 (Híbrido V3.0)

**Para desenvolvimento:**
- Seguir padrões estabelecidos nos 558+ arquivos
- Manter compatibilidade com Windows PowerShell
- Usar apenas caracteres ASCII
- Documentar mudanças neste arquivo
- Priorizar sistemas validados com 15+ acertos

---
*Documento atualizado: 18/11/2025*
*Versão: 4.0 (Incluindo Sistema Auto-Treino Contínuo + Análise de Transição Posicional)*
*Total de arquivos analisados: 558+*
*Sistemas integrados: 17 (incluindo auto-treino)*
*Precisão máxima: 79.9% (IA Neural) | 44.4% (Auto-Treino ≥13 acertos)*
*Análise de Transição: 53.070 transições calculadas em matrizes 25x25*