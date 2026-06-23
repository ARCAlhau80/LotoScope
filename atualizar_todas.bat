@echo off
chcp 65001 >nul
title LotoScope - Atualizador de Banco de Dados
cd /d "%~dp0"

echo ============================================
echo LotoScope - Atualizador Multi-Loteria
echo ============================================
echo.

python atualizar_todas.py
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] Erro durante atualizacao - veja os logs acima.
    pause
    exit /b %errorlevel%
)

echo.
echo ============================================
echo Todas as 9 loterias atualizadas!
echo ============================================
pause