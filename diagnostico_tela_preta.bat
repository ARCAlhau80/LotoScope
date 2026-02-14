@echo off
REM ==================================================
REM SCRIPT DE DIAGN脫STICO - TELA PRETA LOTOSCOPE
REM ==================================================

echo 🔍 VERIFICANDO CAUSAS DA TELA PRETA...
echo.

echo 📋 1. VERIFICANDO PROCESSOS PYTHON ATIVOS:
tasklist /FI "IMAGENAME eq python.exe" /FI "STATUS eq running"
if %errorlevel% neq 0 (
    echo ✅ Nenhum processo Python ativo
) else (
    echo ⚠️ PROCESSOS PYTHON ENCONTRADOS!
)
echo.

echo 📋 2. VERIFICANDO JANELAS COM T脥TULO VAZIO OU SUSPEITAS:
echo Janelas potencialmente problem谩ticas:
powershell -Command "Get-Process | Where-Object {$_.MainWindowTitle -eq '' -and $_.ProcessName -notlike 'svchost*' -and $_.ProcessName -notlike 'System*'} | Select-Object ProcessName, Id, @{Name='WindowTitle';Expression={if($_.MainWindowTitle -eq '') {'[VAZIO]'} else {$_.MainWindowTitle}}} | Format-Table -AutoSize"
echo.

echo 📋 3. VERIFICANDO EXTENS찾ES VS CODE ATIVAS:
echo Processos VS Code que podem estar abrindo janelas:
tasklist /FI "IMAGENAME eq Code.exe" | find "Code.exe"
echo.

echo 📋 4. VERIFICANDO AGENDAMENTOS SUSPEITOS:
echo Tarefas agendadas relacionadas a Python:
schtasks /query /fo LIST | findstr /I "python\|loto\|script"
echo.

echo 📋 5. VERIFICANDO ARQUIVOS .BAT NO DIRET脫RIO:
echo Arquivos batch que podem executar automaticamente:
dir "C:\Users\AR CALHAU\source\repos\LotoScope\*.bat" /s /b
echo.

echo 💡 RECOMENDA플ES:
echo.
echo 1️⃣ Se a tela preta aparece ao trabalhar no VS Code:
echo    - Desative extens천es desnecessárias
echo    - Reinicie o VS Code
echo.
echo 2️⃣ Se aparece aleatoriamente:
echo    - Verifique se algum site no navegador tem pop-ups
echo    - Feche abas desnecessárias do Chrome/Edge
echo.
echo 3️⃣ Se aparece ap처s executar scripts:
echo    - Execute: python super_menu.py
echo    - Pressione 0 para sair corretamente
echo.
echo 4️⃣ Para monitoramento cont죾uo:
echo    - Execute: python monitor_processos.py monitor
echo.

pause