@echo off
REM Inicia o OpenCode Proxy Server
echo ============================================================
echo  LotoScope - Iniciando OpenCode Proxy Server
echo ============================================================
echo.

REM Verificar se já está rodando
curl -s http://127.0.0.1:8111/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Proxy já está rodando na porta 8111
) else (
    echo [1/2] Iniciando OpenCode Proxy Server...
    start /B .venv\Scripts\python.exe opencode_proxy.py
    timeout /t 2 /nobreak >nul
    echo [2/2] Verificando status...
    curl -s http://127.0.0.1:8111/health
    echo.
)

echo.
echo ============================================================
echo  Proxy Server pronto!
echo ============================================================
echo.
echo Configuração:
echo   OPENCODE_BASE_URL=http://127.0.0.1:8111/v1
echo.
echo Comandos:
echo   python lotoscope_agents.py delegate "pergunta"
echo   python lotoscope_agents.py call-llm analyst "tarefa"
echo.
pause
