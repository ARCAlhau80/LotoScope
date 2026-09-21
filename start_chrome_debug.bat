@echo off
title Apostador CAIXA - Iniciar Chrome com Remote Debug
echo ============================================================
echo   Apostador CAIXA - Chrome com Remote Debugging (porta 9222)
echo ============================================================
echo.
echo Este script abre o seu Chrome com o SEU perfil/logado e com a
echo porta 9222 habilitada. Depois rode o Apostador em modo --attach
echo para preencher os volantes DENTRO desta janela (ja logado).
echo.
echo IMPORTANTE: feche todas as janelas do Chrome antes de rodar
echo (o Chrome so aceita a porta de debug se nao houver outra
echo instancia usando o mesmo perfil).
echo.
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "PROFILE=%LOCALAPPDATA%\Google\Chrome\User Data"
set "DEBUG_PORT=9222"
echo Abrindo Chrome (perfil: %PROFILE%) na porta %DEBUG_PORT%...
start "" "%CHROME%" --remote-debugging-port=%DEBUG_PORT% --user-data-dir="%PROFILE%" "https://www.loteriasonline.caixa.gov.br/silce-web/#/home"
echo.
echo Chrome aberto. Faca login no portal se necessario.
echo Agora rode: apostador_automacao_cli.py <arquivo> --loteria <id> --attach --debug-port 9222
pause
