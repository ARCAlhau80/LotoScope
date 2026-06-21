@echo off
chcp 65001 >nul
title LotoScope - Atualizador de Banco de Dados
cd /d "%~dp0.."

echo ============================================
echo   LotoScope - Atualizador Multi-Loteria
echo ============================================
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_lotofacil import AtualizadorLotofacil; AtualizadorLotofacil().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Lotofácil & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_megasena import AtualizadorMegaSena; AtualizadorMegaSena().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Mega-Sena & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_quina import AtualizadorQuina; AtualizadorQuina().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Quina & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_duplasena import AtualizadorDuplaSena; AtualizadorDuplaSena().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Dupla Sena & pause
echo.

echo ============================================
echo   ✅ Todas as loterias atualizadas!
echo ============================================
pause
