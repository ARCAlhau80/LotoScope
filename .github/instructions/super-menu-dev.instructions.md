---
description: "Use when developing, extending, or debugging super_menu.py — the main control center of LotoScope (4800+ lines). Covers menu structure, adding new options, navigation patterns, I/O conventions, and how to integrate new analysis modules. Also applies to any file that imports from super_menu or is called by it."
name: "Super Menu Dev Standards"
applyTo: "**/super_menu.py"
---

# Super Menu — Padrões de Desenvolvimento

## Overview

`super_menu.py` é o centro de controle do LotoScope: ~4800 linhas, ~35+ opções numeradas, estrutura de menus aninhados. Toda funcionalidade nova deve ser integrada aqui (ou acessível via aqui).

**Localização:** `lotofacil_lite/interfaces/super_menu.py`

## Estrutura de Menu

```python
# Loop principal — NUNCA modificar o fluxo principal sem revisar todas as opções
while True:
    print_menu_principal()
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == "0":
        break          # Sair
    elif opcao == "1":
        # ... opção 1
    elif opcao == "22":
        menu_opcao_22()  # Sub-menu em função separada
    # ...
```

## Como Adicionar Uma Nova Opção

### Passo 1: Definir o número da opção
- Verificar se o número não conflita com opções existentes
- Sub-opções usam formato "22.1", "30.2", "7.12", etc.

### Passo 2: Adicionar entrada no menu display
```python
# Na função que imprime o menu, adicionar linha como:
print("  [XX] 🎯 NOME DA NOVA OPÇÃO")
```

### Passo 3: Implementar o handler
```python
elif opcao == "XX":
    print("\n" + "="*60)
    print("🎯 TÍTULO DA NOVA OPÇÃO")
    print("="*60 + "\n")
    
    try:
        # Importar módulo se necessário (dentro do elif para lazy loading)
        sys.path.insert(0, BASE_DIR)
        from meu_novo_modulo import MinhaClasse
        
        # Implementação
        resultado = MinhaClasse().executar()
        
    except ImportError as e:
        print(f"❌ Módulo não encontrado: {e}")
    except pyodbc.Error as e:
        print(f"❌ Erro de banco: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n[ENTER para continuar...]")
```

## Convenções de I/O

```python
# Cabeçalho de seção:
print("\n" + "="*60)
print("🎯 TÍTULO DA SEÇÃO")
print("="*60)

# Separadores menores:
print("-"*40)

# Confirmação do usuário:
confirmar = input("\nDeseja continuar? (S/N): ").strip().upper()
if confirmar != 'S':
    print("Cancelado.")
    return

# Entrada numérica com validação:
try:
    nivel = int(input("Nível (0-8): ").strip())
    if not 0 <= nivel <= 8:
        raise ValueError("Fora do range")
except ValueError:
    print("❌ Opção inválida. Usando padrão = 3.")
    nivel = 3
```

## Imports no Topo do Arquivo

```python
# Super_menu importa tudo no topo OU faz lazy imports dentro de cada elif
# PREFERIR lazy imports para módulos pesados (evita lentidão no startup):
elif opcao == "31":
    import sys
    sys.path.insert(0, BASE_DIR)
    from filtro_probabilistico import FiltroProbabilistico  # lazy
```

## Integração com Módulos do Projeto

```python
# Módulos chave que super_menu usa:
# filtro_probabilistico.py         → FiltroProbabilistico
# analise_anomalias_frequencia.py  → AnalisadorAnomalias
# sistema_aprendizado_ml.py        → SistemaML
# estrategia_combo20.py            → EstrategiaC1C2

# Path base (definido no topo do arquivo):
BASE_DIR = r"C:\Users\AR CALHAU\source\repos\LotoScope"
INTERFACES_DIR = r"C:\Users\AR CALHAU\source\repos\LotoScope\lotofacil_lite\interfaces"
```

## Opções Existentes (Referência Rápida)

| Opção | Funcionalidade |
|---|---|
| 7 | Análises e estatísticas (sub-menu com 7.x) |
| 7.12 → 10 | Association Rules v2.0 |
| 7.13 | Heatmap número × posição |
| 22 | Sistema C1/C2 Complementar (sub-menu) |
| 23 | Verificador de TXT (single e batch) |
| 30 | Backtesting (sub-menu) |
| 30.2 | Pool 23 Backtesting com filtros |
| 31 | Pool 23 Gerador Híbrido ⭐ PRINCIPAL |

## Regras

- NUNCA remover opções existentes sem criar alias/deprecation notice
- SEMPRE testar a nova opção isoladamente antes de integrar
- Toda opção deve ter tratamento de exceção com mensagem amigável
- Input de concurso deve aceitar tanto número inteiro quanto "último"
- **🔴 REGRA INVIOLÁVEL — Paridade Opção 31 ↔ Opção 30.2:**
  Toda feature, filtro, prompt ou lógica implementada na **Opção 31** (Pool 23 Gerador)
  **DEVE obrigatoriamente ser replicada** na **Opção 30.2** (Pool 23 Backtesting).
  As duas opções devem manter paridade funcional. Ao concluir uma alteração na Opção 31,
  verificar imediatamente se a Opção 30.2 precisa da mesma mudança e aplicá-la.
