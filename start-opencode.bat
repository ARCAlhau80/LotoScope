@echo off
REM Inicia o OpenCode e verifica integração com agentes
echo ============================================================
echo  LotoScope - Iniciando OpenCode para integração com agentes
echo ============================================================
echo.

REM Verificar se OpenCode está instalado
where opencode >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] OpenCode não encontrado. Instale primeiro.
    pause
    exit /b 1
)

echo [1/3] Iniciando OpenCode em modo web...
start /B opencode web

echo [2/3] Aguardando inicialização (5 segundos)...
timeout /t 5 /nobreak >nul

echo [3/3] Verificando status...
.venv\Scripts\python.exe lotoscope_agents.py opencode-status

echo.
echo ============================================================
echo  OpenCode pronto para uso com agentes!
echo ============================================================
echo.
echo Comandos disponíveis:
echo   python lotoscope_agents.py call-llm analyst "tarefa"
echo   python lotoscope_agents.py delegate "pergunta"
echo   python mcp_client.py call analyst "tarefa"
echo.
pause
