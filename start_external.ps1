$ErrorActionPreference = 'Continue'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "============================================================"
Write-Host "  LotoScope Dashboard - Exposicao externa para teste"
Write-Host "============================================================"
Write-Host ""

function Escrever([string]$msg) { Write-Host $msg }

# --- 1. Localizar ngrok -------------------------------------------------
$ngrok = $null
$candidates = @(
    "$env:LOCALAPPDATA\Programs\ngrok\ngrok.exe"
)
$winget = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Ngrok.Ngrok*" -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName 'ngrok.exe' }
$candidates += $winget
$cmdNgrok = Get-Command ngrok -ErrorAction SilentlyContinue
if ($cmdNgrok) { $candidates += $cmdNgrok.Source }

foreach ($c in $candidates) {
    if ($c -and (Test-Path $c)) { $ngrok = $c; break }
}
if (-not $ngrok) {
    Escrever "[ERRO] ngrok nao encontrado. Instale com: winget install Ngrok.Ngrok"
    Read-Host "Pressione Enter para sair"
    exit 1
}
Escrever "[LotoScope] ngrok OK: $ngrok"

# --- 2. Dominio ngrok ---------------------------------------------------
$domain = 'https://uncontaminated-unplighted-jolynn.ngrok-free.dev'
$domainFile = Join-Path $root 'NGROK_DOMAIN.txt'
if (Test-Path $domainFile) {
    $domain = (Get-Content $domainFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if (-not $domain) { $domain = 'https://uncontaminated-unplighted-jolynn.ngrok-free.dev' }
}
Escrever "[LotoScope] Dominio ngrok: $domain"
Escrever "[LotoScope] Para trocar, crie NGROK_DOMAIN.txt na raiz do projeto."
Escrever ""

# --- 3. Garantir dashboard ativo em 3003 --------------------------------
$serverUp = $false
try {
    $r = Invoke-WebRequest 'http://127.0.0.1:3003' -UseBasicParsing -TimeoutSec 3
    $serverUp = $true
} catch {}

if ($serverUp) {
    Escrever "[LotoScope] Dashboard ja ativo em http://127.0.0.1:3003 (reusando)."
} else {
    Escrever "[LotoScope] Subindo dashboard em http://0.0.0.0:3003 (janela separada)..."
    Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', ('"' + (Join-Path $root 'start_dashboard_server.bat') + '"')
    $serverUp = $false
    for ($i = 0; $i -lt 90; $i++) {
        Start-Sleep -Milliseconds 1000
        try {
            Invoke-WebRequest 'http://127.0.0.1:3003' -UseBasicParsing -TimeoutSec 2 | Out-Null
            $serverUp = $true
            break
        } catch {}
        if ($i % 15 -eq 14) { Escrever "  ... aguardando o dashboard subir ($($i + 1)s)" }
    }
    if (-not $serverUp) {
        Escrever "[ERRO] O dashboard nao respondeu em 127.0.0.1:3003 em 90s."
        Escrever "       Verifique a janela 'LotoScope Dashboard Server' aberta."
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}
Escrever "[LotoScope] Servidor pronto."
Escrever ""

# --- 4. Tunnel ngrok -----------------------------------------------------
Escrever "[LotoScope] Encerrando tunnels ngrok antigos..."
Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

Escrever "[LotoScope] Iniciando tunnel ngrok em background..."
$proc = Start-Process -FilePath $ngrok -ArgumentList @('http', '127.0.0.1:3003', "--url=$domain") -WindowStyle Hidden -PassThru
if (-not $proc) {
    Escrever "[ERRO] Nao foi possivel iniciar o ngrok."
    Read-Host "Pressione Enter para sair"
    exit 1
}

# --- 5. Capturar URL publica ---------------------------------------------
$url = $null
for ($i = 0; $i -lt 30 -and -not $url; $i++) {
    Start-Sleep -Milliseconds 1000
    try {
        $t = Invoke-RestMethod 'http://127.0.0.1:4040/api/tunnels' -TimeoutSec 3
        $url = @($t.tunnels | Select-Object -First 1 -ExpandProperty public_url)[0]
    } catch {}
}

if (-not $url) {
    Escrever ""
    Escrever "[ERRO] ngrok nao respondeu com uma URL publica."
    Escrever "       Dominio: $domain"
    Escrever "       Verifique o authtoken: $ngrok config add-authtoken SEU_TOKEN"
    Escrever "       Verifique se o dominio esta reservado em https://dashboard.ngrok.com/domains"
    Escrever "       Veja o dashboard local do ngrok: http://127.0.0.1:4040"
    Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue
    Read-Host "Pressione Enter para sair"
    exit 1
}

# --- 6. Exibir e manter aberto -------------------------------------------
Escrever ""
Escrever "============================================================"
Escrever "  SERVICO EXTERNO ATIVO"
Escrever "  URL:      $url"
Escrever "============================================================"
try { Set-Content -Path (Join-Path $root 'URL_EXTERNA.txt') -Value $url -Encoding ascii } catch {}
Escrever "  URL salva em URL_EXTERNA.txt"
Escrever ""
Escrever "  ATENCAO: o dashboard NAO tem autenticacao. Use apenas para"
Escrever "  testes controlados e pare quando terminar."
Escrever ""
Escrever "  Deixe esta janela ABERTA. O tunnel so funciona enquanto"
Escrever "  ela estiver aberta."
Escrever ""
Read-Host "Pressione Enter para PARAR o tunnel"
Escrever "[LotoScope] Parando tunnel..."
Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue
Escrever "[LotoScope] Tunnel parado."
Escrever "  Para parar o servidor tambem, feche a janela 'LotoScope Dashboard Server'."
exit 0