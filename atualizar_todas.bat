@echo off
chcp 65001 >nul
title LotoScope - Atualizador de Banco de Dados
cd /d "%~dp0"

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

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_lotomania import AtualizadorLotomania; AtualizadorLotomania().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Lotomania & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_diadesorte import AtualizadorDiaDeSorte; AtualizadorDiaDeSorte().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro no Dia de Sorte & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_timemania import AtualizadorTimemania; AtualizadorTimemania().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Timemania & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_supersete import AtualizadorSuperSete; AtualizadorSuperSete().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro no Super Sete & pause
echo.

python -c "import sys; sys.path.insert(0, '.'); from shared.loterias.atualizador_milionaria import AtualizadorMilionaria; AtualizadorMilionaria().atualizar_completo(qtde_por_vez=5)"
if %errorlevel% neq 0 echo ⚠️ Erro na Mais Milionária & pause
echo.

echo ============================================
echo   ✅ 9 loterias atualizadas!
echo ============================================
pause
