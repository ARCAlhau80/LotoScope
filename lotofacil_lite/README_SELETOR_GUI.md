# 🎯 SELETOR DE COMBINAÇÕES ALEATÓRIAS - GUI

## 📋 **DESCRIÇÃO**
Aplicativo desktop com interface gráfica para seleção aleatória de combinações de arquivos TXT gerados pelos sistemas de análise da Lotofácil.

## 🚀 **FUNCIONALIDADES**
- ✅ **Seleção de Arquivo**: Interface para escolher arquivos TXT de combinações
- ✅ **Quantidade Configurável**: Escolha quantas combinações extrair (6, 10, 15, 100, etc.)
- ✅ **Seleção Aleatória**: Algoritmo de amostragem aleatória sem repetição
- ✅ **Visualização**: Preview das combinações selecionadas
- ✅ **Estatísticas**: Análise automática das combinações escolhidas
- ✅ **Exportação**: Salva resultado em novo arquivo TXT
- ✅ **Interface Moderna**: Design intuitivo com Tkinter

## 🎮 **COMO USAR**

### **1. Executar o Aplicativo**
```bash
python seletor_combinacoes_gui.py
```

### **2. Selecionar Arquivo**
- Clique em "📂 Selecionar Arquivo TXT"
- Escolha um arquivo gerado pelos sistemas (ex: `combinacoes_avancadas_moderado_*.txt`)
- O aplicativo mostrará quantas combinações foram encontradas

### **3. Configurar Quantidade**
- Digite a quantidade desejada no campo
- Ou use os botões rápidos: **6**, **10**, **15**, **25**, **50**, **100**

### **4. Gerar Seleção**
- Clique em "🎯 Gerar Seleção Aleatória"
- As combinações serão selecionadas aleatoriamente
- Resultado aparece na área de visualização

### **5. Salvar Resultado**
- Clique em "💾 Salvar Resultado" 
- Escolha local e nome do arquivo
- Arquivo será salvo com cabeçalho e estatísticas

## 📊 **FORMATOS SUPORTADOS**

### **Arquivo de Entrada**
```
# Comentários são ignorados
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
# Mais combinações...
```

### **Arquivo de Saída**
```
# SELEÇÃO ALEATÓRIA DE COMBINAÇÕES - LOTOSCOPE
# Gerado em: 13/08/2025 17:52:30
# Arquivo origem: combinacoes_avancadas_moderado_20250813_164227.txt
# Total disponível: 8,000 combinações
# Selecionadas: 15 combinações
#
# Formato: N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
#============================================================
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
5,8,12,15,18,21,24,3,6,9,13,16,19,22,25
# ... mais combinações
```

## 📈 **ESTATÍSTICAS INCLUÍDAS**
- **Soma Média**: Média das somas das 15 dezenas
- **Números Mais Frequentes**: Top 5 números com maior aparição
- **Range de Somas**: Menor e maior soma encontrada
- **Cobertura Numérica**: Quantos números únicos (1-25) foram utilizados

## 🎯 **CASOS DE USO**

### **Para Apostas Menores**
- Selecione 6-15 combinações para jogos focados
- Ideal para testes com orçamento limitado

### **Para Análise**
- Selecione 50-100 combinações para estudos
- Compare performance de diferentes sistemas

### **Para Grupos**
- Divida milhares de combinações em lotes menores
- Distribua entre múltiplos jogadores

## ⚙️ **REQUISITOS TÉCNICOS**
- **Python 3.7+**
- **Tkinter** (incluído na maioria das instalações Python)
- **Windows/Linux/MacOS**

## 📁 **ARQUIVOS COMPATÍVEIS**
O aplicativo funciona com arquivos gerados por:
- ✅ Sistema de Inteligência Preditiva
- ✅ Sistema de Previsão Adaptativa  
- ✅ Sistema de Otimização Probabilística
- ✅ Gerador Avançado
- ✅ Qualquer arquivo TXT com formato de combinações

## 🛠️ **INTEGRAÇÃO COM MENU**
O aplicativo está integrado ao menu principal:
```
10 - 🖥️ SELETOR DE COMBINAÇÕES GUI (aplicativo desktop)
```

## 💡 **DICAS DE USO**
1. **Performance**: Arquivos com milhões de combinações podem demorar para carregar
2. **Memória**: Grandes arquivos consomem mais RAM
3. **Backup**: Sempre mantenha o arquivo original
4. **Nomenclatura**: Use nomes descritivos para os arquivos salvos

## 🎨 **INTERFACE**
```
┌─────────────────────────────────────────┐
│ 🎯 SELETOR DE COMBINAÇÕES ALEATÓRIAS    │
├─────────────────────────────────────────┤
│ 📁 Arquivo de Origem                    │
│ [📂 Selecionar] arquivo.txt             │
│ 📊 Total: 8,000 combinações             │
├─────────────────────────────────────────┤
│ ⚙️ Configuração da Seleção              │
│ Quantidade: [15] [6][10][15][25][50][100]│
├─────────────────────────────────────────┤
│ [🎯 Gerar Seleção] [💾 Salvar]          │
├─────────────────────────────────────────┤
│ 📊 Resultado da Seleção                 │
│ ┌─────────────────────────────────────┐ │
│ │ 1: 01,02,03,04,05,06,07,08,09,10... │ │
│ │ 2: 03,05,07,09,11,13,15,17,19,21... │ │
│ │ ... mais combinações ...             │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---
**Desenvolvido por AR CALHAU - LotoScope System**
