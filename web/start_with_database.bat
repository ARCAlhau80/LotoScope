@echo off
echo.
echo 🔧 LotoScope Web - Instalação com Integração de Banco
echo ====================================================
echo.

REM Verificar se estamos no diretório correto
if not exist "backend\app.py" (
    echo ❌ Erro: Execute este script a partir da pasta web/
    echo    Diretório atual: %CD%
    pause
    exit /b 1
)

echo 📂 Diretório: %CD%
echo.

REM Ir para o diretório backend
cd backend

echo 📦 Instalando dependências básicas...
pip install Flask Flask-CORS python-dotenv requests

echo.
echo 🗄️ Tentando instalar pyodbc para integração com banco...
echo    Isso pode falhar se não houver compilador C++
echo.

REM Tentar diferentes métodos de instalação do pyodbc
echo ⚡ Método 1: Instalação padrão
pip install pyodbc

if %errorlevel% equ 0 (
    echo ✅ pyodbc instalado com sucesso!
    set PYODBC_INSTALLED=true
    goto :start_server
) else (
    echo ⚠️ Instalação padrão falhou, tentando versão pré-compilada...
)

echo ⚡ Método 2: Tentando versão específica
pip install pyodbc==4.0.35

if %errorlevel% equ 0 (
    echo ✅ pyodbc versão 4.0.35 instalado!
    set PYODBC_INSTALLED=true
    goto :start_server
) else (
    echo ⚠️ Versão específica falhou...
)

echo ⚡ Método 3: Tentando wheel pré-compilado
pip install --only-binary=all pyodbc

if %errorlevel% equ 0 (
    echo ✅ pyodbc wheel instalado!
    set PYODBC_INSTALLED=true
    goto :start_server
) else (
    echo ⚠️ Wheel pré-compilado falhou...
)

echo.
echo 🔄 pyodbc não foi instalado, mas o sistema funcionará em modo simulação
echo    Todas as funcionalidades da interface estarão disponíveis
echo    Apenas não haverá integração real com o banco de dados
echo.
set PYODBC_INSTALLED=false

:start_server
echo.
echo 🌐 Iniciando servidor Flask...
echo.
echo 📍 URLs disponíveis:
echo    Interface: http://localhost:5000
echo    API Health: http://localhost:5000/api/health
echo.
echo 💡 Status:
if "%PYODBC_INSTALLED%"=="true" (
    echo    ✅ Banco de dados: Integração completa
) else (
    echo    ⚠️ Banco de dados: Modo simulação
)
echo    ✅ Interface: Totalmente funcional
echo    ✅ Cálculos: Algoritmos inteligentes
echo.
echo ⏳ Iniciando em 3 segundos...
echo    Para parar: Ctrl+C
echo.
timeout /t 3 /nobreak >nul

python app.py

echo.
echo 🔚 Servidor finalizado
pause