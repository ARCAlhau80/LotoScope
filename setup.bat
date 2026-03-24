@echo off
cd /d "%~dp0"
title IA Squad - Setup Menu
color 0B

set "ISGT_PATH=C:\Users\AR CALHAU\source\repos\ISGT"

:MENU
cls
echo.
echo  ============================================
echo   IA Squad - Setup Menu
echo  ============================================
echo.
echo   Projeto: %CD%
echo   Template: %ISGT_PATH%
echo.
echo  --------------------------------------------
echo   [1] Semi-Automatico  (detecta + confirma)
echo   [2] Automatico       (detecta + aplica)
echo   [3] Manual           (preenche tudo)
echo  --------------------------------------------
echo   [4] Alterar caminho do template
echo   [5] Sair
echo  --------------------------------------------
echo.
set /p OPT="  Escolha [1-5]: "

if "%OPT%"=="1" goto SEMI
if "%OPT%"=="2" goto AUTO
if "%OPT%"=="3" goto MANUAL
if "%OPT%"=="4" goto TEMPLATE
if "%OPT%"=="5" goto FIM
echo.
echo   Opcao invalida!
timeout /t 2 >nul
goto MENU

:TEMPLATE
echo.
set /p ISGT_PATH="  Novo caminho do template: "
if not exist "%ISGT_PATH%\setup-ia-squad.ps1" (
    echo.
    echo   ERRO: setup-ia-squad.ps1 nao encontrado em "%ISGT_PATH%"
    pause
)
goto MENU

:SEMI
echo.
echo   Modo Semi-Automatico: detecta projeto e pede confirmacao...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ISGT_PATH%\setup-ia-squad.ps1"
goto DONE

:AUTO
echo.
echo   Modo Automatico: detecta projeto e aplica sem perguntas...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ISGT_PATH%\setup-ia-squad.ps1" -Auto
goto DONE

:MANUAL
echo.
set /p P_NAME="  Nome do projeto: "
set /p P_DESC="  Descricao: "
set /p P_LANG="  Linguagem (ex: Java, Python, TypeScript): "
set /p P_FW="  Framework (ex: Spring Boot, FastAPI, React): "
set /p P_BUILD="  Comando de build: "
set /p P_TEST="  Comando de teste: "
set /p P_RUN="  Comando de run: "
set /p P_DB="  Banco de dados (ex: PostgreSQL, Oracle): "
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ISGT_PATH%\setup-ia-squad.ps1" -Auto -ProjectName "%P_NAME%" -ProjectDesc "%P_DESC%" -Language "%P_LANG%" -Framework "%P_FW%" -BuildCmd "%P_BUILD%" -TestCmd "%P_TEST%" -RunCmd "%P_RUN%" -DbType "%P_DB%"
goto DONE

:DONE
echo.
echo  ============================================
echo   Setup concluido!
echo  ============================================
echo.
pause
goto MENU

:FIM
echo.
echo   Ate mais!
echo.
timeout /t 1 >nul
