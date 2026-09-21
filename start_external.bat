@echo off
title LotoScope - Exposicao Externa (teste)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_external.ps1"
if errorlevel 1 (
    echo.
    echo [LotoScope] Falha ao iniciar. Veja a mensagem acima.
    pause
)