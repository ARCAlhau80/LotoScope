@echo off
title MCP Graph Dashboard - LotoScope
echo ========================================
echo    MCP Graph Dashboard - LotoScope
echo ========================================
echo.

set PATH=C:\Program Files\nodejs;%PATH%
cd /d "C:\Users\AR CALHAU\source\repos\LotoScope"

echo Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Node.js nao encontrado!
    echo Instale com: winget install OpenJS.NodeJS.LTS
    pause
    exit /b 1
)

echo Node.js OK
echo Iniciando servidor na porta 3000...
echo.
echo Dashboard: http://localhost:3000
echo Pressione Ctrl+C para parar
echo ========================================
echo.

npx -y @mcp-graph-workflow/mcp-graph serve --port 3000
pause
