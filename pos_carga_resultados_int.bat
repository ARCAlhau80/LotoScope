@echo off
title Pos-Carga Resultados_INT - LotoScope
echo ========================================
echo    POS-CARGA RESULTADOS_INT - LOTOSCOPE
echo ========================================
echo.

cd /d "C:\Users\AR CALHAU\source\repos\LotoScope"

set "PYTHON_EXE=C:\Users\AR CALHAU\source\repos\LotoScope\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERRO: Python da venv nao encontrado em:
    echo   %PYTHON_EXE%
    echo.
    echo Ative/crie a venv antes de rodar este pos-carga.
    pause
    exit /b 1
)

echo Recomputando campos posicionais da Resultados_INT...
echo.
"%PYTHON_EXE%" "C:\Users\AR CALHAU\source\repos\LotoScope\pos_carga_resultados_int.py"

echo.
echo ========================================
echo   EXECUCAO FINALIZADA
echo ========================================
pause