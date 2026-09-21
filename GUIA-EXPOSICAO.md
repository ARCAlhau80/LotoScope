# LotoScope — Guia de Exposição Externa

## Como Usar (resumo)

```bat
start_external.bat
```

O script:

1. Localiza o `ngrok` (pasta dedicada, WinGet ou PATH).
2. Sobe o dashboard Next.js em `http://0.0.0.0:3003` (janela separada).
3. Aguarda o servidor responder em `127.0.0.1:3003`.
4. Mata túneis ngrok antigos e abre o túnel para `127.0.0.1:3003` no domínio abaixo.
5. Captura a URL pública via API local do ngrok (`127.0.0.1:4040/api/tunnels`).
6. Salva a URL em `URL_EXTERNA.txt`.
7. **Fica aberto** — o túnel só funciona enquanto a janela estiver aberta. Pressione uma tecla para parar.

## URL Pública

```
https://uncontaminated-unplighted-jolynn.ngrok-free.dev
```

> Mesmo domínio usado no IASMART-QUEEN. Como o domínio suporta **um túnel por vez**, o túnel do IASMART-QUEEN precisa estar parado. O script já encerra qualquer ngrok em execução ao iniciar.

> **Importante (ngrok free):** ao abrir a URL pela primeira vez, o ngrok mostra uma página de aviso ("You are about to visit…"). Clique em **Visit Site** para continuar.

## Configuração

- **Domínio:** por padrão usa `uncontaminated-unplighted-jolynn.ngrok-free.dev`. Para trocar, crie `NGROK_DOMAIN.txt` na raiz do projeto com o novo domínio (ex.: `https://meuapp.ngrok-free.dev`).
- **Authtoken:** configurado em `%LOCALAPPDATA%\ngrok\ngrok.yml`. Se precisar reconfigurar:
  ```
  %LOCALAPPDATA%\Programs\ngrok\ngrok.exe config add-authtoken SEU_TOKEN
  ```
- **Banco de dados:** o dashboard lê o SQL Server local (padrão `localhost` / `sa`). O servidor Next.js faz as consultas localmente; quem acessa de fora só vê a UI + API.

## O que fica exposto

O dashboard completo (Next.js em `:3003`), incluindo:

- UI web + todas as rotas `/api/*` (dashboard-data, jogos-diversos, ranking, ai-analysis, chat, apostador…).
- As análises/Predições (Poisson, colunas posicionais, gerador diversificado etc.) usam o histórico e o banco local.

## ⚠️ Segurança — leia antes de expor

- **O dashboard NÃO tem autenticação.** Qualquer pessoa com a URL pode acessar.
- Rotas sensíveis estão expostas, incluindo `/api/apostador/bet` (aposta automatizada) e `/api/apostador/parse`. **Não** exponha se não for estritamente para testes controlados.
- Use apenas para testes rápidos e **pare o túnel ao terminar** (tecla no `start_external.bat` ou `taskkill /f /im ngrok.exe`).

## Troubleshooting

| Erro | Causa / Solução |
|------|-----------------|
| `ERR_NGROK_3200` (endpoint offline) | Túnel não está ativo. Rode `start_external.bat` e mantenha a janela aberta. |
| `ERR_NGROK_8012` (upstream refused) | O servidor não respondeu em `127.0.0.1:3003`. Verifique a janela "LotoScope Dashboard Server" e se a porta 3003 está livre (`netstat -ano \| findstr 3003`). |
| `[ERRO] ngrok nao respondeu` | Authtoken não configurado ou domínio não reservado no dashboard.ngrok.com. |
| "You are about to visit…" | Página de aviso do ngrok free — clique em **Visit Site**. |
| Domínio já em uso | Outro túnel (ex.: IASMART-QUEEN) está usando o mesmo domínio. Pare-o e rode de novo. |

## Parar tudo

```powershell
taskkill /f /im ngrok.exe
# e feche a janela "LotoScope Dashboard Server"
```

## Dashboard local do ngrok (tráfego)

```
http://127.0.0.1:4040
```