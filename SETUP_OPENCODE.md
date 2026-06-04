# Como Iniciar o OpenCode para Integração com Agentes

## 1. Iniciar o OpenCode

O OpenCode precisa estar rodando para que os agentes possam chamá-lo via API.

### Opção A: Via Terminal (modo interativo)
```powershell
opencode
```

### Opção B: Via Web (expõe API HTTP)
```powershell
opencode web
```

Isso vai iniciar um servidor HTTP que expõe a API compatível com OpenAI/Ollama.

## 2. Verificar Porta

Após iniciar, o OpenCode vai mostrar no log a porta que está usando. Geralmente:
- **Porta 11434** (padrão Ollama)
- **Porta 3000** (padrão web)
- **Porta 8080** (alternativa)

## 3. Configurar Variáveis de Ambiente

Antes de usar os agentes, configure:

```powershell
# Porta do OpenCode (ajuste conforme o log)
$env:OPENCODE_BASE_URL = "http://localhost:11434/v1"

# API Key (padrão para validação local)
$env:OPENCODE_API_KEY = "opencode-go"

# Modelo (opcional, padrão: qwen3.7-plus)
$env:OPENCODE_MODEL = "qwen3.7-plus"
```

## 4. Testar Conexão

```powershell
# Verificar status
python lotoscope_agents.py opencode-status

# Deve retornar:
# {
#   "available": true,
#   "base_url": "http://localhost:11434/v1",
#   "model": "qwen3.7-plus",
#   "message": "OpenCode disponível"
# }
```

## 5. Usar Agentes com LLM

### Via CLI
```powershell
# Chamar agente SEM LLM (apenas tools locais)
python lotoscope_agents.py call analyst "verificar frequências"

# Chamar agente COM LLM (OpenCode como backend)
python lotoscope_agents.py call-llm analyst "analisar padrões dos últimos 30 concursos"

# Delegar diretamente ao OpenCode
python lotoscope_agents.py delegate "explique a estratégia Pool 23"
```

### Via MCP (Copilot)
```python
# No chat do Copilot:
@LotoScope Analyst analise o concurso 3700

# O agente vai:
# 1. Tentar resolver com tools locais (SQL, execução)
# 2. Se não souber, chama OpenCode via lotoscope_delegate
# 3. Retorna resposta completa
```

## 6. Fluxo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUXO COM OPENCODE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Usuário → @Agente X (Copilot)                              │
│       ↓                                                     │
│  Agente recebe comando                                      │
│       ↓                                                     │
│  Agente executa tools locais (SQL, arquivos, etc)           │
│       ↓                                                     │
│  ┌────────────────────────────────────────                 │
│  │  Agente sabe resolver?                 │                 │
│  │  SIM → Retorna resultado               │                 │
│  │  NÃO → lotoscope_delegate              │                 │
│  └────────────────────────────────────────┘                 │
│       ↓                                                     │
│  OpenCode (LLM local) processa                              │
│       ↓                                                     │
│  OpenCode retorna resposta                                  │
│       ↓                                                     │
│  Agente retorna ao usuário                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 7. Troubleshooting

### OpenCode não conecta
```powershell
# Verificar se está rodando
opencode status

# Verificar porta
netstat -ano | findstr "LISTENING" | findstr "11434\|3000\|8080"

# Reiniciar
opencode web
```

### Erro de autenticação
```powershell
# Verificar API key
$env:OPENCODE_API_KEY = "opencode-go"
```

### Modelo não encontrado
```powershell
# Listar modelos disponíveis
opencode models

# Configurar modelo correto
$env:OPENCODE_MODEL = "qwen3.7-plus"
```

## 8. Exemplos de Uso

### Exemplo 1: Análise com Fallback
```powershell
# Agente tenta resolver localmente primeiro
python lotoscope_agents.py call analyst "buscar últimos 10 concursos"

# Se não souber, usa OpenCode
python lotoscope_agents.py call-llm analyst "interpretar padrões encontrados"
```

### Exemplo 2: Delegação Direta
```powershell
# Delegar pergunta complexa ao OpenCode
python lotoscope_agents.py delegate "explique a diferença entre INVERTIDA v3.0 e SUPERÁVIT"
```

### Exemplo 3: Workflow com LLM
```powershell
# Executar workflow (agentes podem usar LLM internamente)
python lotoscope_agents.py orchestrate pos_sorteio
```

## 9. Configuração Avançada

### Timeout personalizado
```powershell
$env:OPENCODE_TIMEOUT = "120"  # segundos
```

### URL customizada
```powershell
# Se OpenCode roda em outra máquina
$env:OPENCODE_BASE_URL = "http://192.168.1.100:11434/v1"
```

### Modelo diferente
```powershell
# Usar outro modelo (se disponível)
$env:OPENCODE_MODEL = "llama3.1"
```

## 10. Scripts de Inicialização Rápida

### start-opencode.bat
```batch
@echo off
echo Iniciando OpenCode...
start opencode web
timeout /t 5
echo OpenCode iniciado. Verificando status...
python lotoscope_agents.py opencode-status
pause
```

### test-integration.bat
```batch
@echo off
echo Testando integração com OpenCode...
python lotoscope_agents.py opencode-status
echo.
echo Testando chamada com LLM...
python lotoscope_agents.py call-llm coordinator "olá, teste de integração"
pause
```
