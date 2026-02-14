@echo off
chcp 65001 >nul
title LotoScope AI Assistant

echo.
echo ███████╗ ███████╗ ████████╗ ███████╗ ███████╗ ██████╗  ███████╗ ██████╗  ███████╗
echo ██╔════╝ ██╔════╝ ╚══██╔══╝ ██╔════╝ ██╔════╝ ██╔══██╗ ██╔════╝ ██╔══██╗ ██╔════╝
echo ██║  ███╗██║  ███╗    ██║    ██║  ███╗███████║  ██████╔╝ ███████║  ██████╔╝ █████╗  
echo ██║   ██║██║   ██║    ██║    ██║   ██║╚════██║  ██╔═══╝  ╚════██║  ██╔═══╝  ██╔══╝  
echo ╚██████╔╝╚██████╔╝    ██║    ╚██████╔╝███████║  ██║      ███████║  ██║      ███████╗
echo  ╚═════╝  ╚═════╝     ╚═╝     ╚═════╝ ╚══════╝  ╚═╝      ╚══════╝  ╚═╝      ╚══════╝
echo.
echo                      🤖 AI ASSISTANT COM LLAMA LOCAL 🤖
echo.

cd /d "%~dp0"

REM Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo    Instale Python 3.8+ de https://python.org
    pause
    exit /b 1
)

REM Menu principal
:menu
echo.
echo ═══════════════════════════════════════════════════════════════
echo 🚀 MENU PRINCIPAL - LOTOSCOPE AI
echo ═══════════════════════════════════════════════════════════════
echo.
echo [1] 🤖 Iniciar Chat Interativo
echo [2] 🔍 Verificar Sistema
echo [3] ⚙️  Instalar/Configurar Llama
echo [4] 📊 Executar Gerador Dinâmico
echo [5] 🧪 Testar Assistente
echo [6] 📚 Ver Documentação
echo [7] ❌ Sair
echo.
set /p opcao="Escolha uma opção [1-7]: "

if "%opcao%"=="1" goto chat
if "%opcao%"=="2" goto verificar
if "%opcao%"=="3" goto instalar
if "%opcao%"=="4" goto gerador
if "%opcao%"=="5" goto testar
if "%opcao%"=="6" goto docs
if "%opcao%"=="7" goto sair

echo ❌ Opção inválida!
timeout /t 2 >nul
cls
goto menu

:chat
echo.
echo 🤖 Iniciando Chat Interativo...
python lotoscope_ai_chat.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro ao iniciar chat. Verifique o sistema.
    pause
)
goto menu

:verificar
echo.
echo 🔍 Verificando Sistema...
python verificar_sistema.py
pause
goto menu

:instalar
echo.
echo ⚙️ Configurando Llama...
python setup_llama.py
pause
goto menu

:gerador
echo.
echo 📊 Executando Gerador Dinâmico...
python gerador_academico_dinamico_megasena.py
pause
goto menu

:testar
echo.
echo 🧪 Testando Assistente...
python -c "
from lotoscope_ai_assistant import LotoScopeAIAssistant
import sys

try:
    assistant = LotoScopeAIAssistant()
    status_ok, status_msg = assistant.check_ollama_status()
    print(f'Status: {status_msg}')
    
    if status_ok:
        print('✅ Teste básico aprovado!')
        resposta = assistant.responder('Olá, você está funcionando?')
        print(f'Resposta do AI: {resposta[:100]}...')
    else:
        print('❌ Sistema não está pronto')
        
except Exception as e:
    print(f'❌ Erro no teste: {e}')
    sys.exit(1)
"
pause
goto menu

:docs
echo.
echo 📚 Documentação do LotoScope AI Assistant
echo ═══════════════════════════════════════════
echo.
echo 🎯 PRINCIPAIS FUNCIONALIDADES:
echo    • Chat interativo com IA especializada em loteria
echo    • Análise automática de código Python
echo    • Sugestões de otimização e melhorias  
echo    • Pesquisa de padrões em resultados históricos
echo    • Geração de combinações inteligentes
echo.
echo 💬 COMANDOS ESPECIAIS DO CHAT:
echo    /analyze arquivo.py    - Analisa código
echo    /improve tópico        - Sugere melhorias
echo    /patterns jogo         - Pesquisa padrões
echo    /status               - Status do sistema
echo    /config               - Mostra configurações
echo    /help                 - Ajuda completa
echo    /clear                - Limpa conversa
echo    /quit                 - Sair do chat
echo.
echo 🔧 ARQUIVOS IMPORTANTES:
echo    • lotoscope_ai_chat.py        - Interface de chat
echo    • lotoscope_ai_assistant.py   - Core do assistente
echo    • config.ini                  - Configurações
echo    • setup_llama.py              - Instalador automático
echo.
pause
goto menu

:sair
echo.
echo 👋 Obrigado por usar o LotoScope AI Assistant!
echo    Desenvolvido com IA local para máxima privacidade
echo.
timeout /t 3 >nul
exit

REM Tratamento de erro geral
:erro
echo.
echo ❌ Ocorreu um erro inesperado!
echo    Verifique se todos os arquivos estão presentes
echo    e se o Python está corretamente instalado.
echo.
pause
goto menu
