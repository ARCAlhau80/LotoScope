@echo off
title Super Menu Lotofacil Web - Configurador Firewall
color 0A

echo.
echo 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
echo 🎯 SUPER MENU LOTOFACIL - CONFIGURADOR WEB
echo 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
echo.
echo ⚡ Resolvendo problemas de Firewall do Windows...
echo.

REM Verifica se está rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Executando como Administrador - OK
) else (
    echo ⚠️  IMPORTANTE: Para resolver firewall, execute como Administrador
    echo    Clique com botao direito no arquivo e "Executar como administrador"
    echo.
    echo 🔄 Tentando executar normalmente...
)

echo.
echo 🛡️ Configurando regras de firewall para Streamlit...
echo.

REM Adiciona regra para permitir Python no firewall
netsh advfirewall firewall add rule name="Python Streamlit" dir=in action=allow program="C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python39_64\python.exe" enable=yes 2>nul
if %errorLevel% == 0 (
    echo ✅ Regra de firewall adicionada para Python
) else (
    echo ⚠️  Não foi possível adicionar regra automaticamente
)

REM Adiciona regra para porta 8501
netsh advfirewall firewall add rule name="Streamlit Port 8501" dir=in action=allow protocol=TCP localport=8501 enable=yes 2>nul
if %errorLevel% == 0 (
    echo ✅ Porta 8501 liberada no firewall
) else (
    echo ⚠️  Não foi possível liberar porta automaticamente
)

echo.
echo 🌐 Iniciando aplicação web em modo seguro...
echo.
echo 📱 URLs de Acesso:
echo    Local:   http://localhost:8501
echo    Rede:    http://127.0.0.1:8501
echo.
echo 💡 DICAS IMPORTANTES:
echo    - Se aparecer popup do firewall, clique em "Permitir"
echo    - Use Ctrl+C para parar o servidor
echo    - Mantenha esta janela aberta
echo.

REM Define variáveis para evitar conflitos
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=127.0.0.1
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo 🚀 Iniciando Super Menu Web...
echo ================================================
"C:/Program Files (x86)/Microsoft Visual Studio/Shared/Python39_64/python.exe" -m streamlit run super_menu_web.py --server.address=127.0.0.1 --server.port=8501 --browser.gatherUsageStats=false

echo.
echo 🔴 Servidor encerrado.
echo.
pause
