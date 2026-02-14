@echo off
echo 🚀 Iniciando LotoScope Web...
echo.

REM Verificar se estamos no diretório correto
if not exist "backend\app.py" (
    echo ❌ Erro: Execute este script a partir da pasta web/
    pause
    exit /b 1
)

echo 📦 Instalando dependências...
cd backend
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo.
echo 🌐 Iniciando servidor Flask...
echo 📍 Acesse: http://localhost:5000
echo.
echo ⚠️  Para parar o servidor, pressione Ctrl+C
echo.

python app.py

pause