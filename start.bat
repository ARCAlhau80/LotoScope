@echo off
title LotoScope - All Services
cd /d "%~dp0"
color 0A

echo ================================================
echo   LotoScope - Iniciando todos os servicos
echo ================================================
echo.

:: Verificar Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado!
    pause
    exit /b 1
)
echo [OK] Node.js encontrado

:: Verificar Ollama
set "OLLAMA_PATH=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not exist "%OLLAMA_PATH%" (
    echo [AVISO] Ollama nao encontrado em %OLLAMA_PATH%
    echo         Chat usara OpenRouter como fallback
) else (
    echo [OK] Ollama encontrado
)

echo.
echo ================================================
echo  Iniciando servicos em paralelo...
echo ================================================
echo.

:: 1. Ollama (porta 11434)
if exist "%OLLAMA_PATH%" (
    echo [1/2] Ollama (http://localhost:11434)
    start "Ollama" cmd /c "title Ollama && "%OLLAMA_PATH%" serve"
    timeout /t 3 /nobreak >nul
)

:: 2. Next.js Dashboard (porta 3003)
echo [2/2] Next.js Dashboard (http://localhost:3003)
start "Next.js Dashboard" cmd /c "title Next.js Dashboard && cd /d "%~dp0dashboard" && npx next dev --port 3003"

echo.
echo ================================================
echo  Todos os servicos foram iniciados!
echo ================================================
echo.
echo  Ollama:              http://localhost:11434
echo  Next.js Dashboard:   http://localhost:3003
echo.
echo  Pressione qualquer tecla para abrir o dashboard...
echo  Feche esta janela para encerrar todos.
echo ================================================
echo.

pause >nul
start http://localhost:3003
