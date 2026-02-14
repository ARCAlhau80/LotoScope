@echo off
echo.
echo 🚀 LotoScope Web - Inicialização Simplificada
echo ============================================
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

if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Erro ao instalar algumas dependências, mas continuando...
    echo    A aplicação pode funcionar em modo limitado
    echo.
)

echo.
echo 🌐 Iniciando servidor Flask...
echo.
echo 📍 URLs disponíveis:
echo    Interface: http://localhost:5000
echo    API Health: http://localhost:5000/api/health
echo.
echo 💡 Dicas:
echo    - Interface totalmente funcional
echo    - Modo simulação (sem banco de dados)
echo    - Para parar: Ctrl+C
echo.
echo ⏳ Iniciando em 3 segundos...
timeout /t 3 /nobreak >nul

python app.py

echo.
echo 🔚 Servidor finalizado
pause